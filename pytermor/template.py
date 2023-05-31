# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from .ansi import *
from .exception import LogicError
from .color import resolve_color
from .common import ExtendedEnum
from .style import Style, NOOP_STYLE, MergeMode
from .text import Text, Fragment, apply_style_words_selective


class TemplateTagOption(str, ExtendedEnum):
    STYLE_WORDS_SELECTIVE = "|"


@dataclass(frozen=True)
class _TemplateTagRaw:
    persist: str | None
    name: str | None
    options: str
    action: str
    attrs: str
    pos: str
    clear: str


class TemplateEngine:
    _TAG_REGEX = re.compile(
        r"""                  ##### TAG PREFIX #######
        ((?P<persist>[?!@])   # save tag to local map as fallback/overwrite/explicitly
         (?P<name>[\w-]+)     # … under specified name  
        )?                    # … or make a one-use tag
        :                     # … and assemble the SGR and insert the bytes
        (?![^\\]\\)           # ignore escaped with single backslash, but not double
        \[(?:                 ####### TAG BODY #######
            (?P<pos>0)            # reset cursor
            |                     # … OR clear current line / the whole screen
            (?P<clear>(<<|<|<>|<<>>|>|>>))  #
            |
            (?P<options>[|]*)     # … OR /with options/ 
            (?P<action>[+-]?)     # … open or close style  /empty=open/
            (?P<attrs>[a-zA-Z][\w =-]*|)   # … add style attributes OR close last  
            
        )\]
        """,
        re.VERBOSE,
    )
    _COMMENT_REGEX = re.compile(r"#\[.*?\]")
    _ESCAPE_REGEX = re.compile(r"([^\\])\\\[")

    PERSIST_TO_MERGE_MODE = {
        "?": MergeMode.FALLBACK,
        "!": MergeMode.OVERWRITE,
        "@": MergeMode.REPLACE,
    }
    CLEAR_TO_SEQ = {
        "<>": make_clear_line().assemble(),
        "<<>>": make_clear_display().assemble(),
        "<": make_clear_line_before_cursor().assemble(),
        ">": make_clear_line_after_cursor().assemble(),
        "<<": make_clear_display_before_cursor().assemble(),
        ">>": make_clear_display_after_cursor().assemble(),
    }

    def __init__(self, custom_styles: t.Dict[str, Style] = None):
        self._user_styles: t.Dict[str, Style] = custom_styles or {}

    def substitute(self, tpl: str) -> Text:
        result = Text()
        tpl_cursor = 0
        style_buffer = NOOP_STYLE
        st_opts = []
        logging.debug(f"Parsing the template ({len(tpl)})")

        tpl_nocom = self._COMMENT_REGEX.sub("", tpl)
        for tag_match in self._TAG_REGEX.finditer(tpl_nocom):
            span = tag_match.span()
            tpl_part = self._ESCAPE_REGEX.sub(r"\1[", tpl[tpl_cursor: span[0]])
            if len(tpl_part) > 0 or style_buffer != NOOP_STYLE:
                if TemplateTagOption.STYLE_WORDS_SELECTIVE in st_opts:
                    for part in apply_style_words_selective(tpl_part, style_buffer):
                        result += part
                    # add open style for engine to properly handle the :[-closing] tag:
                    tpl_part = ""
                result += Fragment(tpl_part, style_buffer, close_this=False)

            tpl_cursor = span[1]
            tagr = _TemplateTagRaw(**tag_match.groupdict())
            if tagr.action == "-" and not tagr.attrs:
                result += Fragment("", style_buffer, close_prev=True)
            elif tagr.pos:
                result += Fragment(make_reset_cursor().assemble(), None)
            elif tagr.clear:
                result += Fragment(self.CLEAR_TO_SEQ.get(tagr.clear, NOOP_SEQ), None)

            style_buffer = NOOP_STYLE
            st_opts = []

            input_style = self._tag_to_style(tagr, self._user_styles)
            if merge_mode := self.PERSIST_TO_MERGE_MODE.get(tagr.persist):
                self._user_styles[tagr.name] = self._user_styles.get(
                    tagr.name, NOOP_STYLE.clone()
                ).merge(merge_mode, input_style)
                continue

            if tagr.action == "-":
                result += Fragment("", input_style, close_prev=True)
            else:
                style_buffer = input_style
                st_opts = [
                    {v: k for k, v in TemplateTagOption.dict().items()}.get(opt)
                    for opt in (tagr.options or [])
                ]
            continue

        result += tpl_nocom[tpl_cursor:]
        return result

    def _tag_to_style(
        self, raw: _TemplateTagRaw, custom_styles: t.Dict[str, Style]
    ) -> Style | None:
        style_attrs = {}
        base_style = NOOP_STYLE
        if raw.attrs:
            for style_attr in raw.attrs.split(" "):
                if not style_attr:
                    continue
                if style_attr in custom_styles.keys():
                    if base_style != NOOP_STYLE:
                        raise LogicError(
                            f"Only one custom style per tag is allowed: ({style_attr})"
                        )
                    base_style = custom_styles[style_attr]
                    continue

                if style_attr.startswith("fg=") or style_attr.startswith("bg="):
                    style_attrs.update({k: v for k, v in (style_attr.split("="),)})
                    continue

                if style_attr in Style.renderable_attributes:
                    style_attrs.update({style_attr: True})
                    continue

                try:
                    if color := resolve_color(style_attr):
                        style_attrs.update({"fg": color})
                        continue
                except LookupError:
                    pass

                raise ValueError(f'Unknown style name or attribute: "{style_attr}"')
        return Style(base_style, **style_attrs)


_template_engine = TemplateEngine()
