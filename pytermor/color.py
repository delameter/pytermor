# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

from abc import abstractmethod, ABCMeta
from typing import Dict, Tuple, Generic, TypeVar

from . import sequence
from .sequence import SequenceSGR, color_indexed, color_rgb


class Color(metaclass=ABCMeta):
    _color_map: _ColorMap[Color]

    @staticmethod
    def hex_value_to_channels(hex_value: int) -> Tuple[int, int, int]:
        return ((hex_value & 0xff0000) >> 16,
                (hex_value & 0xff00) >> 8,
                (hex_value & 0xff))

    @classmethod
    def _init_color_map(cls):
        if not hasattr(cls, '_color_map'):
            cls._color_map = _ColorMap[cls.__class__]()

    def __init__(self, hex_value: int = None):
        self._hex_value: int | None = hex_value

        self._init_color_map()
        self._color_map.add_exact(self)

    @abstractmethod
    def to_sgr_default(self, bg: bool) -> SequenceSGR: raise NotImplementedError

    @abstractmethod
    def to_sgr_indexed(self, bg: bool) -> SequenceSGR: raise NotImplementedError

    @abstractmethod
    def to_sgr_rgb(self, bg: bool) -> SequenceSGR: raise NotImplementedError

    @property
    def hex_value(self) -> int|None:
        return self._hex_value

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._hex_value == other._hex_value

    def _repr_hex_value(self):  # pragma: no cover
        if self._hex_value is not None:
            return f'0x{self._hex_value:06x}'
        return ''


class ColorDefault(Color):
    def __init__(self, hex_value: int, seq_fg: SequenceSGR, seq_bg: SequenceSGR):
        super().__init__(hex_value)
        self._seq_fg = seq_fg
        self._seq_bg = seq_bg

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._hex_value == other._hex_value and \
               self._seq_bg == other._seq_bg and \
               self._seq_fg == other._seq_fg

    @classmethod
    def find_closest(cls, hex_value: int) -> ColorDefault:
        cls._init_color_map()
        return cls._color_map.find_closest(hex_value)

    def to_sgr_default(self, bg: bool) -> SequenceSGR:
        if bg:
            return self._seq_bg
        return self._seq_fg

    def to_sgr_indexed(self, bg: bool) -> SequenceSGR:
        return ColorRGB(self.hex_value).to_sgr_indexed(bg=bg)

    def to_sgr_rgb(self, bg: bool) -> SequenceSGR:
        return ColorRGB(self.hex_value).to_sgr_rgb(bg=bg)

    def __repr__(self):
        return f'{self.__class__.__name__}[fg={self._seq_fg!r}, bg={self._seq_bg!r}, {self._repr_hex_value()}]'


class ColorIndexed(Color):
    def __init__(self, hex_value: int, code: int):
        super().__init__(hex_value)
        self._code = code

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._hex_value == other._hex_value and \
               self._code == other._code

    @classmethod
    def find_closest(cls, hex_value: int) -> ColorIndexed:
        cls._init_color_map()
        return cls._color_map.find_closest(hex_value)

    def to_sgr_default(self, bg: bool) -> SequenceSGR:
        return ColorRGB(self.hex_value).to_sgr_default(bg=bg)

    def to_sgr_indexed(self, bg: bool) -> SequenceSGR:
        return color_indexed(self._code, bg=bg)

    def to_sgr_rgb(self, bg: bool) -> SequenceSGR:
        return ColorRGB(self.hex_value).to_sgr_rgb(bg=bg)

    def __repr__(self):
        return f'{self.__class__.__name__}[{self._code}, {self._repr_hex_value()}]'


class ColorRGB(Color):
    @classmethod
    def find_closest(cls, hex_value: int) -> ColorRGB:
        cls._init_color_map()
        return cls._color_map.find_closest(hex_value)

    def to_sgr_default(self, bg: bool) -> SequenceSGR:
        if not self._hex_value:
            return sequence.NOOP
        return ColorDefault.find_closest(self._hex_value).to_sgr_default(bg=bg)

    def to_sgr_indexed(self, bg: bool) -> SequenceSGR:
        if not self._hex_value:
            return sequence.NOOP
        return ColorIndexed.find_closest(self._hex_value).to_sgr_indexed(bg=bg)

    def to_sgr_rgb(self, bg: bool) -> SequenceSGR:
        if not self._hex_value:
            return sequence.NOOP
        return color_rgb(*self.hex_value_to_channels(self._hex_value), bg=bg)

    def __repr__(self):
        return f'{self.__class__.__name__}[{self._repr_hex_value()}]'


