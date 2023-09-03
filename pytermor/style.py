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
from typing import Any

from .color import Color, NOOP_COLOR, resolve_color, IColorValue, ColorRGB, RenderColor
from .common import CDT, FT
from .cval import cv
from .exception import ArgTypeError, LogicError


class MergeMode(str, enum.Enum):
    FALLBACK = "?"
    OVERWRITE = "!"
    REPLACE = "@"


@dataclass()
class Style:
    """
    Create new text render descriptior.

    Both ``fg`` and ``bg`` can be specified as existing ``Color`` instance as well
    as plain *str* or *int* (for the details see `resolve_color()`).

        >>> Style(fg='green', bold=True)
        <Style[green +BOLD]>
        >>> Style(bg=0x0000ff)
        <Style[|#0000ff]>
        >>> Style(fg='DeepSkyBlue1', bg='gray3')
        <Style[x39|x232]>

    Attribute merging from ``fallback`` works this way:

        - If constructor argument is *not* empty (*True*, *False*, ``Color``
          etc.), keep it as attribute value.
        - If constructor argument is empty (*None*, ``NOOP_COLOR``), take the
          value from ``fallback``'s corresponding attribute.

    See `merge_fallback()` and `merge_overwrite()` methods and take the
    differences into account. The method used in the constructor is the first one.

    .. important ::
        Both empty (i.e., *None*) attributes of type ``Color`` after initialization
        will be replaced with special constant `NOOP_COLOR`, which behaves like
        there was no color defined, and at the same time makes it safer to work
        with nullable color-type variables. Merge methods are aware of this and
        trear `NOOP_COLOR` as *None*.

    .. important ::
        *None* and `NOOP_COLOR` are always treated as placeholders for fallback
        values, i.e., they can't be used as *resetters* -- that's what `DEFAULT_COLOR`
        is for.

    :param fallback:    Copy empty attributes from speicifed fallback style.
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

    _fg: Color = field(default=None, init=False)
    _bg: Color = field(default=None, init=False)
    _underline_color: Color = field(default=None, init=False)

    @property
    def fg(self) -> Color:
        """
        Foreground (i.e., text) color. Can be set as `CDT` or ``Color``,
        stored always as ``Color``.
        """
        return self._fg

    @property
    def bg(self) -> Color:
        """
        Background color. Can be set as `CDT` or ``Color``, stored always
        as ``Color``.
        """
        return self._bg

    @property
    def underline_color(self) -> Color:
        """
        Underline color. Can be set as `CDT` or ``Color``, stored always
        as ``Color``.
        """
        return self._underline_color

    @fg.setter
    def fg(self, val: CDT | RenderColor | None):
        self._fg: RenderColor = self._resolve_color(val)

    @bg.setter
    def bg(self, val: CDT | RenderColor | None):
        self._bg: RenderColor = self._resolve_color(val)

    @underline_color.setter
    def underline_color(self, val: CDT | RenderColor | None):
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
    Arbitary string used by some `renderers <IRenderer>`, e.g. by `
    `HtmlRenderer``, which will include the value of this property to an output
    element class list. This property is not inheritable.
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
        fg: CDT | Color = None,
        bg: CDT | Color = None,
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
        underline_color: CDT | Color = None,
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

    def autopick_fg(self) -> Style:
        """
        Pick ``fg_color`` depending on ``bg_color``. Set ``fg_color`` to
        either 3% gray (almost black) if background is bright, or to 80% gray
        (bright gray) if it is dark. If background is None, do nothing.

        .. todo ::

            check if there is a better algorithm,
            because current thinks text on :hex:`#000080` should be black

        Modifies the instance in-place and returns it as well (for chained calls).
        """
        self._ensure_not_frozen()
        if not self._bg:
            return self

        h, s, v = self._bg.hsv
        if v >= 0.45:
            self._fg = cv.GRAY_3
        else:
            self._fg = cv.GRAY_82
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
        and `bg`).

        Modifies the instance in-place and returns it as well (for chained calls).

        .. code-block ::
            :caption: Merging different values in fallback mode

                     FALLBACK   BASE(SELF)   RESULT
                     +-------+   +------+   +------+
            ATTR-1   | False --Ø | True ===>| True |  BASE val is in priority
            ATTR-2   | True -----| None |-->| True |  no BASE val, taking FALLBACK val
            ATTR-3   | None  |   | True ===>| True |  BASE val is in priority
            ATTR-4   | None  |   | None |   | None |  no vals, keeping unset
                     +-------+   +------+   +------+

        .. seealso ::
            `merge_styles` for the examples.

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
        and `bg`).

        Modifies the instance in-place and returns it as well (for chained calls).

        .. code-block ::
            :caption: Merging different values in overwrite mode

                    BASE(SELF)  OVERWRITE    RESULT
                     +------+   +-------+   +-------+
            ATTR-1   | True ==Ø | False --->| False |  OVERWRITE val is in priority
            ATTR-2   | None |   | True ---->| True  |  OVERWRITE val is in priority
            ATTR-3   | True ====| None  |==>| True  |  no OVERWRITE val, keeping BASE val
            ATTR-4   | None |   | None  |   | None  |  no vals, keeping unset
                     +------+   +-------+   +-------+

        .. seealso ::
            `merge_styles` for the examples.

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

        .. code-block ::
            :caption: Merging different values in replace mode

                    BASE(SELF)   REPLACE     RESULT
                     +------+   +-------+  +-------+
            ATTR-1   | False =Ø | True --->| True  |  REPLACE val is in priority
            ATTR-2   | True ==Ø | False -->| False |  REPLACE val is in priority
            ATTR-3   | None |   | False -->| False |  REPLACE val is in priority
            ATTR-4   | True ==Ø | None --->| None  |   ... even when it is unset
                     +------+   +-------+  +-------+

        :param replacement:  Style to merge the attributes with.
        """ ""
        self._ensure_not_frozen()
        for attr in self.renderable_attributes:
            replacement_val = getattr(replacement, attr)
            setattr(self, attr, replacement_val)
        return self

    def _ensure_not_frozen(self) -> None:
        if hasattr(self, "_frozen") and self._frozen:
            raise LogicError(f"{self.__class__.__qualname__} is immutable")

    def _resolve_color(self, arg: CDT | IColorValue | None) -> RenderColor | None:
        if arg is None:
            return NOOP_COLOR
        if isinstance(arg, RenderColor):
            return arg
        if isinstance(arg, IColorValue):
            return ColorRGB(arg.int)
        if isinstance(arg, (str, int)) and not isinstance(arg, bool):
            # undesirable isinstance(True, int) --> #000001
            return resolve_color(arg)
        raise ArgTypeError(arg, "arg", CDT, IColorValue, None)

    def __setattr__(self, name: str, value: Any) -> None:
        self._ensure_not_frozen()
        super().__setattr__(name, value)

    def __eq__(self, other: Style) -> bool:
        if not isinstance(other, Style):  # pragma: no cover
            return False
        return all(
            getattr(self, attr) == getattr(other, attr) for attr in self._attributes
        )

    def __repr__(self) -> str:
        frozen = "*" if self._frozen else ""
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


