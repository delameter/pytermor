# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""
High-level abstraction defining text colors and attributes.
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

    Example usage::

        Style(color.RED).render('Red text')
        Style('green', bold=True).render('Green text')
        Style(bg_color=0x0000ff).render('Blue background')

    :param fg_color:    Foreground (i.e., text) color.
    :param bg_color:    Background color.
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
    def __init__(self, fg_color: Color|str|int = None, bg_color: Color|str|int = None, blink: bool = False,
                 bold: bool = False, crosslined: bool = False, dim: bool = False, double_underlined: bool = False,
                 inversed: bool = False, italic: bool = False, overlined: bool = False, underlined: bool = False):
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

    def render(self, text: Any = None) -> str:
        """
        Returns ``text`` with all attributes and colors applied.

        By default uses `SequenceSGR` renderer, that means that output will contain
        ANSI escape sequences.
        """
        from .renderer import default_renderer
        return default_renderer.render(self, text)

    def _resolve_color(self, arg: Color|int|str|None) -> Color:
        if isinstance(arg, Color):
            return arg

        if isinstance(arg, int):
            return ColorRGB(arg)

        if isinstance(arg, str):
            arg_mapped = arg.upper()
            resolved_color = getattr(color, arg_mapped, None)
            if resolved_color is None:
                raise KeyError(f'Code "{arg}" -> "{arg_mapped}" is not a name of Color preset')
            if not isinstance(resolved_color, Color):
                raise ValueError(f'Attribute is not valid Color: {resolved_color}')
            return resolved_color

        return NOOP_COLOR

    def __repr__(self):
        props_set = [
            f'fg={self.fg_color.hex_value:06x}' if self.fg_color.hex_value else 'no fg',
            f'bg={self.bg_color.hex_value:06x}' if self.bg_color.hex_value else 'no bg',
        ]
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

    @classmethod
    def _opt_arg(cls, arg: Style|None):
        return arg or NOOP

    def __repr__(self):
        props_set = len(list(filter(
            lambda a: isinstance(a, Style),
            [getattr(self, attr_name) for attr_name in dir(self) if not attr_name.startswith('_')]
        )))
        return self.__class__.__name__ + '[{:d} props]'.format(props_set)
