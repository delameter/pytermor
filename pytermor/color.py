# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""
@TODO

@TODO black/white text selection depending on bg

.. testsetup:: *

    from pytermor.color import Color, ColorDefault, ColorIndexed, ColorRGB
"""
from __future__ import annotations

from abc import abstractmethod, ABCMeta
from typing import Dict, Tuple, Generic, TypeVar, List, Optional

from . import sequence, intcode
from .exception import LogicError
from .sequence import SequenceSGR, color_indexed, color_rgb


class Color(metaclass=ABCMeta):
    """
    Abstract superclass for other ``Colors``.
    """
    _approx_initialized: bool = False
    _approx: Approximator[Color]

    def __init__(self, hex_value: int = None):
        self._hex_value: int | None = hex_value

        self._init_approx()
        self._approx.add_to_map(self)

    @staticmethod
    def hex_value_to_hsv_channels(hex_value: int) -> Tuple[int, float, float]:
        """
        Transforms ``hex_value`` in ``0xffffff`` format into tuple of three
        numbers corresponding to *hue*, *saturation* and *value* channel values
        respectively. *Hue* is within [0, 359] range, *saturation* and *value* are
        within [0; 1] range.
        """
        if not isinstance(hex_value, int):
            raise TypeError(f"Argument type should be 'int', got: {type(hex_value)}")

        # https://en.wikipedia.org/wiki/HSL_and_HSV#From_RGB
        r, g, b = Color.hex_value_to_rgb_channels(hex_value)
        rn, gn, bn = r/255, g/255, b/255

        vmax = max(rn, gn, bn)
        vmin = min(rn, gn, bn)
        c = vmax - vmin
        v = vmax

        if c == 0:
            h = 0
        elif v == rn:
            h = 60 * (0 + (gn - bn)/c)
        elif v == gn:
            h = 60 * (2 + (bn - rn)/c)
        elif v == bn:
            h = 60 * (4 + (rn - gn)/c)
        else:
            raise LogicError('Impossible if-branch, algorithm is implemented incorrectly')

        if v == 0:
            s = 0
        else:
            s = c/v

        return h, s, v

    @staticmethod
    def hex_value_to_rgb_channels(hex_value: int) -> Tuple[int, int, int]:
        """
        Transforms ``hex_value`` in ``0xffffff`` format into tuple of three
        integers corresponding to *red*, *blue* and *green* channel value
        respectively. Values are within [0; 255] range.

        >>> Color.hex_value_to_rgb_channels(0x80ff80)
        (128, 255, 128)
        >>> Color.hex_value_to_rgb_channels(0x000001)
        (0, 0, 1)
        """
        if not isinstance(hex_value, int):
            raise TypeError(f"Argument type should be 'int', got: {type(hex_value)}")

        return ((hex_value & 0xff0000) >> 16,
                (hex_value & 0xff00) >> 8,
                (hex_value & 0xff))

    @classmethod
    def _init_approx(cls):
        if cls._approx_initialized:
            return
        cls._approx_initialized = True
        cls._approx = Approximator[cls.__class__](cls)

    @classmethod
    @abstractmethod
    def get_default(cls) -> Color:
        """
        :return: Fallback instance of `Color` inheritor (if registries are empty).
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def find_closest(cls, hex_value: int) -> Color:
        """
        Wrapper for `Approximator.find_closest()`.

        :param hex_value: Integer color value in ``0xffffff`` format.
        :return:          Nearest found color of specified type.
        """
        raise NotImplementedError

    @abstractmethod
    def to_sgr(self, bg: bool = False) -> SequenceSGR:
        raise NotImplementedError

    @property
    def hex_value(self) -> int | None:
        return self._hex_value

    def format_value(self, prefix: str|None = '0x', noop_str: str = '^') -> str:
        if self._hex_value is None:
            return noop_str
        return f'{prefix or "":s}{self._hex_value:06x}'


class ColorDefault(Color):
    def __init__(self, hex_value: int, code_fg: int, code_bg: int):
        self._code_fg: int = code_fg
        self._code_bg: int = code_bg
        super().__init__(hex_value)

    @classmethod
    def get_default(cls) -> ColorDefault:
        return BLACK

    @classmethod
    def find_closest(cls, hex_value: int) -> ColorDefault:
        """
        Wrapper for `Approximator.find_closest()`.

        .. attention::
           Use this method only if you know what you are doing. *Default* mode
           colors may vary in a huge range depending on user terminal setup
           (colors even can have exactly the opposite value of what's listed in
           preset list). Much more reliable and predictable approach is to use
           `ColorIndexed.find_closest` instead.

        :param hex_value: Integer color value in ``0xffffff`` format.
        :return:          Nearest found `ColorDefault` instance.

        >>> ColorDefault.find_closest(0x660000)
        ColorDefault[fg=31, bg=41, 0x800000]
        """
        return cls._approx.find_closest(hex_value)

    def to_sgr(self, bg: bool = False) -> SequenceSGR:
        if bg:
            return SequenceSGR(self._code_bg)
        return SequenceSGR(self._code_fg)

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return (self._hex_value == other._hex_value
                and self._code_bg == other._code_bg
                and self._code_fg == other._code_fg)

    def __repr__(self):
        return f'{self.__class__.__name__}[' \
               f'fg={self._code_fg!r}, ' \
               f'bg={self._code_bg!r}, ' \
               f'{self.format_value()}]'


