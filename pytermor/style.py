# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""
.. testsetup:: *

   from pytermor.style import *
"""
from __future__ import annotations

import typing as t
from dataclasses import dataclass, field

from . import cv, color
from .color import IColor, NOOP_COLOR
from .common import ArgTypeError


@dataclass()
class Style:
    """ style """

    _fg: IColor = field(default=None, init=False)
    _bg: IColor = field(default=None, init=False)

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

    @property
    def _attributes(self) -> t.FrozenSet:
        return frozenset(list(self.__dict__.keys()) + ["_fg", "_bg"])

    @staticmethod
    def make(fmt: IColor|Style|None) -> Style:
        if not fmt:
            return NOOP_STYLE
        if isinstance(fmt, IColor):
            if fmt == NOOP_COLOR:
                return NOOP_STYLE
            return Style(fg=fmt)
        if isinstance(fmt, Style):
            return fmt
        raise ArgTypeError(type(fmt), "fmt", fn=Style.make)

    def __init__(
        self,
        parent: Style = None,
        fg: IColor|int|str = None,
        bg: IColor|int|str = None,
        *,
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
        """Create a new ``Style()``. Both ``fg`` and ``bg`` can be specified as:

            1. :class:`.Color` instance or library preset;
            2. `*str*` -- name of any of these presets, case-insensitive;
            3. `*int*` -- color value in hexadecimal RGB format;
            4. *None* -- the color will be unset.

        Inheritance ``parent`` -> ``child`` works this way:

            - If an argument in child's constructor is empty (*None*), take value from
              ``parent``'s corresponding attribute.
            - If an argument in child's constructor is *not* empty (``True``,
              ``False``, `Color` etc.), use it as child's attribute.

        .. note ::
            Both empty (i.e., *None*) attributes of type `Color` after initialization
            will be replaced with special constant `NOOP_COLOR`, which behaves like
            there was no color defined, and at the same time makes it safer to work
            with nullable color-type variables.

        All arguments except ``parent``, ``fg`` and ``bg`` are *kwonly*\ -type args.

        >>> Style(fg='green', bold=True)
        <Style[fg=<Color16[#32,008000?,green]>,bg=<_NoopColor[NOP]>,bold]>
        >>> Style(bg=0x0000ff)
        <Style[fg=<_NoopColor[NOP]>,bg=<ColorRGB[0000FF]>]>
        >>> Style(fg='DeepSkyBlue1', bg='gray3')
        <Style[fg=<Color256[#39,00AFFF,deep-sky-blue-1]>,bg=<Color256[#232,080808,gray-3]>]>

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
        :param class_name:  Arbitary string used by some _get_renderers, e.g. by
                            ``HtmlRenderer``.
        """
        if fg is not None:
            self._fg = self._resolve_color(fg)
        if bg is not None:
            self._bg = self._resolve_color(bg)

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
            self._fg = cv.GRAY_3
        else:
            self._fg = cv.GRAY_82
        return self

    def flip(self) -> Style:
        """
        Swap foreground color and background color.
        :return: self
        """
        self._fg, self._bg = self._bg, self._fg
        return self

    def clone(self) -> Style:
        return Style(self)

    def _clone_from(self, parent: Style):
        for attr in self.renderable_attributes:
            self_val = getattr(self, attr)
            parent_val = getattr(parent, attr)
            if self_val is None and parent_val is not None:
                setattr(self, attr, parent_val)

    def _resolve_color(self, arg: str|int|IColor|None) -> IColor|None:
        if arg is None:
            return NOOP_COLOR
        if isinstance(arg, IColor):
            return arg
        if isinstance(arg, (str, int)):
            return color.resolve(arg)
        raise ArgTypeError(type(arg), "arg", fn=self._resolve_color)

    def __eq__(self, other: Style):
        return all(
            getattr(self, attr) == getattr(other, attr) for attr in self._attributes
        )

    def __repr__(self):
        if self == NOOP_STYLE:
            props_set = ["NOP"]
        elif self._fg is None or self._bg is None:
            props_set = ["uninitialized"]
        else:
            props_set = [f"fg={self.fg!r}", f"bg={self.bg!r}"]
            for attr_name in self.renderable_attributes:
                attr = getattr(self, attr_name)
                if isinstance(attr, bool) and attr is True:
                    props_set.append(attr_name)

        return f"<{self.__class__.__name__}[{','.join(props_set)}]>"

    @property
    def fg(self) -> IColor:
        return self._fg

    @property
    def bg(self) -> IColor:
        return self._bg

    @fg.setter
    def fg(self, val: str|int|IColor|None):
        self._fg: IColor = self._resolve_color(val)

    @bg.setter
    def bg(self, val: str|int|IColor|None):
        self._bg: IColor = self._resolve_color(val)


NOOP_STYLE = Style()
""" Special style passing the text through without any modifications. """


class Styles:
    """
    Some ready-to-use styles. Can be used as examples.
    """

    WARNING = Style(fg=cv.YELLOW)
    WARNING_LABEL = Style(WARNING, bold=True)
    WARNING_ACCENT = Style(fg=cv.HI_YELLOW)

    ERROR = Style(fg=cv.RED)
    ERROR_LABEL = Style(ERROR, bold=True)
    ERROR_ACCENT = Style(fg=cv.HI_RED)

    CRITICAL = Style(bg=cv.RED, fg=cv.HI_WHITE)
    CRITICAL_LABEL = Style(CRITICAL, bg=cv.HI_RED, bold=True)
    CRITICAL_ACCENT = Style(CRITICAL_LABEL, blink=True)
