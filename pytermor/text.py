# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""
Module with output formatters. By default :class:`SgrRenderer` is used. It
also contains compatibility settings, see `SgrRenderer.setup()`.

Working with non-default renderer can be achieved in two ways:

    a. Method `RendererManager.set_default()` sets the default renderer globally.
       After that calling `render()` will automatically invoke said renderer
       and all formatting will be applied.
    b. Alternatively, you can use renderer's own instance method ``render()``
       directly and avoid messing up with the manager:
       ``HtmlRenderer().render(<Text>)``

.. rubric:: TL;DR

To unconditionally print formatted message to output terminal, do something like
this:

>>> RendererManager.set_default_to_force_formatting()
>>> render('Warning: AAAA', Styles.WARNING)
'\\x1b[33mWarning: AAAA\\x1b[39m'


.. testsetup:: *

    from pytermor.text import *

"""
from __future__ import annotations

import re
import sys
import typing as t
import collections
import dataclasses

from .common import LogicError, Renderable
from .color import Color, NOOP_COLOR
from .util import ljust_sgr, rjust_sgr, center_sgr
from .style import Style, NOOP_STYLE, Styles
from .renderer import AbstractRenderer, RendererManager

""" Special style passing the text through without any modifications. """


@dataclasses.dataclass
class _TextFragment(t.Sized):
    string: str = ""
    style: Style = NOOP_STYLE
    close_this: bool = True
    close_prev: bool = False

    def __post_init__(self):
        if self.close_prev:
            self.close_this = True

    def __len__(self) -> int:
        return len(self.string)

    def __repr__(self):
        props_set = [f'"{self.string}"', f"{self.style!r}"]
        if self.close_this:
            props_set.append("close_this")
        if self.close_prev:
            props_set.append("close_prev")

        return self.__class__.__name__ + "[" + ", ".join(props_set) + "]"


class Text(Renderable):
    WIDTH_MAX_LEN_REGEXP = re.compile(r"[\d.]+$")
    ALIGN_LEFT = "<"
    ALIGN_RIGHT = ">"
    ALIGN_CENTER = "^"
    ALIGN_FUNC_MAP = {
        None: ljust_sgr,
        ALIGN_LEFT: ljust_sgr,
        ALIGN_RIGHT: rjust_sgr,
        ALIGN_CENTER: center_sgr,
    }

    def __init__(
        self,
        string: str = "",
        style: Style = NOOP_STYLE,
        close_this: bool = True,
        close_prev: bool = False,
    ):
        self._fragments: t.Deque[_TextFragment] = collections.deque()
        self.append(string, style, close_this, close_prev)

    def render(
        self, renderer: AbstractRenderer|t.Type[AbstractRenderer] = None
    ) -> str:
        if isinstance(renderer, type):
            renderer = renderer()
        return self._render_using(renderer or RendererManager.get_default())

    def _render_using(self, renderer: AbstractRenderer) -> str:
        result = ""
        attrs_stack: t.Dict[str, t.List[bool | Color | None]] = {
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

    def raw(self) -> str:
        return "".join(frag.string for frag in self._fragments)

    def append(
        self,
        string: str | Text,
        style: Style = NOOP_STYLE,
        close_this: bool = True,
        close_prev: bool = False,
    ) -> Text:
        if isinstance(string, str):
            self._fragments.append(_TextFragment(string, style, close_this, close_prev))
        elif isinstance(string, Text):
            if style != NOOP_STYLE:
                self._fragments.append(_TextFragment("", style, close_this, close_prev))
            self._fragments.extend(string._fragments)
        else:
            raise TypeError("Only str or another Text can be added to Text instance")
        return self

    def prepend(
        self,
        string: str | Text,
        style: Style = NOOP_STYLE,
        close_this: bool = True,
        close_prev: bool = False,
    ) -> Text:
        if isinstance(string, str):
            self._fragments.appendleft(
                _TextFragment(string, style, close_this, close_prev)
            )
        elif isinstance(string, Text):
            if style != NOOP_STYLE:
                self._fragments.appendleft(
                    _TextFragment("", style, close_this, close_prev)
                )
            self._fragments.extendleft(string._fragments)
        else:
            raise TypeError("Only str or another Text can be added to Text instance")
        return self

    def __len__(self) -> int:
        return sum(len(frag) for frag in self._fragments)

    def __add__(self, other: str | Text) -> Text:
        self.append(other)
        return self

    def __iadd__(self, other: str | Text) -> Text:
        self.append(other)
        return self

    def __radd__(self, other: str | Text) -> Text:
        self.prepend(other)
        return self

    def __format__(self, format_spec: str) -> str:
        """
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
            align_func = self.ALIGN_FUNC_MAP.get(align)
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
        if width_and_max_len_match := cls.WIDTH_MAX_LEN_REGEXP.search(format_spec):
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
            format_spec = cls.WIDTH_MAX_LEN_REGEXP.sub("", format_spec)

        align = None
        if format_spec.endswith((cls.ALIGN_LEFT, cls.ALIGN_RIGHT, cls.ALIGN_CENTER)):
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
    TAG_REGEXP = re.compile(
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

    ESCAPE_REGEXP = re.compile(r"([^\\])\\\[")
    SPLIT_REGEXP = re.compile(r"([^\s,]+)?([\s,]*)")

    def __init__(self, custom_styles: t.Dict[str, Style] = None):
        self._custom_styles: t.Dict[str, Style] = custom_styles or {}

    def parse(self, tpl: str) -> Text:
        result = Text()
        tpl_cursor = 0
        style_buffer = NOOP_STYLE
        split_style = False

        for tag_match in self.TAG_REGEXP.finditer(tpl):
            span = tag_match.span()
            tpl_part = self.ESCAPE_REGEXP.sub(r"\1[", tpl[tpl_cursor : span[0]])
            if len(tpl_part) > 0 or style_buffer != NOOP_STYLE:
                if split_style:
                    for tpl_chunk, sep in self.SPLIT_REGEXP.findall(tpl_part):
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
                raise LogicError(f"Unknown tag operand: {_TemplateTag}")

        result.append(tpl[tpl_cursor:])
        return result

    def _tag_to_style(self, tag: _TemplateTag) -> Style | None:
        if tag.comment:
            return None
        if tag.style in self._custom_styles.keys():
            return self._custom_styles[tag.style]

        style_attrs = {}
        for style_attr in tag.style.split(" "):
            if style_attr.startswith("fg=") or style_attr.startswith("bg="):
                style_attrs.update({k: v for k, v in (style_attr.split("="),)})
            else:
                if style_attr not in Style.renderable_attributes:
                    raise ValueError(f'Unknown style name or attribute: "{style_attr}"')
                style_attrs.update({style_attr: True})
        return Style(**style_attrs)


def render(string: t.Any, style: Style = NOOP_STYLE, renderer: AbstractRenderer = None):
    if isinstance(string, Text) and style == NOOP_STYLE:
        return string.render(renderer)
    return Text(string, style).render(renderer)


def echo(
    string: t.Any,
    style: Style = NOOP_STYLE,
    renderer: AbstractRenderer = None,
    nl: bool = True,
    file: t.IO = sys.stdout,
    flush: bool = True,
):
    print(
        render(string, style, renderer), end="\n" if nl else "", file=file, flush=flush
    )