class ColorIndexed(Color):
    def __init__(self, hex_value: int, code: int):
        self._code = code
        super().__init__(hex_value)

    @classmethod
    def get_default(cls) -> ColorIndexed:
        return IDX_BLACK

    @classmethod
    def find_closest(cls, hex_value: int) -> ColorIndexed:
        """
        Wrapper for `Approximator.find_closest()`.

        .. note::

           Approximation algorithm ignores colors 000-015 from the *indexed*
           palette and will return colors with int codes in 016-255 range only.
           The reason for this is the same as for discouraging the usage of
           `ColorDefault` method version -- because aforementioned colors actually
           depend on end-user terminal settings and the final result can be
           differ drastically from what's the developer imagined.

        :param hex_value: Integer color value in ``0xffffff`` format.
        :return:          Nearest found `ColorIndexed` instance.

        >>> ColorIndexed.find_closest(0xd9dbdb)
        ColorIndexed[code=253, 0xdadada]
        """
        return cls._approx.find_closest(hex_value)

    def to_sgr(self, bg: bool = False) -> SequenceSGR:
        return color_indexed(self._code, bg=bg)

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return (self._hex_value == other._hex_value
                and self._code == other._code)

    def __repr__(self):
        return f'{self.__class__.__name__}[' \
               f'code={self._code}, ' \
               f'{self.format_value()}]'


class ColorRGB(Color):
    @classmethod
    def get_default(cls) -> ColorRGB:
        return RGB_BLACK

    @classmethod
    def find_closest(cls, hex_value: int) -> ColorRGB:
        """
        In case of `ColorRGB` we suppose that user's terminal is not limited to a
        palette, therefore RGB-type color map works by simplified algorithm --
        it just checks if instance with same hex value was already created
        and returns it if that's the case, or returns a brand new instance
        with specified color value otherwise.

        :param hex_value: Integer color value in ``0xffffff`` format.
        :return:          Existing `ColorRGB` instance or newly created one.

        >>> existing_color1 = ColorRGB(0x660000)
        >>> existing_color2 = ColorRGB(0x660000)
        >>> existing_color1 == existing_color2
        True
        >>> existing_color1 is existing_color2  # different instances
        False
        >>> existing_color1 == ColorRGB.find_closest(0x660000)
        True
        >>> existing_color1 is ColorRGB.find_closest(0x660000)  # same instance
        True
        """

        if exact := cls._approx.get_exact(hex_value):
            return exact
        return ColorRGB(hex_value)

    def to_sgr(self, bg: bool = False) -> SequenceSGR:
        if not self._hex_value:
            return sequence.NOOP
        return color_rgb(*self.hex_value_to_rgb_channels(self._hex_value), bg=bg)

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._hex_value == other._hex_value

    def __repr__(self):
        return f'{self.__class__.__name__}[{self.format_value()}]'


# -----------------------------------------------------------------------------

TypeColor = TypeVar('TypeColor', 'ColorDefault', 'ColorIndexed', 'ColorRGB')
""" Any non-abstract `Color` type. """


class Approximator(Generic[TypeColor]):
    """
    Class contains a dictionary of registred `Colors <Color>` indexed by hex code
    along with cached nearest color search results to avoid unnecessary instance
    copies and search repeating.
    """

    def __init__(self, parent_type: TypeColor):
        """
        Called in `Color`-type class constructors. Each `Color` type should have
        class variable with instance of `Approximator` and create it by itself if it's
        not present.

        :param parent_type: Parent `Color` type.
        """
        self._parent_type: TypeColor = parent_type
        self._lookup_table: Dict[int, TypeColor] = dict()
        self._approximation_cache: Dict[int, TypeColor] = dict()

    def add_to_map(self, color: TypeColor):
        """
        Called in `Color`-type class constructors. Add a new element in color
        lookup table if it wasn't there, and then drop cached search results
        as they are most probably useless after registering a new color (i.e.
        now there will be better result for at least one cached value).

        :param color: `Color` instance being created.
        """

        if color.hex_value is not None:
            if color.hex_value not in self._lookup_table.keys():
                self._approximation_cache.clear()
                self._lookup_table[color.hex_value] = color

    def get_exact(self, hex_value: int) -> Optional[TypeColor]:
        """
        Public interface for searching exact values in the *lookup table*, or
        global registry of created instances of specified ``Color`` class.

        :param hex_value: Color value in RGB format.
        :return:          ``Color`` with specified value. Type is equal
                          to type of the parent of selected color map.
        """
        return self._lookup_table.get(hex_value, None)

    def find_closest(self, hex_value: int) -> TypeColor:
        """
        Search for nearest to ``hex_value`` registered color. Is used by
        `SGRRenderer` to find supported color alternatives in case user's terminal is
        incapable of operating in better mode.

        :param hex_value: Color value in RGB format.
        :return:          Nearest to ``hex_value`` registered ``Color``. Type is equal
                          to type of the parent of selected color map.
                          If no colors of required type were created (table and cache
                          are empty), invokes `get_default() <Color.get_default()>`
                          ``Color`` method.
        """
        if hex_value in self._approximation_cache.keys():
            return self._approximation_cache.get(hex_value)

        if len(self._approximation_cache) == 0:  # there was on-addition cache reset
            self._approximation_cache = self._lookup_table.copy()

        if len(self._approximation_cache) == 0:
            # rare case when `find_closest` classmethod is called from `Color` type
            # without registered instances, but it's still possible (for example,
            # developer can interrupt preset creation or just comment it out).
            # return the first available instance of the required type:
            return self._parent_type.get_default()

        closest = self.approximate(hex_value)[0]
        self._approximation_cache[hex_value] = closest
        return closest

    def approximate(self, hex_value: int, max_results: int = 1) -> List[TypeColor]:
        """
        Core color approximation method. Iterate the registred SGRs table, or
        *lookup table*, containing parents' instances, and compute the euclidean
        distance from argument to each color of the palette. Sort the results and
        return the first ``<max_results>`` of them.

        .. note::
            It's not guaranteed that this method will **always** succeed in
            searching (the result list can be empty). Consider using `find_closest`
            instead, if you really want to be sure that at least some color will
            be returned. Another option is to use special "color" named `NOOP`.

        :param hex_value:   Color RGB value.
        :param max_results: Maximum amount of values to return.
        :return:            Closest `Color` instances found, sorted by color
                            distance descending (i.e. 0th element is always the
                            closest to the input value).
        """
        input_r, input_g, input_b = Color.hex_value_to_rgb_channels(hex_value)
        result: Dict[int, float] = dict()

        for cached_hex, cached_color in self._lookup_table.items():
            # sRGB euclidean distance @TODO rewrite using HSV distance?
            # https://en.wikipedia.org/wiki/Color_difference#sRGB
            # https://stackoverflow.com/a/35114586/5834973
            map_r, map_g, map_b = Color.hex_value_to_rgb_channels(cached_hex)
            distance_sq = (pow(map_r - input_r, 2) + pow(map_g - input_g, 2) + pow(
                map_b - input_b, 2))

            result[cached_color.hex_value] = distance_sq

        if len(result) == 0:
            # normally it's impossible to get here; this exception almost
            # certainly means that there is a bug somewhere in this class.
            raise LogicError(f'There are '  # pragma: no cover
                             f'no registred {self._parent_type.__name__} '
                             f'instances')

        sorted_result = sorted(result.items(), key=lambda cd: cd[1])
        return [self.get_exact(c) for c, d in sorted_result[:max_results]]

    def __repr__(self):
        return f'{self.__class__.__name__}[' \
               f'{self._parent_type.__name__}, ' \
               f'lookup {len(self._lookup_table)}, ' \
               f'cached {len(self._approximation_cache)}]'


