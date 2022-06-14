# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""
Module containing different output formatters. By default :class:`SGRRenderer` is used.

There is a module-level variable :data:`default_renderer` that is called from `style.Style.render()` method.
You can change the default renderer by calling ``set_as_default()`` class method of one
of the renderers. Alternatively, you can use renderer's own class method ``render()``.

Usage::

    >>> DebugRenderer.set_as_default()
    >>> Style('red').render('_text_')
    'ǝ[31m_text_ǝ[39m'
    >>> NoOpRenderer.render(Style('red'), 'text')
    'text'

"""
# terminal -> \e[nm
# tmux -> #[fg= bg=]
# html -> <span style='color: n'>
# debug -> ǝ[30;46m
# text ->
from __future__ import annotations

import abc
import sys
from abc import abstractmethod

from .util import ReplaceSGR
from .span import Span
from .sequence import SequenceSGR
from .style import Style
from .color import Color, ColorRGB, ColorIndexed, ColorDefault


class _Renderer(metaclass=abc.ABCMeta):
    @classmethod
    def set_as_default(cls):
        this.default_renderer = cls

    @classmethod
    @abstractmethod
    def render(cls, style: Style, text: str) -> str: raise NotImplementedError


class SGRRenderer(_Renderer):
    """
    Default renderer that `style.Style.render()` invokes. Transforms `Color` instances defined in ``style``
    argument into ANSI control sequence characters and merges them with input string.
    """
    _terminal_supports_indexed: bool|None = None
    _terminal_supports_rgb: bool|None = None

    @classmethod
    def render(cls, style: Style, text: str):
        """
        Render ``text`` with ``style`` applied as ANSI control sequences.

        Automatically determines terminal capabilities and maps RGB colors to closest *indexed* colors if terminal
        doesn't support RGB output. In case terminal doesn't support even 256 colors, falls back to *default* colors,
        searching for closest counterparts in 16-color table.

        Type of output ``SequenceSGR`` depends on type of `Color` variables in ``style`` argument. Keeping all that
        in mind, let's summarize:

        1. `ColorRGB` can be rendered as True Color sequence, indexed sequence and default (16-color) sequence depending
           on terminal capabilities.
        2. `ColorIndexed` can be rendered as indexed sequence or default sequence.
        3. `ColorDefault` will be rendered as default-color sequence.

        :param style: Style to apply.
        :param text: Input string.
        :return: Input string enclosed in SGR sequences.
        """
        opening_seq = cls._render_color(style.fg_color, False) + cls._render_color(style.bg_color, True)
        return Span(opening_seq).wrap(text)

    @classmethod
    def _render_color(cls, color: Color, bg: bool) -> SequenceSGR:
        if cls._terminal_supports_rgb is None or cls._terminal_supports_indexed is None:
            cls._determine_capabilities()

        if isinstance(color, ColorRGB):
            if cls._terminal_supports_rgb:
                return color.to_sgr_rgb(bg=bg)
            elif cls._terminal_supports_indexed:
                return color.to_sgr_indexed(bg=bg)
            else:
                return color.to_sgr_default(bg=bg)

        elif isinstance(color, ColorIndexed):
            if cls._terminal_supports_indexed:
                return color.to_sgr_indexed(bg=bg)
            else:
                return color.to_sgr_default(bg=bg)

        elif isinstance(color, ColorDefault):
            return color.to_sgr_default(bg=bg)

        raise NotImplementedError(f'Unknown Color inhertior {color!s}')

    @classmethod
    def _determine_capabilities(cls):
        cls._terminal_supports_indexed = False
        cls._terminal_supports_rgb = False  # @TODO


class TmuxRenderer(_Renderer):
    pass


class NoOpRenderer(_Renderer):
    @classmethod
    def render(cls, style: Style, text: str) -> str:
        return text


class HtmlRenderer(_Renderer):
    pass


class DebugRenderer(_Renderer):
    @classmethod
    def render(cls, style: Style, text: str) -> str:
        return ReplaceSGR(r'ǝ\2\3\5').apply(SGRRenderer.render(style, text))


this = sys.modules[__name__]
this.default_renderer = SGRRenderer
