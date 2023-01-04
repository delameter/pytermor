# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""
"Front-end" module of the library. Contains classes supporting high-level
operations such as nesting-aware style application, concatenating and cropping
of styled strings before the rendering, text alignment and wrapping, etc.
"""
from __future__ import annotations

import collections
import dataclasses
import math
import re
import sys
import typing as t
from abc import abstractmethod, ABC
from typing import Union, overload

from .color import IColor, NOOP_COLOR
from .common import LogicError, ArgTypeError, FT, RT, Align, logger, measure
from .renderer import IRenderer, RendererManager
from .style import Style, NOOP_STYLE, make_style
from .utilmisc import get_preferable_wrap_width, get_terminal_width
from .utilstr import ljust_sgr, rjust_sgr, center_sgr, wrap_sgr, pad


@dataclasses.dataclass
class _Fragment(t.Sized):
    string: str = ""
    fmt: FT = None
    close_this: bool = True
    close_prev: bool = False

    def __post_init__(self):
        if self.close_prev:
            self.close_this = True
        self._style = make_style(self.fmt)

    def __eq__(self, o: t.Any) -> bool:
        if not isinstance(o, type(self)):
            return False
        return (
            self.string == o.string
            and self.fmt == o.fmt
            and self.close_this == o.close_this
            and self.close_prev == o.close_prev
        )

    @property
    def style(self) -> Style:
        return self._style

    def __len__(self) -> int:
        return len(self.string)

    def __repr__(self):
        max_sl = 9
        sample = self.string[:max_sl] + ("‥" * (len(self.string) > max_sl))
        props_set = [f'({len(self.string)}, "{sample}")', repr(self._style)]
        flags = []
        if self.close_this:
            flags.append("+CT")
        if self.close_prev:
            flags.append("+CP")
        props_set.append(" ".join(flags))

        return f"<{self.__class__.__qualname__}>[" + ", ".join(props_set) + "]"


class IRenderable(t.Sized, ABC):
    def __init__(self):
        """
        Renderable abstract class. Can be inherited when the default style
        overlaps resolution mechanism implemented in `Text` is not good enough.
        """
        self._is_frozen: bool = False
        self._renders_cache: t.Dict[IRenderer, str] = dict()

    def render(self, renderer: IRenderer | t.Type[IRenderer] = None) -> str:
        if isinstance(renderer, type):
            renderer = renderer()
        if renderer is None:
            renderer = RendererManager.get_default()

        use_cache = renderer.is_caching_allowed and self._is_frozen
        if use_cache and (cached := self._renders_cache.get(renderer, None)):
            return cached

        result = self._render_using(renderer)
        if use_cache:
            self._renders_cache.update({renderer: result})
        return result

    @abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, o: t.Any) -> bool:
        raise NotImplementedError

    @abstractmethod
    def _render_using(self, renderer: IRenderer) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def raw(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def fragments(self) -> t.Sequence[_Fragment]:
        raise NotImplementedError


class String(IRenderable):
    def __init__(self, string: str = "", fmt: FT = None):
        """

        :param string:
        :param fmt:
        """
        super().__init__()
        self._fragment = _Fragment(string, fmt)
        self._is_frozen = True

    def __len__(self) -> int:
        return len(self._fragment)

    def __eq__(self, o: String) -> bool:
        if not isinstance(o, type(self)):
            return False
        return self._fragment == o._fragment

    def __repr__(self) -> str:
        result = f"<{self.__class__.__qualname__}>[F=1, %s]"
        return result % repr(self._fragment)

    @property
    def raw(self) -> str:
        return self._fragment.string

    @property
    def style(self) -> Style:
        return self._fragment.style

    @property
    def fragments(self) -> t.List[_Fragment]:
        return [self._fragment]

    def _render_using(self, renderer: IRenderer) -> str:
        return renderer.render(self.raw, self._fragment.style)


class FixedString(String):
    """
    A
    """

    def __init__(
        self,
        string: str = "",
        fmt: FT = None,
        width: int = 0,
        align: Align | str = Align.LEFT,
        *,
        pad_left: int = 0,
        pad_right: int = 0,
        overflow_char: str = None,
    ):
        """
        .. note ::
            All arguments except ``string``, ``fmt``, ``width`` and ``align``
            are *kwonly*-type args.

        :param string:
        :param fmt:
        :param width:
        :param align:
        :param pad_left:
        :param pad_right:
        :param overflow_char: # @TODO
        """
        self._is_frozen = True
        self._string_origin = string

        self._width = max(0, width) or len(string)
        self._align = self._resolve_align(align)
        self._pad_left = max(0, pad_left)
        self._pad_right = max(0, pad_right)

        if not isinstance(self._align, Align):
            raise ValueError(f"Invalid align value: {self._align}")
        if self.max_width < 0:
            raise ValueError("Resulting width should be >= 0")

        string_processed = self._apply_attrs(string)
        super().__init__(string_processed, fmt)

    def __len__(self) -> int:
        return self._width

    def __eq__(self, o: t.Any) -> bool:
        if not isinstance(o, type(self)):
            return False
        return (
            self._fragment == o._fragment
            and self._align == o._align
            and self._width == o._width
            and self._pad_left == o._pad_left
            and self._pad_right == o._pad_right
        )

    @property
    def max_width(self) -> int:
        return self._width - (self._pad_left + self._pad_right)

    @property
    def origin(self) -> str:
        return self._string_origin

    @property
    def raw(self) -> str:
        return self._fragment.string

    def _resolve_align(self, align: str | Align) -> Align:
        if isinstance(align, Align):
            return align
        try:
            return Align[align.upper()]
        except KeyError:
            raise ValueError(f"Invalid align value: '{align}'")

    def _apply_attrs(self, string: str) -> str:
        if not isinstance(string, str):
            raise TypeError("FixedString accepts only raw strings as 'string' argument")
        aligned = f"{string:{self._align.value}{self._width}s}"
        cropped = self._crop(aligned)
        return pad(self._pad_left) + cropped + pad(self._pad_right)

    def _crop(self, aligned: str) -> str:
        max_width = self.max_width
        if (overflow := len(aligned) - max_width) <= 0:
            return aligned

        if self._align is Align.LEFT:
            return aligned[:max_width]

        if self._align is Align.RIGHT:
            return aligned[-max_width:]

        if overflow % 2 == 1:
            right_overflow = math.ceil(overflow / 2)
        else:
            right_overflow = math.floor(overflow / 2)
        left_overflow = overflow - right_overflow
        return aligned[left_overflow:-right_overflow]


class FrozenText(IRenderable):
    _WIDTH_MAX_LEN_REGEXP = re.compile(r"[\d.]+$")
    _ALIGN_LEFT = "<"  # @TODO effectively is a duplicate of common.Align enum
    _ALIGN_RIGHT = ">"
    _ALIGN_CENTER = "^"
    _ALIGN_FUNC_MAP = {
        None: ljust_sgr,
        _ALIGN_LEFT: ljust_sgr,
        _ALIGN_RIGHT: rjust_sgr,
        _ALIGN_CENTER: center_sgr,
    }

    def __init__(
        self,
        string: RT = "",
        fmt: FT = None,
        *,
        close_this: bool = True,
        close_prev: bool = False,
    ):
        """
        .. note ::
            All arguments except ``string`` and ``fmt`` are *kwonly*-type args.

        :param string:
        :param fmt:
        :param close_this:
        :param close_prev:
        """
        super().__init__()
        self._is_frozen = True
        self._fragments: t.Deque[_Fragment] = collections.deque(
            self._make_fragments(string, fmt, close_this, close_prev)
        )

    def __eq__(self, o: t.Any) -> bool:
        if not isinstance(o, type(self)):
            return False
        return self._fragments == o._fragments

    def _make_fragments(
        self,
        string: RT,
        fmt: FT = None,
        close_this: bool = True,
        close_prev: bool = False,
    ) -> t.Sequence[_Fragment]:
        if isinstance(string, str):
            return [_Fragment(string, fmt, close_this, close_prev)]
        elif isinstance(string, IRenderable):
            if fmt is not None and fmt != NOOP_STYLE and fmt != NOOP_COLOR:
                return [_Fragment("", fmt, close_this, close_prev)]
            return string.fragments
        raise ArgTypeError(type(string), "string", fn=self._make_fragments)

    def _render_using(self, renderer: IRenderer) -> str:
        result = ""
        attrs_stack: t.Dict[str, t.List[bool | IColor | None]] = {
            attr: [None] for attr in Style.renderable_attributes
        }
        for frag in self._fragments:
            for attr in Style.renderable_attributes:
                frag_attr = getattr(frag.style, attr)
                if frag_attr is not None and frag_attr != NOOP_COLOR:
                    attrs_stack[attr].append(frag_attr)

            result += renderer.render(
                frag.string, Style(**{k: v[-1] for k, v in attrs_stack.items()})
            )
            if not frag.close_prev and not frag.close_this:
                continue

            for attr in Style.renderable_attributes:
                frag_attr = getattr(frag.style, attr)
                if frag_attr is not None and frag_attr != NOOP_COLOR:
                    attrs_stack[attr].pop()  # close this
                    if frag.close_prev:
                        attrs_stack[attr].pop()
                    if len(attrs_stack[attr]) == 0:
                        raise LogicError(
                            "There are more closing styles than opening ones, "
                            f'cannot proceed (attribute "{attr}" in {frag})'
                        )

        return result

    @property
    def raw(self) -> str:
        return "".join(frag.string for frag in self._fragments)

    @property
    def fragments(self) -> t.Deque[_Fragment]:
        return self._fragments

    def __len__(self) -> int:
        return sum(len(frag) for frag in self._fragments)

    def __str__(self) -> str:
        raise LogicError("Casting to str is prohibited, use render() instead.")

    def __repr__(self) -> str:
        frags = len(self._fragments)
        result = f"<{self.__class__.__qualname__}>[F={frags}%s]"
        if frags == 0:
            return result % ""
        return result % (", " + repr(self._fragments[0]))

    def __format__(self, format_spec: str) -> str:
        """
        Adds a support of formatting the instances using f-strings.
        The text
        ``:s`` mode is required.
        Supported features:
          - length;
          - max length;
          - alignment;
          - filling.

        Example: ``{:A^12.5s}``
        """
        return self.render_fixed(*self._parse_format_spec(format_spec))

    def render_fixed(
        self, width: int, max_len: int, align: str, fill: str, renderer: IRenderer = None
    ) -> str:
        renderer = renderer or RendererManager.get_default()
        if max_len is None:
            result = self._render_using(renderer)
            cur_len = len(self)
        else:
            result = ""
            cur_len = 0
            cur_frag_idx = 0
            while cur_len < max_len and cur_frag_idx < len(self._fragments):
                allowed_len = max_len - cur_len
                cur_frag = self._fragments[cur_frag_idx]
                cur_frag_string = cur_frag.string[:allowed_len]
                result += renderer.render(cur_frag_string, cur_frag.style)

                cur_len += len(cur_frag_string)
                cur_frag_idx += 1

        if width is not None and width > cur_len:
            align_func_args = (result, width, (fill or " "), cur_len)
            align_func = self._ALIGN_FUNC_MAP.get(align)
            return align_func(*align_func_args)
        return result

    @classmethod
    def _parse_format_spec(
        cls, format_spec_orig: str
    ) -> t.Tuple[int | None, int | None, str | None, str | None]:
        format_spec = format_spec_orig
        if len(format_spec) == 0 or format_spec[-1] == "s":
            format_spec = format_spec[:-1]
        elif format_spec[-1] in "1234567890":
            pass
        else:
            "".__format__(format_spec_orig)
            raise LogicError(f"Unrecognized format spec: '{format_spec_orig}'")

        width = None
        max_len = None
        if width_and_max_len_match := cls._WIDTH_MAX_LEN_REGEXP.search(format_spec):
            width_max_len = width_and_max_len_match.group(0)
            if "." in width_max_len:
                if width_max_len.startswith("."):
                    max_len = int(width_max_len.replace(".", ""))
                else:
                    width, max_len = (
                        (int(val) if val else None) for val in width_max_len.split(".")
                    )
            else:
                width = int(width_max_len)
            format_spec = cls._WIDTH_MAX_LEN_REGEXP.sub("", format_spec)

        align = None
        if format_spec.endswith((cls._ALIGN_LEFT, cls._ALIGN_RIGHT, cls._ALIGN_CENTER)):
            align = format_spec[-1]
            format_spec = format_spec[:-1]

        fill = None
        if len(format_spec) > 0:
            fill = format_spec[-1]
            format_spec = format_spec[:-1]

        if len(format_spec) > 0:
            "".__format__(format_spec_orig)
            raise LogicError(f"Unrecognized format spec: '{format_spec_orig}'")

        return width, max_len, align, fill


class Text(FrozenText):
    def __init__(
        self,
        string: RT = "",
        fmt: FT = None,
        *,
        close_this: bool = True,
        close_prev: bool = False,
    ):
        """
        .. note ::
            All arguments except ``string`` and ``fmt`` are *kwonly*-type args.

        :param string:
        :param fmt:
        :param close_this:
        :param close_prev:
        """
        super().__init__(string, fmt, close_this=close_this, close_prev=close_prev)
        self._is_frozen = False

    def __eq__(self, o: t.Any) -> bool:
        if not isinstance(o, type(self)):
            return False
        return self._fragments == o._fragments

    def append(
        self, string: RT = "", fmt: FT = None, *, close_this=True, close_prev=False
    ) -> Text:
        self._fragments.extend(self._make_fragments(string, fmt, close_this, close_prev))
        return self

    def prepend(
        self,
        string: RT = "",
        fmt: FT = None,
        *,
        close_this: bool = True,
        close_prev: bool = False,
    ) -> Text:
        self._fragments.extendleft(
            self._make_fragments(string, fmt, close_this, close_prev)
        )
        return self

    def __add__(self, other: RT) -> Text:
        self.append(other)
        return self

    def __iadd__(self, other: RT) -> Text:
        self.append(other)
        return self

    def __radd__(self, other: RT) -> Text:
        self.prepend(other)
        return self


class SimpleTable(IRenderable):
    """
    Table class with dynamic (not bound to each other) rows.

    Allows 0 or 1 dynamic-width cell in each row, while all the others should be
    static, i.e., be instances of `FixedString`.

    >>> echo(
    ...     SimpleTable(
    ...     [
    ...         FixedString("1"),
    ...         FixedString("word", width=6, align='center'),
    ...         "smol string"
    ...     ],
    ...     [
    ...         FixedString("2"),
    ...         FixedString("padded word", width=6, align='left', pad_left=1),
    ...         "biiiiiiiiiiiiiiiiiiiiiiiiiiiiiiig string"
    ...     ],
    ...     width=30,
    ...     sep="|"
    ... ), file=sys.stdout)
    |1| word |    smol string    |
    |2| padde|biiiiiiiiiiiiiiiiii|

    """

    def __init__(
        self,
        *rows: t.Iterable[t.Iterable[RT]],
        width: int = None,
        sep: str = 2 * " ",
        border_st: Style = NOOP_STYLE,
    ):
        """
        Create

        .. note ::
            All arguments except ``*rows`` are *kwonly*-type args.

        :param rows:
        :param width:
        :param sep:
        :param border_st:
        """
        super().__init__()
        self._max_width: int = width or get_terminal_width()
        self._column_sep: FixedString = FixedString(sep, border_st)
        self._border_st = border_st
        self._rows: list[list[RT]] = []
        self.add_rows(rows)

    def add_header_row(self, *cells: RT):
        self.add_separator_row()
        self.add_row(*cells)
        self.add_separator_row()

    def add_footer_row(self, *cells: RT):
        self.add_separator_row()
        self.add_row(*cells)
        self.add_separator_row()

    def add_separator_row(self):
        self._rows.append([String("-" * self._max_width, self._border_st)])

    def add_rows(self, rows: t.Iterable[t.Iterable[RT]]):
        for row in rows:
            self.add_row(*row)

    def add_row(self, *cells: RT):
        fixed_cell_count = sum(1 if isinstance(c, FixedString) else 0 for c in cells)
        if fixed_cell_count < len(cells) - 1:
            raise TypeError(
                "Row should have no more than one dynamic width cell, "
                "all the others should be instances of FixedString."
            )

        row = [*self._make_row(*cells)]
        if self._sum_len(*cells, fixed_only=True) > self._max_width:
            raise ValueError(f"Row is too long (>{self._max_width})")
        self._rows.append(row)

    def __len__(self) -> int:
        raise NotImplementedError

    def __eq__(self, o: t.Any) -> bool:
        if not isinstance(o, type(self)):
            return False
        return self._rows == o._rows

    def __repr__(self) -> str:
        frags = len(self.fragments)
        result = f"<{self.__class__.__qualname__}>[R={len(self._rows)}, F={frags}%s]"
        if frags == 0:
            return result % ""
        return result % (", " + repr(self.fragments[0]))

    def _make_row(self, *cells: RT) -> t.Iterable[RT]:
        yield self._column_sep
        for cell in cells:
            if not isinstance(cell, IRenderable):
                cell = String(cell)
            yield cell
            yield self._column_sep

    def _render_using(self, renderer: IRenderer) -> str:
        def render_row(*cells: RT) -> str:
            fixed_len = self._sum_len(*cells, fixed_only=True)
            free_len = self._max_width - fixed_len
            for cell in cells:
                if not isinstance(cell, FixedString):
                    yield Text(cell).render_fixed(free_len, free_len, "^", " ", renderer)
                    continue
                yield render(cell, renderer=renderer)

        return "\n".join("".join(render_row(*row)) for row in self._rows)

    def _sum_len(self, *cells: RT, fixed_only: bool) -> int:
        return sum(len(c) for c in cells if not fixed_only or isinstance(c, FixedString))

    @property
    def raw(self) -> str:
        return "\n".join(
            self._column_sep.raw.join(cell.raw for cell in row) for row in self._rows
        )

    @property
    def row_count(self) -> int:
        return len(self._rows)

    @property
    def fragments(self) -> t.List[_Fragment]:
        def _iter_fragments():
            for row in self._rows:
                for cell in row:
                    yield from cell.fragments

        return [*_iter_fragments()]


# -----------------------------------------------------------------------------


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
          (?P<set>@[\w]+)?
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
            tpl_part = self._ESCAPE_REGEXP.sub(r"\1[", tpl[tpl_cursor : span[0]])
            if len(tpl_part) > 0 or style_buffer != NOOP_STYLE:
                if split_style:
                    for tpl_chunk, sep in self._SPLIT_REGEXP.findall(tpl_part):
                        if len(tpl_chunk) > 0:
                            result.append(tpl_chunk, style_buffer, close_this=True)
                        result.append(sep)
                    # add open style for engine to properly handle the :[-closing] tag:
                    tpl_part = ""
                result.append(tpl_part, style_buffer, close_this=False)

            tpl_cursor = span[1]
            style_buffer = NOOP_STYLE
            split_style = False

            tag = _TemplateTag(**tag_match.groupdict())
            style = self._tag_to_style(tag)
            if tag.set:
                self._custom_styles[tag.set] = style
            elif tag.add:
                if tag.close:
                    result.append("", style, close_prev=True)
                else:
                    style_buffer = style
                    split_style = tag.split
            elif tag.comment:
                pass
            else:
                raise ValueError(f"Unknown tag operand: {_TemplateTag}")

        result.append(tpl[tpl_cursor:])
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


@measure(msg="Rendering")
def render(
    string: RT | t.Iterable[RT] = "",
    fmt: IColor | Style = NOOP_STYLE,
    renderer: IRenderer = None,
    parse_template: bool = False,
    *,
    no_log: bool = False,  # noqa
) -> str | t.List[str]:
    """
    .

    :param string:
    :param fmt:
    :param renderer:
    :param parse_template:
    :param no_log:
    :return:
    """
    if string == "" and fmt == NOOP_STYLE:
        return ""
    sclass = string.__class__.__name__

    if parse_template:
        if not isinstance(string, str):
            raise ValueError("Template parsing is supported for raw strings only.")
        try:
            string = _template_engine.parse(string)
        except Union[ValueError, LogicError] as e:
            string += f" [pytermor] Template parsing failed with {e}"
        return render(string, fmt, renderer, parse_template=False)

    if isinstance(string, t.Sequence) and not isinstance(string, str):
        # debug(f"Rendering as iterable ({len(string)}:d)")
        return [render(s, fmt, renderer, parse_template) for s in string]

    if isinstance(string, IRenderable):
        if fmt == NOOP_STYLE:
            # debug(f"Invoking instance's render method ({sclass}, {fmt!r})")
            return string.render(renderer)

        # debug(f"Composing new Text due to nonempty fmt ({fmt!r})")
        return Text(fmt=fmt).append(string).render(renderer)

    if isinstance(string, str):
        if fmt == NOOP_STYLE:
            # debug(f"Omitting the rendering ({sclass}, {fmt!r})")
            return string

        # debug(f"Composing new String due to nonempty fmt ({sclass}, {fmt!r})")
        return String(string, fmt).render(renderer)

    raise ArgTypeError(type(string), "string", fn=render)


def echo(
    string: RT | t.Iterable[RT] = "",
    fmt: IColor | Style = NOOP_STYLE,
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
    fmt: IColor | Style = NOOP_STYLE,
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
    val_list = []
    for value in values:
        if isinstance(value, IRenderable) and not isinstance(value, Text):
            val_list.append(Text(value))
            continue
        val_list.append(value)
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
        result += value + pad(gape_len)
        gapes_amount -= 1
        spaces_amount -= gape_len

    return result
