# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

import enum
import os
import sys
import typing as t
from abc import ABCMeta, abstractmethod
from functools import reduce

from .common import Renderable, logger
from .ansi import SequenceSGR, NOOP_SEQ, SeqIndex, get_closing_seq
from .util import ReplaceSGR
from .color import Color, Color16, Color256, ColorRGB, NOOP_COLOR
from .style import Style, NOOP_STYLE, Styles


class RendererManager:
    _default: AbstractRenderer = None

    @classmethod
    def set_default(
        cls, renderer: AbstractRenderer|t.Type[AbstractRenderer] = None
    ) -> AbstractRenderer:
        """
        Set up renderer preferences.

        :param renderer:
            Default renderer to use globally. Passing None will result in library
            default setting restored (`SgrRenderer`). Default renderer is used
            when no other is specified, e.g. in `render()` package method.

        :return: Renderer instance set as default.

        >>> renderer('text', Style(fg='red'), DebugRenderer)
        '|ǝ31|text|ǝ39|'
        >>> renderer('text', Style(fg='red'), NoOpRenderer)
        'text'
        """
        if isinstance(renderer, type):
            renderer = renderer()
        cls._default = renderer or SgrRenderer()
        return cls._default

    @classmethod
    def get_default(cls) -> AbstractRenderer:
        """
        Get global default renderer instance (`SgrRenderer`, or the one
        provided with `setup`).
        """
        return cls._default

    @classmethod
    def set_default_to_disable_formatting(cls):
        """
        Shortcut for forcing all control sequences to be omitted when using
        a default renderer (i.e., doesn't specifying it).
        """
        cls.set_default(SgrRenderer(OutputMode.NO_ANSI))

    @classmethod
    def set_default_to_force_formatting(cls):
        """
        Shortcut for forcing all control sequences to be present in the
        output when using a default renderer (i.e., doesn't specifying it).
        """
        cls.set_default(SgrRenderer(OutputMode.TRUE_COLOR))


class AbstractRenderer(metaclass=ABCMeta):
    """Renderer interface."""

    @abstractmethod
    def render(self, string: t.Any, style: Style = NOOP_STYLE) -> str:
        """
        Apply colors and attributes described in ``style`` argument to
        ``string`` and return the result. Output format depends on renderer's
        class (which defines the implementation).
        """
        raise NotImplementedError


class OutputMode(enum.IntEnum):
    """
    Determines what types of SGR sequences are allowed to use in the output.
    See `SgrRenderer` documentation for exact color mappings.
    """

    NO_ANSI = enum.auto()
    """Disable all formatting"""
    XTERM_16 = enum.auto()
    """16-colors mode"""
    XTERM_256 = enum.auto()
    """256-colors mode"""
    TRUE_COLOR = enum.auto()
    """RGB mode"""
    AUTO = enum.auto()
    """Let the renderer to decide"""


