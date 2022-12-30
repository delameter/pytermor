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
import time
import typing as t
from abc import abstractmethod, ABC
from typing import Union

from .color import IColor, NOOP_COLOR
from .common import LogicError, ArgTypeError, FT, RT, Align, logger
from .renderer import IRenderer, RendererManager
from .style import Style, NOOP_STYLE, make_style
from .utilmisc import get_preferable_wrap_width
from .utilstr import ljust_sgr, rjust_sgr, center_sgr, wrap_sgr, pad, dump


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

    def __eq__(self, o: object) -> bool:
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
        props_set = [f'"{self.string:.10s}"({len(self.string)})', f"{self._style!r}"]
        if self.close_this:
            props_set.append("close_this")
        if self.close_prev:
            props_set.append("close_prev")

        return f"<{self.__class__.__qualname__}>[" + ", ".join(props_set) + "]"


class IRenderable(t.Sized, ABC):
    """
    Renderable abstract class. Can be inherited when the default style
    overlaps resolution mechanism implemented in `Text` is not good enough.
    """

    def __init__(self):
        self._is_frozen: bool = False
        self._renders_cache: t.Dict[IRenderer, str] = dict()

    def render(
        self, renderer: IRenderer | t.Type[IRenderer] = None, stderr: bool = False
    ) -> str:
        if isinstance(renderer, type):
            renderer = renderer()
        before_s = time.time_ns() / 1e9
        rendered = self._render(renderer or RendererManager.get_default())
        after_s = time.time_ns() / 1e9
        if not stderr:
            from .utilnum import format_si_metric

            logger.debug(f"Rendered in {format_si_metric((after_s-before_s), 's')}")
            logger.log(level=5, msg=dump(rendered, "Dump"))
        return rendered

    def _render(self, renderer: IRenderer) -> str:
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
    def __eq__(self, o: IRenderable) -> bool:
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
    def __init__(self, string: str = "", fmt: IColor | Style = NOOP_STYLE):
        super().__init__()
        self._fragment = _Fragment(string, fmt)
        self._is_frozen = True

    def __len__(self) -> int:
        return len(self._fragment)

    def __eq__(self, o: String) -> bool:
        if not isinstance(o, type(self)):
            return False
        return self._fragment == o._fragment

    @property
    def raw(self) -> str:
        return self._fragment.string

    @property
    def style(self) -> Style:
        return self._fragment.style

    @property
    def fragments(self) -> t.Sequence[_Fragment]:
        return [self._fragment]

    def _render_using(self, renderer: IRenderer) -> str:
        return renderer.render(self.raw, self._fragment.style)


