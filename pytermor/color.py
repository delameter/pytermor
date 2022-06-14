# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

from abc import abstractmethod, ABCMeta
from typing import Dict, Tuple

from . import sequence
from .sequence import SequenceSGR, color_indexed, color_rgb


class Color(metaclass=ABCMeta):
    _type_color_map: Dict[type, Dict[int, Color]] = dict()

    @staticmethod
    def hex_value_to_channels(hex_value: int) -> Tuple[int, int, int]:
        return (hex_value & 0xFF0000) >> 16, (hex_value & 0xFF00) >> 8, (hex_value & 0xFF)

    @classmethod
    def _get_hex_color_map(cls):
        return cls._type_color_map[cls]

    @classmethod
    def find_closest(cls, hex_value: int) -> Color:
        hex_color_map = cls._get_hex_color_map()
        if hex_value in hex_color_map.keys():
            return hex_color_map.get(hex_value)

        input_r, input_g, input_b = cls.hex_value_to_channels(hex_value)
        min_distance_sq = pow(255, 2) * 3
        closest = None
        for map_hex, map_color in hex_color_map.items():
            # sRGB euclidean distance
            # https://en.wikipedia.org/wiki/Color_difference#sRGB
            map_r, map_g, map_b = cls.hex_value_to_channels(map_hex)
            distance_sq = pow(map_r - input_r, 2) + pow(map_g - input_g, 2) + pow(map_b - input_b, 2)

            if distance_sq < min_distance_sq:
                min_distance_sq = distance_sq
                closest = map_color

        if closest is None:
            raise RuntimeError(f'There are no registred {cls.__name__} instances')
        return closest

    def __init__(self, hex_value: int = None):
        self._hex_value: int | None = hex_value

        if type(self) not in self._type_color_map:
            self._type_color_map[type(self)] = dict()

        if hex_value not in self._type_color_map[type(self)].keys():
            self._type_color_map[type(self)][hex_value] = self

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._hex_value == other._hex_value

    @abstractmethod
    def to_sgr_default(self, bg: bool) -> SequenceSGR: raise NotImplementedError

    @abstractmethod
    def to_sgr_indexed(self, bg: bool) -> SequenceSGR: raise NotImplementedError

    @abstractmethod
    def to_sgr_rgb(self, bg: bool) -> SequenceSGR: raise NotImplementedError

    @property
    def hex_value(self) -> int|None:
        return self._hex_value


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

    def to_sgr_default(self, bg: bool) -> SequenceSGR:
        if bg:
            return self._seq_bg
        return self._seq_fg

    def to_sgr_indexed(self, bg: bool) -> SequenceSGR:
        return ColorRGB(self.hex_value).to_sgr_indexed(bg=bg)

    def to_sgr_rgb(self, bg: bool) -> SequenceSGR:
        return ColorRGB(self.hex_value).to_sgr_rgb(bg=bg)


class ColorIndexed(Color):
    def __init__(self, hex_value: int, code: int):
        super().__init__(hex_value)
        self._code = code

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._hex_value == other._hex_value and \
               self._code == other._code

    def to_sgr_default(self, bg: bool) -> SequenceSGR:
        return ColorRGB(self.hex_value).to_sgr_default(bg=bg)

    def to_sgr_indexed(self, bg: bool) -> SequenceSGR:
        return color_indexed(self._code, bg=bg)

    def to_sgr_rgb(self, bg: bool) -> SequenceSGR:
        return ColorRGB(self.hex_value).to_sgr_rgb(bg=bg)


class ColorRGB(Color):
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
        value = '[]'
        if self._hex_value is not None:
            value = f'[0x{self._hex_value:06x}]'
        return self.__class__.__name__ + value


# -----------------------------------------------------------------------------
# Color presets
# -----------------------------------------------------------------------------

NOOP = ColorRGB()

WHITE = ColorRGB(0xffffff)
RED = ColorDefault(0x800000, sequence.RED, sequence.BG_RED)
GREEN = ColorDefault(0x008000, sequence.GREEN, sequence.BG_GREEN)
YELLOW = ColorDefault(0x808000, sequence.YELLOW, sequence.BG_YELLOW)
HI_RED = ColorIndexed(0xff0000, 9)
LIGHT_GREEN = ColorIndexed(0x87ff87, 119)
BLACK = ColorDefault(0x000000, sequence.BLACK, sequence.BG_BLACK)
