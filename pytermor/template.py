# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------

from __future__ import annotations

import re
import typing as t

import logging
from .exception import LogicError
from .style import Style, NOOP_STYLE, merge_styles
from .text import Text, Fragment, apply_style_words_selective


class _TemplateTag:
    def __init__(
        self,
        setf: str | None,
        seto: str | None,
        setx: str | None,
        add: str | None,
        comment: str | None,
        split: str | None,
        close: str | None,
        style: str | None,
    ):
        self.setf: str | None = setf.replace("?", "") if setf else None
        self.seto: str | None = seto.replace("!", "") if seto else None
        self.setx: str | None = setx.replace("@", "") if setx else None
        self.add: bool = bool(add)
        self.comment: bool = bool(comment)
        self.split: bool = bool(split)
        self.close: bool = bool(close)
        self.style: str | None = style

# USE CASES
#  f"@name:[fg=icathian_yellow]@version:[fg=superuser]"
#     f":[name bold]pytermor :[version]{pt.__version__}:[-version]:[-bold] {pt.__updated__}:[-name]"
#
#  @Todo: ':[-version -bold]'  WHY YOU NO WORK


class TemplateEngine:
    _TAG_REGEXP = re.compile(
        r"""
        (?: (?# instruction type)
          (?: (?# reg prefix)
               (?P<setf>\?\w+)  (?#    register new style in fallback mode)
              |(?P<seto>!\w+)   (?# or register new style in overwrite mode)
              |(?P<setx>@\w+)   (?# or register new style in exact mode)
          )?  (?# or use it right away) 
          (?P<add>:)       (?# insert style rendered as SGRs)
          |(?P<comment>\#)  (?# ignoted by parser)
        )
        (?![^\\]\\)  (?# ignore [ escaped with single backslash, but not double)
        \[
          (?P<split>\|)?
          (?P<close>-)?
          (?P<style>[\w =]+)
        \]
        """,
        re.VERBOSE,
    )

    _ESCAPE_REGEXP = re.compile(r"([^\\])\\\[")

    def __init__(self, custom_styles: t.Dict[str, Style] = None):
        self._custom_styles: t.Dict[str, Style] = custom_styles or {}

    def substitute(self, tpl: str) -> Text:
        result = Text()
        tpl_cursor = 0
        style_buffer = NOOP_STYLE
        split_style = False
        logging.debug(f"Parsing the template ({len(tpl)})")

        for tag_match in self._TAG_REGEXP.finditer(tpl):
            span = tag_match.span()
            tpl_part = self._ESCAPE_REGEXP.sub(r"\1[", tpl[tpl_cursor: span[0]])
            if len(tpl_part) > 0 or style_buffer != NOOP_STYLE:
                if split_style:
                    for part in apply_style_words_selective(tpl_part, style_buffer):
                        result += part
                    # add open style for engine to properly handle the :[-closing] tag:
                    tpl_part = ""
                result += Fragment(tpl_part, style_buffer, close_this=False)

            tpl_cursor = span[1]
            style_buffer = NOOP_STYLE
            split_style = False

            tag = _TemplateTag(**tag_match.groupdict())
            style = self._tag_to_style(tag)
            if tagp := (tag.setf or tag.seto):
                self._custom_styles[tagp] = merge_styles(
                    self._custom_styles.get(tagp, NOOP_STYLE),
                    fallbacks=[tag.setf or NOOP_STYLE],
                    overwrites=[tag.seto or NOOP_STYLE],
                )
            elif tag.setx:
                self._custom_styles[tag.setx] = style
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