class _NoOpStyle(Style):
    def __init__(self):
        super().__init__(frozen=True)

    def __bool__(self) -> bool:
        return False


NOOP_STYLE = _NoOpStyle()
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
    DIM = Style(dim=True, frozen=True)
    ITALIC = Style(italic=True, frozen=True)
    UNDERLINED = Style(underlined=True, frozen=True)

    WARNING = Style(fg=cv.YELLOW, frozen=True)
    """ """
    WARNING_LABEL = Style(WARNING, frozen=True, bold=True)
    """ """
    WARNING_ACCENT = Style(fg=cv.HI_YELLOW, frozen=True)
    """ """

    ERROR = Style(fg=cv.RED, frozen=True)
    """ """
    ERROR_LABEL = Style(ERROR, frozen=True, bold=True)
    """ """
    ERROR_ACCENT = Style(fg=cv.HI_RED, frozen=True)
    """ """

    CRITICAL = Style(bg=cv.RED_3, fg=cv.HI_WHITE, frozen=True)
    """ """
    CRITICAL_LABEL = Style(CRITICAL, frozen=True, bold=True)
    """ """
    CRITICAL_ACCENT = Style(CRITICAL_LABEL, frozen=True, blink=True)
    """ """

    INCONSISTENCY = Style(bg=cv.RED_3, fg=cv.HI_YELLOW, frozen=True)
    """ """


def is_ft(arg) -> bool:
    return isinstance(arg, (type(None), int, str, IColorValue, Style))


