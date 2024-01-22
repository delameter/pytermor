# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
"""
"Front-end" module of the library containing *renderables* -- classes that
support high-level operations such as nesting-aware style application,
concatenating and cropping of styled strings before the rendering, text
alignment and wrapping, etc. Also provides rendering entrypoints `render()` and
`echo()`.

:fas:`sitemap;sd-text-primary` `guide.text_class_diagram`

"""
from __future__ import annotations

import re
import sys
import textwrap
import typing as t
from abc import ABC, abstractmethod
from collections import deque
from copy import copy
from typing import overload

from .common import Align, FT, RT, flatten1, get_qname, fit, pad, isiterable, instantiate
from .color import Color
from .exception import ArgTypeError, LogicError
from .renderer import IRenderer, OutputMode, RendererManager, SgrRenderer
from .style import NOOP_STYLE, Style, is_ft, make_style
from .term import get_preferable_wrap_width, get_terminal_width

# from typing_extensions import deprecated
# waiting till it will make its way to stdlib


SELECT_WORDS_REGEX = re.compile(r"(\S+)?(\s*)")

_PRIVATE_REPLACER = "\U000E5750"


# suggestion on @rewriting the renderables:
# -----------------------------------------------------------------------
# class Fragment(collections.UserString):       # <- this is a base class
#    _fmt: pytermor.FT
#
#    @overload
#    def __add__(self: Fragment, other: str) -> Fragment: ...
#    @overload
#    def __add__(self: Fragment, other: Fragment) -> Fragment|Text: ...
#    @overload
#    def __add__(self: Fragment, other: Text) -> Text: ...
#    ...
#
# class Text(collections.UserString):       # <- this is a container class
#    _frags: deque[Fragments]
#   ...
#


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
    def as_fragments(self) -> t.List[Fragment]:
        """a-s"""
        ...

    @abstractmethod
    def raw(self) -> str:
        """pass"""

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

    @staticmethod
    def _resolve_renderer(local_override: IRenderer | t.Type[IRenderer] = None) -> IRenderer:
        if local_override is not None:
            if (inst := instantiate(IRenderer, local_override)) is not None:
                return inst
        return RendererManager.get()


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
        if not isinstance(o, type(self)):  # pragma: no cover
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
        props_set = [f"({len(self._string)}, {sample!r})", repr(self._style)]
        flags = []
        if self._close_this:
            flags.append("+CT")
        if self._close_prev:
            flags.append("+CP")
        props_set.append(" ".join(flags))

        return f"<{self.__class__.__qualname__}[" + ", ".join(props_set) + "]>"

    def __add__(self, other: str | Fragment) -> Fragment | Text:
        if isinstance(other, str):
            other = Fragment(other)
        return Text(self, other)

    def __iadd__(self, other: str | Fragment) -> Fragment | Text:
        return self.__add__(other)

    def __radd__(self, other: str | Fragment) -> Fragment | Text:
        if isinstance(other, str):
            other = Fragment(other)
        return Text(other, self)

    def __format__(self, format_spec: str) -> str:
        formatted = self._string.__format__(format_spec)
        return self._resolve_renderer().render(formatted, self._style)

    def as_fragments(self) -> t.List[Fragment]:
        return [self]

    def raw(self) -> str:
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
    Multi-fragment text with style nesting support.

    :param align: default is left
    """

    def __init__(
        self,
        *fargs: RT | FT,
        width: int = None,
        align: str | Align = None,
        fill: str = " ",
        overflow: str = "",
        pad: int = 0,
        pad_styled: bool = True,
    ):
        self._fragments: deque[Fragment] = deque(self._parse_fargs(fargs))

        self._width = width
        self._align = Align.resolve(align)

        if len(fill) == 0:  # pragma: no cover
            raise ValueError("Fill cannot be an empty string")
        self._fill = fill

        self._overflow = overflow
        self._pad = pad
        self._pad_styled = pad_styled

    def __len__(self) -> int:
        return self._width or sum(len(frag) for frag in self._fragments)

    def __eq__(self, o: t.Any) -> bool:
        if not isinstance(o, type(self)):  # pragma: no cover
            return False
        return (
            self._fragments == o._fragments
            and self._width == o._width
            and self._align == o._align
            and self._fill == o._fill
            and self._overflow == o._overflow
        )

    def __str__(self) -> str:  # pragma: no cover
        raise LogicError("Casting to str is prohibited, use render() instead.")

    def __repr__(self) -> str:  # @todo refactor
        frags = len(self._fragments)
        result = f"<{self.__class__.__qualname__}[%sF={frags}%s]>"
        if self._width is not None:
            result %= f"W={self._width}, ", "%s"
        else:
            result %= "", "%s"
        if frags == 0:
            return result % ""
        return result % (", " + ", ".join([repr(f) for f in self._fragments]))

    def __add__(self, other: str | Fragment) -> FrozenText:
        return self.append(other)

    def __iadd__(self, other: str | Fragment) -> FrozenText:
        raise LogicError("FrozenText is immutable")

    def __radd__(self, other: str | Fragment) -> FrozenText:
        return self.prepend(other)

    @classmethod
    def _parse_fargs(
        cls,
        fargs: t.Iterable[RT | FT | t.Tuple[str, FT]],
    ) -> t.Iterable[Fragment]:
        """
        str FT prohibited unless on odd place

        :param fargs:
        :type fargs:
        :return:
        :rtype:
        """
        fargs = [*fargs]
        str_stack = deque()

        def ss_unload() -> str:
            result = "".join(str_stack)
            str_stack.clear()
            return result

        def ss_frag() -> Fragment:
            return Fragment(ss_unload())

        def ss_apply(ft: FT) -> Fragment:
            st = make_style(ft)
            return Fragment(ss_unload(), st)

        while len(fargs) or str_stack:
            if not len(fargs):
                yield ss_frag()
                continue

            farg = fargs.pop(0)
            if isinstance(farg, tuple):
                if str_stack:  # discharge stack
                    yield ss_frag()
                if len(farg):
                    yield from cls._parse_fargs(farg)

            elif isinstance(farg, IRenderable):
                if str_stack:  # discharge
                    yield ss_frag()
                yield from farg.as_fragments()

            elif is_ft(farg):
                if isinstance(farg, str) and not str_stack:
                    str_stack.append(farg)
                    continue
                try:
                    yield ss_apply(farg)
                except LookupError:  # discharge
                    yield ss_frag()
                    str_stack.append(farg)
            else:
                raise TypeError(f"Expected RT|FT, got {type(farg)}: {farg}")

    def as_fragments(self) -> t.List[Fragment]:
        if self.has_width:
            raise NotImplementedError(
                f"Cannot make Fragments from fixed-width {get_qname(self.__class__)}"
            )  # @TODO
        return [*self._fragments]

    def raw(self) -> str:
        return "".join(f.raw() for f in self._fragments)

    def render(self, renderer: IRenderer | t.Type[IRenderer] = None) -> str:
        """
        Core rendering method

        :param renderer:
        :type renderer:
        :return:
        :rtype:
        """
        max_len = len(self) + self._pad
        if self._width is not None:
            max_len = max(0, self._width - self._pad)

        result_parts: t.List[t.Tuple[str, Style]] = []
        cur_len = 0
        cur_frag_idx = 0
        overflow_buf = self._overflow[:max_len]
        overflow_start = max_len - len(overflow_buf)
        attrs_stack: t.Dict[str, t.List[bool | Color | None]] = {
            attr: [None] for attr in Style.renderable_attributes
        }
        renderer = self._resolve_renderer(renderer)

        # cropping and overflow handling
        while cur_len < max_len and cur_frag_idx < len(self._fragments):
            max_frag_len = max_len - cur_len
            frag = self._fragments[cur_frag_idx]
            frag_part = frag.raw()[:max_frag_len]
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

        # aligning and filling
        model_result = cur_len * "@"
        model = fit(model_result, (self._width or max_len), self._align, "", " ")

        spare_left, spare_right = pad(model.count(" ")), ""
        if model_result:
            spare_left, _, spare_right = model.partition(model_result)

        fill_left = fit("", len(spare_left), "right", "", self._fill)
        fill_right = fit("", len(spare_right), "left", "", self._fill)
        if not self._pad_styled or len(result_parts) == 0:
            result_parts.insert(0, (fill_left, NOOP_STYLE))
            result_parts.append((fill_right, NOOP_STYLE))
        else:
            first_fp, first_st = result_parts.pop(0)
            result_parts.insert(0, (fill_left + first_fp, first_st))
            last_fp, last_st = result_parts.pop()
            result_parts.append((last_fp + fill_right, last_st))

        return "".join(renderer.render(fp, st) for fp, st in result_parts)

    @property
    def allows_width_setup(self) -> bool:
        return True

    @property
    def has_width(self) -> bool:
        return self._width is not None

    def append(self, *args: RT | FT) -> FrozenText:
        return FrozenText(*self.as_fragments(), *self._parse_fargs(args))

    def prepend(self, *args: RT | FT) -> FrozenText:
        return FrozenText(*self._parse_fargs(args), *self.as_fragments())

    def set_width(self, width: int):  # pragma: no cover
        raise LogicError("FrozenText is immutable")


class Text(FrozenText):
    def __iadd__(self, other: str | Fragment) -> Text:
        return self.append(other)

    def append(self, *args: RT | FT) -> Text:
        self._fragments.extend(self._parse_fargs(args))
        return self

    def prepend(self, *args: RT | FT) -> Text:
        self._fragments.extendleft(self._parse_fargs(args))
        return self

    def set_width(self, width: int):
        self._width = width

    def split_by_spaces(self):
        self.split(regex=SELECT_WORDS_REGEX)

    def split(self, regex: t.Pattern):
        origin_fragments = copy(self._fragments)
        self._fragments.clear()

        for frag in origin_fragments:
            self._fragments += apply_style_selective(regex, frag.raw(), frag.style)
        origin_fragments.clear()


class Composite(IRenderable):
    """
    Simple class-container supporting concatenation of
    any `IRenderable` instances with each other without
    extra logic on top of it. Renders parts joined by an
    empty string.

    :param parts: text parts in any format implementing
                  `IRenderable` interface.
    """

    def __init__(self, *parts: RT):
        super().__init__()
        renderables = [self.as_renderable(p) for p in parts]
        self._parts: deque[IRenderable] = deque(renderables)

    def __len__(self) -> int:
        return sum(len(part) for part in self._parts)

    def __eq__(self, o: t.Any) -> bool:
        if not isinstance(o, type(self)):  # pragma: no cover
            return False
        return self._parts == o._parts

    def __repr__(self) -> str:
        frags = len(self._parts)
        result = f"<{self.__class__.__qualname__}[F={frags}%s]>"
        if frags == 0:
            return result % ""
        return result % (", " + ", ".join([repr(f) for f in self._parts]))

    def __add__(self, other: RT) -> Composite:
        self._parts.append(self.as_renderable(other))
        return self

    def __iadd__(self, other: RT) -> Composite:
        self._parts.append(self.as_renderable(other))
        return self

    def __radd__(self, other: RT) -> Composite:
        self._parts.appendleft(self.as_renderable(other))
        return self

    def as_renderable(self, rt: RT) -> IRenderable:
        if isinstance(rt, IRenderable):
            return rt
        return Fragment(rt)

    def as_fragments(self) -> t.List[Fragment]:
        return flatten1([p.as_fragments() for p in self._parts])

    def raw(self) -> str:
        return "".join(p.raw() for p in self._parts)

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
    .. deprecated:: 2.74
       SimpleTable is discouraged to use as it has very limited application and
       will be replaced with something much more generic in the future.

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
        if not isinstance(o, type(self)):  # pragma: no cover
            return False
        return self._rows == o._rows

    def __repr__(self) -> str:
        frags = len(flatten1(self._rows))
        result = f"<{self.__class__.__qualname__}[R={len(self._rows)}, F={frags}]>"
        return result

    def as_fragments(self) -> t.List[Fragment]:
        raise NotImplementedError

    def raw(self) -> str:
        return "\n".join(*[[cell.raw() for cell in row] for row in self._rows])

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


def is_rt(arg) -> bool:
    return isinstance(arg, (str, IRenderable))


def render(
    string: RT | t.Iterable[RT] = "",
    fmt: FT = NOOP_STYLE,
    renderer: IRenderer | t.Type[IRenderer] = None,
) -> str | t.List[str]:
    """
    .

    :param string: 2
    :param fmt: 2
    :param renderer: 2
    :return:
    """
    if string == "" and not fmt:
        return ""

    if isiterable(string):
        return [render(s, fmt, renderer) for s in string]

    if isinstance(string, str):
        if not fmt:
            return string
        return Fragment(string, fmt).render(renderer)

    if isinstance(string, IRenderable):
        return string.render(renderer)

    raise ArgTypeError(string, "string", RT, t.Iterable[RT])


def echo(
    string: RT | t.Iterable[RT] = "",
    fmt: FT = NOOP_STYLE,
    renderer: IRenderer = None,
    *,
    nl: bool = True,
    file: t.IO = None,
    flush: bool = True,
    wrap: bool | int = False,
    indent_first: int = 0,
    indent_subseq: int = 0,
) -> None:
    """
    .

    :param string:
    :param fmt:
    :param renderer:
    :param nl:
    :param file:          if not set, `sys.stdout` will be used instead
    :param flush:
    :param wrap:
    :param indent_first:
    :param indent_subseq:
    """
    file = file or sys.stdout
    end = "\n" if nl else ""
    will_wrap = wrap or indent_first or indent_subseq

    fmtd = render(string, fmt, renderer)

    if will_wrap:
        force_width = wrap if isinstance(wrap, int) else None
        width = get_preferable_wrap_width(force_width)
        result = wrap_sgr(fmtd, width, indent_first, indent_subseq).rstrip("\n")
    elif isiterable(fmtd):
        result = "".join(fmtd)
    else:
        result = fmtd

    print(result, end=end, file=file, flush=flush)


def echoi(
    string: RT | t.Iterable[RT] = "",
    fmt: FT = NOOP_STYLE,
    renderer: IRenderer = None,
    *,
    file: t.IO = None,
    flush: bool = True,
) -> None:
    """
    echo inline

    :param string:
    :param fmt:
    :param renderer:
    :param file:        if not set, `sys.stdout` will be used instead
    :param flush:
    :return:
    """
    echo(string, fmt, renderer, nl=False, file=file, flush=flush)


# fmt: off
@overload
def distribute_padded(max_len: int, *values: str, pad_left: int = 0, pad_right: int = 0) -> str:
    ...
@overload
def distribute_padded(max_len: int, *values: RT, pad_left: int = 0, pad_right: int = 0) -> Text:
    ...
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


def wrap_sgr(
    rendered: str | list[str], width: int, indent_first: int = 0, indent_subseq: int = 0
) -> str:
    """
    A workaround to make standard library ``textwrap.wrap()`` more friendly
    to an SGR-formatted strings.

    The main idea is

    :param rendered:
    :param width:
    :param indent_first:
    :param indent_subseq:
    """
    # re.split(r"(\n\n+)|(?<!\n)\n(?!\n)", "\n\n".join(rendered))

    # initially was written as a part of es7s/core
    # package, and transferred here later
    sgrs: list[str] = []

    def push(m: t.Match):
        sgrs.append(m.group())
        return _PRIVATE_REPLACER

    if isinstance(rendered, str):  # input can be just one paragraph
        rendered = [rendered]

    inp = "\n\n".join(rendered).split("\n\n")
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


def apply_style_words_selective(string: str, st: Style) -> t.Sequence[Fragment]:
    """ ... """
    return apply_style_selective(SELECT_WORDS_REGEX, string, st)


def apply_style_selective(
    regex: t.Pattern, string: str, st: Style = NOOP_STYLE
) -> t.Sequence[Fragment]:
    """
    Main purpose: application of under(over|cross)lined styles to strings
    containing more than one word. Although the method can be used with any style and
    splitting rule provided. The result is a sequence of `Fragments <Fragment>`
    with styling applied only to specified parts of the original string.

    Regex should consist of two groups, first for parts to apply style to, second
    for parts to return without any style (see `NOOP_STYLE`). This regex is
    used internally for python's `re.findall()` method.

    The example below demonstrates how to color all the capital letters in the string
    in red color:

        >>> render([
        ...     *apply_style_selective(
        ...         re.compile(R'([A-Z]+)([^A-Z]+|$)'),
        ...         "A few CAPITALs",
        ...         Style(fg='red'),
        ...     )
        ... ], renderer=SgrRenderer(OutputMode.XTERM_16))
        ['\x1b[31mA\x1b[39m', ' few ', '\x1b[31mCAPITAL\x1b[39m', 's']

        .. container:: highlight highlight-manual highlight-adjacent highlight-output output

            :red:`A` few :red:`CAPITAL`\ s

    :param regex:
    :param string:
    :param st:
    """
    for part, sep in regex.findall(string):
        if len(part) > 0:
            yield Fragment(part, st, close_this=True)
        if len(sep) > 0:
            yield Fragment(sep)
