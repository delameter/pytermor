# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
"""
.. todo ::
    S
"""
from __future__ import annotations

import typing as t
from dataclasses import dataclass, field
from typing import Any

from .color import IColor, NOOP_COLOR, resolve_color, CDT
from .cval import CVAL as cv
from .common import ArgTypeError, LogicError

FT = t.TypeVar("FT", int, str, IColor, "Style", None)
"""
:abbr:`FT (Format type)` is a style descriptor. Used as a shortcut precursor for actual 
styles. Primary handler is `make_style()`.
"""


@dataclass()
class Style:
    """
    Create new text render descriptior.

    Both ``fg`` and ``bg`` can be specified as existing ``IColor`` instance as well
    as plain *str* or *int* (for the details see `resolve_color()`).

        >>> Style(fg='green', bold=True)
        <Style[green:NOP +BOLD]>
        >>> Style(bg=0x0000ff)
        <Style[NOP:0000FF]>
        >>> Style(fg='DeepSkyBlue1', bg='gray3')
        <Style[X39[00AFFF]:X232[080808]]>

    Attribute merging from ``fallback`` works this way:

        - If constructor argument is *not* empty (*True*, *False*, ``IColor``
          etc.), keep it as attribute value.
        - If constructor argument is empty (*None*, ``NOOP_COLOR``), take the
           value from ``fallback``'s corresponding attribute.

    See `merge_fallback()` and `merge_overwrite()` methods and take the
    differences into account. The method used in the constructor is the first one.

    .. important ::
        Both empty (i.e., *None*) attributes of type ``IColor`` after initialization
        will be replaced with special constant `NOOP_COLOR`, which behaves like
        there was no color defined, and at the same time makes it safer to work
        with nullable color-type variables. Merge methods are aware of this and
        trear `NOOP_COLOR` as *None*.

    .. important ::
        *None* and `NOOP_COLOR` are always treated as placeholders for fallback
        values, i.e., they can't be used as *resetters* -- that's what `DEFAULT_COLOR`
        is for.

    .. note ::
        All arguments except ``fallback``, ``fg`` and ``bg`` are *kwonly*-type args.

    :param fallback:    Copy empty attributes from speicifed fallback style.
                        See `merge_fallback()`.
    :param fg:          Foreground (=text) color.
    :param bg:          Background color.
    :param bold:        Bold or increased intensity.
    :param dim:         Faint, decreased intensity.
    :param italic:      Italic.
    :param underlined:  Underline.
    :param overlined:   Overline.
    :param crosslined:  Strikethrough.
    :param double_underlined:
                        Double underline.
    :param inversed:    Swap foreground and background colors.
    :param blink:       Blinking effect.
    :param class_name:  Custom class name for the element.
    """

    _fg: IColor = field(default=None, init=False)
    _bg: IColor = field(default=None, init=False)

    @property
    def fg(self) -> IColor:
        """
        Foreground (i.e., text) color. Can be set as `CDT` or ``IColor``,
        stored always as ``IColor``.
        """
        return self._fg

    @property
    def bg(self) -> IColor:
        """
        Background color. Can be set as `CDT` or ``IColor``, stored always
        as ``IColor``.
        """
        return self._bg

    @fg.setter
    def fg(self, val: CDT | IColor):
        self._fg: IColor = self._resolve_color(val)

    @bg.setter
    def bg(self, val: CDT | IColor):
        self._bg: IColor = self._resolve_color(val)


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
            "bold",
            "dim",
            "italic",
            "underlined",
            "overlined",
            "crosslined",
            "double_underlined",
            "inversed",
            "blink",
        ]
    )

    @property
    def _attributes(self) -> t.FrozenSet:
        return frozenset({*self.__dict__.keys(), "_fg", "_bg"} - {'_initialized'})

    def __init__(
        self,
        fallback: Style = None,
        fg: CDT | IColor = None,
        bg: CDT | IColor = None,
        *,
        bold: bool = None,
        dim: bool = None,
        italic: bool = None,
        underlined: bool = None,
        overlined: bool = None,
        crosslined: bool = None,
        double_underlined: bool = None,
        inversed: bool = None,
        blink: bool = None,
        class_name: str = None,
    ):
        if fg is not None:
            self._fg = self._resolve_color(fg)
        if bg is not None:
            self._bg = self._resolve_color(bg)

        self.bold = bold
        self.dim = dim
        self.italic = italic
        self.underlined = underlined
        self.overlined = overlined
        self.crosslined = crosslined
        self.double_underlined = double_underlined
        self.inversed = inversed
        self.blink = blink
        self.class_name = class_name

        if fallback is not None:
            self.merge_fallback(fallback)

        if self._fg is None:
            self._fg = NOOP_COLOR
        if self._bg is None:
            self._bg = NOOP_COLOR

        self._initialized = True

    def autopick_fg(self) -> Style:
        """
        Pick ``fg_color`` depending on ``bg_color``. Set ``fg_color`` to
        either 3% gray (almost black) if background is bright, or to 80% gray
        (bright gray) if it is dark. If background is None, do nothing.

        .. todo ::

            check if there is a better algorithm,
            because current thinks text on :hex:`#000080` should be black
        """
        if self._bg is None or self._bg.hex_value is None:
            return self

        h, s, v = self._bg.to_hsv()
        if v >= 0.45:
            self._fg = cv.GRAY_3
        else:
            self._fg = cv.GRAY_82
        return self

    def flip(self) -> Style:
        """
        Swap foreground color and background color.
        """
        self._fg, self._bg = self._bg, self._fg
        return self

    def clone(self) -> Style:
        """
        C
        """
        return Style(self)

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

    def merge_overwrite(self, overwrite: Style):
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
        for attr in self.renderable_attributes:
            overwrite_val = getattr(overwrite, attr)
            if overwrite_val is not None and overwrite_val != NOOP_COLOR:
                setattr(self, attr, overwrite_val)
        return self

    def _resolve_color(self, arg: str | int | IColor | None) -> IColor | None:
        if arg is None:
            return NOOP_COLOR
        if isinstance(arg, IColor):
            return arg
        if isinstance(arg, (str, int)):
            return resolve_color(arg)
        raise ArgTypeError(type(arg), "arg", fn=self._resolve_color)

    def __eq__(self, other: Style) -> bool:
        if not isinstance(other, Style):
            return False
        return all(
            getattr(self, attr) == getattr(other, attr) for attr in self._attributes
        )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}[{self.repr_attrs(False)}]>"

    def repr_attrs(self, verbose: bool) -> str:
        if self == NOOP_STYLE:
            colors_set = ["NOP"]
        elif self._fg is None or self._bg is None:
            colors_set = ["uninitialized"]
        else:
            colors_set = []
            for attr_name in ("fg", "bg"):
                val: IColor = getattr(self, attr_name)
                colors_set.append(val.repr_attrs(verbose))

        props_set = [":".join(colors_set)]
        for attr_name in self.renderable_attributes:
            attr = getattr(self, attr_name)
            if isinstance(attr, bool):
                props_set.append(("+" if attr else "-") + attr_name.upper())
        return " ".join(props_set)



