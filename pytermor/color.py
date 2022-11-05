# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""
Yare-yare daze

.. testsetup:: *

    from pytermor.color import *

"""
from __future__ import annotations

import typing as t
from abc import ABCMeta, abstractmethod

from .ansi import SequenceSGR, NOOP_SEQ, HI_COLORS, BG_HI_COLORS, IntCode
from .common import ConflictError, logger


CT = t.TypeVar("CT", "Color16", "Color256", "ColorRGB")


class Index:
    _name_index: t.Dict[str, Color | int] = {}

    @classmethod
    def register(cls, color: Color, aliases: t.List[str] = None):
        for name in [color.name, *(aliases or [])]:
            if not name:
                continue
            name_norm = name.lower()
            if name_norm in cls._name_index.keys():
                raise ConflictError(f"Color '{name_norm}' (<- '{name}') already exists")
            cls._name_index[name_norm] = color

    @classmethod
    def register_virtual(cls, hex_value: int, name: str):
        """

        :param hex_value:
        :param name:
        :return:
        """
        name_norm = name.lower()
        if name_norm in cls._name_index.keys():
            raise ConflictError(f"Color '{name_norm}' (<- '{name}') already exists")
        cls._name_index[name_norm] = hex_value

    @classmethod
    def resolve(cls, name: str) -> Color:
        """
        Case-insensitive search through registry contents.

        :param name:      name of the color to look up for.
        :raises KeyError: if no color with specified name is registered.
        :returns:         `Color` instance.
        """
        name_norm = name.lower()
        if (color := cls._name_index.get(name_norm)) is None:
            raise KeyError(f"Color '{name_norm}' (<- '{name}') does not exist")
        if isinstance(color, Color):
            return color
        return ColorRGB(color)


class Color(metaclass=ABCMeta):
    """
    Abstract superclass for other ``Colors``.
    """

    _index: Index = Index()
    _map: t.Dict[int, t.Tuple[CT, int, int, int]]  # {code: (Color, r, g, b)}
    _approx_query_cache: t.Dict[int, CT]

    @classmethod
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_map"):
            cls._map = dict()
        if not hasattr(cls, "_approx_query_cache"):
            cls._approx_query_cache = dict()
        return super().__new__(cls)

    def __init__(self, hex_value: int, name: str = None):
        self._hex_value: int = hex_value
        self._name: str | None = name

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._hex_value == other._hex_value

    @abstractmethod
    def to_sgr(self, bg: bool, bound: t.Type[Color] = None) -> SequenceSGR:
        raise NotImplementedError

    @abstractmethod
    def to_tmux(self, bg: bool) -> str:
        raise NotImplementedError

    def to_hsv(self) -> t.Tuple[float, float, float]:
        return self.hex_to_hsv(self._hex_value)

    def to_rgb(self) -> t.Tuple[int, int, int]:
        return self.hex_to_rgb(self._hex_value)

    def format_value(self, prefix: str = "0x") -> str:
        """ """
        return f"{prefix:s}{self._hex_value:06x}"

    @property
    def hex_value(self) -> int:
        """ """
        return self._hex_value

    @property
    def name(self) -> str | None:
        """ """
        return self._name

    @classmethod
    def find_closest(cls: t.Type[CT], hex_value: int) -> CT:
        """
        Search for color nearest to ``hex_value`` and return it. Is used to find
        applicable color alternatives if user's terminal is incapable of operating
        in more advanced mode.

        :param hex_value: Color RGB value.
        :return: Nearest to ``hex_value`` instance of ``Color`` or found. Type depends
                 on class of the method.
        """
        if hex_value in cls._approx_query_cache.keys():
            return cls._approx_query_cache.get(hex_value)

        closest = cls._get_map_sorted_by_dist(hex_value)[0][0]
        cls._approx_query_cache[hex_value] = closest
        return closest

    @classmethod
    def approximate(cls: t.Type[CT], hex_value: int, max_results: int = 1) -> t.List[CT]:
        """
        Search for colors nearest to ``hex_value`` and return the first
        ``<max_results>`` of them.

        :param hex_value:      Color RGB value.
        :param max_results:    Maximum amount of values to return.
        :return: Closest `Color` instance(s) found, sorted by color distance
                 descending, i.e., 0-th element is the closest to the input value.
        """
        sorted_result = cls._get_map_sorted_by_dist(hex_value)
        return [r[0] for r in sorted_result[:max_results]]

    @classmethod
    def _get_map_sorted_by_dist(
        cls: t.Type[CT], hex_value: int
    ) -> t.List[t.Tuple[CT, float]]:
        """
        Iterate the registered colors table and compute the euclidean distance
        from argument to each color of the palette. Sort the results and return them.

            sRGB euclidean distance
            https://en.wikipedia.org/wiki/Color_difference#sRGB
            https://stackoverflow.com/a/35114586/5834973

        .. todo :: rewrite using HSV distance?

        :param hex_value:
        :return:
        """
        input_r, input_g, input_b = cls.hex_to_rgb(hex_value)
        result: t.List[t.Tuple[CT, float]] = list()

        for _, (map_color, map_r, map_g, map_b) in cls._map.items():
            distance_sq: float = (
                pow(map_r - input_r, 2)
                + pow(map_g - input_g, 2)
                + pow(map_b - input_b, 2)
            )
            result.append((map_color, distance_sq))

        return sorted(result, key=lambda r: r[1])

    @classmethod
    def find_by_code(cls: t.Type[CT], code: int) -> CT:
        try:
            if color := cls._map.get(code):
                return color[0]
            raise KeyError(f"Color #{code} does not exist")
        except AttributeError as e:
            raise RuntimeError(
                "Code map does not exist. Use concrete class, e.g.: Color16.find_by_code()"
            ) from e

    @classmethod
    def _add_to_map(cls: t.Type[CT], color: CT, code: int = None):
        if code is None:
            code = len(cls._map)

        if code in cls._map.keys():
            existing = cls._map.get(code)[0]
            if existing != color:
                logger.warning(f"Color #{code} already exists ({existing}), skipping")
                return

        r, g, b = color.to_rgb()
        cls._map[code] = (color, r, g, b)

    @staticmethod
    def hex_to_hsv(hex_value: int) -> t.Tuple[float, float, float]:
        """
        Transforms ``hex_value`` in ``0xffffff`` format into tuple of three numbers
        corresponding to *hue*, *saturation* and *value* channel values respectively.
        *Hue* is within [0, 359] range, *saturation* and *value* are within [0; 1] range.
        """
        if not isinstance(hex_value, int):
            raise TypeError(f"Argument type should be 'int', got: {type(hex_value)}")

        # fmt: off
        # https://en.wikipedia.org/wiki/HSL_and_HSV#From_RGB

        r, g, b = Color.hex_to_rgb(hex_value)
        rn, gn, bn = r / 255, g / 255, b / 255
        vmax = max(rn, gn, bn)
        vmin = min(rn, gn, bn)
        c = vmax - vmin
        v = vmax

        h = 0
        if c == 0:     pass
        elif v == rn:  h = 60 * (0 + (gn - bn) / c)
        elif v == gn:  h = 60 * (2 + (bn - rn) / c)
        elif v == bn:  h = 60 * (4 + (rn - gn) / c)

        if v == 0:     s = 0
        else:          s = c / v

        if h < 0:      h += 360

        return h, s, v
        # fmt: on

    @staticmethod
    def hex_to_rgb(hex_value: int) -> t.Tuple[int, int, int]:
        """
        Transforms ``hex_value`` in ``0xffffff`` format into tuple of three
        integers corresponding to *red*, *blue* and *green* channel value
        respectively. Values are within [0; 255] range.

        >>> Color.hex_to_rgb(0x80ff80)
        (128, 255, 128)
        >>> Color.hex_to_rgb(0x000001)
        (0, 0, 1)
        """
        if not isinstance(hex_value, int):
            raise TypeError(f"Argument type should be 'int', got: {type(hex_value)}")

        return (
            (hex_value & 0xFF0000) >> 16,
            (hex_value & 0xFF00) >> 8,
            (hex_value & 0xFF),
        )

    @staticmethod
    def rgb_to_hex(r: int, g: int, b: int) -> int:
        """ """
        return (r << 16) + (g << 8) + b


class Color16(Color):
    def __init__(
        self,
        hex_value: int,
        code_fg: int,
        code_bg: int,
        name: str = None,
        aliases: t.List[str] = None,
        add_to_map: bool = False,
    ):
        super().__init__(hex_value, name)
        self._code_fg: int = code_fg
        self._code_bg: int = code_bg

        self._index.register(self, aliases)
        if add_to_map:
            self._add_to_map(self, self._code_fg)

    def to_sgr(self, bg: bool, bound: t.Type[Color] = None) -> SequenceSGR:
        if bg:
            return SequenceSGR(self._code_bg)
        return SequenceSGR(self._code_fg)

    def to_tmux(self, bg: bool) -> str:
        if self._name is None:
            raise ValueError("Translation to tmux format failed: color name required")
        code = self._code_bg if bg else self._code_fg
        is_hi = code in HI_COLORS or code in BG_HI_COLORS
        tmux_name = ("bright" if is_hi else "") + self._name.lower()
        return tmux_name

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return (
            self._hex_value == other._hex_value
            and self._code_bg == other._code_bg
            and self._code_fg == other._code_fg
        )

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"[fg={self._code_fg!r}, bg={self._code_bg!r}, {self.format_value()}]"
        )


class Color256(Color):
    def __init__(
        self,
        hex_value: int,
        code: int,
        name: str = None,
        add_to_map: bool = False,
        color16_equiv: int = None,
    ):
        super().__init__(hex_value, name)
        self._code: int | None = code

        self._color16_equiv: Color16 | None = None
        if color16_equiv:
            self._color16_equiv = Color16.find_by_code(color16_equiv)

        if not self._color16_equiv:
            self._index.register(self)
        if add_to_map:
            self._add_to_map(self, self._code)

    def to_sgr(self, bg: bool, bound: t.Type[Color] = None) -> SequenceSGR:
        if bound is ColorRGB:
            return SequenceSGR.init_color_rgb(*self.to_rgb())

        if bound is Color256 or bound is None:
            return SequenceSGR.init_color_256(self._code, bg)

        if self._color16_equiv:
            return self._color16_equiv.to_sgr(bg, bound)

        return Color16.find_closest(self.hex_value).to_sgr(bg, bound)

    def to_tmux(self, bg: bool) -> str:
        return f"colour{self._code}"

    @property
    def code(self) -> int:
        return self._code

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._hex_value == other._hex_value and self._code == other._code

    def __repr__(self):
        return f"{self.__class__.__name__}[code={self._code}, {self.format_value()}]"


class ColorRGB(Color):
    def __init__(self, hex_value: int, name: str = None, add_to_map: bool = False):
        super().__init__(hex_value, name)

        self._index.register(self)
        if add_to_map:
            self._add_to_map(self)

    def to_sgr(self, bg: bool, bound: t.Type[Color] = None) -> SequenceSGR:
        if bound is ColorRGB or bound is None:
            return SequenceSGR.init_color_rgb(*self.to_rgb(), bg)

        return bound.find_closest(self._hex_value).to_sgr(bg, bound)

    def to_tmux(self, bg: bool) -> str:
        return self.format_value("#")

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._hex_value == other._hex_value

    def __repr__(self):
        return f"{self.__class__.__name__}[{self.format_value()}]"


class _NoopColor(Color):
    def __init__(self):
        super().__init__(0)

    def to_sgr(self, bg: bool, bound: t.Type[Color] = None) -> SequenceSGR:
        return NOOP_SEQ

    def to_tmux(self, bg: bool) -> str:
        return ""

    @property
    def hex_value(self) -> int:
        raise ValueError("No color for NO-OP instance")

    def format_value(self, prefix: str = "0x") -> str:
        return "NOP"


NOOP_COLOR = _NoopColor()
"""
Special `Color` instance always rendering into empty string.
"""


# fmt: off
BLACK      = Color16(0x000000, IntCode.BLACK,      IntCode.BG_BLACK,      'black',     None,              True)
RED        = Color16(0x800000, IntCode.RED,        IntCode.BG_RED,        'red',       None,              True)
GREEN      = Color16(0x008000, IntCode.GREEN,      IntCode.BG_GREEN,      'green',     None,              True)
YELLOW     = Color16(0x808000, IntCode.YELLOW,     IntCode.BG_YELLOW,     'yellow',    None,              True)
BLUE       = Color16(0x000080, IntCode.BLUE,       IntCode.BG_BLUE,       'blue',      None,              True)
MAGENTA    = Color16(0x800080, IntCode.MAGENTA,    IntCode.BG_MAGENTA,    'magenta',   None,              True)
CYAN       = Color16(0x008080, IntCode.CYAN,       IntCode.BG_CYAN,       'cyan',      None,              True)
WHITE      = Color16(0xc0c0c0, IntCode.WHITE,      IntCode.BG_WHITE,      'white',     None,              True)
GRAY       = Color16(0x808080, IntCode.GRAY,       IntCode.BG_GRAY,       'gray',      ['grey'],          True)
HI_RED     = Color16(0xff0000, IntCode.HI_RED,     IntCode.BG_HI_RED,     'hired',     ['brightred'],     True)
HI_GREEN   = Color16(0x00ff00, IntCode.HI_GREEN,   IntCode.BG_HI_GREEN,   'higreen',   ['brightgreen'],   True)
HI_YELLOW  = Color16(0xffff00, IntCode.HI_YELLOW,  IntCode.BG_HI_YELLOW,  'hiyellow',  ['brightyellow'],  True)
HI_BLUE    = Color16(0x0000ff, IntCode.HI_BLUE,    IntCode.BG_HI_BLUE,    'hiblue',    ['brightblue'],    True)
HI_MAGENTA = Color16(0xff00ff, IntCode.HI_MAGENTA, IntCode.BG_HI_MAGENTA, 'himagenta', ['brightmagenta'], True)
HI_CYAN    = Color16(0x00ffff, IntCode.HI_CYAN,    IntCode.BG_HI_CYAN,    'hicyan',    ['brightcyan'],    True)
HI_WHITE   = Color16(0xffffff, IntCode.HI_WHITE,   IntCode.BG_HI_WHITE,   'hiwhite',   ['brightwhite'],   True)
# fmt: on
