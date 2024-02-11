# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
"""
Renderers transform :class:`.Style` instances into lower-level abstractions like
:term:`SGR sequences <SGR>`, tmux-compatible directives, HTML markup etc.,
depending on a renderer type. Default global renderer type is `SgrRenderer`.

:fas:`sitemap;sd-text-primary` `guide.renderer_class_diagram`

"""
from __future__ import annotations

from logging import getLogger
import os
import re
import sys
import typing as t
from abc import ABCMeta, abstractmethod
from functools import reduce
from hashlib import md5

from .ansi import ColorTarget, NOOP_SEQ, SeqIndex, SequenceSGR, get_closing_seq
from .color import Color16, Color256, ColorRGB, DEFAULT_COLOR, Color, NOOP_COLOR, RenderColor
from .common import ExtendedEnum,  get_qname, instantiate
from .config import ConfigManager
from .style import FT, NOOP_STYLE, Style, Styles, make_style

_T = t.TypeVar("_T", bound="IRenderer")


def _digest(fingerprint: str) -> int:
    return int.from_bytes(md5(fingerprint.encode()).digest(), "big")


class RendererManager:
    """
    Class for global rendering mode setup. For the details and recommendations
    see `guide.renderer_setup`.

    .. important ::
        All methods which are named ``render`` and have an argument named
        ``renderer`` (e.g., `text.render()`) use the global default one if said
        argument is omitted or set to *None*.
    """

    _default: IRenderer = None
    _global_override: IRenderer | t.Type[IRenderer] = None

    @classmethod
    def override(cls, renderer: IRenderer | t.Type[IRenderer] = None):
        # noinspection PyUnresolvedReferences
        """
        Override a global default renderer. Resolving priority is described in
        `guide.renderer_priority`.

        :param renderer:
            Can be provided as a **type**, in which case manager will
            instantiate it with default arguments, or as already instantiated
            and set up renderer, which will be registered as global. Calling
            this method without an argument resets the override, which makes
            default renderer class will be the one defined in configuration
            instead (see :option:`renderer_classname`).
        """
        cls._global_override = renderer

    @classmethod
    def get(cls) -> IRenderer:
        """
        Get current renderer instance. Resolving priority is described in
        `guide.renderer_priority`.
        """

        if cls._global_override is not None:
            if (inst := instantiate(IRenderer,  cls._global_override)) is not None:
                return inst

        classname = ConfigManager.get().renderer_classname
        return instantiate(IRenderer, classname, cls._get_default())

    @classmethod
    def _get_default(cls) -> IRenderer:
        if cls._default is None:
            cls._default = SgrRenderer()
        return cls._default


class IRenderer(metaclass=ABCMeta):
    """Renderer interface."""

    def __init__(self, *, allow_cache: bool = None, allow_format: bool = None) -> None:
        super().__init__()
        self._allow_cache: bool | None = allow_cache
        self._allow_format: bool | None = allow_format

    def __hash__(self) -> int:
        """
        Method returning a unique number reflecting current renderer's state. Used for
        rendered strings caching. Two renderers of the same class and with the same
        settings should have equal hashes, so that cached strings could be reused.
        When the internal state of the renderer changes, this number should change as
        well, in order to invalidate the caches.
        """

    @property
    def is_caching_allowed(self) -> bool:  # pragma: no cover
        """
        :return: *True* if caching of renderer's results makes any sense and *False*
                 otherwise.
        """
        if self._allow_cache is None:
            raise RuntimeError("Renderer is not initialized")
        return self._allow_cache

    @property
    def is_format_allowed(self) -> bool:  # pragma: no cover
        """
        :return: *True* if renderer is set up to produce formatted output and will do
                 it on invocation, and *False* otherwise.
        """
        if self._allow_format is None:
            raise RuntimeError("Renderer is not initialized")
        return self._allow_format

    @abstractmethod
    def render(self, string: str, fmt: FT = None) -> str:
        """
        Apply colors and attributes described in ``fmt`` argument to
        ``string`` and return the result. Output format depends on renderer's
        class, which defines the implementation.

        .. important ::

            Renderer's method `IRenderer.render()` can work only with primitive *str*
            instances. `IRenderable` instances like `Fragment` or `Text` should be
            rendered using module-level function `render()` or their own instance
            method `IRenderable.render()`.

        :param string: String to format.
        :param fmt:    Style or color to apply. If ``fmt`` is a ``IColor`` instance,
                       it is assumed to be a foreground color. See `FT`.
        :return: String with formatting applied, or without it, depending on
                 renderer settings.
        """

    def is_256_color_supported(self) -> bool:
        """
        Return *True* if it's OK to use ``xterm-256`` color palette
        and *False* otherwise. Non-SGR renderers returns *True* if
        formatting is allowed, and *false* when it's not.
        """
        return self._allow_format

    def is_true_color_supported(self) -> bool:
        """
        Return *True* if the output device can handle ``True Color``/RGB palette
        and *False* otherwise. Non-SGR renderers returns *True* if formatting is
        allowed, and *false* when it's not.
        """
        return self._allow_format

    def clone(self: _T, *args: t.Any, **kwargs: t.Any) -> _T:  # pragma: no cover
        """
        Make a copy of the renderer with the same setup.
        """
        return self.__class__()

    def __repr__(self) -> str:
        return f"<{get_qname(self)}[]>"


