# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""
Module with output formatters. By default :class:`SGRRenderer` is used. It
also contains compatibility settings, see `SGRRenderer.set_up()`.

Working with non-default renderer can be achieved in two ways:

a. Method `RendererManager.set_up()` sets the default renderer globally.
b. Alternatively, you can use renderer's own class method `Renderer.render()`
   directly and avoid calling `Style.render()` method whatsoever.

.. testsetup:: *

    from pytermor.renderer import *
    from pytermor.style import Style

    SGRRenderer.set_up(force_styles = True)

"""
from __future__ import annotations

import abc
import sys
from abc import abstractmethod
from typing import Type

from . import sequence
from .color import Color, ColorRGB, ColorIndexed, ColorDefault
from .sequence import SequenceSGR, NOOP as NOOP_SEQ
from .span import Span
from .style import Style
from .util import ReplaceSGR


class RendererManager:
    _default: Type[Renderer] = None

    @classmethod
    def set_up(cls, default_renderer: Type[Renderer]|None = None):
        """
        Set up renderer preferences. Affects all renderer types.

        :param default_renderer:
            Default renderer to use globally. Passing None will result in library
            default setting restored (`SGRRenderer`).

        >>> RendererManager.set_up(DebugRenderer)
        >>> Style('red').render('text')
        '|ǝ31|text|ǝ39|'

        >>> NoOpRenderer.render(Style('red'), 'text')
        'text'
        """
        cls._default = default_renderer or SGRRenderer

    @classmethod
    def get_default(cls) -> Type[Renderer]:
        """ Get global default renderer type. """
        return cls._default


class Renderer(metaclass=abc.ABCMeta):
    """ Abstract ancestor of all renderers. """

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
    Default renderer that `Style.render() <style.Style.render>` invokes. Transforms
    `Color` instances defined in ``style`` argument into ANSI control sequence
    characters and merges them with input string.
    """
    _force_styles: bool|None = False
    _compatibility_indexed: bool = False
    _compatibility_default: bool = False

    @classmethod
    def set_up(cls, force_styles: bool|None = False,
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

            Disable *indexed* output mode and use *default* 16-color sequences instead.
            If this setting is set to *True*, the value of ``compatibility_indexed``
            will be ignored completely. Useful when combined with ``curses`` -- that
            way you can check the terminal capabilities from the inside of that
            terminal and switch to different output mode at once.

        """
        cls._force_styles = force_styles
        cls._compatibility_indexed = compatibility_indexed
        cls._compatibility_default = compatibility_default

    @classmethod
    def render(cls, style: Style, text: str):
        """
        Render ``text`` with ``style`` applied as ANSI control sequences.

        Respects compatibility preferences (see `RendererManager.set_up()`) and
        maps RGB colors to closest *indexed* colors if terminal doesn't support
        RGB output. In case terminal doesn't support even 256 colors, falls back
        to *default* colors, searching for closest counterparts in 16-color table.

        Type of output ``SequenceSGR`` depends on type of `Color` variables in
        ``style`` argument. Keeping all that
        in mind, let's summarize:

        1. `ColorRGB` can be rendered as True Color sequence, indexed sequence
           or default (16-color) sequence depending on terminal capabilities.
        2. `ColorIndexed` can be rendered as indexed sequence or default sequence.
        3. `ColorDefault` will be rendered as default-color sequence.

        >>> SGRRenderer.render(Style('red', bold=True), 'text')
        '\\x1b[1;31mtext\\x1b[22;39m'

        :param style: Style to apply.
        :param text: Input string.
        :return: Input string enclosed in SGR sequences.
        """
        opening_seq = cls._render_attributes(style) + \
                      cls._render_color(style.fg, False) + \
                      cls._render_color(style.bg, True)

        return Span(opening_seq).wrap(text)

    @classmethod
    def _render_attributes(cls, style: Style) -> SequenceSGR:
        result = NOOP_SEQ
        if style.blink:             result += sequence.BLINK_DEFAULT
        if style.bold:              result += sequence.BOLD
        if style.crosslined:        result += sequence.CROSSLINED
        if style.dim:               result += sequence.DIM
        if style.double_underlined: result += sequence.DOUBLE_UNDERLINED
        if style.inversed:          result += sequence.INVERSED
        if style.italic:            result += sequence.ITALIC
        if style.overlined:         result += sequence.OVERLINED
        if style.underlined:        result += sequence.UNDERLINED
        return result

    @classmethod
    def _render_color(cls, color: Color, bg: bool) -> SequenceSGR:
        use_styles = cls._determine_style_usage()
        if not use_styles:
            return NOOP_SEQ

        hex_value = color.hex_value

        if isinstance(color, ColorRGB):
            if cls._compatibility_default:
                return ColorDefault.find_closest(hex_value).to_sgr(bg=bg)
            if cls._compatibility_indexed:
                return ColorIndexed.find_closest(hex_value).to_sgr(bg=bg)
            return color.to_sgr(bg=bg)

        elif isinstance(color, ColorIndexed):
            if cls._compatibility_default:
                return ColorDefault.find_closest(hex_value).to_sgr(bg=bg)
            return color.to_sgr(bg=bg)

        elif isinstance(color, ColorDefault):
            return color.to_sgr(bg=bg)

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
        Special renderer type that does nothing with the input string and just
        returns it as is.

        >>> NoOpRenderer.render(Style('red', bold=True), 'text')
        'text'

        :param style: Style to ignore.
        :param text: Input string.
        :return: Input string without changes.
        """
        return text


class HtmlRenderer(Renderer):
    @classmethod
    def render(cls, style: Style, text: str) -> str:
        """
        >>> HtmlRenderer.render(Style('red', bold=True), 'text')
        '<span style="color: #800000; font-weight: bold">text</span>'
        """
        span_styles = []
        span_classes = []
        if style.fg.hex_value is not None:
            span_styles.append(f'color: {style.fg.format_value("#")}')
        if style.bg.hex_value is not None:
            span_styles.append(f'background-color: {style.bg.format_value("#")}')
        if style.blink:
            pass  # modern browsers doesn't support it without piling up markup and stylesheets
        if style.bold:
            span_styles.append('font-weight: bold')
        if style.crosslined:
            span_styles.append('text-decoration: line-through')
        if style.italic:
            span_styles.append('font-style: italic')

        return f'<span style="{"; ".join(span_styles)}" class="{" ".join(span_classes)}">{text}</span>'  # @TODO
        # attribues, bg color


class DebugRenderer(Renderer):
    @classmethod
    def render(cls, style: Style, text: str) -> str:
        """
        >>> DebugRenderer.render(Style('red', bold=True), 'text')
        '|ǝ1;31|text|ǝ22;39|'
        """
        return ReplaceSGR(r'|ǝ\3|').apply(SGRRenderer.render(style, text))


RendererManager.set_up()
