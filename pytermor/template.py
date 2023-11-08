# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------

from __future__ import annotations

import logging
import re
import typing as t
from abc import abstractmethod, ABCMeta
from collections import deque
from dataclasses import dataclass
from typing import Union

from .ansi import SequenceCSI, SeqIndex
from .color import resolve_color, DEFAULT_COLOR
from .common import get_qname
from .exception import LogicError
from .renderer import IRenderer
from .style import MergeMode, NOOP_STYLE, Style, merge_styles
from .term import (
    make_clear_display,
    make_clear_display_after_cursor,
    make_clear_display_before_cursor,
    make_clear_line,
    make_clear_line_after_cursor,
    make_clear_line_before_cursor,
    make_reset_cursor,
)
from .text import Fragment, Text, apply_style_words_selective, apply_style_selective
from .text import render as text_render

_T = t.TypeVar("_T")


class _StyleSplitter(metaclass=ABCMeta):
    def __init__(self, tag_style: Style):
        self._tag_style = tag_style

    @property
    def tag_style(self) -> Style:
        return self._tag_style

    @abstractmethod
    def apply(self, tpl_text: str) -> t.Sequence[Fragment]:
        raise NotImplementedError


class _SplitterWordsSelectiveWSpace(_StyleSplitter):
    def apply(self, tpl_text: str) -> t.Sequence[Fragment]:
        return apply_style_words_selective(tpl_text, self._tag_style)


class _SplitterWordsSelectiveComma(_StyleSplitter):
    def apply(self, tpl_text: str) -> t.Sequence[Fragment]:
        return apply_style_selective(
            re.compile(r"([^,]+)?([, ]*)"), tpl_text, self._tag_style
        )


@dataclass(frozen=True)
class _TemplateTagGroups:
    register: str | None
    name: str | None
    split: str
    action: str
    attrs: str
    pos: str
    clear: str


class _TemplateTag:
    _REGISTER_TO_MERGE_MODE = {
        "?": MergeMode.FALLBACK,
        "!": MergeMode.OVERWRITE,
        "@": MergeMode.REPLACE,
    }
    _CLEAR_TO_SEQ = {
        "<>": make_clear_line(),
        "<<>>": make_clear_display(),
        "<": make_clear_line_before_cursor(),
        ">": make_clear_line_after_cursor(),
        "<<": make_clear_display_before_cursor(),
        ">>": make_clear_display_after_cursor(),
    }
    _SPLITTERS = {
        "|": _SplitterWordsSelectiveWSpace,
        ",": _SplitterWordsSelectiveComma,
    }

    _ACTION_OPENER = "+"
    _ACTION_TERMINATOR = "-"
    _ACTION_RESETTER = "$"

    def __init__(self, raw: str, **groups):
        self._raw = raw
        self._groups = _TemplateTagGroups(**groups)

    @property
    def raw(self) -> str:
        return self._raw

    @property
    def groups(self) -> _TemplateTagGroups:
        return self._groups

    @property
    def reg_merge_mode(self) -> MergeMode | None:
        return self._REGISTER_TO_MERGE_MODE.get(self._groups.register, None)

    @property
    def clear_seq(self) -> SequenceCSI:
        return self._CLEAR_TO_SEQ.get(self._groups.clear, None)

    @property
    def is_opener(self) -> bool:
        return self._groups.action in (self._ACTION_OPENER, "")

    @property
    def is_terminator(self) -> bool:
        return self._groups.action == self._ACTION_TERMINATOR

    @property
    def is_resetter(self) -> bool:
        return self._groups.action == self._ACTION_RESETTER

    @property
    def splitter(self) -> type[_StyleSplitter] | None:
        if not self._groups.split:
            return None
        if self._groups.split not in self._SPLITTERS.keys():  # pragma: no cover
            raise LogicError(
                f"Invalid template tag style splitter: '{self._groups.split}'"
            )
        return self._SPLITTERS.get(self._groups.split)

    def style(self, custom_styles: t.Dict[str, Style]) -> Style | None:
        if not self._groups.attrs:
            return NOOP_STYLE

        style_attrs = {}
        base_style = NOOP_STYLE
        for style_attr in self._groups.attrs.split(" "):
            if not style_attr:
                continue
            if style_attr in custom_styles.keys():
                if base_style != NOOP_STYLE:
                    raise LogicError(f"Max. one custom style per tag: ({style_attr})")
                base_style = custom_styles[style_attr]
                continue

            if re.match("fg|bg|underline_color", style_attr):
                style_attrs.update(
                    {
                        k: (v or DEFAULT_COLOR)
                        for (k, _, v) in (style_attr.partition("="),)
                    }
                )
                continue

            if style_attr in Style.renderable_attributes:
                style_attrs.update({style_attr: True})
                continue

            try:
                color = resolve_color(style_attr)
                style_attrs.update({"fg": color})
                continue
            except LookupError:
                pass

            raise ValueError(f'Unknown style name or attribute: "{style_attr}"')

        return Style(base_style, **style_attrs)


class _LoggingStack(deque[_T], metaclass=ABCMeta):
    def __init__(self, name: str, *, maxlen: int = None):
        super().__init__(maxlen=maxlen)
        self._name = name

    def append(self, st: _T) -> None:
        super().append(st)

    def pop(self) -> _T:
        st = super().pop()
        return st

    def clear(self) -> None:
        super().clear()

    def __repr__(self) -> str:
        return ",".join(map(self._repr_item, self))

    @abstractmethod
    def _repr_item(self, o: _T) -> str:
        raise NotImplementedError


class _FragmentStack(_LoggingStack[Fragment]):
    def _repr_item(self, o: Fragment) -> str:  # pragma: no cover
        return str(o)