def make_style(fmt: FT = None) -> Style:
    """
    General :class:`.Style` constructor. Accepts a variety of argument types:

        - `CDT` (*str* or *int*)
            This argument type implies the creation of basic :class:`.Style`
            with the only attribute set being `fg` (i.e., text color). For the
            details on color resolving see `resolve_color()`.

        - :class:`.Style`
            Existing style instance. Return it as is.

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


def merge_styles(
    origin: Style = NOOP_STYLE,
    *,
    fallbacks: t.Iterable[Style] = (),
    overwrites: t.Iterable[Style] = (),
) -> Style:
    """
    Bulk style merging method. First merge `fallbacks` `styles <.Style>` with the
    ``origin`` in the same order they are iterated, using `merge_fallback()` algorithm;
    then do the same for `overwrites` styles, but using `merge_overwrite()` merge
    method.

    .. important ::
        The original `origin` is left untouched, as all the operations are performed on
        its clone. To make things clearer the name of the argument differs from the ones
        that are modified in-place (``base`` and ``origin``).

    .. code-block ::
       :caption: Dual mode merge diagram

                                       +-----+                                 +-----+
          >---->---->----->---->------->     >-------(B)-update---------------->     |
          |    |    |     |    |       |     |                                 |  R  |
          |    |    |     |    |       |  B  >=>Ø    [0]>-[1]>-[2]> .. -[n]>   |  E  |
       [0]>-[1]>-[2]>- .. >-[n]>->Ø    |  A  >=>Ø       |    |    |        |   |  S  |
          |    |    >- .. ------->Ø    |  S  >=>Ø       >---(D)-update----->--->  U  |
          |    >-----  .. ------->Ø    |  E  | (C) drop                        |  L  |
          >----------  .. ------->Ø    |     |=================(E)=keep========>  T  |
                                (A)    |     |                                 |     |
                  FALLBACKS    drop    +-----+            OVERWRITES           +-----+

    The key actions are marked with (**A**) to (**E**) letters. In reality the algorithm
    works in slightly different order, but the exact scheme would be less illustrative.

    :(A),(B):
        Iterate ``fallback`` styles one by one; discard all the attributes of a
        current ``fallback`` style, that are already set in ``origin`` style
        (i.e., that are not *Nones*). Update all ``origin`` style empty attributes
        with corresponding ``fallback`` values, if they exist and are not empty.
        Repeat these steps for the next ``fallback`` in the list, until the list
        is empty.

        .. code-block :: python
            :caption: Fallback merge algorithm example №1

            >>> origin = Style(fg='red')
            ...
            >>> fallbacks = [Style(fg='blue'), Style(bold=True), Style(bold=False)]
            ...
            >>> merge_styles(origin, fallbacks=fallbacks)
            <Style[red +BOLD]>

        In the example above:

            - the first fallback will be ignored, as `fg` is already set;
            - the second fallback will be applied (``origin`` style will now have `bold`
              set to *True*;
            - which will make the handler ignore third fallback completely; if third
              fallback was encountered earlier than the 2nd one, ``origin`` `bold` attribute
              would have been set to *False*, but alas.

        .. note ::

            Fallbacks allow to build complex style conditions, e.g. take a look into
            `Highlighter.colorize()` method::

                int_st = merge_styles(st, fallbacks=[Style(bold=True)])

            Instead of using ``Style(st, bold=True)`` the merging algorithm is invoked.
            This changes the logic of "bold" attribute application -- if there is a
            necessity to explicitly forbid bold text at origin/parent level, one could write::

                STYLE_NUL = Style(STYLE_DEFAULT, cv.GRAY, bold=False)
                STYLE_PRC = Style(STYLE_DEFAULT, cv.MAGENTA)
                STYLE_KIL = Style(STYLE_DEFAULT, cv.BLUE)
                ...

            As you can see, resulting ``int_st`` will be bold for all styles other
            than ``STYLE_NUL``.

            .. code-block :: python
                :caption: Fallback merge algorithm example №2

                >>> merge_styles(Style(fg=cv.BLUE), fallbacks=[Style(bold=True)])
                <Style[blue +BOLD]>
                >>> merge_styles(Style(fg=cv.GRAY, bold=False), fallbacks=[Style(bold=True)])
                <Style[gray -BOLD]>


    :(C),(D),(E):
        Iterate ``overwrite`` styles one by one; discard all the attributes of a ``origin``
        style that have a non-empty counterpart in ``overwrite`` style, and put
        corresponding ``overwrite`` attribute values instead of them. Keep ``origin``
        attribute values that have no counterpart in current ``overwrite`` style (i.e.,
        if attribute value is *None*). Then pick next ``overwrite`` style from the input
        list and repeat all these steps.

        .. code-block :: python
            :caption: Overwrite merge algorithm example

            >>> origin = Style(fg='red')
            ...
            >>> overwrites = [Style(fg='blue'), Style(bold=True), Style(bold=False)]
            ...
            >>> merge_styles(origin, overwrites=overwrites)
            <Style[blue -BOLD]>

        In the example above all the ``overwrites`` will be applied in order they were
        put into *list*, and the result attribute values are equal to the last
        encountered non-empty values in ``overwrites`` list.

    :param origin:     Initial style, or the source of attributes.
    :param fallbacks:  List of styles to be used as a backup attribute storage, or.
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