class OutputMode(str, ExtendedEnum):
    """
    Determines what types of SGR sequences are allowed to use in the output.
    """

    NO_ANSI = "no_ansi"
    """
    The renderer discards all color and format information completely.
    """
    XTERM_16 = "xterm_16"
    """
    16-colors mode. Enforces the renderer to approximate all color types
    to `Color16` and render them as basic mode selection SGR sequences
    (:ansi:`ESC`\\ ``[31m``, :ansi:`ESC`\\ ``[42m`` etc). See `Color.approximate()` for approximation
    algorithm details.
    """
    XTERM_256 = "xterm_256"
    """
    256-colors mode. Allows the renderer to use either `Color16` or `Color256` 
    (but RGB will be approximated to 256-color pallette).
    """
    TRUE_COLOR = "true_color"
    """
    RGB color mode. Does not apply restrictions to color rendering.
    """
    AUTO = "auto"
    """
    Lets the renderer select the most suitable mode by itself. See
    `guide.output_mode_select` for the details.
    """


class SgrRenderer(IRenderer):
    """
    Default renderer invoked by `Text.render()`. Transforms `Color` instances
    defined in ``fmt`` into ANSI control sequence bytes and merges them with
    input string. Type of resulting `SequenceSGR` depends on type of `Color`
    instances in ``fmt`` argument and current output mode of the renderer.

    1. `ColorRGB` can be rendered as True Color sequence, 256-color sequence
       or 16-color sequence depending on specified `OutputMode` and
       `Config.prefer_rgb`.
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
    '\x1b[1;33mtext\x1b[22;39m'
    >>> SgrRenderer(OutputMode.NO_ANSI).render('text', Styles.WARNING_LABEL)
    'text'

    Detailed `OutputMode.AUTO` algorithm is described in `guide.output_mode_select`.

    :cache allowed:    *True*
    :format allowed:   *False* if `output_mode` is `OutputMode.NO_ANSI`,
                       *True* otherwise.

    :param output_mode:
               can be set up explicitly, or kept at the default value
               `OutputMode.AUTO`; in the latter case the renderer will
               select the appropriate mode by itself (see `guide.output_mode_select`).
    :param io: specified in order to check if output device is a tty
               or not and can be omitted when output mode is set up
               explicitly.
    """

    _COLOR_UPPER_BOUNDS: t.Dict[OutputMode, t.Type[Color]] = {
        OutputMode.XTERM_16: Color16,
        OutputMode.XTERM_256: Color256,
        OutputMode.TRUE_COLOR: ColorRGB,
    }

    _STYLE_ATTR_TO_SGR: t.Dict[str, SequenceSGR] = {
        "blink": SeqIndex.BLINK_SLOW,
        "bold": SeqIndex.BOLD,
        "crosslined": SeqIndex.CROSSLINED,
        "dim": SeqIndex.DIM,
        "double_underlined": SeqIndex.DOUBLE_UNDERLINED,
        "curly_underlined": SeqIndex.CURLY_UNDERLINED,
        "inversed": SeqIndex.INVERSED,
        "italic": SeqIndex.ITALIC,
        "overlined": SeqIndex.OVERLINED,
        "underlined": SeqIndex.UNDERLINED,
        "framed": SeqIndex.FRAMED,
    }

    def __init__(self, output_mode: str | OutputMode = OutputMode.AUTO, io: t.IO = sys.stdout):
        self._output_mode: OutputMode = self._determine_output_mode(output_mode, io)
        self._color_upper_bound: t.Type[Color] | None = self._COLOR_UPPER_BOUNDS.get(
            self._output_mode, None
        )
        super().__init__(
            allow_cache=True,
            allow_format=(self._output_mode is not OutputMode.NO_ANSI),
        )
        getLogger(__package__).debug(f"Instantiated {self!r} => {getattr(io, 'name', repr(io))}")

    def __hash__(self) -> int:
        # although this renderer is immutable, its state can be set up differently
        # on initialization. ``_color_upper_bound`` is a derived variable from
        # ``_output_mode`` with one-to-one mapping, thus it can be omitted.
        return _digest(self.__class__.__qualname__ + "." + self._output_mode.value)

    def __repr__(self):
        attrs = [
            self._output_mode.name,
            get_qname(self._color_upper_bound),
        ]
        return f"<{get_qname(self)}[{', '.join(attrs)}]>"

    def render(self, string: str, fmt: FT = None) -> str:
        style = make_style(fmt)
        opening_seq = (
                self._render_attributes(style)
                + self._render_color(style.fg, ColorTarget.FG)
                + self._render_color(style.bg, ColorTarget.BG)
                + self._render_color(style.underline_color, ColorTarget.UNDERLINE)
        )
        closing_seq = get_closing_seq(opening_seq)
        rendered_text = ""

        # in case there are line breaks -- split text to lines and apply
        # SGRs for each line separately. it increases the chances that style
        # will be correctly displayed regardless of implementation details of
        # user's pager, multiplexer, terminal emulator etc.
        for line in string.splitlines(keepends=True):
            rendered_text += f"{opening_seq}{line}{closing_seq}"
        return rendered_text

    def is_256_color_supported(self) -> bool:
        return self._output_mode in [OutputMode.XTERM_256, OutputMode.TRUE_COLOR]

    def is_true_color_supported(self) -> bool:
        return self._output_mode in [OutputMode.TRUE_COLOR]

    def clone(self) -> SgrRenderer:
        return SgrRenderer(self._output_mode)

    def _determine_output_mode(self, arg_value: OutputMode, io: t.IO) -> OutputMode:
        logger = getLogger(__package__)
        ioname = "<" + getattr(io, "name", "?").strip("<>") + ">"

        if not isinstance(arg_value, OutputMode):
            arg_value = OutputMode.resolve_by_value(arg_value)

        if arg_value is not OutputMode.AUTO:
            logger.debug(f"Using explicit value from the constructor arg: {arg_value}")
            return arg_value

        config_forced_value = OutputMode.resolve_by_value(
            ConfigManager.get().force_output_mode
        )
        if config_forced_value is not OutputMode.AUTO:
            logger.debug(f"Using forced value from env/config: {config_forced_value}")
            return config_forced_value

        isatty = None
        if io and not io.closed:
            isatty = io.isatty()
        term = os.environ.get("TERM", None)
        colorterm = os.environ.get("COLORTERM", None)

        logger.debug(f"{ioname} Determining output mode automatically: {config_forced_value}")
        logger.debug(f"{ioname} {get_qname(io)} is a terminal: {isatty}")
        logger.debug(f"{ioname} Environment: TERM='{term}'")
        logger.debug(f"{ioname} Environment: COLORTERM='{colorterm}'")

        if not isatty:
            return OutputMode.NO_ANSI
        if term == "xterm":
            return OutputMode.NO_ANSI
        if term == "xterm-color":
            return OutputMode.XTERM_16
        if colorterm in ("truecolor", "24bit"):
            return OutputMode.TRUE_COLOR
        return OutputMode.resolve_by_value(ConfigManager.get().default_output_mode)

    def _render_attributes(self, style: Style) -> t.List[SequenceSGR] | SequenceSGR:
        if not self.is_format_allowed:
            return NOOP_SEQ

        result = []
        for attr_name, sgr in self._STYLE_ATTR_TO_SGR.items():
            if getattr(style, attr_name):
                result.append(sgr)
        if not result:
            return NOOP_SEQ

        return reduce(lambda p, c: p + c, result, NOOP_SEQ)

    def _render_color(self, color: RenderColor, target: ColorTarget) -> SequenceSGR:
        if not self.is_format_allowed:
            return NOOP_SEQ
        return color.to_sgr(target, self._color_upper_bound)


