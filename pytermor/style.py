# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
"""
Reusable data classes that control the appearance of the output -- colors
(text/background/underline) and attributes (*bold*, *underlined*, *italic*, etc.).
Instances can inherit attributes from each other, which allows to avoid meaningless
definition repetitions; multiple inheritance is also supported.
"""
from __future__ import annotations

import enum
import typing as t
from dataclasses import dataclass, field
from typing import Any, Union

from .color import (
    Color,
    NOOP_COLOR,
    BG_LUMINANCE_THRESHOLD,
    CONTRAST_RATIO_THRESHOLD,
    resolve_color,
    IColorValue,
    ColorRGB,
    RenderColor,
    RealColor,
    CDT,
    XYZ,
)
from .cval import cv
from .exception import ArgTypeError, LogicError


CXT = Union[CDT, IColorValue, RenderColor, None]
"""
.. todo ::
    TODO
"""


class MergeMode(str, enum.Enum):
    """Enumeration of merge modes used by `TemplateEngine`."""

    FALLBACK = "?"
    """ See `Style.merge_fallback()` """

    OVERWRITE = "!"
    """ See `Style.merge_overwrite()` """

    REPLACE = "@"
    """ See `Style.merge_replace()` """


# noinspection NonAsciiCharacters
@dataclass()
class Style:
    """
    Create new text render descriptor. Both ``fg`` and ``bg`` can be specified
    as existing `Color` instance, as well as plain *str* or *int* (for the
    details see `resolve_color()`). This applies to ``underline_color`` as well.

    :param fallback:    Copy unfilled attributes from specified fallback style.
                        See `merge_fallback()`.
    :param fg:          Foreground (=text) color.
    :param bg:          Background color.
    :param frozen:      Set to *True* to make an immutable instance.
    :param bold:        Bold or increased intensity.
    :param dim:         Faint, decreased intensity.
    :param italic:      Italic.
    :param underlined:  Underline.
    :param overlined:   Overline.
    :param crosslined:  Strikethrough.
    :param double_underlined:
                        Double underline.
    :param curly_underlined:
                        Curly underline.
    :param underline_color:
                        Underline color, if applicable.
    :param inversed:    Swap foreground and background colors.
    :param blink:       Blinking effect.
    :param framed:      Enclosed in a rectangle border.
    :param class_name:  Custom class name for the element.
    """

    _fg: RenderColor | RealColor = field(default=None, init=False)
    _bg: RenderColor | RealColor = field(default=None, init=False)
    _underline_color: RenderColor | RealColor = field(default=None, init=False)

    @property
    def fg(self) -> RenderColor | RealColor:
        """
        Foreground (i.e., text) color. Can be set as `CDT` or ``Color``,
        stored always as ``Color``.
        """
        return self._fg

    @property
    def bg(self) -> RenderColor | RealColor:
        """
        Background color. Can be set as `CDT` or ``Color``, stored always
        as ``Color``.
        """
        return self._bg

    @property
    def underline_color(self) -> RenderColor | RealColor:
        """
        Underline color. Can be set as `CDT` or ``Color``, stored always
        as ``Color``.
        """
        return self._underline_color

    @fg.setter
    def fg(self, val: CXT):
        self._fg: RenderColor = self._resolve_color(val)

    @bg.setter
    def bg(self, val: CXT):
        self._bg: RenderColor = self._resolve_color(val)

    @underline_color.setter
    def underline_color(self, val: CXT):
        self._underline_color: RenderColor = self._resolve_color(val)

    bold: bool
    """ Bold or increased intensity (depending on terminal settings)."""
    dim: bool
    """ 
    Faint, decreased intensity. 

    .. admonition:: Terminal-based rendering

        Terminals apply this effect to foreground (=text) color, but when 
        it's used together with `inversed`, they usually make the background 
        darker instead.

        Also note that usually it affects indexed colors only and has no effect
        on RGB-based ones (True Color mode).
    """
    italic: bool
    """ Italic (some terminals may display it as inversed instead). """
    underlined: bool
    """ Underline. """
    overlined: bool
    """ Overline. """
    crosslined: bool
    """ Strikethrough."""
    double_underlined: bool
    """ Double underline. """
    curly_underlined: bool
    """ Curly underline. """
    inversed: bool
    """ 
    Swap foreground and background colors. When inversed effect is active, 
    changing the background color will actually change the text color, and
    vice versa. 
    """
    blink: bool
    """ 
    Blinking effect. Supported by a limited set of `renderers <IRenderer>`.
    """
    framed: bool
    """ 
    Add a rectangular border around the text; the border color is equal to 
    the text color. Supported by a limited set of `renderers <IRenderer>` and 
    (even more) limited amount of terminal emulators.
    """

    class_name: str
    """ 
    Arbitrary string used by some `renderers <IRenderer>`, e.g. by 
    ``HtmlRenderer``, which will include the value of this property to
    an output element class list. This property is not inheritable.
    """

    renderable_attributes = frozenset(
        [
            "fg",
            "bg",
            "underline_color",
            "bold",
            "dim",
            "italic",
            "underlined",
            "overlined",
            "crosslined",
            "double_underlined",
            "curly_underlined",
            "underline_color",
            "inversed",
            "blink",
            "framed",
        ]
    )

    @property
    def _attributes(self) -> t.FrozenSet:
        return frozenset({*self.__dict__.keys(), "_fg", "_bg"} - {"_MERGE_FN_MAP"})

    def __init__(
        self,
        fallback: Style = None,
        fg: CXT = None,
        bg: CXT = None,
        frozen: bool = False,
        *,
        bold: bool = None,
        dim: bool = None,
        italic: bool = None,
        underlined: bool = None,
        overlined: bool = None,
        crosslined: bool = None,
        double_underlined: bool = None,
        curly_underlined: bool = None,
        underline_color: CXT = None,
        inversed: bool = None,
        blink: bool = None,
        framed: bool = None,
        class_name: str = None,
    ):
        self._MERGE_FN_MAP: t.Dict[MergeMode, t.Callable[[Style], Style]] = {
            MergeMode.FALLBACK: self.merge_fallback,
            MergeMode.OVERWRITE: self.merge_overwrite,
            MergeMode.REPLACE: self.merge_replace,
        }

        if fg is not None:  # invoke setters
            self.fg = fg
        if bg is not None:
            self.bg = bg
        if underline_color is not None:
            self.underline_color = underline_color

        self._frozen = False

        self.bold = bold
        self.dim = dim
        self.italic = italic
        self.underlined = underlined
        self.overlined = overlined
        self.crosslined = crosslined
        self.double_underlined = double_underlined
        self.curly_underlined = curly_underlined
        self.inversed = inversed
        self.blink = blink
        self.framed = framed
        self.class_name = class_name

        if fallback is not None:
            if not isinstance(fallback, Style):
                suggestion = None
                if isinstance(fallback, (int, str, RenderColor)):  # pragma: no cover
                    suggestion = "To set a fg without fallback use Style(fg=<color>)"
                raise ArgTypeError(fallback, "fallback", Style, suggestion=suggestion)
            self.merge_fallback(fallback)

        if self._fg is None:
            self._fg = NOOP_COLOR
        if self._bg is None:
            self._bg = NOOP_COLOR
        if self._underline_color is None:
            self._underline_color = NOOP_COLOR

        self._frozen = frozen

    def clone(self, frozen=False) -> Style:
        """
        Make a copy of the instance. Note that a copy is mutable by default
        even if an original was frozen.

        :param frozen: Set to *True* to make an immutable instance.
        """
        return Style(self, frozen=frozen)

    def autopick_fg(self, *, preserve_origin=False, transparent_as_black=False) -> Style:
        """
        Set ``fg_color``  depending on ``bg_color``: to either
        :colorbox:`gray-0` if background is bright, or to :colorbox:`gray-100`
        if it is dark. For the details see `guide.styles.autopick_fg`. If
        background is None, do nothing, unless ``transparent_as_black`` is set
        to *True*.

        .. list-table:: Results for different parameter combinations; note that blue text
                        on black bg has lower contrast ratio than required, so in order
                        to keep text readable foreground is set to white even when
                        `preserve_origin=True`.
           :header-rows: 1

           * - Parameters
             - ``bg=``\ :colorbox:`#FFF`
             - ``bg=``\ :colorbox:`#000`
           * - ``preserve_origin=``\ *False*, ``fg`` :comment:`is irrelevant`
             - black on white
             - :whiteonblack:`white on black`
           * - ``preserve_origin=``\ *True*, ``fg=``\ :colorbox:`#F00`
             - :red:`red on white`
             - :redonblack:`red on black`
           * - ``preserve_origin=``\ *True*, ``fg=``\ :colorbox:`#00F`
             - :blue:`blue on white`
             - :whiteonblack:`white on black` |warn|

        Modifies the instance in-place and returns it as well (for chained
        calls).

        :param preserve_origin:
                    Set to *True* to update the foreground color only when
                    necessary (i.e., if the contrast is good enough, no action
                    will be performed).
        :param transparent_as_black:
                    Set to *True* to treat transparent background (i.e.
                    `NOOP_COLOR`) like a black one.
        """
        self._ensure_not_frozen()

        ref_bg: XYZ
        if isinstance(self._bg, RealColor):
            ref_bg = self._bg.xyz
        else:
            if transparent_as_black:
                ref_bg = cv.GRAY_0.xyz
            else:
                return self

        if preserve_origin and XYZ.contrast(ref_bg, self._fg) >= CONTRAST_RATIO_THRESHOLD:
            return self

        if ref_bg.y > BG_LUMINANCE_THRESHOLD:
            self._fg = cv.GRAY_0
        else:
            self._fg = cv.GRAY_100
        return self

    def flip(self) -> Style:
        """
        Swap foreground color and background color. Modifies the instance in-place
        and returns it as well (for chained calls).
        """
        self._ensure_not_frozen()
        self._fg, self._bg = self._bg, self._fg
        return self

    def merge(self, mode: MergeMode, other: Style) -> Style:
        """
        Method that allows specifying merging mode as an argument. Initially
        designed for template substitutions done by `TemplateEngine`. Invokes
        either of these (depending on ``mode`` value):

            - `merge_fallback()`
            - `merge_overwrite()`
            - `merge_replace()`

        :param mode:    Merge mode to use.
        :param other:   Style to merge the attributes with.
        """
        return self._MERGE_FN_MAP.get(mode)(other)

    def merge_fallback(self, fallback: Style) -> Style:
        """
        Merge current style with specified ``fallback`` `style <Style>`, following
        the rules:

            1. ``self`` attribute value is in priority, i.e. when both ``self`` and
               ``fallback`` attributes are defined, keep ``self`` value.
            2. If ``self`` attribute is *None*, take the value from ``fallback``'s
               corresponding attribute, and vice versa.
            3. If both attribute values are *None*, keep the *None*.

        All attributes corresponding to constructor arguments except ``fallback``
        are subject to merging. `NOOP_COLOR` is treated like *None* (default for `fg`
        and `bg`). See `guide.styles.merging` for more details.

        Modifies the instance in-place and returns it as well (for chained calls).

        :param fallback: Style to merge the attributes with.
        """
        self._ensure_not_frozen()
        for attr in self.renderable_attributes:
            self_val = getattr(self, attr)
            if self_val is None or self_val == NOOP_COLOR:
                # @TODO refactor? maybe usage of NOOP instances is not as good as
                #       it seemed to be in the beginning
                # @FIXME replace Nones to constant _UNSETs or smth
                fallback_val = getattr(fallback, attr)
                if fallback_val is not None and fallback_val != NOOP_COLOR:
                    setattr(self, attr, fallback_val)
        return self

    def merge_overwrite(self, overwrite: Style) -> Style:
        """
        Merge current style with specified ``overwrite`` `style <Style>`, following
        the rules:

            1. ``overwrite`` attribute value is in priority, i.e. when both ``self``
               and ``overwrite`` attributes are defined, replace ``self`` value with
               ``overwrite`` one (in contrast to `merge_fallback()`, which works the
               opposite way).
            2. If ``self`` attribute is *None*, take the value from ``overwrite``'s
               corresponding attribute, and vice versa.
            3. If both attribute values are *None*, keep the *None*.

        All attributes corresponding to constructor arguments except ``fallback``
        are subject to merging. `NOOP_COLOR` is treated like *None* (default for `fg`
        and `bg`). See `guide.styles.merging` for more details.

        Modifies the instance in-place and returns it as well (for chained calls).

        :param overwrite:  Style to merge the attributes with.
        """
        self._ensure_not_frozen()
        for attr in self.renderable_attributes:
            overwrite_val = getattr(overwrite, attr)
            if overwrite_val is not None and overwrite_val != NOOP_COLOR:
                setattr(self, attr, overwrite_val)
        return self

    def merge_replace(self, replacement: Style) -> Style:
        """
        Not an actual "merge": discard all the attributes of the current
        instance and replace them with the values from  `replacement`. Generally
        speaking, it makes sense only in `TemplateEngine` context, as style
        management using the template tags is quite limited, while there are
        far more elegant ways to do the same from the regular python code.

        Modifies the instance in-place and returns it as well (for chained calls).

        :param replacement:  Style to merge the attributes with.
        """
        self._ensure_not_frozen()
        for attr in self.renderable_attributes:
            replacement_val = getattr(replacement, attr)
            setattr(self, attr, replacement_val)
        return self

    def _ensure_not_frozen(self) -> None:
        if hasattr(self, "_frozen") and self._frozen:
            raise LogicError(f"{self.__class__.__qualname__} is immutable")

    def _resolve_color(self, arg: CXT) -> RenderColor | RealColor | None:
        if arg is None:
            return NOOP_COLOR
        if isinstance(arg, RenderColor):
            return arg
        if isinstance(arg, IColorValue):
            return ColorRGB(arg.int)
        if isinstance(arg, (str, int)) and not isinstance(arg, bool):
            # undesirable isinstance(True, int) --> #000001
            return resolve_color(arg)
        raise ArgTypeError(arg, "arg", CXT, IColorValue, None)

    def __setattr__(self, name: str, value: Any) -> None:
        self._ensure_not_frozen()
        super().__setattr__(name, value)

    def __eq__(self, other: Style) -> bool:
        if not isinstance(other, Style):  # pragma: no cover
            return False
        return all(getattr(self, attr) == getattr(other, attr) for attr in self._attributes)

    def __repr__(self) -> str:
        frozen = "@" if self._frozen else ""
        return f"<{frozen}{self.__class__.__name__}[{self.repr_attrs(False)}]>"

    def repr_attrs(self, verbose: bool) -> str:
        if self._fg is None or self._bg is None:  # reachable only in debugger
            colors = ["uninitialized"]  # pragma: no cover
        else:
            colors = []
            for attr_name in ("fg", "bg"):
                val: Color = getattr(self, attr_name)
                prefix = "" if attr_name == "fg" else "|"
                valstr = prefix + val.repr_attrs(verbose)
                if not valstr.endswith("NOP"):
                    colors.append(valstr)

        props = []
        for attr_name in self.renderable_attributes:
            attr = getattr(self, attr_name)
            if isinstance(attr, RenderColor) and attr and attr_name == "underline_color":
                if len(colors):
                    colors.append(" ")
                colors.append("U:" + attr.repr_attrs(verbose))
            elif isinstance(attr, bool):
                prefix = "+" if attr else "-"
                prop = attr_name.upper()
                if not verbose:
                    prop = prop[:4]
                props.append(prefix + prop)
        return " ".join(["".join(colors), *sorted(props)]).strip()