class FixedString(String):
    """
    .. todo ::

       store already formatted string right after initialization, and provide
       it as `raw` when joining several Renderables, or else width limit, padding
       and aligning simply do not work.
    """

    def __init__(
        self,
        string: str = "",
        fmt: IColor | Style = NOOP_STYLE,
        align: Align = Align.LEFT,
        *,
        width: int = 0,
        pad_left: int = 0,
        pad_right: int = 0,
        overflow_char: str = None,  # @TODO
    ):
        super().__init__(string, fmt)
        self._is_frozen = True
        self._align = align
        self._width = max(0, width) or len(string)
        self._pad_left = max(0, pad_left)
        self._pad_right = max(0, pad_right)

        if not isinstance(self._align, Align):
            raise ValueError(f"Invalid align value: {self._align}")
        if self.max_width < 0:
            raise ValueError("Resulting width should be >= 0")

    def __len__(self) -> int:
        return self._width

    def __eq__(self, o: String) -> bool:
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
        return self._fragment.string

    @property
    def raw(self) -> str:
        string = self._fragment.string
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
    _ALIGN_LEFT = "<"
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
        string: str | IRenderable = "",
        fmt: IColor | Style = NOOP_STYLE,
        *,
        close_this: bool = True,
        close_prev: bool = False,
    ):
        super().__init__()
        self._is_frozen = True
        self._fragments: t.Deque[_Fragment] = collections.deque(
            self._make_fragments(string, fmt, close_this, close_prev)
        )

    def __eq__(self, o: IRenderable) -> bool:
        if not isinstance(o, type(self)):
            return False
        return self._fragments == o._fragments

    def _make_fragments(
        self,
        string: str | IRenderable,
        fmt: IColor | Style = NOOP_STYLE,
        close_this: bool = True,
        close_prev: bool = False,
    ) -> t.Sequence[_Fragment]:
        if isinstance(string, str):
            return [_Fragment(string, fmt, close_this, close_prev)]
        elif isinstance(string, IRenderable):
            if fmt != NOOP_STYLE and fmt != NOOP_COLOR:
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
    def fragments(self) -> t.Sequence[_Fragment]:
        return self._fragments

    def __len__(self) -> int:
        return sum(len(frag) for frag in self._fragments)

    def __str__(self) -> str:
        raise LogicError("Casting to str is prohibited, use render() instead.")

    def __repr__(self) -> str:
        result = f"<{self.__class__.__qualname__}[%s]>"
        frags = len(self._fragments)
        if frags == 0:
            return result % ""
        return result % (repr(self._fragments[0]) + f"({frags})")

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
        width, max_len, align, fill = self._parse_format_spec(format_spec)

        renderer = RendererManager.get_default()
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
        string: str | IRenderable = "",
        fmt: IColor | Style = NOOP_STYLE,
        *,
        close_this: bool = True,
        close_prev: bool = False,
    ):
        super().__init__(string, fmt, close_this=close_this, close_prev=close_prev)
        self._is_frozen = False

    def __eq__(self, o: IRenderable) -> bool:
        if not isinstance(o, type(self)):
            return False
        return self._fragments == o._fragments

    def append(
        self,
        string: str | IRenderable = "",
        fmt: IColor | Style = NOOP_STYLE,
        *,
        close_this: bool = True,
        close_prev: bool = False,
    ) -> Text:
        self._fragments.extend(self._make_fragments(string, fmt, close_this, close_prev))
        return self

    def prepend(
        self,
        string: str | Text = "",
        fmt: IColor | Style = NOOP_STYLE,
        *,
        close_this: bool = True,
        close_prev: bool = False,
    ) -> Text:
        self._fragments.extendleft(
            self._make_fragments(string, fmt, close_this, close_prev)
        )
        return self

    def __add__(self, other: str | Text) -> Text:
        self.append(other)
        return self

    def __iadd__(self, other: str | Text) -> Text:
        self.append(other)
        return self

    def __radd__(self, other: str | Text) -> Text:
        self.prepend(other)
        return self


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


def render(
    string: RT | t.Iterable[RT] = "",
    fmt: IColor | Style = NOOP_STYLE,
    renderer: IRenderer = None,
    parse_template: bool = False,
    *,
    stderr: bool = False,
) -> str | t.List[str]:
    """
    .

    :param string:
    :param fmt:
    :param renderer:
    :param parse_template:
    :param stderr:
    :return:
    """
    if string == "" and fmt == NOOP_STYLE:
        return ""
    debug = lambda msg: logger.debug(msg) if not stderr else None
    sclass = string.__class__.__name__

    if parse_template:
        if not isinstance(string, str):
            raise ValueError("Template parsing is supported for raw strings only.")
        try:
            string = _template_engine.parse(string)
        except Union[ValueError, LogicError] as e:
            string += f" [pytermor] Template parsing failed with {e}"
        return render(string, fmt, renderer, parse_template=False, stderr=stderr)

    if isinstance(string, t.Sequence) and not isinstance(string, str):
        debug(f"Rendering as iterable ({len(string)}:d)")
        return [render(s, fmt, renderer, parse_template, stderr=stderr) for s in string]

    if isinstance(string, IRenderable):
        if fmt == NOOP_STYLE:
            debug(f"Invoking instance's render method ({sclass}, {fmt!r})")
            return string.render(renderer, stderr)

        debug(f"Composing new Text due to nonempty fmt ({fmt!r})")
        return Text(fmt=fmt).append(string).render(renderer, stderr)

    if isinstance(string, str):
        if fmt == NOOP_STYLE:
            debug(f"Omitting the rendering ({sclass}, {fmt!r})")
            return string

        debug(f"Composing new String due to nonempty fmt ({sclass}, {fmt!r})")
        return String(string, fmt).render(renderer, stderr)

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
        result = wrap_sgr(result, width, indent_first, indent_subseq)

    print(result, end=end, file=file, flush=flush)
