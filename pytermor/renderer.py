# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
"""
Renderers transform `Style` instances into lower-level abstractions like
:term:`SGR sequences <SGR>`, tmux-compatible directives, HTML markup etc.,
depending on renderer type. Default global renderer type is `SgrRenderer`.
"""
from __future__ import annotations

import logging
import os
import re
import sys
import typing as t
from abc import ABCMeta, abstractmethod
from functools import reduce
from hashlib import md5

from .ansi import ColorTarget, NOOP_SEQ, SeqIndex, SequenceSGR, get_closing_seq
from .color import Color16, Color256, ColorRGB, IColor, NOOP_COLOR
from .common import ExtendedEnum, get_qname
from .config import get_config
from .style import FT, NOOP_STYLE, Style, Styles, make_style

T = t.TypeVar("T", bound="IRenderer")


def _digest(fingerprint: str) -> int:
    return int.from_bytes(md5(fingerprint.encode()).digest(), "big")


class RendererManager:
    """
    Class for global rendering mode setup. For the details and recommendations
    see `guide.renderer_setup`.
    """

    _default: IRenderer = None

    @classmethod
    def set_default(cls, renderer: IRenderer | t.Type[IRenderer] = None):
        # noinspection PyUnresolvedReferences
        """
        Select a global renderer. See also: `guide.renderer_priority`.

        :param renderer:
            Default renderer to use globally. Calling this method without arguments
            will result in library default renderer `SgrRenderer` being set as default.

            All the methods with the ``renderer`` argument (e.g., `text.render()`)
            will use the global default one if said argument is omitted or set to *None*.

            You can specify either the renderer class, in which case manager will
            instantiate it with the default parameters, or provide already instantiated
            and set up renderer, which will be registered as global.
        """
        if isinstance(renderer, type):
            renderer = renderer()
        if renderer is not None:
            cls._default = renderer
            return

        renderer_classname: str = get_config().renderer_class
        if not (renderer_class := getattr(__import__(__package__), renderer_classname)):
            logging.warning(f"Renderer class does not exist: '{renderer_classname}'")
            renderer_class = SgrRenderer
        cls._default = renderer_class()

    @classmethod
    def get_default(cls) -> IRenderer:
        """
        Get global renderer instance (`SgrRenderer`, or the one provided earlier with
        `set_default()`).
        """
        return cls._default


class IRenderer(metaclass=ABCMeta):
    """Renderer interface."""

    def __hash__(self) -> int:
        """
        Method returning a unique number reflecting current renderer's state. Used for
        rendered strings caching. Two renderers of the same class and with the same
        settings should have equal hashes, so that cached strings could be reused.
        When the internal state of the renderer changes, this number should change as
        well, in order to invalidate the caches.
        """

    @property
    @abstractmethod
    def is_caching_allowed(self) -> bool:
        """
        Class-level property.

        :return: *True* if caching of renderer's results makes any sense and *False*
                 otherwise.
        """

    @property
    @abstractmethod
    def is_format_allowed(self) -> bool:
        """
        :return: *True* if renderer is set up to use the formatting and will do
                 it on invocation, and *False* otherwise.
        """

    @abstractmethod
    def render(self, string: str, fmt: FT = None) -> str:
        """
        Apply colors and attributes described in ``fmt`` argument to
        ``string`` and return the result. Output format depends on renderer's
        class, which defines the implementation.

        :param string: String to format.
        :param fmt:    Style or color to apply. If ``fmt`` is a ``IColor`` instance,
                       it is assumed to be a foreground color. See `FT`.
        :return: String with formatting applied, or without it, depending on
                 renderer settings.
        """

    def clone(self: T, *args: t.Any, **kwargs: t.Any) -> T:
        """
        Make a copy of the renderer with the same setup.
        """
        return self.__class__()

    def __repr__(self):
        return self.__class__.__qualname__ + "[]"