# -- Color presets ------------------------------------------------------------

ColorRGB._init_approx()
ColorIndexed._init_approx()
ColorDefault._init_approx()

NOOP = ColorRGB()
"""
Special instance of `Color` class always rendering into empty string.
"""

BLACK = ColorDefault(0x000000, intcode.BLACK, intcode.BG_BLACK)
RED = ColorDefault(0x800000, intcode.RED, intcode.BG_RED)
GREEN = ColorDefault(0x008000, intcode.GREEN, intcode.BG_GREEN)
YELLOW = ColorDefault(0x808000, intcode.YELLOW, intcode.BG_YELLOW)
BLUE = ColorDefault(0x000080, intcode.BLUE, intcode.BG_BLUE)
MAGENTA = ColorDefault(0x800080, intcode.MAGENTA, intcode.BG_MAGENTA)
CYAN = ColorDefault(0x008080, intcode.CYAN, intcode.BG_CYAN)
WHITE = ColorDefault(0xc0c0c0, intcode.WHITE, intcode.BG_WHITE)
GRAY = ColorDefault(0x808080, intcode.GRAY, intcode.BG_GRAY)
HI_RED = ColorDefault(0xff0000, intcode.HI_RED, intcode.BG_HI_RED)
HI_GREEN = ColorDefault(0x00ff00, intcode.HI_GREEN, intcode.BG_HI_GREEN)
HI_YELLOW = ColorDefault(0xffff00, intcode.HI_YELLOW, intcode.BG_HI_YELLOW)
HI_BLUE = ColorDefault(0x0000ff, intcode.HI_BLUE, intcode.BG_HI_BLUE)
HI_MAGENTA = ColorDefault(0xff00ff, intcode.HI_MAGENTA, intcode.BG_HI_MAGENTA)
HI_CYAN = ColorDefault(0x00ffff, intcode.HI_CYAN, intcode.BG_HI_CYAN)
HI_WHITE = ColorDefault(0xffffff, intcode.HI_WHITE, intcode.BG_HI_WHITE)