class _StyleStack(_LoggingStack[Style]):
    @property
    def current(self) -> Style:
        return merge_styles(NOOP_STYLE, overwrites=[*self])

    def _repr_item(self, o: Style) -> str:
        return o.repr_attrs(verbose=False)


class _SplitterStack(_LoggingStack[_StyleSplitter]):
    def __init__(self, name: str) -> None:
        super().__init__(name, maxlen=1)

    def _repr_item(self, o: _StyleSplitter) -> str:
        return get_qname(o)


class TemplateEngine:
    """
    @TODO
    """

    _TAG_REGEX = re.compile(
        r"""                  ##### TAG PREFIX #######
        ((?P<register>[?!@])  # save tag to local map as fallback/overwrite/explicitly
         (?P<name>[\w-]+)     # /under specified name/  
        )?                    # or make a one-use tag and insert encoded SGR  
        :                     ########################
        (?![^\\]\\)           # /ignore escaped with single backslash, but not double/
        \[(?:                 ####### TAG BODY #######
            (?P<pos>\^)                     #   reset cursor
            |                               # OR
            (?P<clear>(<<|<|<>|<<>>|>|>>))  #   clear current line / the whole screen
            |                               # OR
            (?P<split>[|,]?)                #   /with splitting/ 
            (?P<action>[+$-]?)              #   open style/reset styles/close style
            (?P<attrs>[a-zA-Z][\w =#-]*|)   #   /with style attributes/ or /close last/  
            
        )\]
        """,
        re.VERBOSE,
    )
    _COMMENT_REGEX = re.compile(r"#\[.*?\]")
    _ESCAPE_REGEX = re.compile(r"([^\\])\\\[")

    def __init__(
        self, custom_styles: t.Dict[str, Style] = None, global_style: Style = NOOP_STYLE
    ):
        self._user_styles: t.Dict[str, Style] = custom_styles or {}
        self._global_style = global_style

    def reset(self):
        self._user_styles.clear()

    def render(self, tpl: str, renderer: IRenderer) -> str:
        return text_render(self.substitute(tpl), renderer=renderer)

    def substitute(self, tpl: str) -> Text:
        tpl_parts = self._split(tpl)

        logging.getLogger(__package__).debug(f"Split to {len(tpl_parts)} parts")
        return self._assemble(tpl_parts)

    def _split(self, tpl: str) -> deque[Union[str, _TemplateTag]]:
        tpl_cursor = 0
        tpl_nocom = self._COMMENT_REGEX.sub("", tpl)
        tpl_parts = deque[Union[str, _TemplateTag]]()

        for idx, tag_match in enumerate(self._TAG_REGEX.finditer(tpl_nocom)):
            tpl_span = tag_match.span()
            text_before = self._ESCAPE_REGEX.sub(
                r"\1[", tpl_nocom[tpl_cursor : tpl_span[0]]
            )
            tpl_cursor = tpl_span[1]
            if text_before:
                tpl_parts.append(text_before)
            tpl_parts.append(_TemplateTag(tag_match.group(), **tag_match.groupdict()))

        if text_last := tpl_nocom[tpl_cursor:]:
            tpl_parts.append(text_last)

        return tpl_parts

    def _assemble(self, tpl_parts: deque[Union[str, _TemplateTag]]) -> Text:
        result = _FragmentStack("result")
        st_stack = _StyleStack("stack")
        spl_stack = _SplitterStack("spl st")

        from_stack = st_stack.pop
        to_stack = st_stack.append

        for idx, tpl_part in enumerate(tpl_parts):
            _stacks_str = f"[" + "] [".join(repr(s) for s in [spl_stack, st_stack]) + "]"

            if isinstance(tpl_part, str):

                if spl_stack:
                    for segm in (splitter := spl_stack.pop()).apply(tpl_part):
                        result.append(segm)
                    # add open style for engine to properly handle the :[-closing] tag:
                    to_stack(splitter.tag_style)
                    continue

                result.append(Fragment(tpl_part, st_stack.current))
                continue

            tag = t.cast(_TemplateTag, tpl_part)
            tag_style = tag.style(self._user_styles)

            if splitter := tag.splitter:
                spl_stack.append(splitter(tag_style))

            elif tag.reg_merge_mode:
                existing_st = self._user_styles.get(tag.groups.name, NOOP_STYLE.clone())
                updated_st = existing_st.merge(tag.reg_merge_mode, tag_style)
                self._user_styles[tag.groups.name] = updated_st

            elif tag.groups.pos:
                result.append(Fragment(make_reset_cursor().assemble()))

            elif tag.groups.clear:
                result.append(Fragment(tag.clear_seq.assemble()))

            elif tag.is_resetter:
                st_stack.clear()
                result.append(Fragment(SeqIndex.RESET.assemble()))

            elif tag.is_terminator:
                if not st_stack:
                    continue
                if not tag.groups.attrs:
                    from_stack()
                else:
                    if (st_prev := from_stack()) != tag_style:
                        raise LogicError(
                            f"Terminator '{tag.raw}' doesn't match corresponding opener: {st_prev}"
                        )

            elif tag.is_opener:
                to_stack(tag_style)

            else:  # pragma: no cover
                raise LogicError(f"Invalid tag: {tag.raw}")

        for idx, frag in enumerate(result):
            if not frag.style:
                result[idx] = Fragment(frag.raw(), self._global_style)
            else:
                frag.style.merge_overwrite(self._global_style)
        return Text(*result)


_template_engine = TemplateEngine()

substitute = _template_engine.substitute
""" yes """
render = _template_engine.render
""" yes yes """