class TmuxRenderer(IRenderer):
    """
    Translates `Styles <Style>` attributes into
    `tmux-compatible <https://man7.org/linux/man-pages/man1/tmux.1.html#STYLES>`_
    markup. [#]_

    >>> TmuxRenderer().render('text',  Style(fg='blue', bold=True))
    '#[fg=blue bold]text#[fg=default nobold]'

    :cache allowed:    *True*
    :format allowed:   *True*, because tmux markup can be used without regard
                       to the type of output device and its capabilities -- all the
                       dirty work will be done by the multiplexer himself.

    .. [#] `tmux <https://github.com/tmux/tmux>`_ is a commonly used terminal
            multiplexer.
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

    def __init__(self) -> None:
        super().__init__(allow_cache=True, allow_format=True)

    def __hash__(self) -> int:  # stateless
        return _digest(self.__class__.__qualname__)

    def render(self, string: str, fmt: FT = None) -> str:
        style = make_style(fmt)
        command_open, command_close = self._render_attributes(style)
        rendered_text = ""
        for line in string.splitlines(keepends=True):
            rendered_text += command_open + line + command_close
        return rendered_text

    def _render_attributes(self, style: Style) -> t.Tuple[str, ...]:
        cmd_open: t.List[t.Tuple[str, str]] = []
        cmd_close: t.List[t.Tuple[str, str]] = []

        for attr_name, tmux_name in self.STYLE_ATTR_TO_TMUX_MAP.items():
            attr_val = getattr(style, attr_name)
            if attr_val is None:
                continue
            if isinstance(attr_val, RenderColor):
                if attr_val == NOOP_COLOR or attr_name not in ("fg", "bg"):
                    continue  # skipping underline_color
                target = ColorTarget.BG if attr_name == "bg" else ColorTarget.FG
                cmd_open.append((tmux_name + "=", attr_val.to_tmux(target)))
                cmd_close.append((tmux_name + "=", "default"))
            elif isinstance(attr_val, bool):  # @TODO unreachable ?
                if not attr_val:  # pragma: no cover
                    continue
                cmd_open.append((tmux_name, ""))
                cmd_close.append(("no" + tmux_name, ""))
            else:
                raise TypeError(  # pragma: no cover
                    f"Unexpected attribute type: {type(attr_val)} for '{attr_name}'"
                )
        return self._encode_tmux_command(cmd_open), self._encode_tmux_command(cmd_close)

    def _encode_tmux_command(self, kv: t.List[t.Tuple[str, str]]) -> str:
        if len(kv) == 0:
            return ""
        return "#[" + (" ".join(f"{k}{v}" for k, v in kv)) + "]"


class NoopRenderer(IRenderer):
    """
    Special renderer type that does nothing with the input string and just
    returns it as is (i.e. raw text without any `Styles<Style>` applied.
    Often used as a default argument value (along with similar "NoOps" like
    `NOOP_STYLE`, `NOOP_COLOR` etc.)

    >>> NoopRenderer().render('text', Style(fg='green', bold=True))
    'text'

    :cache allowed:    *False*
    :format allowed:   *False*, nothing to apply |rarr| nothing to allow.
    """

    def __init__(self):
        super().__init__(allow_cache=False, allow_format=False)

    def __bool__(self) -> bool:  # pragma: no cover
        return False

    def __hash__(self) -> int:  # pragma: no cover
        return _digest(self.__class__.__qualname__)  # stateless

    def render(self, string: str, fmt: FT = None) -> str:
        """
        Return the `string` argument untouched, don't mind the `fmt`.

        :param string: String to :strike:`format` ignore.
        :param fmt:    Style or color to :strike:`appl`  discard.
        """
        # if not isinstance(string, str):
        # return string.string   # ?? @why
        return string


class HtmlRenderer(IRenderer):
    """
    Translate `Styles <Style>` attributes into a rudimentary HTML markup.
    All the formatting is inlined into ``style`` attribute of the ``<span>``
    elements. Can be optimized by extracting the common styles as CSS classes
    and referencing them by DOM elements instead.

    >>> HtmlRenderer().render('text', Style(fg='red', bold=True))
    '<span style="color: #800000; font-weight: 700">text</span>'

    :cache allowed:    *True*
    :format allowed:   *True*, because the capabilities of the terminal have
                       nothing to do with HTML markup meant for web-browsers.
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

    def __init__(self) -> None:
        super().__init__(allow_cache=True, allow_format=True)

    def __hash__(self) -> int:  # stateless
        return _digest(self.__class__.__qualname__)

    def render(self, string: str, fmt: FT = None) -> str:
        style = make_style(fmt)
        opening_tag, closing_tag = self._render_attributes(style)
        return f"{opening_tag}{string}{closing_tag}"  # @TODO  # attribues

    def _render_attributes(self, style: Style = NOOP_STYLE) -> t.Tuple[str, str]:
        if style == NOOP_STYLE:
            return "", ""

        span_styles: t.Dict[str, t.Set[str]] = dict()
        for attr in self._get_default_attrs():
            span_styles[attr] = set()

        empty_colors = [NOOP_COLOR, DEFAULT_COLOR]
        if style.fg not in empty_colors:
            span_styles["color"].add(style.fg.format_value("#"))
        if style.bg not in empty_colors:
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

        span_class_str = "" if style.class_name is None else f' class="{style.class_name}"'
        span_style_str = "; ".join(
            f"{k}: {' '.join(sorted(v))}" for k, v in sorted(span_styles.items()) if len(v) > 0
        )
        return f'<span{span_class_str} style="{span_style_str}">', "</span>"

    def _get_default_attrs(self) -> t.List[str]:
        return self.DEFAULT_ATTRS


class SgrDebugger(SgrRenderer):
    """
    Subclass of regular `SgrRenderer` with two differences -- instead of rendering the
    proper ANSI escape sequences it renders them with :ansi:`ESC` character replaced by "ǝ",
    and encloses the whole sequence into '()' for visual separation.

    Can be used for debugging of assembled sequences, because such a transformation
    reliably converts a control sequence into a harmless piece of bytes completely
    ignored by the terminals.

    >>> SgrDebugger(OutputMode.XTERM_16).render('text', Style(fg='red', bold=True))
    '(ǝ[1;31m)text(ǝ[22;39m)'

    :cache allowed:    *True*
    :format allowed:   adjustable
    """

    REPLACE_REGEX = re.compile(r"\x1b(\[[0-9;]*m)")

    def __init__(self, output_mode: OutputMode = OutputMode.AUTO):
        super().__init__(output_mode)
        self._format_override: bool | None = None

    def __hash__(self) -> int:
        # build the hash from instance's state as well as ancestor's state -- that way
        # it will reflect the changes in either of configurations. actually, sometimes
        # the hashes will be different, but the results would have been the same;
        # e.g., `SgrDebugger` with ``_format_override`` set to *False* and
        # `SgrDebugger` without the override and with `NO_ANSI` output mode
        # has different hashes, but produce exactly the same outputs. however,
        # this can be disregarded, as it is not worth the efforts to implement an
        # advanced logic and correct state computation when it comes to a debug renderer.
        return _digest(
            ".".join(
                [
                    self.__class__.__qualname__,
                    str(self._format_override),
                    str(super().__hash__()),
                ]
            )
        )

    @property
    def is_format_allowed(self) -> bool:
        if self._format_override is not None:
            return self._format_override
        return super().is_format_allowed

    def render(self, string: str, fmt: FT = None) -> str:
        origin = super().render(string, fmt)
        return self.REPLACE_REGEX.sub(r"(ǝ\1)", origin)

    def clone(self) -> SgrDebugger:
        cloned = SgrDebugger(self._output_mode)
        cloned._format_override = self._format_override
        return cloned

    def set_format_always(self):
        """
        Force all control sequences to be present in the output.
        """
        self._format_override = True

    def set_format_auto(self):
        """
        Reset the force formatting flag and let the renderer decide by itself
        (see `SgrRenderer` docs for the details).
        """
        self._format_override = None

    def set_format_never(self):
        """
        Force disabling of all output formatting.
        """
        self._format_override = False


# @todo
# class Win32Renderer