class _NoOpStyle(Style):
    def __bool__(self) -> bool:
        return False

    def __setattr__(self, name: str, value: Any):
        if hasattr(self, '_initialized'):
            raise LogicError("NOOP_STYLE is immutable")
        super().__setattr__(name, value)


NOOP_STYLE = _NoOpStyle()
""" 
Special style passing the text through without any modifications. 
    
.. important ::
    Casting to *bool* results in **False** for all ``NOOP`` instances in the 
    library (`NOOP_SEQ`, `NOOP_COLOR` and `NOOP_STYLE`). This is intended. 

This class is immutable, i.e. `LogicError` will be raised upon an attempt to
modify any of its attributes, which can lead to schrödinbugs::

    st1.merge_fallback(Style(bold=True), [Style(italic=False)])

If ``st1`` is a regular style instance, the statement above will always work
(and pass the tests), but if it happens to be a `NOOP_STYLE`, this will result 
in an exception. To protect from this outcome one could merge styles via frontend 
method `merge_styles` only, which always makes a copy of base argument and thus
cannot lead to such behaviour.

"""


class Styles:
    """
    Some ready-to-use styles. Can be used as examples.

    """

    WARNING = Style(fg=cv.YELLOW)
    """ """
    WARNING_LABEL = Style(WARNING, bold=True)
    """ """
    WARNING_ACCENT = Style(fg=cv.HI_YELLOW)
    """ """

    ERROR = Style(fg=cv.RED)
    """ """
    ERROR_LABEL = Style(ERROR, bold=True)
    """ """
    ERROR_ACCENT = Style(fg=cv.HI_RED)
    """ """

    CRITICAL = Style(bg=cv.RED_3, fg=cv.HI_WHITE)
    """ """
    CRITICAL_LABEL = Style(CRITICAL, bold=True)
    """ """
    CRITICAL_ACCENT = Style(CRITICAL_LABEL, blink=True)
    """ """


