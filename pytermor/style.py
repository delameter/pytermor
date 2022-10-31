# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------

from __future__ import annotations

import typing as t
from dataclasses import dataclass, field

from . import color
from .color import Color, NOOP_COLOR, ColorRGB, Index


@dataclass
class Style:
    """Create a new ``Style()``.

    Key difference between ``Styles`` and ``Spans`` or ``SGRs`` is that
    ``Styles`` describe colors in RGB format and therefore support output
    rendering in several different formats (see :mod:`._render`).

    Both ``fg`` and ``bg`` can be specified as:

    1. :class:`.Color` instance or library preset;
    2. name of any of these presets, case-insensitive;
    3. integer color value in hexademical RGB format.
    4. None -- the color will be unset.

    Inheritance ``parent`` -> ``child`` works this way:

    1. If an argument in child's constructor is empty (=None), take value from
       ``parent``'s corresponding attribute.
    2. If an argument in child's constructor is *not* empty (=True|False|Color etc.),
       use it as child's attribute.

    .. note ::
        There will be no empty (=None) attributes of type `Color` after initialization
        -- they are replaced with special constant `NOOP_COLOR`, that works as if
        there was no color defined and allows to avoid writing of boilerplate code
        to check if a color is None here and there.

    :param parent:      Style to copy attributes without value from.
    :param fg:          Foreground (i.e., text) color.
    :param bg:          Background color.
    :param blink:       Blinking effect; *supported by limited amount of Renderers*.
    :param bold:        Bold or increased intensity.
    :param crosslined:  Strikethrough.
    :param dim:         Faint, decreased intensity.
    :param double_underlined:
                        Faint, decreased intensity.
    :param inversed:    Swap foreground and background colors.
    :param italic:      Italic.
    :param overlined:   Overline.
    :param underlined:  Underline.
    :param class_name:  Arbitary string used by some renderers, e.g. by
                        ``HtmlRenderer``.

    >>> Style(fg='green', bold=True)
    Style[fg=008000, ~, bold]
    >>> Style(bg=0x0000ff)
    Style[~, bg=0000ff]
    >>> Style(fg='DeepSkyBlue1', bg='gray3')
    Style[fg=00afff, bg=080808]
    """

    _fg: Color = field(default=None, init=False)
    _bg: Color = field(default=None, init=False)

    renderable_attributes = frozenset(
        [
            "fg",
            "bg",
            "blink",
            "bold",
            "crosslined",
            "dim",
            "double_underlined",
            "inversed",
            "italic",
            "overlined",
            "underlined",
        ]
    )

    def __init__(
        self,
        parent: Style = None,
        fg: Color | int | str = None,
        bg: Color | int | str = None,
        blink: bool = None,
        bold: bool = None,
        crosslined: bool = None,
        dim: bool = None,
        double_underlined: bool = None,
        inversed: bool = None,
        italic: bool = None,
        overlined: bool = None,
        underlined: bool = None,
        class_name: str = None,
    ):
        if fg is not None:
            self._fg = self._resolve_color(fg, True)
        if bg is not None:
            self._bg = self._resolve_color(bg, True)

        self.blink = blink
        self.bold = bold
        self.crosslined = crosslined
        self.dim = dim
        self.double_underlined = double_underlined
        self.inversed = inversed
        self.italic = italic
        self.overlined = overlined
        self.underlined = underlined
        self.class_name = class_name

        if parent is not None:
            self._clone_from(parent)

        if self._fg is None:
            self._fg = NOOP_COLOR
        if self._bg is None:
            self._bg = NOOP_COLOR

    def autopick_fg(self) -> Style:
        """
        Pick ``fg_color`` depending on ``bg_color``. Set ``fg_color`` to
        either 3% gray (almost black) if background is bright, or to 80% gray
        (bright gray) if it is dark. If background is None, do nothing.

        .. todo ::

            check if there is a better algorithm,
            because current thinks text on #000080 should be black

        :return: self
        """
        if self._bg is None or self._bg.hex_value is None:
            return self

        h, s, v = self._bg.to_hsv()
        if v >= 0.45:
            self._fg = index.GRAY_3
        else:
            self._fg = index.GRAY_82
        return self

    def flip(self) -> Style:
        """
        Swap foreground color and background color.
        :return: self
        """
        self._fg, self._bg = self._bg, self._fg
        return self

    # noinspection PyMethodMayBeStatic
    def _resolve_color(self, arg: str | int | Color, nullable: bool) -> Color | None:
        if isinstance(arg, Color):
            return arg
        if isinstance(arg, int):
            return ColorRGB(arg)
        if isinstance(arg, str):
            return Index.resolve(arg)
        return None if nullable else NOOP_COLOR

    @property
    def attributes(self) -> t.FrozenSet:
        return frozenset(list(self.__dict__.keys()) + ["fg", "bg"])

    @property
    def _attributes(self) -> t.FrozenSet:
        return frozenset(list(self.__dict__.keys()) + ["_fg", "_bg"])

    def clone(self) -> Style:
        return Style(self)

    def _clone_from(self, parent: Style):
        for attr in self.renderable_attributes:
            self_val = getattr(self, attr)
            parent_val = getattr(parent, attr)
            if self_val is None and parent_val is not None:
                setattr(self, attr, parent_val)

    def __eq__(self, other: Style):
        return all(
            getattr(self, attr) == getattr(other, attr) for attr in self._attributes
        )

    def __repr__(self):
        if self._fg is None or self._bg is None:
            return self.__class__.__name__ + "[uninitialized]"
        props_set = [self.fg.format_value("fg="), self.bg.format_value("bg=")]
        for attr_name in self.renderable_attributes:
            attr = getattr(self, attr_name)
            if isinstance(attr, bool) and attr is True:
                props_set.append(attr_name)

        return self.__class__.__name__ + "[{:s}]".format(", ".join(props_set))

    @property
    def fg(self) -> Color:
        return self._fg

    @property
    def bg(self) -> Color:
        return self._bg

    @fg.setter
    def fg(self, val: str | int | Color):
        self._fg: Color = self._resolve_color(val, nullable=False)

    @bg.setter
    def bg(self, val: str | int | Color):
        self._bg: Color = self._resolve_color(val, nullable=False)


NOOP_STYLE = Style()


class Styles:
    """
    Some ready-to-use styles. Can be used as examples.
    """

    WARNING = Style(fg=color.YELLOW)
    WARNING_LABEL = Style(WARNING, bold=True)
    WARNING_ACCENT = Style(fg=color.HI_YELLOW)

    ERROR = Style(fg=color.RED)
    ERROR_LABEL = Style(ERROR, bold=True)
    ERROR_ACCENT = Style(fg=color.HI_RED)

    CRITICAL = Style(bg=color.HI_RED, fg=color.HI_WHITE)
    CRITICAL_LABEL = Style(CRITICAL, bold=True)
    CRITICAL_ACCENT = Style(CRITICAL, bold=True, blink=True)