class FrozenStyle(Style):
    def __init__(self, *args, **kwargs):
        kwargs.update(dict(frozen=True))
        super().__init__(*args, **kwargs)


class NoOpStyle(Style):
    def __init__(self):
        super().__init__(frozen=True)

    def __bool__(self) -> bool:
        return False


NOOP_STYLE = NoOpStyle()
# noinspection NonAsciiCharacters
""" 
Special style passing the text through without any modifications. 

.. important ::
    Casting to *bool* results in **False** for all ``NOOP`` instances in the 
    library (`NOOP_SEQ`, `NOOP_COLOR` and `NOOP_STYLE`). This is intended. 

This class is immutable, i.e. `LogicError` will be raised upon an attempt to
modify any of its attributes, which could potentially lead to schrödinbugs::

    st1.merge_fallback(Style(bold=True), [Style(italic=False)])

If ``st1`` is a regular style instance, it's safe to call self-modifying methods,
but if it happens to be a `NOOP_STYLE`, the statement could have been alter the 
internal state of the style, which is referenced all over the library, which could 
lead to the changes appearing in an unexpected places.  

To be safe from this outcome one could merge styles via frontend method `merge_styles`, 
which always makes a copy of ``origin`` argument and thus cannot lead to such results.
"""


class Styles:
    """
    Some ready-to-use styles which also can be used as examples. All instances
    are immutable.
    """

    BOLD = Style(bold=True, frozen=True)
    """ BOLD """
    DIM = Style(dim=True, frozen=True)
    """ DIM """
    ITALIC = Style(italic=True, frozen=True)
    """ ITALIC """
    UNDERLINED = Style(underlined=True, frozen=True)
    """ UNDERLINED """

    WARNING = Style(fg=cv.YELLOW, frozen=True)
    """ WARNING """
    WARNING_LABEL = Style(WARNING, frozen=True, bold=True)
    """ WARNING_LABEL """
    WARNING_ACCENT = Style(fg=cv.HI_YELLOW, frozen=True)
    """ WARNING_ACCENT """

    ERROR = Style(fg=cv.RED, frozen=True)
    """ ERROR """
    ERROR_LABEL = Style(ERROR, frozen=True, bold=True)
    """ ERROR_LABEL """
    ERROR_ACCENT = Style(fg=cv.HI_RED, frozen=True)
    """ ERROR_ACCENT """

    CRITICAL = Style(bg=cv.RED_3, fg=cv.HI_WHITE, frozen=True)
    """ CRITICAL """
    CRITICAL_LABEL = Style(CRITICAL, frozen=True, bold=True)
    """ CRITICAL_LABEL """
    CRITICAL_ACCENT = Style(CRITICAL_LABEL, frozen=True, blink=True)
    """ CRITICAL_ACCENT """

    INCONSISTENCY = Style(bg=cv.RED_3, fg=cv.HI_YELLOW, frozen=True)
    """ INCONSISTENCY """