def make_style(fmt: FT = None) -> Style:
    """
    General `Style` constructor. Accepts a variety of argument types:

        - `CDT` (*str* or *int*)
            This argument type implies the creation of basic `Style` with
            the only attribute set being `fg` (i.e., text color). For the
            details on color resolving see `resolve_color()`.

        - `Style`
            Existing style instance. Return it as is.

        - *None*
            Return `NOOP_STYLE`.

    :param FT fmt: See `FT`.
    """
    if fmt is None:
        return NOOP_STYLE
    if isinstance(fmt, Style):
        return fmt
    if isinstance(fmt, (str, int, IColor)):
        return Style(fg=fmt)
    raise ArgTypeError(type(fmt), "fmt", fn=make_style)


def merge_styles(
    base: Style = NOOP_STYLE,
    *,
    fallbacks: t.Iterable[Style] = (),
    overwrites: t.Iterable[Style] = (),
) -> Style:
    """
    Bulk style merging method. First merge `fallbacks` `styles <Style>` with the
    ``base`` in the same order they are iterated, using `merge_fallback()` algorithm;
    then do the same for `overwrites` styles, but using `merge_overwrite()` merge
    method.

    The original `base` is left untouched, as all the operations are performed on
    its clone.

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
        current ``fallback`` style, that are already set in ``base`` style
        (i.e., that are not *Nones*). Update all ``base`` style empty attributes
        with corresponding ``fallback`` values, if they exist and are not empty.
        Repeat these steps for the next ``fallback`` in the list, until the list
        is empty.

        .. code-block :: python
            :caption: Fallback merge algorithm example №1

            >>> base = Style(fg='red')
            >>> fallbacks = [Style(fg='blue'), Style(bold=True), Style(bold=False)]
            >>> merge_styles(base, fallbacks=fallbacks)
            <Style[red:NOP +BOLD]>

        In the example above:

            - the first fallback will be ignored, as `fg` is already set;
            - the second fallback will be applied (``base`` style will now have `bold`
              set to *True*;
            - which will make the handler ignore third fallback completely; if third
              fallback was encountered earlier than the 2nd one, ``base`` `bold` attribute
              would have been set to *False*, but alas.

        .. note ::

            Fallbacks allow to build complex style conditions, e.g. take a look into
            `Highlighter.colorize()` method::

                int_st = merge_styles(st, fallbacks=[Style(bold=True)])

            Instead of using ``Style(st, bold=True)`` the merging algorithm is invoked.
            This changes the logic of "bold" attribute application -- if there is a
            necessity to explicitly forbid bold text at base/parent level, one could write::

                STYLE_NUL = Style(STYLE_DEFAULT, cv.GRAY, bold=False)
                STYLE_PRC = Style(STYLE_DEFAULT, cv.MAGENTA)
                STYLE_KIL = Style(STYLE_DEFAULT, cv.BLUE)
                ...

            As you can see, resulting ``int_st`` will be bold for all styles other
            than ``STYLE_NUL``.

            .. code-block :: python
                :caption: Fallback merge algorithm example №2

                >>> merge_styles(Style(fg=cv.BLUE), fallbacks=[Style(bold=True)])
                <Style[blue:NOP +BOLD]>
                >>> merge_styles(Style(fg=cv.GRAY, bold=False), fallbacks=[Style(bold=True)])
                <Style[gray:NOP -BOLD]>


    :(C),(D),(E):
        Iterate ``overwrite`` styles one by one; discard all the attributes of a ``base``
        style that have a non-empty counterpart in ``overwrite`` style, and put
        corresponding ``overwrite`` attribute values instead of them. Keep ``base``
        attribute values that have no counterpart in current ``overwrite`` style (i.e.,
        if attribute value is *None*). Then pick next ``overwrite`` style from the input
        list and repeat all these steps.

        .. code-block :: python
            :caption: Overwrite merge algorithm example

            >>> base = Style(fg='red')
            >>> overwrites = [Style(fg='blue'), Style(bold=True), Style(bold=False)]
            >>> merge_styles(base, overwrites=overwrites)
            <Style[blue:NOP -BOLD]>

        In the example above all the ``overwrites`` will be applied in order they were
        put into *list*, and the result attribute values are equal to the last
        encountered non-empty values in ``overwrites`` list.

    :param base:       Basis style instance.
    :param fallbacks:  List of styles to be used as a backup attribute storage, when
                       there is no value set for the attribute in question. Uses
                       `merge_fallback()` merging strategy.
    :param overwrites: List of styles to be used as attribute storage force override
                       regardless of actual `base` attribute valuse.
    :return:           Clone of ``base`` style with all specified styles merged into.
    """
    result = base.clone()
    for fallback in fallbacks:
        result.merge_fallback(fallback)
    for overwrite in overwrites:
        result.merge_overwrite(overwrite)
    return result
