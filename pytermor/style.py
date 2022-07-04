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

    Both ``fg_color`` and ``bg_color`` can be specified as:

    1. :class:`.Color` instance or library preset;
    2. key code -- name of for any of aforementioned presets, case-insensitive;
    3. integer color value in hexademical RGB format.

    .. doctest ::

        >>> Style('green', bold=True)
        Style[fg=008000, no bg, bold]
        >>> Style(bg_color=0x0000ff)
        Style[no fg, bg=0000ff]
        >>> Style(color.IDX_DEEP_SKY_BLUE_1, color.IDX_GREY_93)
        Style[fg=00afff, bg=eeeeee]

    :param fg_color:    Foreground (i.e., text) color.
    :param bg_color:    Background color.
    :param auto_fg:
        Automatically select ``fg_color`` based on ``bg_color`` (black or white
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
    def __init__(self, fg_color: str|int|Color = None, bg_color: str|int|Color = None,
                 auto_fg: bool = False, blink: bool = False, bold: bool = False,
                 crosslined: bool = False, dim: bool = False,
                 double_underlined: bool = False, inversed: bool = False,
                 italic: bool = False, overlined: bool = False,
                 underlined: bool = False):
        self.fg_color: Color = self._resolve_color(fg_color)
        self.bg_color: Color = self._resolve_color(bg_color)
        self.blink: bool = blink
        self.bold: bool = bold
        self.crosslined: bool = crosslined
        self.dim: bool = dim
        self.double_underlined: bool = double_underlined
        self.inversed: bool = inversed
        self.italic: bool = italic
        self.overlined: bool = overlined
        self.underlined: bool = underlined

        if auto_fg:
            self._pick_fg_for_bg()

    def render(self, text: Any = None) -> str:
        """
        Returns ``text`` with all attributes and colors applied.

        By default uses `SequenceSGR` renderer, that means that output will contain
        ANSI escape sequences.
        """
        from .renderer import DefaultRenderer
        return DefaultRenderer.render(self, text)

    def _pick_fg_for_bg(self):
        if self.bg_color is None or self.bg_color.hex_value is None:
            return

        h, s, v = Color.hex_value_to_hsv_channels(self.bg_color.hex_value)
        if v >= .45:
            self.fg_color = color.RGB_BLACK
        else:
            self.fg_color = color.RGB_WHITE

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
        props_set = [self.fg_color.format_value('fg=') or 'no fg',
                     self.bg_color.format_value('bg=') or 'no bg', ]
        for attr_name in dir(self):
            if not attr_name.startswith('_'):
                attr = getattr(self, attr_name)
                if isinstance(attr, bool) and attr is True:
                    props_set.append(attr_name)

        return self.__class__.__name__ + '[{:s}]'.format(', '.join(props_set))


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