FT = Union[int, str, IColorValue, Style, None]
"""
:abbr:`FT (Format type)` is a style descriptor. Used as a shortcut precursor for actual 
styles. Primary handler is `make_style()`.
"""


def is_ft(arg: any) -> bool:
    """User-side type checking shortcut."""
    return isinstance(arg, FT)


def make_style(fmt: FT = None) -> Style:
    """
    General :class:`.Style` constructor. Supported argument types:

        - :class:`.Style` or *str*
            Existing style instance, which is returned as is, OR a name of the constant
            defined in `Styles`; if there are no constant with that name found in the class,
            the function assumes that the string is either a hex color value or a color name.

        - `CDT` (*str* or *int*)
            This argument type implies the creation of basic :class:`.Style`
            with the only attribute set being `fg` (i.e., text color). The color
            can be specified as hexadecimal RGB value or a color name in a free form.
            For the details on color resolving see `resolve_color()`.

        - `IColorValue` (`RGB` or `HSV` etc.)
            Color value is also accepted as `fmt` and is used as `fg` color of
            newly created style.

        - *None*
            Return `NOOP_STYLE`.

    :param FT fmt: See `FT`.
    """
    if fmt is None:
        return NOOP_STYLE
    if isinstance(fmt, Style):
        return fmt
    if isinstance(fmt, str):
        if hasattr(Styles, stn := fmt.upper()):
            return getattr(Styles, stn)
    if isinstance(fmt, (str, int, IColorValue)):
        return Style(fg=fmt)
    raise ArgTypeError(fmt, "fmt", FT, None)


# noinspection NonAsciiCharacters
def merge_styles(
    origin: Style = NOOP_STYLE,
    *,
    fallbacks: t.Iterable[Style] = (),
    overwrites: t.Iterable[Style] = (),
) -> Style:
    """
    Bulk style merging method. For the detailed explanation see `guide.styles.merging`.

    :param origin:     Initial style, or the source of attributes.
    :param fallbacks:  List of styles to be used as a backup attribute storage, or,
                       in other words, to be "merged up" with the origin; affects the unset
                       attributes of the current style and replaces these values with its
                       own. Uses `merge_fallback()` merging strategy.
    :param overwrites: List of styles to be used as attribute storage force override
                       regardless of actual `origin` attribute valuse (so called
                       "merging down" with the origin).
    :return:           Clone of ``origin`` style with all specified styles merged into.
    """
    result = origin.clone()
    for fallback in fallbacks:
        result.merge_fallback(fallback)
    for overwrite in overwrites:
        result.merge_overwrite(overwrite)
    return result
