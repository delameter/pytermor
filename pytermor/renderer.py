# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""
Module with output formatters. Default global renderer type is `SgrRenderer`.

Customizing of rendering mode can be accomplished in two ways:

    a. Method `RendererManager.set_default()` sets the default renderer globally.
       After that calling `text.render()` will automatically invoke a said renderer
       and all formatting will be applied.
    b. Alternatively, you can use renderer's own instance method ``render()``
       directly and avoid messing up with the manager:
       `HtmlRenderer.render()`.

Generally speaking, if you need to invoke a custom renderer just once, it's
convenient to use the second method for this case and use the global one
in all the others.

On the contrary, if there is a necessity to use more than one renderer
alternatingly, it's better to avoid using the global one at all, and just
instantiate and invoke two _get_renderers independently.

.. rubric :: TL;DR

To unconditionally print formatted message to standard output, do something like
this:

    >>> from pytermor import render, RendererManager, Styles
    >>> RendererManager.set_default_to_force_formatting()
    >>> render('Warning: AAAA', Styles.WARNING)
    '\\x1b[33mWarning: AAAA\\x1b[39m'

.. testsetup:: *

    from pytermor.renderer import *
    from pytermor import render

"""
from __future__ import annotations

import enum
import os
import sys
import typing as t
from abc import ABCMeta, abstractmethod
from functools import reduce

from .ansi import SequenceSGR, NOOP_SEQ, SeqIndex, get_closing_seq
from .color import Color, Color16, Color256, ColorRGB, NOOP_COLOR
from .common import logger
from .style import Style, NOOP_STYLE, Styles
from .utilstr import ReplaceSGR


class RendererManager:
    _default: AbstractRenderer = None

    @classmethod
    def set_default(cls, renderer: AbstractRenderer | t.Type[AbstractRenderer] = None):
        """
        Select a global renderer.

            >>> RendererManager.set_default(SgrRendererDebugger(OutputMode.XTERM_16))
            >>> render('text', Style(fg='red'))
            '|ǝ31|text|ǝ39|'

        :param renderer:
            Default renderer to use globally. Calling this method without arguments
            will result in library default renderer `SgrRenderer` being set as default.

            All the methods with the ``renderer`` argument (e.g., `text.render()`)
            will use the global default one if said argument is omitted or set to *None*.

            You can specify either the renderer class, in which case manager will
            instantiate it with the default parameters, or provide already instantiated
            and set up renderer, which will be registred as global.
        """
        if isinstance(renderer, type):
            renderer = renderer()
        cls._default = renderer or SgrRenderer()

    @classmethod
    def get_default(cls) -> AbstractRenderer:
        """
        Get global renderer instance (`SgrRenderer`, or the one provided with
        `set_default()`).
        """
        return cls._default

    @classmethod
    def set_default_to_force_formatting(cls):
        """ deprecated """
        cls.set_default_format_always()

    @classmethod
    def set_default_to_disable_formatting(cls):
        """ deprecated """
        cls.set_default_format_never()

    @classmethod
    def set_default_format_always(cls):
        """
        Shortcut for forcing all control sequences to be present in the
        output of a global renderer.

        Note that it applies only to the renderer that is set up as default at
        the moment of calling this method, i.e., all previously created instances,
        as well as the ones that will be created afterwards, are unaffected.
        """
        cls.set_default(SgrRenderer(OutputMode.TRUE_COLOR))

    @classmethod
    def set_default_format_never(cls):
        """
        Shortcut for disabling all output formatting of a global renderer.
        """
        cls.set_default(SgrRenderer(OutputMode.NO_ANSI))


class AbstractRenderer(metaclass=ABCMeta):
    """Renderer interface."""

    @property
    @abstractmethod
    def is_format_allowed(self) -> bool:
        """
        :return:
        """

    @abstractmethod
    def render(self, string: t.Any, fmt: Color|Style = NOOP_STYLE) -> str:
        """
        Apply colors and attributes described in ``fmt`` argument to
        ``string`` and return the result. Output format depends on renderer's
        class, which defines the implementation.

        :param string: String to format.
        :param fmt:    Style or color to apply. If ``fmt`` is a `Color` instance,
                       it is assumed to be a foreground color.
        :return: String with formatting applied, or without it, depending on
                 renderer settings.
        """

    def __repr__(self):
        return self.__class__.__qualname__ + '[]'


class OutputMode(enum.Enum):
    """
    Determines what types of SGR sequences are allowed to use in the output.
    """

    NO_ANSI = 'no_ansi'
    """
    The renderer discards all color and format information completely.
    """ 
    XTERM_16 = 'xterm_16'
    """
    16-colors mode. Enforces the renderer to approximate all color types
    to `Color16` and render them as basic mode selection SGR sequences
    (``ESC[31m``, ``ESC[42m`` etc). See `Color.approximate()` for approximation
    algorithm details.
    """
    XTERM_256 = 'xterm_256'
    """
    256-colors mode. Allows the renderer to use either `Color16` or `Color256` 
    (but RGB will be approximated to 256-color pallette).
    """
    TRUE_COLOR = 'true_color'
    """
    RGB color mode. Does not apply restrictions to color rendering.
    """
    AUTO = 'auto'
    """
    Lets the renderer select the most suitable mode by itself.
    See `SgrRenderer` constructor documentation for the details. 
    """


class SgrRenderer(AbstractRenderer):
    """
    .. todo ::
        make render() protected (?)

    Default renderer invoked by `Text.render()`. Transforms `Color` instances
    defined in ``style`` into ANSI control sequence bytes and merges them with
    input string. Type of resulting `SequenceSGR` depends on type of `Color`
    instances in ``style`` argument and current output mode of the renderer.

    1. `ColorRGB` can be rendered as True Color sequence, 256-color sequence
       or 16-color sequence depending on specified `OutputMode`.
    2. `Color256` can be rendered as 256-color sequence or 16-color
       sequence.
    3. `Color16` will be rendered as 16-color sequence.
    4. Nothing of the above will happen and all formatting will be discarded
       completely if output device is not a terminal emulator or if the developer
       explicitly set up the renderer to do so (`OutputMode.NO_ANSI`).

    Renderer approximates RGB colors to closest **indexed** colors if terminal doesn't
    support RGB output. In case terminal doesn't support even 256 colors, it
    falls back to 16-color palette and picks closest samples again the same way.
    See `OutputMode` documentation for exact mappings.

    >>> SgrRenderer(OutputMode.XTERM_256).render('text', Styles.WARNING_LABEL)
    '\\x1b[1;33mtext\\x1b[22;39m'
    >>> SgrRenderer(OutputMode.NO_ANSI).render('text', Styles.WARNING_LABEL)
    'text'

    :param output_mode:
        SGR output mode to use. Valid values are listed in `OutputMode` enum.

        With `OutputMode.AUTO` the renderer will first check if the output
        device is a terminal emulator, and use `OutputMode.NO_ANSI` when it
        is not. Otherwise, the renderer will read ``TERM`` environment
        variable and follow these rules:

            - `OutputMode.NO_ANSI` if ``TERM`` is set to ``xterm``.
            - `OutputMode.XTERM_16` if ``TERM`` is set to ``xterm-color``.
            - `OutputMode.XTERM_256` in all other cases.

        Special case is when ``TERM`` equals to ``xterm-256color`` **and**
        ``COLORTERM`` is either ``truecolor`` or  ``24bit``, then
        `OutputMode.TRUE_COLOR` will be used.
    """

    _COLOR_UPPER_BOUNDS: t.Dict[OutputMode, t.Type[Color]] = {
        OutputMode.XTERM_16: Color16,
        OutputMode.XTERM_256: Color256,
        OutputMode.TRUE_COLOR: ColorRGB,
    }
    _color_upper_bound: t.Type[Color | None] = None

    _output_mode: OutputMode = OutputMode.AUTO

    def __init__(self, output_mode: OutputMode = OutputMode.AUTO):
        self._output_mode = self._determine_output_mode(output_mode)
        self._color_upper_bound = self._COLOR_UPPER_BOUNDS.get(self._output_mode, None)

        logger.debug(f"Output mode: {output_mode.name} -> {self._output_mode.name}")
        logger.debug(f"Color upper bound: {self._color_upper_bound}")

    @property
    def is_format_allowed(self) -> bool:
        return self._output_mode is not OutputMode.NO_ANSI

    def render(self, string: t.Any, fmt: Color|Style = NOOP_STYLE) -> str:
        style = Style.make(fmt)
        opening_seq = (
            self._render_attributes(style, squash=True)
            + self._render_color(style.fg, False)
            + self._render_color(style.bg, True)
        )

        # in case there are line breaks -- split text to lines and apply
        # SGRs for each line separately. it increases the chances that style
        # will be correctly displayed regardless of implementation details of
        # user's pager, multiplexer, terminal emulator etc.
        rendered_text = ""
        for line in str(string).splitlines(keepends=True):
            rendered_text += (
                opening_seq.assemble() + line + get_closing_seq(opening_seq).assemble()
            )
        return rendered_text

    def _determine_output_mode(self, arg_value: OutputMode) -> OutputMode:
        if arg_value is not OutputMode.AUTO:
            return arg_value

        isatty = sys.stdout.isatty()
        term = os.environ.get("TERM", None)
        colorterm = os.environ.get("COLORTERM", None)
        logger.debug(f"Stdout is a terminal: {isatty}")
        logger.debug(f"Environment: TERM='{term}'")
        logger.debug(f"Environment: COLORTERM='{colorterm}'")

        if not isatty:
            return OutputMode.NO_ANSI
        if term == "xterm":
            return OutputMode.NO_ANSI
        if term == "xterm-color":
            return OutputMode.XTERM_16
        if colorterm in ("truecolor", "24bit"):
            return OutputMode.TRUE_COLOR
        return OutputMode.XTERM_256

    def _render_attributes(
        self, style: Style, squash: bool
    ) -> t.List[SequenceSGR] | SequenceSGR:
        if not self.is_format_allowed:
            return NOOP_SEQ if squash else [NOOP_SEQ]

        result = []
        if style.blink:
            result += [SeqIndex.BLINK_SLOW]
        if style.bold:
            result += [SeqIndex.BOLD]
        if style.crosslined:
            result += [SeqIndex.CROSSLINED]
        if style.dim:
            result += [SeqIndex.DIM]
        if style.double_underlined:
            result += [SeqIndex.DOUBLE_UNDERLINED]
        if style.inversed:
            result += [SeqIndex.INVERSED]
        if style.italic:
            result += [SeqIndex.ITALIC]
        if style.overlined:
            result += [SeqIndex.OVERLINED]
        if style.underlined:
            result += [SeqIndex.UNDERLINED]

        if squash:
            return reduce(lambda p, c: p + c, result, NOOP_SEQ)
        return result

    def _render_color(self, color: Color, bg: bool) -> SequenceSGR:
        if not self.is_format_allowed or color == NOOP_COLOR:
            return NOOP_SEQ
        return color.to_sgr(bg, self._color_upper_bound)


class TmuxRenderer(AbstractRenderer):
    """
    tmux

    >>> TmuxRenderer().render('text',  Style(fg='blue', bold=True))
    '#[fg=blue bold]text#[fg=default nobold]'
    """

    STYLE_ATTR_TO_TMUX_MAP = {
        "fg": "fg",
        "bg": "bg",
        "blink": "blink",
        "bold": "bold",
        "crosslined": "strikethrough",
        "dim": "dim",
        "double_underlined": "double-underscore",
        "inversed": "reverse",
        "italic": "italics",
        "overlined": "overline",
        "underlined": "underscore",
    }

    @property
    def is_format_allowed(self) -> bool:
        return True

    def render(self, string: t.Any, fmt: Color|Style = NOOP_STYLE) -> str:
        style = Style.make(fmt)
        command_open, command_close = self._render_attributes(style)
        rendered_text = ""
        for line in str(string).splitlines(keepends=True):
            rendered_text += command_open + line + command_close
        return rendered_text

    def _render_attributes(self, style: Style) -> t.Tuple[str, ...]:
        cmd_open: t.List[t.Tuple[str, str]] = []
        cmd_close: t.List[t.Tuple[str, str]] = []

        for attr_name, tmux_name in self.STYLE_ATTR_TO_TMUX_MAP.items():
            attr_val = getattr(style, attr_name)
            if attr_val is None:
                continue
            if isinstance(attr_val, Color):
                if attr_val == NOOP_COLOR:
                    continue
                cmd_open.append((tmux_name + "=", attr_val.to_tmux(attr_name == "bg")))
                cmd_close.append((tmux_name + "=", "default"))
            elif isinstance(attr_val, bool):
                if not attr_val:
                    continue
                cmd_open.append((tmux_name, ""))
                cmd_close.append(("no" + tmux_name, ""))
            else:
                raise TypeError(
                    f"Unexpected attribute type: {type(attr_val)} for '{attr_name}'"
                )
        return self._encode_tmux_command(cmd_open), self._encode_tmux_command(cmd_close)

    def _encode_tmux_command(self, kv: t.List[t.Tuple[str, str]]) -> str:
        if len(kv) == 0:
            return ""
        return "#[" + (" ".join(f"{k}{v}" for k, v in kv)) + "]"


class NoOpRenderer(AbstractRenderer):
    """
    Special renderer type that does nothing with the input string and just
    returns it as is. That's true only when it _is_ a str beforehand;
    otherwise argument will be casted to str and then returned.

    >>> NoOpRenderer().render('text', Style(fg='green', bold=True))
    'text'
    """

    @property
    def is_format_allowed(self) -> bool:
        return False

    def render(self, string: t.Any, fmt: Color|Style = NOOP_STYLE) -> str:
        return str(string)


class HtmlRenderer(AbstractRenderer):
    """
    html

    >>> HtmlRenderer().render('text', Style(fg='red', bold=True))
    '<span style="color: #800000; font-weight: 700">text</span>'
    """

    DEFAULT_ATTRS = [
        "color",
        "background-color",
        "font-weight",
        "font-style",
        "text-decoration",
        "border",
        "filter",
    ]

    @property
    def is_format_allowed(self) -> bool:
        return True

    def render(self, string: t.Any, fmt: Color|Style = NOOP_STYLE) -> str:
        style = Style.make(fmt)
        opening_tag, closing_tag = self._render_attributes(style)
        return f'{opening_tag}{str(string)}{closing_tag}'  # @TODO  # attribues

    def _render_attributes(self, style: Style = NOOP_STYLE) -> t.Tuple[str, str]:
        if style == NOOP_STYLE:
            return '', ''

        span_styles: t.Dict[str, t.Set[str]] = dict()
        for attr in self._get_default_attrs():
            span_styles[attr] = set()

        if style.fg != NOOP_COLOR:
            span_styles["color"].add(style.fg.format_value("#"))
        if style.bg != NOOP_COLOR:
            span_styles["background-color"].add(style.bg.format_value("#"))

        if style.blink:  # modern browsers doesn't support it without shit piled up
            span_styles["border"].update(("1px", "dotted"))
        if style.bold:
            span_styles["font-weight"].add("700")
        if style.crosslined:
            span_styles["text-decoration"].add("line-through")
        if style.dim:
            span_styles["filter"].update(("saturate(0.5)", "brightness(0.75)"))
        if style.double_underlined:
            span_styles["text-decoration"].update(("underline", "double"))
        if style.inversed:
            span_styles["color"], span_styles["background-color"] = (
                span_styles["background-color"],
                span_styles["color"],
            )
        if style.italic:
            span_styles["font-style"].add("italic")
        if style.overlined:
            span_styles["text-decoration"].add("overline")
        if style.underlined:
            span_styles["text-decoration"].add("underline")

        span_class_str = (
            "" if style.class_name is None else f' class="{style.class_name}"'
        )
        span_style_str = "; ".join(
            f"{k}: {' '.join(v)}" for k, v in span_styles.items() if len(v) > 0
        )
        return f'<span{span_class_str} style="{span_style_str}">', "</span>"

    def _get_default_attrs(self) -> t.List[str]:
        return self.DEFAULT_ATTRS


class SgrRendererDebugger(SgrRenderer):
    """
    SgrRendererDebugger

    >>> SgrRendererDebugger(OutputMode.XTERM_16).render('text', Style(fg='red', bold=True))
    '|ǝ1;31|text|ǝ22;39|'
    """
    def __init__(self, output_mode: OutputMode = OutputMode.AUTO):
        super().__init__(output_mode)
        self._format_override: bool|None = None

    @property
    def is_format_allowed(self) -> bool:
        if self._format_override is not None:
            return self._format_override
        return super().is_format_allowed

    def render(self, string: t.Any, fmt: Color|Style = NOOP_STYLE) -> str:
        return ReplaceSGR(r"|ǝ\3|").apply(super().render(str(string), fmt))

    def set_format_always(self):
        self._format_override = True

    def set_format_auto(self):
        self._format_override = None

    def set_format_never(self):
        self._format_override = False


RendererManager.set_default()
