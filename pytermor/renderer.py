# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""
Module with output formatters. By default :class:`SGRRenderer` is used.

Abstract parent class `Renderer` contains global (library-wide) compatibility
settings. See `Renderer.set_up()`.

Working with non-default renderer can be accomplished in two ways:

    1. There is a module-level variable :data:`DefaultRenderer` determining what renderer
    `Style.render() <style.Style.render>` method will be using. Default renderer can be
    swapped with another one using `Renderer.set_as_default()` class method of the
    latter.

    2. Alternatively, you can use renderer's own class method `Renderer.render()`
    directly and avoid calling ``Style.render()`` method whatsoever.

.. testsetup:: *

    from pytermor.renderer import Renderer, DebugRenderer, NoOpRenderer
    from pytermor.style import Style

.. doctest::

    >>> Renderer.set_up(True)
    >>> DebugRenderer.set_as_default()
    >>> Style('red').render('_text_')
    'ǝ[31m_text_ǝ[39m'
    >>> NoOpRenderer.render(Style('red'), 'text')
    'text'

"""
from __future__ import annotations

import abc
import sys
from abc import abstractmethod

from .util import ReplaceSGR
from .span import Span
from .sequence import SequenceSGR, NOOP as NOOP_SEQ
from .style import Style
from .color import Color, ColorRGB, ColorIndexed, ColorDefault


class Renderer(metaclass=abc.ABCMeta):
    """
    Abstract parent of all other renderers. Among other things also contains
    settings shared between all renderer types that can be customized by developer
    at runtime.
    """
    _force_styles: bool|None = False
    _compatibility_indexed: bool = False
    _compatibility_default: bool = False

    @staticmethod
    def set_up(force_styles: bool|None = False,
               compatibility_indexed: bool = False,
               compatibility_default: bool = False):
        """
        Set up renderer preferences. Affects all renderer types.

        :param force_styles:

            * If set to *None*, all renderers will pass input text through themselves
              without any changes (i.e. no colors and attributes will be applied).
            * If set to *True*, renderers will always apply the formatting regardless
              of other internal rules and algorithms.
            * If set to *False* [default], the final decision will be made
              by every renderer independently, based on their own algorithms.

        :param compatibility_indexed:

            Disable *RGB* (or True Color) output mode. 256-color (*indexed*) sequences
            will be printed out instead of disabled ones. Useful when combined with
            ``curses`` -- that way you can check the terminal capabilities from the
            inside of that terminal and switch to different output mode at once.

        :param compatibility_default:

            Disable *indexed* output mode and use ``default`` 16-color sequences instead.
            If this setting is set to *True*, the value of ``compatibility_indexed``
            will be ignored completely. Useful when combined with ``curses`` -- that
            way you can check the terminal capabilities from the inside of that
            terminal and switch to different output mode at once.

        """
        Renderer._force_styles = force_styles
        Renderer._compatibility_indexed = compatibility_indexed
        Renderer._compatibility_default = compatibility_default

    @classmethod
    def set_as_default(cls):
        """
        Set renderer as default for `Style.render() <style.Style.render>` invocations.
        """
        global DefaultRenderer
        DefaultRenderer = cls

    @classmethod
    @abstractmethod
    def render(cls, style: Style, text: str) -> str:
        """
        Apply colors and attributes described in ``style`` argument to
        ``text`` and return the result. Output format depends on renderer's
        class (which defines the implementation).
        """
        raise NotImplementedError


class SGRRenderer(Renderer):
    """
    Default renderer that `Style.render() <style.Style.render>` invokes. Transforms `Color` instances defined
    in ``style`` argument into ANSI control sequence characters and merges them with input string.
    """

    @classmethod
    def render(cls, style: Style, text: str):
        """
        Render ``text`` with ``style`` applied as ANSI control sequences.

        Respects compatibility preferences (see `set_up()`) and maps RGB colors to
        closest *indexed* colors if terminal doesn't support RGB output. In case
        terminal doesn't support even 256 colors, falls back to ``default`` colors,
        searching for closest counterparts in 16-color table.

        Type of output ``SequenceSGR`` depends on type of `Color` variables in ``style`` argument. Keeping all that
        in mind, let's summarize:

        1. `ColorRGB` can be rendered as True Color sequence, indexed sequence
           and default (16-color) sequence depending on terminal capabilities.
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
        use_styles = cls._determine_style_usage()
        if not use_styles:
            return NOOP_SEQ

        if isinstance(color, ColorRGB):
            if cls._compatibility_default:
                return color.to_sgr_default(bg=bg)
            if cls._compatibility_indexed:
                return color.to_sgr_indexed(bg=bg)
            return color.to_sgr_rgb(bg=bg)

        elif isinstance(color, ColorIndexed):
            if cls._compatibility_default:
                return color.to_sgr_default(bg=bg)
            return color.to_sgr_indexed(bg=bg)

        elif isinstance(color, ColorDefault):
            return color.to_sgr_default(bg=bg)

        raise NotImplementedError(f'Unknown Color inhertior {color!s}')

    @classmethod
    def _determine_style_usage(cls) -> bool:
        if cls._force_styles is True:
            return True
        if cls._force_styles is None:
            return False
        return sys.stdout.isatty()


class TmuxRenderer(Renderer):
    pass


class NoOpRenderer(Renderer):
    @classmethod
    def render(cls, style: Style, text: str) -> str:
        """
        Special renderer type that does nothing with the input string and just returns it as is.

        .. doctest::

            >>> NoOpRenderer.render(Style(0xff00ff), 'text')
            'text'

        :param style: Style to ignore.
        :param text: Input string.
        :return: Input string without changes.
        """
        return text


class HtmlRenderer(Renderer):
    @classmethod
    def render(cls, style: Style, text: str) -> str:
        span_styles = []
        if style.fg_color.hex_value is not None:
            span_styles.append('color: {}'.format(style.fg_color.format_value("#")))
        if style.bg_color.hex_value is not None:
            span_styles.append('background-color: {}'.format(style.bg_color.format_value("#")))

        return f'<span style="{"; ".join(span_styles)}">{text}</span>' # @TODO attribues, bg color


class DebugRenderer(Renderer):
    @classmethod
    def render(cls, style: Style, text: str) -> str:
        return ReplaceSGR(r'ǝ\2\3\5').apply(SGRRenderer.render(style, text))


DefaultRenderer = SGRRenderer