TypeColor = TypeVar('TypeColor', 'ColorDefault', 'ColorIndexed', 'ColorRGB')
""" Any non-abstract Color type for ColorMap generic. """


class _ColorMap(Generic[TypeColor]):
    """
    Class containing a dictionary of registred Colors indexed by hex code as well as cached
    nearest color search results to avoid unnecessary instance copies and repeats of algorithm invocation.
    """
    def __init__(self):
        self._exact_color_map: Dict[int, TypeColor] = dict()
        self._approximate_cache: Dict[int, TypeColor] = dict()

    def add_exact(self, color: TypeColor):
        self._approximate_cache.clear()

        if color.hex_value is not None:
            if color.hex_value not in self._exact_color_map.keys():
                self._exact_color_map[color.hex_value] = color

    def find_closest(self, hex_value: int) -> TypeColor:
        if hex_value in self._exact_color_map.keys():
            return self._exact_color_map.get(hex_value)
        if hex_value in self._approximate_cache.keys():
            return self._approximate_cache.get(hex_value)
        if len(self._approximate_cache) == 0:
            self._approximate_cache = self._exact_color_map.copy()

        input_r, input_g, input_b = Color.hex_value_to_channels(hex_value)
        min_distance_sq = pow(255, 2) * 3 + 1
        closest = None
        for cached_hex, cached_color in self._approximate_cache.items():
            # sRGB euclidean distance
            # https://en.wikipedia.org/wiki/Color_difference#sRGB
            map_r, map_g, map_b = Color.hex_value_to_channels(cached_hex)
            distance_sq = pow(map_r - input_r, 2) + pow(map_g - input_g, 2) + pow(map_b - input_b, 2)

            if distance_sq < min_distance_sq:
                min_distance_sq = distance_sq
                closest = cached_color

        if closest is None:
            raise RuntimeError(f'There are no registred {self!r} instances')

        self._approximate_cache[hex_value] = closest
        return closest


# -----------------------------------------------------------------------------
# Color presets
# -----------------------------------------------------------------------------

NOOP = ColorRGB()
"""
Special instance of `Color` class always rendering into empty string.
"""

BLACK =   ColorDefault(0x000000, sequence.BLACK,   sequence.BG_BLACK)
RED =     ColorDefault(0x800000, sequence.RED,     sequence.BG_RED)
GREEN =   ColorDefault(0x008000, sequence.GREEN,   sequence.BG_GREEN)
YELLOW =  ColorDefault(0x808000, sequence.YELLOW,  sequence.BG_YELLOW)
BLUE =    ColorDefault(0x000080, sequence.BLUE,    sequence.BG_BLUE)
MAGENTA = ColorDefault(0x800080, sequence.MAGENTA, sequence.BG_MAGENTA)
CYAN =    ColorDefault(0x008080, sequence.CYAN,    sequence.BG_CYAN)
WHITE =   ColorDefault(0xc0c0c0, sequence.WHITE,   sequence.BG_WHITE)
GRAY =    ColorDefault(0x808080, sequence.GRAY,    sequence.BG_GRAY)
HI_RED =     ColorDefault(0xff0000, sequence.HI_RED,     sequence.BG_HI_RED)
HI_GREEN =   ColorDefault(0x00ff00, sequence.HI_GREEN,   sequence.BG_HI_GREEN)
HI_YELLOW =  ColorDefault(0xffff00, sequence.HI_YELLOW,  sequence.BG_HI_YELLOW)
HI_BLUE =    ColorDefault(0x0000ff, sequence.HI_BLUE,    sequence.BG_HI_BLUE)
HI_MAGENTA = ColorDefault(0xff00ff, sequence.HI_MAGENTA, sequence.BG_HI_MAGENTA)
HI_CYAN =    ColorDefault(0x00ffff, sequence.HI_CYAN,    sequence.BG_HI_CYAN)
HI_WHITE =   ColorDefault(0xffffff, sequence.HI_WHITE,   sequence.BG_HI_WHITE)