class OutputMode(ExtendedEnum):
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
    (``ESC [31m``, ``ESC [42m`` etc). See `Color.approximate()` for approximation
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
    Lets the renderer select the most suitable mode by itself.
    See `SgrRenderer` constructor documentation for the details. 
    """

    @classmethod
    def resolve_by_value(cls, val: str) -> OutputMode:
        vk = {v: k for k, v in cls.dict().items()}
        if val in vk.keys():
            return vk[val]
        vals_str = ", ".join(vk.keys())
        raise LookupError(f"Invalid output mode: {val}, should be one of: {vals_str}")


class SgrRenderer(IRenderer):
    """
    Default renderer invoked by `Text.render()`. Transforms ``IColor`` instances
    defined in ``style`` into ANSI control sequence bytes and merges them with
    input string. Type of resulting `SequenceSGR` depends on type of ``IColor``
    instances in ``style`` argument and current output mode of the renderer.

    1. `ColorRGB` can be rendered as True Color sequence, 256-color sequence
       or 16-color sequence depending on specified `OutputMode` and
       :term:`Config.prefer_rgb`.
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

    Automatic output mode selection


    With `OutputMode.AUTO` the renderer will return `OutputMode.NO_ANSI`
    for any output device other than terminal emulator, or try to find
    a matching rule from this list:

    .. |ANY| replace:: :aux:`<any>`

    .. |CV_FORCE| replace:: :term:`Config.force_output_mode`
    .. |CV_DEFAULT| replace:: :term:`Config.default_output_mode`

    .. table:: Automatic output mode selection

       +--------+---------------------------+---------------+--------------------+
       | Is a   | ``TERM``                  | ``COLORTERM`` | Result             |
       | tty?   | env. var                  | env. var [#]_ | output mode        |
       +========+===========================+===============+====================+
       |                      |ANY|                         | |CV_FORCE| [#]_    |
       +--------+---------------------------+---------------+--------------------+
       | No     |                   |ANY|                   | `NO_ANSI`          |
       +--------+---------------------------+---------------+--------------------+
       |        | ``xterm-256color``        | ``24bit``,    | `TRUE_COLOR`       |
       | Yes    |                           | ``truecolor`` |                    |
       |        +---------------------------+---------------+--------------------+
       |        | ``*-256color`` [#]_       |     |ANY|     | `XTERM_256`        |
       |        +---------------------------+---------------+--------------------+
       |        | ``xterm-color``           |     |ANY|     | `XTERM_16`         |
       |        +---------------------------+---------------+--------------------+
       |        | ``xterm``                 |     |ANY|     | `NO_ANSI`          |
       |        +---------------------------+---------------+--------------------+
       |        | :aux:`<any other>`        |     |ANY|     | |CV_DEFAULT| [#]_  |
       +--------+---------------------------+---------------+--------------------+

    ..

       .. [#] should both requirements be present, they must be both true
              as well (i.e. logical AND is applied).

       .. [#] empty by default and thus ignored

       .. [#] ``*`` represents any string; that's how e.g. *bash 5*
              determines the color support.

       .. [#] `XTERM_256` by default, but can be customized.

    :param output_mode:
               can be set up explicitly, or kept at the default value
               `OutputMode.AUTO`; in the latter case the renderer will
               select the appropriate mode by itself (see `renderers`_).
    :param io: specified in order to check if output device is a tty
               or not and can be ignored when output mode is set up
               explicitly.
    """

    _COLOR_UPPER_BOUNDS: t.Dict[OutputMode, t.Type[IColor]] = {
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

    def __init__(self, output_mode: OutputMode = OutputMode.AUTO, io: t.IO = sys.stdout):
        self._output_mode: OutputMode = self._determine_output_mode(output_mode, io)
        self._color_upper_bound: t.Type[IColor] | None = self._COLOR_UPPER_BOUNDS.get(
            self._output_mode, None
        )

        logging.debug(
            f"Instantiated {self.__class__.__qualname__}"
            f"[{self._output_mode.name}, "
            f"upper bound {get_qname(self._color_upper_bound)}]"
        )

    def __hash__(self) -> int:
        # although this renderer is immutable, its state can be set up differently
        # on initialization. ``_color_upper_bound`` is a derived variable from
        # ``_output_mode`` with one-to-one mapping, thus it can be omitted.
        return _digest(self.__class__.__qualname__ + "." + self._output_mode.value)

    @property
    def is_caching_allowed(self) -> bool:
        return True

    @property
    def is_format_allowed(self) -> bool:
        return self._output_mode is not OutputMode.NO_ANSI

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

    def clone(self) -> SgrRenderer:
        return SgrRenderer(self._output_mode)

    def _determine_output_mode(self, arg_value: OutputMode, io: t.IO) -> OutputMode:
        if arg_value is not OutputMode.AUTO:
            logging.debug(f"Using explicit value from the constructor arg: {arg_value}")
            return arg_value

        config_forced_value = OutputMode.resolve_by_value(get_config().force_output_mode)
        if config_forced_value is not OutputMode.AUTO:
            logging.debug(f"Using forced value from env/config: {config_forced_value}")
            return config_forced_value

        isatty = io.isatty() if not io.closed else None
        term = os.environ.get("TERM", None)
        colorterm = os.environ.get("COLORTERM", None)

        logging.debug(f"Determining output mode automatically: {config_forced_value}")
        logging.debug(f"{get_qname(io)} is a terminal: {isatty}")
        logging.debug(f"Environment: TERM='{term}'")
        logging.debug(f"Environment: COLORTERM='{colorterm}'")

        if not isatty:
            return OutputMode.NO_ANSI
        if term == "xterm":
            return OutputMode.NO_ANSI
        if term == "xterm-color":
            return OutputMode.XTERM_16
        if colorterm in ("truecolor", "24bit"):
            return OutputMode.TRUE_COLOR
        return OutputMode.resolve_by_value(get_config().default_output_mode)

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

    def _render_color(self, color: IColor, target: ColorTarget) -> SequenceSGR:
        if not self.is_format_allowed or color == NOOP_COLOR:
            return NOOP_SEQ
        return color.to_sgr(target, self._color_upper_bound)


class TmuxRenderer(IRenderer):
    """
    Translates `Styles <Style>` attributes into
    `tmux-compatible <https://man7.org/linux/man-pages/man1/tmux.1.html#STYLES>`_
    markup. `tmux <https://github.com/tmux/tmux>`_ is a commonly used terminal
    multiplexer.

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

    def __hash__(self) -> int:  # stateless
        return _digest(self.__class__.__qualname__)

    @property
    def is_caching_allowed(self) -> bool:
        return True

    @property
    def is_format_allowed(self) -> bool:
        """
        :returns: Always *True*, because tmux markup can be used without regard
                  to the type of output device and its capabilities -- all the
                  dirty work will be done by the multiplexer itself.
        """
        return True

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
            if isinstance(attr_val, IColor):
                if attr_val == NOOP_COLOR or attr_name not in ("fg", "bg"):
                    continue  # skipping underline_color
                target = ColorTarget.BG if attr_name == "bg" else ColorTarget.FG
                cmd_open.append((tmux_name + "=", attr_val.to_tmux(target)))
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


class NoOpRenderer(IRenderer):
    """
    Special renderer type that does nothing with the input string and just
    returns it as is (i.e. raw text without any `Styles<Style>` applied.
    Often used as a default argument value (along with similar "NoOps" like
    `NOOP_STYLE`, `NOOP_COLOR` etc.)

    >>> NoOpRenderer().render('text', Style(fg='green', bold=True))
    'text'

    """

    def __bool__(self) -> bool:
        return False

    def __hash__(self) -> int:  # stateless
        return _digest(self.__class__.__qualname__)

    @property
    def is_caching_allowed(self) -> bool:
        return False

    @property
    def is_format_allowed(self) -> bool:
        """
        :returns: Nothing to apply |rarr| nothing to allow, thus the returned value
                  is always *False*.
        """
        return False

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

    def __hash__(self) -> int:  # stateless
        return _digest(self.__class__.__qualname__)

    @property
    def is_caching_allowed(self) -> bool:
        return True

    @property
    def is_format_allowed(self) -> bool:
        """
        :returns: Always *True*, because the capabilities of the terminal have
                  nothing to do with HTML markup meant for web-browsers.
        """
        return True

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


class SgrDebugger(SgrRenderer):
    """
    Subclass of regular `SgrRenderer` with two differences -- instead of rendering the
    proper ANSI escape sequences it renders them with ``ESC`` character replaced by "ǝ",
    and encloses the whole sequence into '()' for visual separation.

    Can be used for debugging of assembled sequences, because such a transformation
    reliably converts a control sequence into a harmless piece of bytes completely
    ignored by the terminals.

    >>> SgrDebugger(OutputMode.XTERM_16).render('text', Style(fg='red', bold=True))
    '(ǝ[1;31m)text(ǝ[22;39m)'

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
        # advanced logic and correct state computation when it comes to debug renderer.
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
    def is_caching_allowed(self) -> bool:
        return True

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
        Reset the force formatting flag and let the renderer decide by itself (see
        `SgrRenderer` docs for the details).
        """
        self._format_override = None

    def set_format_never(self):
        """
        Force disabling of all output formatting.
        """
        self._format_override = False


class TemplateRenderer(IRenderer):
    @property
    def is_caching_allowed(self) -> bool:
        return True

    @property
    def is_format_allowed(self) -> bool:
        """
        :returns: Always *True*, because template renderer is not expected to
                  put the results directly to a tty.
        """
        return True

    def render(self, string: str, fmt: FT = None) -> str:
        pass

# @todo
# class Win32Renderer


def force_ansi_rendering():
    """
    Shortcut for forcing all control sequences to be present in the
    output of a global renderer.

    Note that it applies only to the renderer that is set up as default at
    the moment of calling this method, i.e., all previously created instances,
    as well as the ones that will be created afterwards, are unaffected.
    """
    RendererManager.set_default(SgrRenderer(OutputMode.TRUE_COLOR))


def force_no_ansi_rendering():
    """
    Shortcut for disabling all output formatting of a global renderer.
    """
    RendererManager.set_default(SgrRenderer(OutputMode.NO_ANSI))


def init_renderer():
    RendererManager.set_default()
