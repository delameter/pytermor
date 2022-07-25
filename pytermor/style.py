# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""
High-level abstraction defining text colors and attributes.

.. testsetup:: *

    from pytermor import color, Style

"""
from __future__ import annotations

from typing import Any

from . import color
from .color import Color, ColorRGB, NOOP as NOOP_COLOR


class Style:
    """
    Create a new ``Style()``.

    Key difference between ``Styles`` and ``Spans`` or ``SGRs`` is that
    ``Styles`` describe colors in RGB format and therefore support output
    rendering in several different formats (see :mod:`.renderer`).

    Both ``fg`` and ``bg_color`` can be specified as:

    1. :class:`.Color` instance or library preset;
    2. key code -- name of any of aforementioned presets, case-insensitive;
    3. integer color value in hexademical RGB format.

    >>> Style('green', bold=True)
    Style[fg=008000, no bg, bold]
    >>> Style(bg=0x0000ff)
    Style[no fg, bg=0000ff]
    >>> Style(color.IDX_DEEP_SKY_BLUE_1, color.IDX_GREY_93)
    Style[fg=00afff, bg=eeeeee]

    :param fg:    Foreground (i.e., text) color.
    :param bg:    Background color.
    :param auto_fg:
        Automatically select ``fg`` based on ``bg_color`` (black or white
        depending on background brightness, if ``bg_color`` is defined).
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
    """
    def __init__(self, fg: str|int|Color = None, bg: str|int|Color = None,
                 auto_fg: bool = False, blink: bool = False, bold: bool = False,
                 crosslined: bool = False, dim: bool = False,
                 double_underlined: bool = False, inversed: bool = False,
                 italic: bool = False, overlined: bool = False,
                 underlined: bool = False):
        self._fg: Color = self._resolve_color(fg)
        self._bg: Color = self._resolve_color(bg)
        self._blink: bool = blink
        self._bold: bool = bold
        self._crosslined: bool = crosslined
        self._dim: bool = dim
        self._double_underlined: bool = double_underlined
        self._inversed: bool = inversed
        self._italic: bool = italic
        self._overlined: bool = overlined
        self._underlined: bool = underlined

        if auto_fg:
            self._pick_fg_for_bg()

    def render(self, text: Any = None) -> str:
        """
        Returns ``text`` with all attributes and colors applied.

        By default uses `SequenceSGR` renderer, that means that output will contain
        ANSI escape sequences.
        """
        from .renderer import RendererManager
        return RendererManager.get_default().render(self, text)
    
    def _pick_fg_for_bg(self):
        if self._bg is None or self._bg.hex_value is None:
            return

        h, s, v = Color.hex_value_to_hsv_channels(self._bg.hex_value)
        if v >= .45:
            self._fg = color.RGB_BLACK
        else:
            self._fg = color.RGB_WHITE

    # noinspection PyMethodMayBeStatic
    def _resolve_color(self, arg: str|int|Color|None) -> Color:
        if isinstance(arg, Color):
            return arg

        if isinstance(arg, int):
            return ColorRGB(arg)

        if isinstance(arg, str):
            arg_mapped = arg.upper()
            resolved_color = getattr(color, arg_mapped, None)
            if resolved_color is None:
                raise KeyError(
                    f'Code "{arg}" -> "{arg_mapped}" is not a name of Color preset')
            if not isinstance(resolved_color, Color):
                raise ValueError(f'Attribute is not valid Color: {resolved_color}')
            return resolved_color

        return NOOP_COLOR

    def __repr__(self):
        props_set = [self._fg.format_value('fg=', 'no fg'),
                     self._bg.format_value('bg=', 'no bg'), ]
        for attr_name in dir(self):
            if not attr_name.startswith('_'):
                attr = getattr(self, attr_name)
                if isinstance(attr, bool) and attr is True:
                    props_set.append(attr_name)

        return self.__class__.__name__ + '[{:s}]'.format(', '.join(props_set))

    @property
    def fg(self) -> Color: return self._fg
    @property
    def bg(self) -> Color: return self._bg
    @property
    def blink(self) -> bool: return self._blink
    @property
    def bold(self) -> bool: return self._bold
    @property
    def crosslined(self) -> bool: return self._crosslined
    @property
    def dim(self) -> bool: return self._dim
    @property
    def double_underlined(self) -> bool: return self._double_underlined
    @property
    def inversed(self) -> bool: return self._inversed
    @property
    def italic(self) -> bool: return self._italic
    @property
    def overlined(self): return self._overlined
    @property
    def underlined(self): return self._underlined


NOOP = Style()


# ---------------------------------------------------------------------------

class Stylesheet:
    def __init__(self, default: Style = None):
        self.default: Style = self._opt_arg(default)

    def _opt_arg(self, arg: Style|None):
        return arg or NOOP

    def __repr__(self):
        styles_set = sum(map(lambda a: int(isinstance(a, Style)),
            [getattr(self, attr_name) for attr_name in dir(self) if
             not attr_name.startswith('_')]))
        return self.__class__.__name__ + '[{:d} props]'.format(styles_set)