IDX_BLACK = ColorIndexed(0x000000, intcode.IDX_BLACK)
IDX_MAROON = ColorIndexed(0x800000, intcode.IDX_MAROON)
IDX_GREEN = ColorIndexed(0x008000, intcode.IDX_GREEN)
IDX_OLIVE = ColorIndexed(0x808000, intcode.IDX_OLIVE)
IDX_NAVY = ColorIndexed(0x000080, intcode.IDX_NAVY)
IDX_PURPLE = ColorIndexed(0x800080, intcode.IDX_PURPLE)
IDX_TEAL = ColorIndexed(0x008080, intcode.IDX_TEAL)
IDX_SILVER = ColorIndexed(0xc0c0c0, intcode.IDX_SILVER)
IDX_GRAY = ColorIndexed(0x808080, intcode.IDX_GRAY)
IDX_RED = ColorIndexed(0xff0000, intcode.IDX_RED)
IDX_LIME = ColorIndexed(0x00ff00, intcode.IDX_LIME)
IDX_YELLOW = ColorIndexed(0xffff00, intcode.IDX_YELLOW)
IDX_BLUE = ColorIndexed(0x0000ff, intcode.IDX_BLUE)
IDX_FUCHSIA = ColorIndexed(0xff00ff, intcode.IDX_FUCHSIA)
IDX_AQUA = ColorIndexed(0x00ffff, intcode.IDX_AQUA)
IDX_WHITE = ColorIndexed(0xffffff, intcode.IDX_WHITE)  #@ todo exclude 0-15 from approximations
IDX_GREY_0 = ColorIndexed(0x000000, intcode.IDX_GREY_0)
IDX_NAVY_BLUE = ColorIndexed(0x00005f, intcode.IDX_NAVY_BLUE)
IDX_DARK_BLUE = ColorIndexed(0x000087, intcode.IDX_DARK_BLUE)
IDX_BLUE_3 = ColorIndexed(0x0000af, intcode.IDX_BLUE_3)
IDX_BLUE_2 = ColorIndexed(0x0000d7, intcode.IDX_BLUE_2)  # Blue3
IDX_BLUE_1 = ColorIndexed(0x0000ff, intcode.IDX_BLUE_1)
IDX_DARK_GREEN = ColorIndexed(0x005f00, intcode.IDX_DARK_GREEN)
IDX_DEEP_SKY_BLUE_4 = ColorIndexed(0x005f5f, intcode.IDX_DEEP_SKY_BLUE_4)
IDX_DEEP_SKY_BLUE_4 = ColorIndexed(0x005f87, intcode.IDX_DEEP_SKY_BLUE_4)
IDX_DEEP_SKY_BLUE_4 = ColorIndexed(0x005faf, intcode.IDX_DEEP_SKY_BLUE_4)
IDX_DODGER_BLUE_3 = ColorIndexed(0x005fd7, intcode.IDX_DODGER_BLUE_3)
IDX_DODGER_BLUE_2 = ColorIndexed(0x005fff, intcode.IDX_DODGER_BLUE_2)
IDX_GREEN_4 = ColorIndexed(0x008700, intcode.IDX_GREEN_4)
IDX_SPRING_GREEN_4 = ColorIndexed(0x00875f, intcode.IDX_SPRING_GREEN_4)
IDX_TURQUOISE_4 = ColorIndexed(0x008787, intcode.IDX_TURQUOISE_4)
IDX_DEEP_SKY_BLUE_3 = ColorIndexed(0x0087af, intcode.IDX_DEEP_SKY_BLUE_3)
IDX_DEEP_SKY_BLUE_3 = ColorIndexed(0x0087d7, intcode.IDX_DEEP_SKY_BLUE_3)
IDX_DODGER_BLUE_1 = ColorIndexed(0x0087ff, intcode.IDX_DODGER_BLUE_1)
IDX_GREEN_3 = ColorIndexed(0x00af00, intcode.IDX_GREEN_3)
IDX_SPRING_GREEN_3 = ColorIndexed(0x00af5f, intcode.IDX_SPRING_GREEN_3)
IDX_DARK_CYAN = ColorIndexed(0x00af87, intcode.IDX_DARK_CYAN)
IDX_LIGHT_SEA_GREEN = ColorIndexed(0x00afaf, intcode.IDX_LIGHT_SEA_GREEN)
IDX_DEEP_SKY_BLUE_2 = ColorIndexed(0x00afd7, intcode.IDX_DEEP_SKY_BLUE_2)
IDX_DEEP_SKY_BLUE_1 = ColorIndexed(0x00afff, intcode.IDX_DEEP_SKY_BLUE_1)
IDX_GREEN_3 = ColorIndexed(0x00d700, intcode.IDX_GREEN_3)
IDX_SPRING_GREEN_3 = ColorIndexed(0x00d75f, intcode.IDX_SPRING_GREEN_3)
IDX_SPRING_GREEN_2 = ColorIndexed(0x00d787, intcode.IDX_SPRING_GREEN_2)
IDX_CYAN_3 = ColorIndexed(0x00d7af, intcode.IDX_CYAN_3)
IDX_DARK_TURQUOISE = ColorIndexed(0x00d7d7, intcode.IDX_DARK_TURQUOISE)
IDX_TURQUOISE_2 = ColorIndexed(0x00d7ff, intcode.IDX_TURQUOISE_2)
IDX_GREEN_1 = ColorIndexed(0x00ff00, intcode.IDX_GREEN_1)
IDX_SPRING_GREEN_2 = ColorIndexed(0x00ff5f, intcode.IDX_SPRING_GREEN_2)
IDX_SPRING_GREEN_1 = ColorIndexed(0x00ff87, intcode.IDX_SPRING_GREEN_1)
IDX_MEDIUM_SPRING_GREEN = ColorIndexed(0x00ffaf, intcode.IDX_MEDIUM_SPRING_GREEN)
IDX_CYAN_2 = ColorIndexed(0x00ffd7, intcode.IDX_CYAN_2)
IDX_CYAN_1 = ColorIndexed(0x00ffff, intcode.IDX_CYAN_1)
IDX_DARK_RED = ColorIndexed(0x5f0000, intcode.IDX_DARK_RED)
IDX_DEEP_PINK_4 = ColorIndexed(0x5f005f, intcode.IDX_DEEP_PINK_4)
IDX_PURPLE_4 = ColorIndexed(0x5f0087, intcode.IDX_PURPLE_4)
IDX_PURPLE_4 = ColorIndexed(0x5f00af, intcode.IDX_PURPLE_4)
IDX_PURPLE_3 = ColorIndexed(0x5f00d7, intcode.IDX_PURPLE_3)
IDX_BLUE_VIOLET = ColorIndexed(0x5f00ff, intcode.IDX_BLUE_VIOLET)
IDX_ORANGE_4 = ColorIndexed(0x5f5f00, intcode.IDX_ORANGE_4)
IDX_GREY_37 = ColorIndexed(0x5f5f5f, intcode.IDX_GREY_37)
IDX_MEDIUM_PURPLE_4 = ColorIndexed(0x5f5f87, intcode.IDX_MEDIUM_PURPLE_4)
IDX_SLATE_BLUE_3 = ColorIndexed(0x5f5faf, intcode.IDX_SLATE_BLUE_3)
IDX_SLATE_BLUE_3 = ColorIndexed(0x5f5fd7, intcode.IDX_SLATE_BLUE_3)
IDX_ROYAL_BLUE_1 = ColorIndexed(0x5f5fff, intcode.IDX_ROYAL_BLUE_1)
IDX_CHARTREUSE_4 = ColorIndexed(0x5f8700, intcode.IDX_CHARTREUSE_4)
IDX_DARK_SEA_GREEN_4 = ColorIndexed(0x5f875f, intcode.IDX_DARK_SEA_GREEN_4)
IDX_PALE_TURQUOISE_4 = ColorIndexed(0x5f8787, intcode.IDX_PALE_TURQUOISE_4)
IDX_STEEL_BLUE = ColorIndexed(0x5f87af, intcode.IDX_STEEL_BLUE)
IDX_STEEL_BLUE_3 = ColorIndexed(0x5f87d7, intcode.IDX_STEEL_BLUE_3)
IDX_CORNFLOWER_BLUE = ColorIndexed(0x5f87ff, intcode.IDX_CORNFLOWER_BLUE)
IDX_CHARTREUSE_3 = ColorIndexed(0x5faf00, intcode.IDX_CHARTREUSE_3)
IDX_DARK_SEA_GREEN_4 = ColorIndexed(0x5faf5f, intcode.IDX_DARK_SEA_GREEN_4)
IDX_CADET_BLUE = ColorIndexed(0x5faf87, intcode.IDX_CADET_BLUE)
IDX_CADET_BLUE = ColorIndexed(0x5fafaf, intcode.IDX_CADET_BLUE)
IDX_SKY_BLUE_3 = ColorIndexed(0x5fafd7, intcode.IDX_SKY_BLUE_3)
IDX_STEEL_BLUE_1 = ColorIndexed(0x5fafff, intcode.IDX_STEEL_BLUE_1)
IDX_CHARTREUSE_3 = ColorIndexed(0x5fd700, intcode.IDX_CHARTREUSE_3)
IDX_PALE_GREEN_3 = ColorIndexed(0x5fd75f, intcode.IDX_PALE_GREEN_3)
IDX_SEA_GREEN_3 = ColorIndexed(0x5fd787, intcode.IDX_SEA_GREEN_3)
IDX_AQUAMARINE_3 = ColorIndexed(0x5fd7af, intcode.IDX_AQUAMARINE_3)
IDX_MEDIUM_TURQUOISE = ColorIndexed(0x5fd7d7, intcode.IDX_MEDIUM_TURQUOISE)
IDX_STEEL_BLUE_1 = ColorIndexed(0x5fd7ff, intcode.IDX_STEEL_BLUE_1)
IDX_CHARTREUSE_2 = ColorIndexed(0x5fff00, intcode.IDX_CHARTREUSE_2)
IDX_SEA_GREEN_2 = ColorIndexed(0x5fff5f, intcode.IDX_SEA_GREEN_2)
IDX_SEA_GREEN_1 = ColorIndexed(0x5fff87, intcode.IDX_SEA_GREEN_1)
IDX_SEA_GREEN_1 = ColorIndexed(0x5fffaf, intcode.IDX_SEA_GREEN_1)
IDX_AQUAMARINE_2 = ColorIndexed(0x5fffd7, intcode.IDX_AQUAMARINE_2)                 # Aquamarine1
IDX_DARK_SLATE_GRAY_2 = ColorIndexed(0x5fffff, intcode.IDX_DARK_SLATE_GRAY_2)
IDX_DARK_RED = ColorIndexed(0x870000, intcode.IDX_DARK_RED)
IDX_DEEP_PINK_4 = ColorIndexed(0x87005f, intcode.IDX_DEEP_PINK_4)
IDX_DARK_MAGENTA = ColorIndexed(0x870087, intcode.IDX_DARK_MAGENTA)
IDX_DARK_MAGENTA = ColorIndexed(0x8700af, intcode.IDX_DARK_MAGENTA)
IDX_DARK_VIOLET = ColorIndexed(0x8700d7, intcode.IDX_DARK_VIOLET)
IDX_PURPLE = ColorIndexed(0x8700ff, intcode.IDX_PURPLE)
IDX_ORANGE_4 = ColorIndexed(0x875f00, intcode.IDX_ORANGE_4)
IDX_LIGHT_PINK_4 = ColorIndexed(0x875f5f, intcode.IDX_LIGHT_PINK_4)
IDX_PLUM_4 = ColorIndexed(0x875f87, intcode.IDX_PLUM_4)
IDX_MEDIUM_PURPLE_3 = ColorIndexed(0x875faf, intcode.IDX_MEDIUM_PURPLE_3)
IDX_MEDIUM_PURPLE_3 = ColorIndexed(0x875fd7, intcode.IDX_MEDIUM_PURPLE_3)
IDX_SLATE_BLUE_1 = ColorIndexed(0x875fff, intcode.IDX_SLATE_BLUE_1)
IDX_YELLOW_4 = ColorIndexed(0x878700, intcode.IDX_YELLOW_4)
IDX_WHEAT_4 = ColorIndexed(0x87875f, intcode.IDX_WHEAT_4)
IDX_GREY_53 = ColorIndexed(0x878787, intcode.IDX_GREY_53)
IDX_LIGHT_SLATE_GREY = ColorIndexed(0x8787af, intcode.IDX_LIGHT_SLATE_GREY)
IDX_MEDIUM_PURPLE = ColorIndexed(0x8787d7, intcode.IDX_MEDIUM_PURPLE)
IDX_LIGHT_SLATE_BLUE = ColorIndexed(0x8787ff, intcode.IDX_LIGHT_SLATE_BLUE)
IDX_YELLOW_4 = ColorIndexed(0x87af00, intcode.IDX_YELLOW_4)
IDX_DARK_OLIVE_GREEN_3 = ColorIndexed(0x87af5f, intcode.IDX_DARK_OLIVE_GREEN_3)
IDX_DARK_SEA_GREEN = ColorIndexed(0x87af87, intcode.IDX_DARK_SEA_GREEN)
IDX_LIGHT_SKY_BLUE_3 = ColorIndexed(0x87afaf, intcode.IDX_LIGHT_SKY_BLUE_3)
IDX_LIGHT_SKY_BLUE_3 = ColorIndexed(0x87afd7, intcode.IDX_LIGHT_SKY_BLUE_3)
IDX_SKY_BLUE_2 = ColorIndexed(0x87afff, intcode.IDX_SKY_BLUE_2)
IDX_CHARTREUSE_2 = ColorIndexed(0x87d700, intcode.IDX_CHARTREUSE_2)
IDX_DARK_OLIVE_GREEN_3 = ColorIndexed(0x87d75f, intcode.IDX_DARK_OLIVE_GREEN_3)
IDX_PALE_GREEN_3 = ColorIndexed(0x87d787, intcode.IDX_PALE_GREEN_3)
IDX_DARK_SEA_GREEN_3 = ColorIndexed(0x87d7af, intcode.IDX_DARK_SEA_GREEN_3)
IDX_DARK_SLATE_GRAY_3 = ColorIndexed(0x87d7d7, intcode.IDX_DARK_SLATE_GRAY_3)
IDX_SKY_BLUE_1 = ColorIndexed(0x87d7ff, intcode.IDX_SKY_BLUE_1)
IDX_CHARTREUSE_1 = ColorIndexed(0x87ff00, intcode.IDX_CHARTREUSE_1)
IDX_LIGHT_GREEN = ColorIndexed(0x87ff5f, intcode.IDX_LIGHT_GREEN)
IDX_LIGHT_GREEN = ColorIndexed(0x87ff87, intcode.IDX_LIGHT_GREEN)
IDX_PALE_GREEN_1 = ColorIndexed(0x87ffaf, intcode.IDX_PALE_GREEN_1)
IDX_AQUAMARINE_1 = ColorIndexed(0x87ffd7, intcode.IDX_AQUAMARINE_1)
IDX_DARK_SLATE_GRAY_1 = ColorIndexed(0x87ffff, intcode.IDX_DARK_SLATE_GRAY_1)
IDX_RED_3 = ColorIndexed(0xaf0000, intcode.IDX_RED_3)
IDX_DEEP_PINK_4 = ColorIndexed(0xaf005f, intcode.IDX_DEEP_PINK_4)
IDX_MEDIUM_VIOLET_RED = ColorIndexed(0xaf0087, intcode.IDX_MEDIUM_VIOLET_RED)
IDX_MAGENTA_3 = ColorIndexed(0xaf00af, intcode.IDX_MAGENTA_3)
IDX_DARK_VIOLET = ColorIndexed(0xaf00d7, intcode.IDX_DARK_VIOLET)
IDX_PURPLE = ColorIndexed(0xaf00ff, intcode.IDX_PURPLE)
IDX_DARK_ORANGE_3 = ColorIndexed(0xaf5f00, intcode.IDX_DARK_ORANGE_3)
IDX_INDIAN_RED = ColorIndexed(0xaf5f5f, intcode.IDX_INDIAN_RED)
IDX_HOT_PINK_3 = ColorIndexed(0xaf5f87, intcode.IDX_HOT_PINK_3)
IDX_MEDIUM_ORCHID_3 = ColorIndexed(0xaf5faf, intcode.IDX_MEDIUM_ORCHID_3)
IDX_MEDIUM_ORCHID = ColorIndexed(0xaf5fd7, intcode.IDX_MEDIUM_ORCHID)
IDX_MEDIUM_PURPLE_2 = ColorIndexed(0xaf5fff, intcode.IDX_MEDIUM_PURPLE_2)
IDX_DARK_GOLDENROD = ColorIndexed(0xaf8700, intcode.IDX_DARK_GOLDENROD)
IDX_LIGHT_SALMON_3 = ColorIndexed(0xaf875f, intcode.IDX_LIGHT_SALMON_3)
IDX_ROSY_BROWN = ColorIndexed(0xaf8787, intcode.IDX_ROSY_BROWN)
IDX_GREY_63 = ColorIndexed(0xaf87af, intcode.IDX_GREY_63)
IDX_MEDIUM_PURPLE_2 = ColorIndexed(0xaf87d7, intcode.IDX_MEDIUM_PURPLE_2)
IDX_MEDIUM_PURPLE_1 = ColorIndexed(0xaf87ff, intcode.IDX_MEDIUM_PURPLE_1)
IDX_GOLD_3 = ColorIndexed(0xafaf00, intcode.IDX_GOLD_3)
IDX_DARK_KHAKI = ColorIndexed(0xafaf5f, intcode.IDX_DARK_KHAKI)
IDX_NAVAJO_WHITE_3 = ColorIndexed(0xafaf87, intcode.IDX_NAVAJO_WHITE_3)
IDX_GREY_69 = ColorIndexed(0xafafaf, intcode.IDX_GREY_69)
IDX_LIGHT_STEEL_BLUE_3 = ColorIndexed(0xafafd7, intcode.IDX_LIGHT_STEEL_BLUE_3)
IDX_LIGHT_STEEL_BLUE = ColorIndexed(0xafafff, intcode.IDX_LIGHT_STEEL_BLUE)
IDX_YELLOW_3 = ColorIndexed(0xafd700, intcode.IDX_YELLOW_3)
IDX_DARK_OLIVE_GREEN_3 = ColorIndexed(0xafd75f, intcode.IDX_DARK_OLIVE_GREEN_3)
IDX_DARK_SEA_GREEN_3 = ColorIndexed(0xafd787, intcode.IDX_DARK_SEA_GREEN_3)
IDX_DARK_SEA_GREEN_2 = ColorIndexed(0xafd7af, intcode.IDX_DARK_SEA_GREEN_2)
IDX_LIGHT_CYAN_3 = ColorIndexed(0xafd7d7, intcode.IDX_LIGHT_CYAN_3)
IDX_LIGHT_SKY_BLUE_1 = ColorIndexed(0xafd7ff, intcode.IDX_LIGHT_SKY_BLUE_1)
IDX_GREEN_YELLOW = ColorIndexed(0xafff00, intcode.IDX_GREEN_YELLOW)
IDX_DARK_OLIVE_GREEN_2 = ColorIndexed(0xafff5f, intcode.IDX_DARK_OLIVE_GREEN_2)
IDX_PALE_GREEN_1 = ColorIndexed(0xafff87, intcode.IDX_PALE_GREEN_1)
IDX_DARK_SEA_GREEN_2 = ColorIndexed(0xafffaf, intcode.IDX_DARK_SEA_GREEN_2)
IDX_DARK_SEA_GREEN_1 = ColorIndexed(0xafffd7, intcode.IDX_DARK_SEA_GREEN_1)
IDX_PALE_TURQUOISE_1 = ColorIndexed(0xafffff, intcode.IDX_PALE_TURQUOISE_1)
IDX_RED_3 = ColorIndexed(0xd70000, intcode.IDX_RED_3)
IDX_DEEP_PINK_3 = ColorIndexed(0xd7005f, intcode.IDX_DEEP_PINK_3)
IDX_DEEP_PINK_3 = ColorIndexed(0xd70087, intcode.IDX_DEEP_PINK_3)
IDX_MAGENTA_3 = ColorIndexed(0xd700af, intcode.IDX_MAGENTA_3)
IDX_MAGENTA_3 = ColorIndexed(0xd700d7, intcode.IDX_MAGENTA_3)
IDX_MAGENTA_2 = ColorIndexed(0xd700ff, intcode.IDX_MAGENTA_2)
IDX_DARK_ORANGE_3 = ColorIndexed(0xd75f00, intcode.IDX_DARK_ORANGE_3)
IDX_INDIAN_RED = ColorIndexed(0xd75f5f, intcode.IDX_INDIAN_RED)
IDX_HOT_PINK_3 = ColorIndexed(0xd75f87, intcode.IDX_HOT_PINK_3)
IDX_HOT_PINK_2 = ColorIndexed(0xd75faf, intcode.IDX_HOT_PINK_2)
IDX_ORCHID = ColorIndexed(0xd75fd7, intcode.IDX_ORCHID)
IDX_MEDIUM_ORCHID_1 = ColorIndexed(0xd75fff, intcode.IDX_MEDIUM_ORCHID_1)
IDX_ORANGE_3 = ColorIndexed(0xd78700, intcode.IDX_ORANGE_3)
IDX_LIGHT_SALMON_3 = ColorIndexed(0xd7875f, intcode.IDX_LIGHT_SALMON_3)
IDX_LIGHT_PINK_3 = ColorIndexed(0xd78787, intcode.IDX_LIGHT_PINK_3)
IDX_PINK_3 = ColorIndexed(0xd787af, intcode.IDX_PINK_3)
IDX_PLUM_3 = ColorIndexed(0xd787d7, intcode.IDX_PLUM_3)
IDX_VIOLET = ColorIndexed(0xd787ff, intcode.IDX_VIOLET)
IDX_GOLD_3 = ColorIndexed(0xd7af00, intcode.IDX_GOLD_3)
IDX_LIGHT_GOLDENROD_3 = ColorIndexed(0xd7af5f, intcode.IDX_LIGHT_GOLDENROD_3)
IDX_TAN = ColorIndexed(0xd7af87, intcode.IDX_TAN)
IDX_MISTY_ROSE_3 = ColorIndexed(0xd7afaf, intcode.IDX_MISTY_ROSE_3)
IDX_THISTLE_3 = ColorIndexed(0xd7afd7, intcode.IDX_THISTLE_3)
IDX_PLUM_2 = ColorIndexed(0xd7afff, intcode.IDX_PLUM_2)
IDX_YELLOW_3 = ColorIndexed(0xd7d700, intcode.IDX_YELLOW_3)
IDX_KHAKI_3 = ColorIndexed(0xd7d75f, intcode.IDX_KHAKI_3)
IDX_LIGHT_GOLDENROD_2 = ColorIndexed(0xd7d787, intcode.IDX_LIGHT_GOLDENROD_2)
IDX_LIGHT_YELLOW_3 = ColorIndexed(0xd7d7af, intcode.IDX_LIGHT_YELLOW_3)
IDX_GREY_84 = ColorIndexed(0xd7d7d7, intcode.IDX_GREY_84)
IDX_LIGHT_STEEL_BLUE_1 = ColorIndexed(0xd7d7ff, intcode.IDX_LIGHT_STEEL_BLUE_1)
IDX_YELLOW_2 = ColorIndexed(0xd7ff00, intcode.IDX_YELLOW_2)
IDX_DARK_OLIVE_GREEN_1 = ColorIndexed(0xd7ff5f, intcode.IDX_DARK_OLIVE_GREEN_1)
IDX_DARK_OLIVE_GREEN_1 = ColorIndexed(0xd7ff87, intcode.IDX_DARK_OLIVE_GREEN_1)
IDX_DARK_SEA_GREEN_1 = ColorIndexed(0xd7ffaf, intcode.IDX_DARK_SEA_GREEN_1)
IDX_HONEYDEW_2 = ColorIndexed(0xd7ffd7, intcode.IDX_HONEYDEW_2)
IDX_LIGHT_CYAN_1 = ColorIndexed(0xd7ffff, intcode.IDX_LIGHT_CYAN_1)
IDX_RED_1 = ColorIndexed(0xff0000, intcode.IDX_RED_1)
IDX_DEEP_PINK_2 = ColorIndexed(0xff005f, intcode.IDX_DEEP_PINK_2)
IDX_DEEP_PINK_1 = ColorIndexed(0xff0087, intcode.IDX_DEEP_PINK_1)
IDX_DEEP_PINK_1 = ColorIndexed(0xff00af, intcode.IDX_DEEP_PINK_1)
IDX_MAGENTA_2 = ColorIndexed(0xff00d7, intcode.IDX_MAGENTA_2)
IDX_MAGENTA_1 = ColorIndexed(0xff00ff, intcode.IDX_MAGENTA_1)
IDX_ORANGE_RED_1 = ColorIndexed(0xff5f00, intcode.IDX_ORANGE_RED_1)
IDX_INDIAN_RED_1 = ColorIndexed(0xff5f5f, intcode.IDX_INDIAN_RED_1)
IDX_INDIAN_RED_1 = ColorIndexed(0xff5f87, intcode.IDX_INDIAN_RED_1)
IDX_HOT_PINK = ColorIndexed(0xff5faf, intcode.IDX_HOT_PINK)
IDX_HOT_PINK = ColorIndexed(0xff5fd7, intcode.IDX_HOT_PINK)
IDX_MEDIUM_ORCHID_1 = ColorIndexed(0xff5fff, intcode.IDX_MEDIUM_ORCHID_1)
IDX_DARK_ORANGE = ColorIndexed(0xff8700, intcode.IDX_DARK_ORANGE)
IDX_SALMON_1 = ColorIndexed(0xff875f, intcode.IDX_SALMON_1)
IDX_LIGHT_CORAL = ColorIndexed(0xff8787, intcode.IDX_LIGHT_CORAL)
IDX_PALE_VIOLET_RED_1 = ColorIndexed(0xff87af, intcode.IDX_PALE_VIOLET_RED_1)
IDX_ORCHID_2 = ColorIndexed(0xff87d7, intcode.IDX_ORCHID_2)
IDX_ORCHID_1 = ColorIndexed(0xff87ff, intcode.IDX_ORCHID_1)
IDX_ORANGE_1 = ColorIndexed(0xffaf00, intcode.IDX_ORANGE_1)
IDX_SANDY_BROWN = ColorIndexed(0xffaf5f, intcode.IDX_SANDY_BROWN)
IDX_LIGHT_SALMON_1 = ColorIndexed(0xffaf87, intcode.IDX_LIGHT_SALMON_1)
IDX_LIGHT_PINK_1 = ColorIndexed(0xffafaf, intcode.IDX_LIGHT_PINK_1)
IDX_PINK_1 = ColorIndexed(0xffafd7, intcode.IDX_PINK_1)
IDX_PLUM_1 = ColorIndexed(0xffafff, intcode.IDX_PLUM_1)
IDX_GOLD_1 = ColorIndexed(0xffd700, intcode.IDX_GOLD_1)
IDX_LIGHT_GOLDENROD_2 = ColorIndexed(0xffd75f, intcode.IDX_LIGHT_GOLDENROD_2)
IDX_LIGHT_GOLDENROD_2 = ColorIndexed(0xffd787, intcode.IDX_LIGHT_GOLDENROD_2)
IDX_NAVAJO_WHITE_1 = ColorIndexed(0xffd7af, intcode.IDX_NAVAJO_WHITE_1)
IDX_MISTY_ROSE_1 = ColorIndexed(0xffd7d7, intcode.IDX_MISTY_ROSE_1)
IDX_THISTLE_1 = ColorIndexed(0xffd7ff, intcode.IDX_THISTLE_1)
IDX_YELLOW_1 = ColorIndexed(0xffff00, intcode.IDX_YELLOW_1)
IDX_LIGHT_GOLDENROD_1 = ColorIndexed(0xffff5f, intcode.IDX_LIGHT_GOLDENROD_1)
IDX_KHAKI_1 = ColorIndexed(0xffff87, intcode.IDX_KHAKI_1)
IDX_WHEAT_1 = ColorIndexed(0xffffaf, intcode.IDX_WHEAT_1)
IDX_CORNSILK_1 = ColorIndexed(0xffffd7, intcode.IDX_CORNSILK_1)
IDX_GREY_100 = ColorIndexed(0xffffff, intcode.IDX_GREY_100)
IDX_GREY_3 = ColorIndexed(0x080808, intcode.IDX_GREY_3)
IDX_GREY_7 = ColorIndexed(0x121212, intcode.IDX_GREY_7)
IDX_GREY_11 = ColorIndexed(0x1c1c1c, intcode.IDX_GREY_11)
IDX_GREY_15 = ColorIndexed(0x262626, intcode.IDX_GREY_15)
IDX_GREY_19 = ColorIndexed(0x303030, intcode.IDX_GREY_19)
IDX_GREY_23 = ColorIndexed(0x3a3a3a, intcode.IDX_GREY_23)
IDX_GREY_27 = ColorIndexed(0x444444, intcode.IDX_GREY_27)
IDX_GREY_30 = ColorIndexed(0x4e4e4e, intcode.IDX_GREY_30)
IDX_GREY_35 = ColorIndexed(0x585858, intcode.IDX_GREY_35)
IDX_GREY_39 = ColorIndexed(0x626262, intcode.IDX_GREY_39)
IDX_GREY_42 = ColorIndexed(0x6c6c6c, intcode.IDX_GREY_42)
IDX_GREY_46 = ColorIndexed(0x767676, intcode.IDX_GREY_46)
IDX_GREY_50 = ColorIndexed(0x808080, intcode.IDX_GREY_50)
IDX_GREY_54 = ColorIndexed(0x8a8a8a, intcode.IDX_GREY_54)
IDX_GREY_58 = ColorIndexed(0x949494, intcode.IDX_GREY_58)
IDX_GREY_62 = ColorIndexed(0x9e9e9e, intcode.IDX_GREY_62)
IDX_GREY_66 = ColorIndexed(0xa8a8a8, intcode.IDX_GREY_66)
IDX_GREY_70 = ColorIndexed(0xb2b2b2, intcode.IDX_GREY_70)
IDX_GREY_74 = ColorIndexed(0xbcbcbc, intcode.IDX_GREY_74)
IDX_GREY_78 = ColorIndexed(0xc6c6c6, intcode.IDX_GREY_78)
IDX_GREY_82 = ColorIndexed(0xd0d0d0, intcode.IDX_GREY_82)
IDX_GREY_85 = ColorIndexed(0xdadada, intcode.IDX_GREY_85)
IDX_GREY_89 = ColorIndexed(0xe4e4e4, intcode.IDX_GREY_89)
IDX_GREY_93 = ColorIndexed(0xeeeeee, intcode.IDX_GREY_93)

RGB_BLACK = ColorRGB(0x000000)
RGB_WHITE = ColorRGB(0xffffff)
