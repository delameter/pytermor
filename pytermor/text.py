# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""
"Front-end" module of the library. Contains classes supporting high-level
operations such as nesting-aware style application, concatenating and cropping
of styled strings before the rendering, text alignment and wrapping, etc.
"""
from __future__ import annotations

import math
import re
import sys
import textwrap
import typing as t
from abc import abstractmethod, ABC
from collections import deque
from typing import overload

from .utilstr import trace, measure
from .color import IColor
from .common import (
    LogicError,
    Align,
    ArgTypeError,
    logger,
    flatten1,
    get_terminal_width,
    get_preferable_wrap_width,
)
from .config import get_config
from .renderer import IRenderer, RendererManager
from .style import Style, make_style, NOOP_STYLE, FT

RT = t.TypeVar("RT", str, "IRenderable")
"""
:abbr:`RT (Renderable type)` includes regular *str*\\ s as well as `IRenderable` 
implementations.
"""


class IRenderable(t.Sized, ABC):
    """
    I
    """

    @abstractmethod
    def __len__(self) -> int:
        """raise NotImplementedError"""

    @abstractmethod
    def __eq__(self, o: t.Any) -> bool:
        """raise NotImplementedError"""

    def __add__(self, other: RT) -> IRenderable:
        ...

    def __iadd__(self, other: RT) -> IRenderable:
        ...

    def __radd__(self, other: RT) -> IRenderable:
        ...

    @abstractmethod
    def _as_fragments(self) -> t.List[Fragment]:
        """ a-s """
        ...

    @abstractmethod
    def render(self, renderer: IRenderer | t.Type[IRenderer] = None) -> str:
        """pass"""

    @abstractmethod
    def set_width(self, width: int):
        """raise NotImplementedError"""

    @property
    @abstractmethod
    def has_width(self) -> bool:
        """return self._width is not None"""

    @property
    @abstractmethod
    def allows_width_setup(self) -> bool:
        """return False"""

    def _resolve_renderer(
        self, renderer: IRenderer | t.Type[IRenderer] = None
    ) -> IRenderer:
        if isinstance(renderer, type):
            return renderer()
        if renderer is None:
            return RendererManager.get_default()
        return renderer

    def _ensure_fragments(self, *args: Fragment):
        for arg in args:
            if not isinstance(arg, Fragment):
                raise ArgTypeError(actual_type=type(arg))


class Fragment(IRenderable):
    """
    <Immutable>

    Can be formatted with f-strings. The text ``:s`` mode is required.
    Supported features:

      - width [of the result];
      - max length [of the content];
      - alignment;
      - filling.

    >>> f"{Fragment('1234567890'):*^8.4s}"
    '**1234**'

    :param str string:
    :param FT fmt:
    :param bool close_this:
    :param bool close_prev:
    """

    def __init__(
        self,
        string: str = "",
        fmt: FT = None,
        *,
        close_this: bool = True,
        close_prev: bool = False,
    ):
        self._string = string
        self._style = make_style(fmt)
        self._close_this = close_this or close_prev
        self._close_prev = close_prev

    def __eq__(self, o: t.Any) -> bool:
        if not isinstance(o, type(self)):
            return False
        return (
            self._string == o._string
            and self._style == o._style
            and self._close_this == o._close_this
            and self._close_prev == o._close_prev
        )

    def __len__(self) -> int:
        return len(self._string)

    def __repr__(self):
        max_sl = 9
        sample = self._string[:max_sl] + ("‥" * (len(self._string) > max_sl))
        props_set = [f'({len(self._string)}, "{sample}")', repr(self._style)]
        flags = []
        if self._close_this:
            flags.append("+CT")
        if self._close_prev:
            flags.append("+CP")
        props_set.append(" ".join(flags))

        return f"<{self.__class__.__qualname__}>[" + ", ".join(props_set) + "]"

    def __add__(self, other: str | Fragment) -> Fragment | Text:
        if isinstance(other, str):
            return Fragment(self._string + other, self._style)
        self._ensure_fragments(other)
        return Text(self, other)

    def __iadd__(self, other: str | Fragment) -> Fragment | Text:
        return self.__add__(other)

    def __radd__(self, other: str | Fragment) -> Fragment | Text:
        if isinstance(other, str):
            return Fragment(other + self._string, self._style)
        self._ensure_fragments(other)
        return Text(other, self)

    def __format__(self, format_spec: str) -> str:
        formatted = self._string.__format__(format_spec)
        return self._resolve_renderer().render(formatted, self._style)

    def _as_fragments(self) -> t.List[Fragment]:
        return [self]

    @property
    def string(self) -> str:
        return self._string

    @property
    def style(self) -> Style:
        return self._style

    @property
    def close_this(self) -> bool:
        return self._close_this

    @property
    def close_prev(self) -> bool:
        return self._close_prev

    @property
    def has_width(self) -> bool:
        return True

    @property
    def allows_width_setup(self) -> bool:
        return False

    def render(self, renderer: IRenderer | t.Type[IRenderer] = None) -> str:
        return self._resolve_renderer(renderer).render(self._string, self._style)

    def set_width(self, width: int):
        self._string = f"{self._string:{width}.{width}s}"


class FrozenText(IRenderable):
    """
    :param align: default is left
    """

    @overload
    def __init__(
        self,
        string: str,
        fmt: FT = NOOP_STYLE,
        *,
        width: int = None,
        align: str | Align = None,
        fill: str = " ",
        overflow: str = "",
        pad: int = 0,
        pad_styled: bool = True,
    ):
        ...

    @overload
    def __init__(
        self,
        *fragments: Fragment,
        width: int = None,
        align: str | Align = None,
        fill: str = " ",
        overflow: str = "",
        pad: int = 0,
        pad_styled: bool = True,
    ):
        ...

    def __init__(
        self,
        *args,
        width: int = None,
        align: str | Align = None,
        fill: str = " ",
        overflow: str = "",
        pad: int = 0,
        pad_styled: bool = True,
    ):
        self._fragments = deque()
        if len(args):
            if isinstance(args[0], str) and (
                len(args) == 1
                or isinstance(args[1], (type(None), int, str, IColor, Style))
            ):
                self._fragments.append(Fragment(*args[0:2]))
            else:
                self._ensure_fragments(*args)
                self._fragments.extend(args)

        self._width = width
        self._align = Align.resolve(align)

        self._fill = fill
        if len(self._fill) != 1:
            raise ValueError("Fill string should be 1-char long")

        self._overflow = overflow
        self._pad = pad
        self._pad_styled = pad_styled

    def __len__(self) -> int:
        return self._width or sum(len(frag) for frag in self._fragments)

    def __eq__(self, o: t.Any) -> bool:
        if not isinstance(o, type(self)):
            return False
        return (
            self._fragments == o._fragments
            and self._width == o._width
            and self._align == o._align
            and self._fill == o._fill
            and self._overflow == o._overflow
        )

    def __str__(self) -> str:
        raise LogicError("Casting to str is prohibited, use render() instead.")

    def __repr__(self) -> str:
        frags = len(self._fragments)
        result = f"<{self.__class__.__qualname__}>[F={frags}%s]"
        if frags == 0:
            return result % ""
        return result % (", " + ", ".join([repr(f) for f in self._fragments]))

    def __add__(self, other: str | Fragment) -> FrozenText:
        return self.append(*as_fragments(other))

    def __iadd__(self, other: str | Fragment) -> FrozenText:
        raise LogicError("FrozenText is immutable")

    def __radd__(self, other: str | Fragment) -> FrozenText:
        return self.prepend(*as_fragments(other))

    def _as_fragments(self) -> t.List[Fragment]:
        return [*self._fragments]

    @property
    def allows_width_setup(self) -> bool:
        return True

    @property
    def has_width(self) -> bool:
        return self._width is not None

    def render(self, renderer: IRenderer | t.Type[IRenderer] = None) -> str:
        max_len = len(self) + self._pad
        if self._width is not None:
            max_len = max(0, self._width - self._pad)

        result_parts: t.List[t.Tuple[str, Style]] = []
        cur_len = 0
        cur_frag_idx = 0
        overflow_buf = self._overflow[:max_len]
        overflow_start = max_len - len(overflow_buf)
        attrs_stack: t.Dict[str, t.List[bool | IColor | None]] = {
            attr: [None] for attr in Style.renderable_attributes
        }
        renderer = self._resolve_renderer(renderer)

        while cur_len < max_len and cur_frag_idx < len(self._fragments):
            # cropping and overflow handling
            max_frag_len = max_len - cur_len
            frag = self._fragments[cur_frag_idx]
            frag_part = frag.string[:max_frag_len]
            next_len = cur_len + len(frag_part)
            if next_len > overflow_start:
                overflow_start_rel = overflow_start - next_len
                overflow_frag_len = max_frag_len - overflow_start_rel

                overflow_part = overflow_buf[:overflow_frag_len]
                frag_part = frag_part[:overflow_start_rel] + overflow_part
                overflow_buf = overflow_buf[overflow_frag_len:]

            # attr open
            for attr in Style.renderable_attributes:
                if frag_attr := getattr(frag.style, attr):
                    attrs_stack[attr].append(frag_attr)

            cur_style = Style(**{k: v[-1] for k, v in attrs_stack.items()})
            result_parts.append((frag_part, cur_style))
            cur_len += len(frag_part)
            cur_frag_idx += 1
            if not frag.close_prev and not frag.close_this:
                continue

            # attr closing
            for attr in Style.renderable_attributes:
                if getattr(frag.style, attr):
                    attrs_stack[attr].pop()  # close this
                    if frag.close_prev:
                        attrs_stack[attr].pop()
                    if len(attrs_stack[attr]) == 0:
                        raise LogicError(
                            "There are more closing styles than opening ones, "
                            f'cannot proceed (attribute "{attr}" in {frag})'
                        )

        if (spare_len := (self._width or max_len) - cur_len) >= 0:
            # aligning and filling
            spare_left = 0
            spare_right = 0
            if self._align == Align.LEFT:
                spare_right = spare_len
            elif self._align == Align.RIGHT:
                spare_left = spare_len
            else:
                if spare_len % 2 == 1:
                    spare_right = math.ceil(spare_len / 2)
                else:
                    spare_right = math.floor(spare_len / 2)
                spare_left = spare_len - spare_right

            if not self._pad_styled or len(result_parts) == 0:
                result_parts = [
                    (spare_left * self._fill, NOOP_STYLE),
                    *result_parts,
                    (spare_right * self._fill, NOOP_STYLE),
                ]
            else:
                first_fp, first_st = result_parts.pop(0)
                result_parts.insert(0, ((spare_left * self._fill) + first_fp, first_st))
                last_fp, last_st = result_parts.pop()
                result_parts.append((last_fp + (spare_right * self._fill), last_st))

        return "".join(renderer.render(fp, st) for fp, st in result_parts)

    def append(self, *fragments: Fragment) -> FrozenText:
        self._ensure_fragments(*fragments)
        return FrozenText(*self._fragments, *fragments)

    def prepend(self, *fragments: Fragment) -> FrozenText:
        self._ensure_fragments(*fragments)
        return FrozenText(*fragments, *self._fragments)

    def set_width(self, width: int):
        raise LogicError("FrozenText is immutable")


class Text(FrozenText):
    def __iadd__(self, other: str | Fragment) -> FrozenText:
        return self.append(*as_fragments(other))

    def append(self, *fragments: Fragment) -> Text:
        self._ensure_fragments(*fragments)
        self._fragments.extend(fragments)
        return self

    def prepend(self, *fragments: Fragment) -> Text:
        self._ensure_fragments(*fragments)
        self._fragments.extendleft(fragments)
        return self

    def set_width(self, width: int):
        self._width = width


class TextComposite(IRenderable):
    """
    Simple class-container supporting concatenation of
    any `IRenderable` instances with each other without
    any extra logic on top of it. Renders parts joined
    by an empty string.
    """
    def __init__(self, *parts: t.Iterable[IRenderable]):
        super().__init__()
        self._parts: deque[IRenderable] = deque(*parts)

    def __len__(self) -> int:
        return sum(len(part) for part in self._parts)

    def __eq__(self, o: t.Any) -> bool:
        if not isinstance(o, type(self)):
            return False
        return self._parts == o._parts

    def __add__(self, other: RT) -> IRenderable:
        self._parts.append(other)
        return self

    def __iadd__(self, other: RT) -> IRenderable:
        self._parts.append(other)
        return self

    def __radd__(self, other: RT) -> IRenderable:
        self._parts.appendleft(other)
        return self

    def _as_fragments(self) -> t.List[Fragment]:
        return flatten1([as_fragments(p) for p in self._parts])

    def render(self, renderer: IRenderer | t.Type[IRenderer] = None) -> str:
        return "".join(p.render(self._resolve_renderer(renderer)) for p in self._parts)

    def set_width(self, width: int):
        raise NotImplementedError

    @property
    def has_width(self) -> bool:
        return False

    @property
    def allows_width_setup(self) -> bool:
        return False


class SimpleTable(IRenderable):
    """
    Table class with dynamic (not bound to each other) rows. By defualt expands to
    the maximum width (terminal size).

    Allows 0 or 1 dynamic-width cell in each row, while all the others should be
    static, i.e., be instances of `FrozenText`.

    >>> echo(
    ...     SimpleTable(
    ...     [
    ...         Text("1", width=1),
    ...         Text("word", width=6, align='center'),
    ...         Text("smol string"),
    ...     ],
    ...     [
    ...         Text("2", width=1),
    ...         Text("padded word", width=6, align='center', pad=2),
    ...         Text("biiiiiiiiiiiiiiiiiiiiiiiiiiiiiiig string"),
    ...     ],
    ...     width=30,
    ...     sep="|"
    ... ), file=sys.stdout)
    |1| word |smol string        |
    |2| padd |biiiiiiiiiiiiiiiiii|

    """

    def __init__(
        self,
        *rows: t.Iterable[RT],
        width: int = None,
        sep: str = 2 * " ",
        border_st: Style = NOOP_STYLE,
    ):
        """
        Create

        .. note ::
            All arguments except ``*rows`` are *kwonly*-type args.

        :param rows:
        :param width: Table width, in characters. When omitted, equals to terminal size
                      if applicable, and to fallback value (80) otherwise.
        :param sep:
        :param border_st:
        """
        super().__init__()
        self._width: int = width or get_terminal_width()
        self._column_sep: Fragment = Fragment(sep, border_st)
        self._border_st = border_st
        self._rows: list[list[IRenderable]] = []
        self.add_rows(rows=rows)

    def __len__(self) -> int:
        return sum(flatten1((len(frag) for frag in row) for row in self._rows))

    def __eq__(self, o: t.Any) -> bool:
        if not isinstance(o, type(self)):
            return False
        return self._rows == o._rows

    def __repr__(self) -> str:
        frags = len(flatten1(self._rows))
        result = f"<{self.__class__.__qualname__}>[R={len(self._rows)}, F={frags}]"
        return result

    def _as_fragments(self) -> t.List[Fragment]:
        raise NotImplementedError

    @property
    def allows_width_setup(self) -> bool:
        return True

    @property
    def has_width(self) -> bool:
        return True

    @property
    def row_count(self) -> int:
        return len(self._rows)

    def add_header_row(self, *cells: RT):
        self.add_separator_row()
        self.add_row(*cells)
        self.add_separator_row()

    def add_footer_row(self, *cells: RT):
        self.add_separator_row()
        self.add_row(*cells)
        self.add_separator_row()

    def add_separator_row(self):
        self._rows.append([Fragment("-" * self._width, self._border_st)])

    def add_rows(self, rows: t.Iterable[t.Iterable[RT]]):
        for row in rows:
            self.add_row(*row)

    def add_row(self, *cells: RT):
        fixed_cell_count = sum(
            int(c.has_width) if isinstance(c, IRenderable) else 1 for c in cells
        )
        if fixed_cell_count < len(cells) - 1:
            raise TypeError(
                "Row should have no more than one dynamic width cell, "
                "all the others should be Text instances with fixed width."
            )

        row = [*self._make_row(*cells)]
        if self._sum_len(*row, fixed_only=True) > self._width:
            raise ValueError(f"Row is too long (>{self._width})")
        self._rows.append(row)

    def pass_row(
        self, *cells: RT, renderer: IRenderer | t.Type[IRenderer] = None
    ) -> str:
        renderer = self._resolve_renderer(renderer)
        return self._render_row(renderer, self._make_row(*cells))

    def render(self, renderer: IRenderer | t.Type[IRenderer] = None) -> str:
        renderer = self._resolve_renderer(renderer)
        return "\n".join(self._render_row(renderer, row) for row in self._rows)

    def set_width(self, width: int):
        self._width = width

    def _make_row(self, *cells: RT) -> t.Iterable[IRenderable]:
        yield self._column_sep
        for cell in cells:
            if not isinstance(cell, IRenderable):
                cell = Fragment(cell)
            yield cell
            yield self._column_sep

    def _render_row(self, renderer: IRenderer, row: t.Iterable[IRenderable]) -> str:
        return "".join(self._render_cells(renderer, *row))

    def _render_cells(self, renderer: IRenderer, *row: IRenderable) -> t.Iterable[str]:
        fixed_len = self._sum_len(*row, fixed_only=True)
        free_len = max(0, self._width - fixed_len)
        for cell in row:
            if not cell.has_width and cell.allows_width_setup:
                cell.set_width(free_len)
            yield cell.render(renderer=renderer)

    def _sum_len(self, *row: IRenderable, fixed_only: bool) -> int:
        return sum(len(c) for c in row if not fixed_only or c.has_width)


class _TemplateTag:
    def __init__(
        self,
        set: str | None,
        add: str | None,
        comment: str | None,
        split: str | None,
        close: str | None,
        style: str | None,
    ):
        self.set: str | None = set.replace("@", "") if set else None
        self.add: bool = bool(add)
        self.comment: bool = bool(comment)
        self.split: bool = bool(split)
        self.close: bool = bool(close)
        self.style: str | None = style


class TemplateEngine:
    _TAG_REGEXP = re.compile(
        r"""
        (?:
          (?P<set>@\w+)?
          (?P<add>:)
          |
          (?P<comment>_)
        )
        (?![^\\]\\) (?# ignore [ escaped with single backslash, but not double)
        \[
          (?P<split>\|)?
          (?P<close>-)?
          (?P<style>[\w =]+)
        \]
        """,
        re.VERBOSE,
    )

    _ESCAPE_REGEXP = re.compile(r"([^\\])\\\[")
    _SPLIT_REGEXP = re.compile(r"([^\s,]+)?([\s,]*)")

    def __init__(self, custom_styles: t.Dict[str, Style] = None):
        self._custom_styles: t.Dict[str, Style] = custom_styles or {}

    def parse(self, tpl: str) -> Text:
        result = Text()
        tpl_cursor = 0
        style_buffer = NOOP_STYLE
        split_style = False
        logger.debug(f"Parsing the template (len {tpl}")

        for tag_match in self._TAG_REGEXP.finditer(tpl):
            span = tag_match.span()
            tpl_part = self._ESCAPE_REGEXP.sub(r"\1[", tpl[tpl_cursor: span[0]])
            if len(tpl_part) > 0 or style_buffer != NOOP_STYLE:
                if split_style:
                    for tpl_chunk, sep in self._SPLIT_REGEXP.findall(tpl_part):
                        if len(tpl_chunk) > 0:
                            result += Fragment(tpl_chunk, style_buffer, close_this=True)
                        result += sep
                    # add open style for engine to properly handle the :[-closing] tag:
                    tpl_part = ""
                result += Fragment(tpl_part, style_buffer, close_this=False)

            tpl_cursor = span[1]
            style_buffer = NOOP_STYLE
            split_style = False

            tag = _TemplateTag(**tag_match.groupdict())
            style = self._tag_to_style(tag)
            if tag.set:
                self._custom_styles[tag.set] = style
            elif tag.add:
                if tag.close:
                    result += Fragment("", style, close_prev=True)
                else:
                    style_buffer = style
                    split_style = tag.split
            elif tag.comment:
                pass
            else:
                raise ValueError(f"Unknown tag operand: {_TemplateTag}")

        result += tpl[tpl_cursor:]
        return result

    def _tag_to_style(self, tag: _TemplateTag) -> Style | None:
        if tag.comment:
            return None

        style_attrs = {}
        base_style = NOOP_STYLE

        for style_attr in tag.style.split(" "):
            if style_attr in self._custom_styles.keys():
                if base_style != NOOP_STYLE:
                    raise LogicError(
                        f"Only one custom style per tag is allowed: ({tag.style})"
                    )
                base_style = self._custom_styles[style_attr]
                continue
            if style_attr.startswith("fg=") or style_attr.startswith("bg="):
                style_attrs.update({k: v for k, v in (style_attr.split("="),)})
                continue
            if style_attr in Style.renderable_attributes:
                style_attrs.update({style_attr: True})
                continue
            raise ValueError(f'Unknown style name or attribute: "{style_attr}"')
        return Style(base_style, **style_attrs)


_template_engine = TemplateEngine()


@trace(enabled=get_config().trace_renders)
@measure(template="Rendered in %s")
def render(
    string: RT | t.Iterable[RT] = "",
    fmt: FT = NOOP_STYLE,
    renderer: IRenderer = None,
    parse_template: bool = False,
    *,
    no_log: bool = False,  # noqa
) -> str | t.List[str]:
    """
    .

    :param string: 2
    :param fmt: 2
    :param renderer: 2
    :param parse_template: 2
    :param no_log: 2
    :return:
    """
    if string == "" and not fmt:
        return ""

    if parse_template:
        if not isinstance(string, str):
            raise ValueError("Template parsing is supported for raw strings only.")
        try:
            string = _template_engine.parse(string)
        except (ValueError, LogicError) as e:
            string += f" [pytermor] Template parsing failed with {e}"
        return render(string, fmt, renderer, parse_template=False)

    if isinstance(string, t.Sequence) and not isinstance(string, str):
        return [render(s, fmt, renderer, parse_template) for s in string]

    if isinstance(string, str):
        if not fmt:
            return string
        return Fragment(string, fmt).render(renderer)

    if isinstance(string, IRenderable):
        return string.render(renderer)

    raise ArgTypeError(type(string), "string", fn=render)


def echo(
    string: RT | t.Iterable[RT] = "",
    fmt: FT = NOOP_STYLE,
    renderer: IRenderer = None,
    parse_template: bool = False,
    *,
    nl: bool = True,
    file: t.IO = sys.stdout,
    flush: bool = True,
    wrap: bool | int = False,
    indent_first: int = 0,
    indent_subseq: int = 0,
):
    """
    .

    :param string:
    :param fmt:
    :param renderer:
    :param parse_template:
    :param nl:
    :param file:
    :param flush:
    :param wrap:
    :param indent_first:
    :param indent_subseq:
    """
    end = "\n" if nl else ""
    result = render(string, fmt, renderer, parse_template=parse_template)

    if wrap or indent_first or indent_subseq:
        force_width = wrap if isinstance(wrap, int) else None
        width = get_preferable_wrap_width(force_width)
        result = wrap_sgr(result, width, indent_first, indent_subseq).rstrip("\n")

    print(result, end=end, file=file, flush=flush)


def echoi(
    string: RT | t.Iterable[RT] = "",
    fmt: FT = NOOP_STYLE,
    renderer: IRenderer = None,
    parse_template: bool = False,
    *,
    file: t.IO = sys.stdout,
    flush: bool = True,
):
    """
    echo inline

    :param string:
    :param fmt:
    :param renderer:
    :param parse_template:
    :param file:
    :param flush:
    :return:
    """
    echo(string, fmt, renderer, parse_template, nl=False, file=file, flush=flush)


# fmt: off
@overload
def distribute_padded(max_len: int, *values: str, pad_left: int = 0, pad_right: int = 0) -> str: ...
@overload
def distribute_padded(max_len: int, *values: RT, pad_left: int = 0, pad_right: int = 0) -> Text: ...
# fmt: on
def distribute_padded(max_len: int, *values, pad_left: int = 0, pad_right: int = 0):
    """

    :param max_len:
    :param values:
    :param pad_left:
    :param pad_right:
    :return:
    """
    val_list = list(values)
    if pad_left:
        val_list.insert(0, "")
    if pad_right:
        val_list.append("")

    values_amount = len(val_list)
    gapes_amount = values_amount - 1
    values_len = sum(len(v) for v in val_list)
    spaces_amount = max_len - values_len
    if spaces_amount < gapes_amount:
        raise ValueError(f"There is not enough space for all values with padding")

    result = ""
    for value_idx, value in enumerate(val_list):
        gape_len = spaces_amount // (gapes_amount or 1)  # for last value
        result += value + (" " * gape_len)
        gapes_amount -= 1
        spaces_amount -= gape_len

    return result


_PRIVATE_REPLACER = "\U000E5750"


def wrap_sgr(
    raw_input: str | list[str], width: int, indent_first: int = 0, indent_subseq: int = 0
) -> str:
    """
    A workaround to make standard library ``textwrap.wrap()`` more friendly
    to an SGR-formatted strings.

    The main idea is

    :param raw_input:
    :param width:
    :param indent_first:
    :param indent_subseq:
    """
    # initially was written as a part of es7s/core
    # package, and transferred here later
    sgrs: list[str] = []

    def push(m: t.Match):
        sgrs.append(m.group())
        return _PRIVATE_REPLACER

    if isinstance(raw_input, str):  # input can be just one paragraph
        raw_input = [raw_input]

    inp = "\n\n".join(raw_input).split("\n\n")
    result = ""
    for raw_line in inp:
        # had an inspiration and wrote it; no idea how does it work exactly, it just does
        replaced_line = re.sub(r"(\s?\S?)((\x1b\[([0-9;]*)m)+)", push, raw_line)
        wrapped_line = f"\n".join(
            textwrap.wrap(
                replaced_line,
                width=width,
                initial_indent=(indent_first * " "),
                subsequent_indent=(indent_subseq * " "),
            )
        )
        final_line = re.sub(_PRIVATE_REPLACER, lambda _: sgrs.pop(0), wrapped_line)
        result += final_line + "\n"
    return result


def as_fragments(string: RT) -> t.List[Fragment]:
    if isinstance(string, str):
        return [Fragment(string)]
    elif isinstance(string, IRenderable):
        return string._as_fragments()
    raise ArgTypeError(type(string), "string", as_fragments)