class SgrRenderer(AbstractRenderer):
    """
    .. todo ::
        make render() protected (?)

    Default renderer invoked by `Text._render()`. Transforms `Color` instances
    defined in ``style`` into ANSI control sequence bytes and merges them with
    input string. Type of output ``SequenceSGR`` depends on type of `Color`
    instances in ``style`` argument and current output mode of the renderer.

    1. `ColorRGB` can be rendered as True Color sequence, 256-color sequence
       or 16-color sequence depending on compatibility settings (see below).
    2. `Color256` can be rendered as 256-color sequence or 16-color
       sequence.
    3. `Color16` will be rendered as 16-color sequence.
    4. Nothing of the above will happen and all Colors will be discarded
       completely if output is not a terminal emulator or if the developer
       explicitly set up the renderer to do so (**force_styles** = False).

    Compatibility preferences (see `SgrRenderer.setup()`) determine
    exact type of output SGRs. Renderer approximates RGB colors to closest
    *indexed* colors if terminal doesn't support RGB output. In case terminal
    doesn't support even 256 colors, falls back to 16-color palette and picks
    closest samples again the same way. Color mode to color type mapping:

    1. `OutputMode.TRUE_COLOR` does not apply restrictions to color rendering.
    2. `OutputMode.XTERM_256` allows the renderer to use either `Color16`
       or `Color256` (but RGB will be approximated to 256-color pallette).
    3. `OutputMode.XTERM_16` enforces the renderer to approximate all color types
       to `Color16` and render them as basic mode selection SGR sequences
       (e.g., ``ESC[31m``, ``ESC[42m`` etc).
    4. `OutputMode.NO_ANSI` discards all color information completely.

    >>> render('text', Styles.WARNING_LABEL, SgrRenderer(OutputMode.XTERM_256))
    '\\x1b[1;33mtext\\x1b[22;39m'
    >>> render('text', Styles.WARNING_LABEL, SgrRenderer(OutputMode.NO_ANSI))
    'text'
    """

    _COLOR_UPPER_BOUNDS: t.Dict[OutputMode, t.Type[Color]] = {
        OutputMode.XTERM_16: Color16,
        OutputMode.XTERM_256: Color256,
        OutputMode.TRUE_COLOR: ColorRGB,
    }
    _color_upper_bound: t.Type[Color | None] = None

    _output_mode: OutputMode = OutputMode.AUTO

    def __init__(self, output_mode: OutputMode = OutputMode.AUTO):
        """
        Set up renderer preferences.

        :param output_mode:
            SGR output mode to use. Valid values are listed in `OutputMode` enum.

            With `OutputMode.AUTO` the renderer will first check if the output
            device is a terminal emulator, and use `OutputMode.NO_ANSI` when it
            is not. Otherwise, the renderer will read ``TERM`` environment
            variable and follow these rules:

                * `OutputMode.NO_ANSI` if ``TERM`` is set to `xterm``.
                * `OutputMode.XTERM_16` if ``TERM`` is set to `xterm-color``.
                * `OutputMode.XTERM_256` in all other cases.

            Special case is when ``TERM`` equals to ``xterm-256color`` **and**
            ``COLORTERM`` is either ``truecolor`` or  ``24bit``, then
            `OutputMode.TRUE_COLOR` will be used.

        :returns: self
        """
        self._output_mode = self._determine_output_mode(output_mode)
        self._color_upper_bound = self._COLOR_UPPER_BOUNDS.get(
            self._output_mode, type(None)
        )

        logger.debug(f"Output mode: {output_mode.name} -> {self._output_mode.name}")
        logger.debug(f"Color upper bound: {self._color_upper_bound}")

    def render(self, string: t.Any, style: Style = NOOP_STYLE):
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

    def is_sgr_usage_allowed(self) -> bool:
        return self._output_mode is not OutputMode.NO_ANSI

    def _determine_output_mode(self, arg_value: OutputMode) -> OutputMode:
        if arg_value is not OutputMode.AUTO:
            return arg_value
        if not sys.stdout.isatty():
            return OutputMode.NO_ANSI

        term = os.environ.get("TERM", None)
        if term == "xterm":
            return OutputMode.NO_ANSI
        if term == "xterm-color":
            return OutputMode.XTERM_16
        if os.environ.get("COLORTERM", None) in ("truecolor", "24bit"):
            return OutputMode.TRUE_COLOR
        return OutputMode.XTERM_256

    def _render_attributes(
        self, style: Style, squash: bool
    ) -> t.List[SequenceSGR] | SequenceSGR:
        if not self.is_sgr_usage_allowed():
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
        if not self.is_sgr_usage_allowed() or color == NOOP_COLOR:
            return NOOP_SEQ
        return color.to_sgr(bg, self._color_upper_bound)


class TmuxRenderer(AbstractRenderer):
    """
    tmux

    >>> render('text', Style(fg='blue', bold=True), TmuxRenderer(OutputMode.XTERM_16))
    '#[bold]#[fg=blue]text#[nobold nodim]#[fg=default]'
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

    def render(self, string: t.Any, style: Style = NOOP_STYLE):
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
            return ''
        return "#[" + (" ".join(f"{k}{v}" for k, v in kv)) + "]"


class NoOpRenderer(AbstractRenderer):
    """
    Special renderer type that does nothing with the input string and just
    returns it as is. That's true only when it _is_ a str beforehand;
    otherwise argument will be casted to str and then returned.

    >>> render('text', Style(fg='green', bold=True), NoOpRenderer)
    'text'
    """

    def render(self, string: t.Any, style: Style = NOOP_STYLE) -> str:
        if isinstance(string, Renderable):
            return string.render(self)
        return str(string)


class HtmlRenderer(AbstractRenderer):
    """
    html

    >>> render('text', Style(fg='red',bold=True), HtmlRenderer)
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

    def render(self, string: t.Any, style: Style = NOOP_STYLE) -> str:
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
        return (
            f'<span{span_class_str} style="{span_style_str}">' + str(string) + "</span>"
        )  # @TODO  # attribues

    def _get_default_attrs(self) -> t.List[str]:
        return self.DEFAULT_ATTRS


class DebugRenderer(SgrRenderer):
    """
    DebugRenderer

    #>>> renderer = DebugRenderer(OutputMode.XTERM_256)
    >>> render('text', style.Style(fg='red', bold=True), DebugRenderer)
    '|ǝ1;31|text|ǝ22;39|'
    """

    def render(self, string: t.Any, style: Style = NOOP_STYLE) -> str:
        return ReplaceSGR(r"|ǝ\3|").apply(super().render(str(string), style))

    def is_sgr_usage_allowed(self) -> bool:
        return True


RendererManager.set_default()
