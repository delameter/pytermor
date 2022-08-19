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

from dataclasses import dataclass, field, InitVar
from typing import Any

from . import color
from .color import Color, ColorRGB, NOOP as NOOP_COLOR


@dataclass
class Style:
    """Create a new ``Style()``.

    Key difference between ``Styles`` and ``Spans`` or ``SGRs`` is that
    ``Styles`` describe colors in RGB format and therefore support output
    rendering in several different formats (see :mod:`.renderer`).

    Both ``fg`` and ``bg`` can be specified as:

    1. :class:`.Color` instance or library preset;
    2. key code -- name of any of aforementioned presets, case-insensitive;
    3. integer color value in hexademical RGB format.
    4. None -- the color will be unset.

    :param fg:          Foreground (i.e., text) color.
    :param bg:          Background color.
    :param inherit:     Parent instance to copy unset properties from.
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
    :param class_name:  Arbitary string used by some renderers, e.g. by ``HtmlRenderer``.

    >>> Style(fg='green', bold=True)
    Style[fg=008000, no bg, bold]
    >>> Style(bg=0x0000ff)
    Style[no fg, bg=0000ff]
    >>> Style(fg=color.IDX_DEEP_SKY_BLUE_1, bg=color.IDX_GREY_93)
    Style[fg=00afff, bg=eeeeee]
    """
    _fg: Color = field(default=None, init=False)
    _bg: Color = field(default=None, init=False)

    def __init__(self, inherit: Style = None, fg: Color|int|str = None,
                 bg: Color|int|str = None, blink: bool = None, bold: bool = None,
                 crosslined: bool = None, dim: bool = None,
                 double_underlined: bool = None, inversed: bool = None,
                 italic: bool = None, overlined: bool = None, underlined: bool = None,
                 class_name: str = None):
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

        if inherit is not None:
            self._clone_from(inherit)

        if self._fg is None:
            self._fg = NOOP_COLOR
        if self._bg is None:
            self._bg = NOOP_COLOR

    def render(self, text: Any = None) -> str:
        """
        Returns ``text`` with all attributes and colors applied.

        By default uses `SequenceSGR` renderer, that means that output will contain
        ANSI escape sequences.
        """
        from .renderer import RendererManager
        return RendererManager.get_default().render(self, text)
    
    def autopick_fg(self) -> Color|None:
        """
        Pick ``fg_color`` depending on ``bg_color`` brightness. Set 4% gray
        or 96% gray as `fg_color` and return it, if ``bg_color`` is defined,
        and do nothing and return None otherwise.

        :return: Suitable foreground color or None.
        """
        if self._bg is None or self._bg.hex_value is None:
            return

        h, s, v = Color.hex_value_to_hsv_channels(self._bg.hex_value)
        if v >= .45:
            self._fg = color.RGB_GRAY_04
        else:
            self._fg = color.RGB_GRAY_96
        # @TODO check if there is a better algorithm,
        #       because current thinks text on #000080 should be black
        return self._fg

    # noinspection PyMethodMayBeStatic
    def _resolve_color(self, arg: str|int|Color, nullable: bool) -> Color|None:
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

        return None if nullable else NOOP_COLOR

    def _clone_from(self, inherit: Style):
        for attr in list(self.__dict__.keys()) + ['_fg', '_bg']:
            inherit_val = getattr(inherit, attr)
            if getattr(self, attr) is None and inherit_val is not None:
                setattr(self, attr, inherit_val)

    def __repr__(self):
        if self._fg is None or self._bg is None:
            return self.__class__.__name__ + '[uninitialized]'
        props_set = [self.fg.format_value('fg=', 'no fg'),
                     self.bg.format_value('bg=', 'no bg'), ]
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

    @fg.setter
    def fg(self, val: str|int|Color):
        self._fg: Color = self._resolve_color(val, nullable=False)

    @bg.setter
    def bg(self, val: str|int|Color):
        self._bg: Color = self._resolve_color(val, nullable=False)


NOOP = Style()

# ---------------------------------------------------------------------------


class Stylesheet:
    """
    whatwhenhow @FIXME
    """
    def __init__(self, default: Style = None):
        self.default: Style = self._opt_arg(default)

    def _opt_arg(self, arg: Style|None):
        return arg or NOOP

    def __repr__(self):
        styles_set = sum(map(lambda a: int(isinstance(a, Style)),
            [getattr(self, attr_name) for attr_name in dir(self) if
             not attr_name.startswith('_')]))
        return self.__class__.__name__ + '[{:d} props]'.format(styles_set)
