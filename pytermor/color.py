# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""
.. testsetup:: *

    from pytermor.color import Color, ColorDefault, ColorIndexed, ColorRGB
"""
from __future__ import annotations

import logging
from abc import abstractmethod, ABCMeta
from typing import Dict, Tuple, Generic, TypeVar, List, Optional

from .common import LogicError, Registry
from .ansi import SequenceSGR, NOOP_SEQ, IntCodes


class Color(metaclass=ABCMeta):
    """
    Abstract superclass for other ``Colors``.
    """
    _approx_initialized: bool = False
    _approx: Approximator[Color]

    def __init__(self, hex_value: int = None, use_for_approximations: bool = False):
        self._hex_value: int | None = hex_value

        self._init_approx()
        if use_for_approximations:
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
            raise LogicError('Impossible if-branch, algorithm is implemented '
                             'incorrectly')

        if v == 0:
            s = 0
        else:
            s = c/v

        if h < 0:
            h += 360

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

    def format_value(self, prefix: str|None = '0x', noop_label: str = '~') -> str:
        if self._hex_value is None:
            return noop_label
        return f'{prefix or "":s}{self._hex_value:06x}'


TypeColor = TypeVar('TypeColor', 'ColorDefault', 'ColorIndexed', 'ColorRGB')
""" Any non-abstract `Color` type. """


class ColorDefault(Color):
    def __init__(self, hex_value: int, code_fg: int, code_bg: int):
        self._code_fg: int = code_fg
        self._code_bg: int = code_bg
        super().__init__(hex_value)

    @classmethod
    def get_default(cls) -> ColorDefault:
        return Colors.BLACK

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
    """ .. todo :: get color by int code """
    _index: Dict[int, ColorIndexed] = dict()

    def __init__(self, hex_value: int, code: int, use_for_approximations: bool = False):
        self._code = code
        super().__init__(hex_value, use_for_approximations)

        if not self._index.get(self._code):
            self._index[self._code] = self
        else:
            logging.warning(f'Indexed color duplicate by code {self._code} '
                            f'detected: {self}. It was NOT added to the index.')

    @classmethod
    def get_default(cls) -> ColorIndexed:
        return Colors.XTERM_GREY_0

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
        return SequenceSGR.init_color_indexed(self._code, bg=bg)

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
        return Colors.RGB_BLACK

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
        if self._hex_value is None:
            return NOOP_SEQ
        return SequenceSGR.init_color_rgb(
            *self.hex_value_to_rgb_channels(self._hex_value), bg=bg)

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._hex_value == other._hex_value

    def __repr__(self):
        return f'{self.__class__.__name__}[{self.format_value()}]'


class Approximator(Generic[TypeColor]):
    """
    Internal class containing a dictionary of registred `Colors <Color>` indexed
    by hex code along with cached nearest color search results to avoid unnecessary
    instance copies and search repeating.
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
        if color.hex_value is None:
            return

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
        `SgrRenderer` to find supported color alternatives in case user's terminal is
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
            be returned. Another option is to use special "color" named `NOOP_COLOR`.

        .. todo :: rewrite using HSV distance?

        :param hex_value:   Color RGB value.
        :param max_results: Maximum amount of values to return.
        :return:            Closest `Color` instances found, sorted by color
                            distance descending (i.e. 0th element is always the
                            closest to the input value).
        """
        input_r, input_g, input_b = Color.hex_value_to_rgb_channels(hex_value)
        result: Dict[int, float] = dict()

        for cached_hex, cached_color in self._lookup_table.items():
            # sRGB euclidean distance
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


ColorRGB._init_approx()
ColorIndexed._init_approx()
ColorDefault._init_approx()


NOOP_COLOR = ColorRGB()
"""
Special instance of `Color` class always rendering into empty string.
"""


class Colors(Registry[TypeColor]):
    """
    Registry of colors presets (`ColorDefault`, `ColorIndexed`, `ColorRGB`).

    .. attention::
       Registry constants are omitted from API doc pages to improve readability
       and avoid duplication. Summary list of all presets can be found in
       `guide.presets` section of the guide.
   """

    BLACK = ColorDefault(0x000000, IntCodes.BLACK, IntCodes.BG_BLACK)
    RED = ColorDefault(0x800000, IntCodes.RED, IntCodes.BG_RED)
    GREEN = ColorDefault(0x008000, IntCodes.GREEN, IntCodes.BG_GREEN)
    YELLOW = ColorDefault(0x808000, IntCodes.YELLOW, IntCodes.BG_YELLOW)
    BLUE = ColorDefault(0x000080, IntCodes.BLUE, IntCodes.BG_BLUE)
    MAGENTA = ColorDefault(0x800080, IntCodes.MAGENTA, IntCodes.BG_MAGENTA)
    CYAN = ColorDefault(0x008080, IntCodes.CYAN, IntCodes.BG_CYAN)
    WHITE = ColorDefault(0xc0c0c0, IntCodes.WHITE, IntCodes.BG_WHITE)
    GRAY = ColorDefault(0x808080, IntCodes.GRAY, IntCodes.BG_GRAY)
    HI_RED = ColorDefault(0xff0000, IntCodes.HI_RED, IntCodes.BG_HI_RED)
    HI_GREEN = ColorDefault(0x00ff00, IntCodes.HI_GREEN, IntCodes.BG_HI_GREEN)
    HI_YELLOW = ColorDefault(0xffff00, IntCodes.HI_YELLOW, IntCodes.BG_HI_YELLOW)
    HI_BLUE = ColorDefault(0x0000ff, IntCodes.HI_BLUE, IntCodes.BG_HI_BLUE)
    HI_MAGENTA = ColorDefault(0xff00ff, IntCodes.HI_MAGENTA, IntCodes.BG_HI_MAGENTA)
    HI_CYAN = ColorDefault(0x00ffff, IntCodes.HI_CYAN, IntCodes.BG_HI_CYAN)
    HI_WHITE = ColorDefault(0xffffff, IntCodes.HI_WHITE, IntCodes.BG_HI_WHITE)

    # - 53 shades of gray -
    # presets with steps by 5% (1% near the edges), by 1/6 and by 1/16

    RGB_BLACK = ColorRGB(0x000000)    # darkest darkness
    RGB_WHITE = ColorRGB(0xffffff)    # brightest whiteness

    RGB_GRAY_1 = ColorRGB(0x020202)  # 1%
    RGB_GRAY_2 = ColorRGB(0x050505)  # 2%
    RGB_GRAY_3 = ColorRGB(0x070707)  # 3%
    RGB_GRAY_4 = ColorRGB(0x0a0a0a)  # 4%
    RGB_GRAY_5 = ColorRGB(0x0c0c0c)  # 5%
    RGB_GRAY_6 = ColorRGB(0x0f0f0f)  # 6%
    RGB_GRAY_7 = ColorRGB(0x111111)  # 7%
    RGB_GRAY_8 = ColorRGB(0x141414)  # 8%
    RGB_GRAY_9 = ColorRGB(0x171717)  # 9%
    RGB_GRAY_10 = ColorRGB(0x191919)  # 10%
    RGB_GRAY_15 = ColorRGB(0x262626)  # 15%
    RGB_GRAY_20 = ColorRGB(0x333333)  # 20%
    RGB_GRAY_25 = ColorRGB(0x404040)  # 25%
    RGB_GRAY_30 = ColorRGB(0x4c4c4c)  # 30%
    RGB_GRAY_35 = ColorRGB(0x595959)  # 35%
    RGB_GRAY_40 = ColorRGB(0x666666)  # 40%
    RGB_GRAY_45 = ColorRGB(0x737373)  # 45%
    RGB_GRAY_50 = ColorRGB(0x808080)  # 50%
    RGB_GRAY_55 = ColorRGB(0x8c8c8c)  # 55%
    RGB_GRAY_60 = ColorRGB(0x999999)  # 60%
    RGB_GRAY_65 = ColorRGB(0xa6a6a6)  # 65%
    RGB_GRAY_70 = ColorRGB(0xb3b3b3)  # 70%
    RGB_GRAY_75 = ColorRGB(0xc0c0c0)  # 75%
    RGB_GRAY_80 = ColorRGB(0xcccccc)  # 80%
    RGB_GRAY_85 = ColorRGB(0xd9d9d9)  # 85%
    RGB_GRAY_90 = ColorRGB(0xe6e6e6)  # 90%
    RGB_GRAY_91 = ColorRGB(0xe8e8e8)  # 91%
    RGB_GRAY_92 = ColorRGB(0xebebeb)  # 92%
    RGB_GRAY_93 = ColorRGB(0xeeeeee)  # 93%
    RGB_GRAY_94 = ColorRGB(0xf1f1f1)  # 94%
    RGB_GRAY_95 = ColorRGB(0xf3f3f3)  # 95%
    RGB_GRAY_96 = ColorRGB(0xf5f5f5)  # 96%
    RGB_GRAY_97 = ColorRGB(0xf8f8f8)  # 97%
    RGB_GRAY_98 = ColorRGB(0xfafafa)  # 98%
    RGB_GRAY_99 = ColorRGB(0xfdfdfd)  # 99%

    RGB_GRAY_1_6S = ColorRGB(0x2a2a2a)  # 1/6
    RGB_GRAY_2_6S = ColorRGB(0x555555)  # 2/6
    RGB_GRAY_3_6S = RGB_GRAY_50         # 3/6
    RGB_GRAY_4_6S = ColorRGB(0xaaaaaa)  # 4/6
    RGB_GRAY_5_6S = ColorRGB(0xd5d5d5)  # 5/6

    RGB_GRAY_1_16S = ColorRGB(0x101010)  # 1/16
    RGB_GRAY_2_16S = ColorRGB(0x202020)  # 2/16
    RGB_GRAY_3_16S = ColorRGB(0x303030)  # 3/16
    RGB_GRAY_4_16S = RGB_GRAY_25         # 4/16
    RGB_GRAY_5_16S = ColorRGB(0x505050)  # 5/16
    RGB_GRAY_6_16S = ColorRGB(0x606060)  # 6/16
    RGB_GRAY_7_16S = ColorRGB(0x707070)  # 7/16
    RGB_GRAY_8_16S = RGB_GRAY_50         # 8/16
    RGB_GRAY_9_16S = ColorRGB(0x909090)  # 9/16
    RGB_GRAY_10_16S = ColorRGB(0xa0a0a0)  # 10/16
    RGB_GRAY_11_16S = ColorRGB(0xb0b0b0)  # 11/16
    RGB_GRAY_12_16S = RGB_GRAY_75         # 12/16
    RGB_GRAY_13_16S = ColorRGB(0xd0d0d0)  # 13/16
    RGB_GRAY_14_16S = ColorRGB(0xe0e0e0)  # 14/16
    RGB_GRAY_15_16S = ColorRGB(0xf0f0f0)  # 15/16

    # Indexed

    XTERM_AQUA = ColorIndexed(0x00ffff, IntCodes.XTERM_AQUA)  # 14
    XTERM_AQUAMARINE_1 = ColorIndexed(0x87ffd7, IntCodes.XTERM_AQUAMARINE_1, use_for_approximations=True)  # 122
    XTERM_AQUAMARINE_2 = ColorIndexed(0x5fffd7, IntCodes.XTERM_AQUAMARINE_2, use_for_approximations=True)  # 86 (orig. Aquamarine1)
    XTERM_AQUAMARINE_3 = ColorIndexed(0x5fd7af, IntCodes.XTERM_AQUAMARINE_3, use_for_approximations=True)  # 79
    XTERM_BLACK = ColorIndexed(0x000000, IntCodes.XTERM_BLACK)  # 0
    XTERM_BLUE = ColorIndexed(0x0000ff, IntCodes.XTERM_BLUE)  # 12
    XTERM_BLUE_1 = ColorIndexed(0x0000ff, IntCodes.XTERM_BLUE_1, use_for_approximations=True)  # 21
    XTERM_BLUE_2 = ColorIndexed(0x0000d7, IntCodes.XTERM_BLUE_2, use_for_approximations=True)  # 20 (orig. Blue3)
    XTERM_BLUE_3 = ColorIndexed(0x0000af, IntCodes.XTERM_BLUE_3, use_for_approximations=True)  # 19
    XTERM_BLUE_VIOLET = ColorIndexed(0x5f00ff, IntCodes.XTERM_BLUE_VIOLET, use_for_approximations=True)  # 57
    XTERM_CADET_BLUE = ColorIndexed(0x5fafaf, IntCodes.XTERM_CADET_BLUE, use_for_approximations=True)  # 73
    XTERM_CADET_BLUE_2 = ColorIndexed(0x5faf87, IntCodes.XTERM_CADET_BLUE_2, use_for_approximations=True)  # 72 (orig. CadetBlue)
    XTERM_CHARTREUSE_1 = ColorIndexed(0x87ff00, IntCodes.XTERM_CHARTREUSE_1, use_for_approximations=True)  # 118
    XTERM_CHARTREUSE_2 = ColorIndexed(0x5fff00, IntCodes.XTERM_CHARTREUSE_2, use_for_approximations=True)  # 82
    XTERM_CHARTREUSE_3 = ColorIndexed(0x87d700, IntCodes.XTERM_CHARTREUSE_3, use_for_approximations=True)  # 112 (orig. Chartreuse2)
    XTERM_CHARTREUSE_4 = ColorIndexed(0x5fd700, IntCodes.XTERM_CHARTREUSE_4, use_for_approximations=True)  # 76 (orig. Chartreuse3)
    XTERM_CHARTREUSE_5 = ColorIndexed(0x5faf00, IntCodes.XTERM_CHARTREUSE_5, use_for_approximations=True)  # 70 (orig. Chartreuse3)
    XTERM_CHARTREUSE_6 = ColorIndexed(0x5f8700, IntCodes.XTERM_CHARTREUSE_6, use_for_approximations=True)  # 64 (orig. Chartreuse4)
    XTERM_CORNFLOWER_BLUE = ColorIndexed(0x5f87ff, IntCodes.XTERM_CORNFLOWER_BLUE, use_for_approximations=True)  # 69
    XTERM_CORNSILK_1 = ColorIndexed(0xffffd7, IntCodes.XTERM_CORNSILK_1, use_for_approximations=True)  # 230
    XTERM_CYAN_1 = ColorIndexed(0x00ffff, IntCodes.XTERM_CYAN_1, use_for_approximations=True)  # 51
    XTERM_CYAN_2 = ColorIndexed(0x00ffd7, IntCodes.XTERM_CYAN_2, use_for_approximations=True)  # 50
    XTERM_CYAN_3 = ColorIndexed(0x00d7af, IntCodes.XTERM_CYAN_3, use_for_approximations=True)  # 43
    XTERM_DARK_BLUE = ColorIndexed(0x000087, IntCodes.XTERM_DARK_BLUE, use_for_approximations=True)  # 18
    XTERM_DARK_CYAN = ColorIndexed(0x00af87, IntCodes.XTERM_DARK_CYAN, use_for_approximations=True)  # 36
    XTERM_DARK_GOLDENROD = ColorIndexed(0xaf8700, IntCodes.XTERM_DARK_GOLDENROD, use_for_approximations=True)  # 136
    XTERM_DARK_GREEN = ColorIndexed(0x005f00, IntCodes.XTERM_DARK_GREEN, use_for_approximations=True)  # 22
    XTERM_DARK_KHAKI = ColorIndexed(0xafaf5f, IntCodes.XTERM_DARK_KHAKI, use_for_approximations=True)  # 143
    XTERM_DARK_MAGENTA = ColorIndexed(0x8700af, IntCodes.XTERM_DARK_MAGENTA, use_for_approximations=True)  # 91
    XTERM_DARK_MAGENTA_2 = ColorIndexed(0x870087, IntCodes.XTERM_DARK_MAGENTA_2, use_for_approximations=True)  # 90 (orig. DarkMagenta)
    XTERM_DARK_OLIVE_GREEN_1 = ColorIndexed(0xd7ff87, IntCodes.XTERM_DARK_OLIVE_GREEN_1, use_for_approximations=True)  # 192
    XTERM_DARK_OLIVE_GREEN_2 = ColorIndexed(0xd7ff5f, IntCodes.XTERM_DARK_OLIVE_GREEN_2, use_for_approximations=True)  # 191 (orig. DarkOliveGreen1)
    XTERM_DARK_OLIVE_GREEN_3 = ColorIndexed(0xafff5f, IntCodes.XTERM_DARK_OLIVE_GREEN_3, use_for_approximations=True)  # 155 (orig. DarkOliveGreen2)
    XTERM_DARK_OLIVE_GREEN_5 = ColorIndexed(0xafd75f, IntCodes.XTERM_DARK_OLIVE_GREEN_5, use_for_approximations=True)  # 149 (orig. DarkOliveGreen3)
    XTERM_DARK_OLIVE_GREEN_4 = ColorIndexed(0x87d75f, IntCodes.XTERM_DARK_OLIVE_GREEN_4, use_for_approximations=True)  # 113 (orig. DarkOliveGreen3)
    XTERM_DARK_OLIVE_GREEN_6 = ColorIndexed(0x87af5f, IntCodes.XTERM_DARK_OLIVE_GREEN_6, use_for_approximations=True)  # 107 (orig. DarkOliveGreen3)
    XTERM_DARK_ORANGE = ColorIndexed(0xff8700, IntCodes.XTERM_DARK_ORANGE, use_for_approximations=True)  # 208
    XTERM_DARK_ORANGE_2 = ColorIndexed(0xd75f00, IntCodes.XTERM_DARK_ORANGE_2, use_for_approximations=True)  # 166 (orig. DarkOrange3)
    XTERM_DARK_ORANGE_3 = ColorIndexed(0xaf5f00, IntCodes.XTERM_DARK_ORANGE_3, use_for_approximations=True)  # 130
    XTERM_DARK_RED = ColorIndexed(0x870000, IntCodes.XTERM_DARK_RED, use_for_approximations=True)  # 88
    XTERM_DARK_RED_2 = ColorIndexed(0x5f0000, IntCodes.XTERM_DARK_RED_2, use_for_approximations=True)  # 52 (orig. DarkRed)
    XTERM_DARK_SEA_GREEN_1 = ColorIndexed(0xafffd7, IntCodes.XTERM_DARK_SEA_GREEN_1, use_for_approximations=True)  # 158
    XTERM_DARK_SEA_GREEN_2 = ColorIndexed(0xd7ffaf, IntCodes.XTERM_DARK_SEA_GREEN_2, use_for_approximations=True)  # 193 (orig. DarkSeaGreen1)
    XTERM_DARK_SEA_GREEN_3 = ColorIndexed(0xafffaf, IntCodes.XTERM_DARK_SEA_GREEN_3, use_for_approximations=True)  # 157 (orig. DarkSeaGreen2)
    XTERM_DARK_SEA_GREEN_4 = ColorIndexed(0xafd7af, IntCodes.XTERM_DARK_SEA_GREEN_4, use_for_approximations=True)  # 151 (orig. DarkSeaGreen2)
    XTERM_DARK_SEA_GREEN_5 = ColorIndexed(0x87d7af, IntCodes.XTERM_DARK_SEA_GREEN_5, use_for_approximations=True)  # 115 (orig. DarkSeaGreen3)
    XTERM_DARK_SEA_GREEN_6 = ColorIndexed(0xafd787, IntCodes.XTERM_DARK_SEA_GREEN_6, use_for_approximations=True)  # 150 (orig. DarkSeaGreen3)
    XTERM_DARK_SEA_GREEN_7 = ColorIndexed(0x87af87, IntCodes.XTERM_DARK_SEA_GREEN_7, use_for_approximations=True)  # 108 (orig. DarkSeaGreen)
    XTERM_DARK_SEA_GREEN_8 = ColorIndexed(0x5faf5f, IntCodes.XTERM_DARK_SEA_GREEN_8, use_for_approximations=True)  # 71 (orig. DarkSeaGreen4)
    XTERM_DARK_SEA_GREEN_9 = ColorIndexed(0x5f875f, IntCodes.XTERM_DARK_SEA_GREEN_9, use_for_approximations=True)  # 65 (orig. DarkSeaGreen4)
    XTERM_DARK_SLATE_GRAY_1 = ColorIndexed(0x87ffff, IntCodes.XTERM_DARK_SLATE_GRAY_1, use_for_approximations=True)  # 123
    XTERM_DARK_SLATE_GRAY_2 = ColorIndexed(0x5fffff, IntCodes.XTERM_DARK_SLATE_GRAY_2, use_for_approximations=True)  # 87
    XTERM_DARK_SLATE_GRAY_3 = ColorIndexed(0x87d7d7, IntCodes.XTERM_DARK_SLATE_GRAY_3, use_for_approximations=True)  # 116
    XTERM_DARK_TURQUOISE = ColorIndexed(0x00d7d7, IntCodes.XTERM_DARK_TURQUOISE, use_for_approximations=True)  # 44
    XTERM_DARK_VIOLET = ColorIndexed(0xaf00d7, IntCodes.XTERM_DARK_VIOLET, use_for_approximations=True)  # 128
    XTERM_DARK_VIOLET_2 = ColorIndexed(0x8700d7, IntCodes.XTERM_DARK_VIOLET_2, use_for_approximations=True)  # 92 (orig. DarkViolet)
    XTERM_DEEP_PINK_1 = ColorIndexed(0xff00af, IntCodes.XTERM_DEEP_PINK_1, use_for_approximations=True)  # 199
    XTERM_DEEP_PINK_2 = ColorIndexed(0xff0087, IntCodes.XTERM_DEEP_PINK_2, use_for_approximations=True)  # 198 (orig. DeepPink1)
    XTERM_DEEP_PINK_3 = ColorIndexed(0xd70087, IntCodes.XTERM_DEEP_PINK_3, use_for_approximations=True)  # 162
    XTERM_DEEP_PINK_4 = ColorIndexed(0xff005f, IntCodes.XTERM_DEEP_PINK_4, use_for_approximations=True)  # 197 (orig. DeepPink2)
    XTERM_DEEP_PINK_5 = ColorIndexed(0xd7005f, IntCodes.XTERM_DEEP_PINK_5, use_for_approximations=True)  # 161 (orig. DeepPink3)
    XTERM_DEEP_PINK_6 = ColorIndexed(0xaf005f, IntCodes.XTERM_DEEP_PINK_6, use_for_approximations=True)  # 125 (orig. DeepPink4)
    XTERM_DEEP_PINK_7 = ColorIndexed(0x87005f, IntCodes.XTERM_DEEP_PINK_7, use_for_approximations=True)  # 89 (orig. DeepPink4)
    XTERM_DEEP_PINK_8 = ColorIndexed(0x5f005f, IntCodes.XTERM_DEEP_PINK_8, use_for_approximations=True)  # 53 (orig. DeepPink4)
    XTERM_DEEP_SKY_BLUE_1 = ColorIndexed(0x00afff, IntCodes.XTERM_DEEP_SKY_BLUE_1, use_for_approximations=True)  # 39
    XTERM_DEEP_SKY_BLUE_2 = ColorIndexed(0x00afd7, IntCodes.XTERM_DEEP_SKY_BLUE_2, use_for_approximations=True)  # 38
    XTERM_DEEP_SKY_BLUE_3 = ColorIndexed(0x0087d7, IntCodes.XTERM_DEEP_SKY_BLUE_3, use_for_approximations=True)  # 32
    XTERM_DEEP_SKY_BLUE_4 = ColorIndexed(0x0087af, IntCodes.XTERM_DEEP_SKY_BLUE_4, use_for_approximations=True)  # 31 (orig. DeepSkyBlue3)
    XTERM_DEEP_SKY_BLUE_5 = ColorIndexed(0x005faf, IntCodes.XTERM_DEEP_SKY_BLUE_5, use_for_approximations=True)  # 25 (orig. DeepSkyBlue4)
    XTERM_DEEP_SKY_BLUE_6 = ColorIndexed(0x005f87, IntCodes.XTERM_DEEP_SKY_BLUE_6, use_for_approximations=True)  # 24 (orig. DeepSkyBlue4)
    XTERM_DEEP_SKY_BLUE_7 = ColorIndexed(0x005f5f, IntCodes.XTERM_DEEP_SKY_BLUE_7, use_for_approximations=True)  # 23 (orig. DeepSkyBlue4)
    XTERM_DODGER_BLUE_1 = ColorIndexed(0x0087ff, IntCodes.XTERM_DODGER_BLUE_1, use_for_approximations=True)  # 33
    XTERM_DODGER_BLUE_2 = ColorIndexed(0x005fff, IntCodes.XTERM_DODGER_BLUE_2, use_for_approximations=True)  # 27
    XTERM_DODGER_BLUE_3 = ColorIndexed(0x005fd7, IntCodes.XTERM_DODGER_BLUE_3, use_for_approximations=True)  # 26
    XTERM_FUCHSIA = ColorIndexed(0xff00ff, IntCodes.XTERM_FUCHSIA)  # 13
    XTERM_GOLD_1 = ColorIndexed(0xffd700, IntCodes.XTERM_GOLD_1, use_for_approximations=True)  # 220
    XTERM_GOLD_2 = ColorIndexed(0xd7af00, IntCodes.XTERM_GOLD_2, use_for_approximations=True)  # 178 (orig. Gold3)
    XTERM_GOLD_3 = ColorIndexed(0xafaf00, IntCodes.XTERM_GOLD_3, use_for_approximations=True)  # 142
    XTERM_GREEN_2 = ColorIndexed(0x00ff00, IntCodes.XTERM_GREEN_2, use_for_approximations=True)  # 46 (orig. Green1)
    XTERM_GREEN_3 = ColorIndexed(0x00d700, IntCodes.XTERM_GREEN_3, use_for_approximations=True)  # 40
    XTERM_GREEN_4 = ColorIndexed(0x00af00, IntCodes.XTERM_GREEN_4, use_for_approximations=True)  # 34 (orig. Green3)
    XTERM_GREEN_5 = ColorIndexed(0x008700, IntCodes.XTERM_GREEN_5, use_for_approximations=True)  # 28 (orig. Green4)
    XTERM_GREEN = ColorIndexed(0x008000, IntCodes.XTERM_GREEN)  # 2
    XTERM_GREEN_YELLOW = ColorIndexed(0xafff00, IntCodes.XTERM_GREEN_YELLOW, use_for_approximations=True)  # 154
    XTERM_GREY_100 = ColorIndexed(0xffffff, IntCodes.XTERM_GREY_100, use_for_approximations=True)  # 231
    XTERM_GREY_93 = ColorIndexed(0xeeeeee, IntCodes.XTERM_GREY_93, use_for_approximations=True)  # 255
    XTERM_GREY_89 = ColorIndexed(0xe4e4e4, IntCodes.XTERM_GREY_89, use_for_approximations=True)  # 254
    XTERM_GREY_85 = ColorIndexed(0xdadada, IntCodes.XTERM_GREY_85, use_for_approximations=True)  # 253
    XTERM_GREY_84 = ColorIndexed(0xd7d7d7, IntCodes.XTERM_GREY_84, use_for_approximations=True)  # 188
    XTERM_GREY_82 = ColorIndexed(0xd0d0d0, IntCodes.XTERM_GREY_82, use_for_approximations=True)  # 252
    XTERM_GREY_78 = ColorIndexed(0xc6c6c6, IntCodes.XTERM_GREY_78, use_for_approximations=True)  # 251
    XTERM_GREY_74 = ColorIndexed(0xbcbcbc, IntCodes.XTERM_GREY_74, use_for_approximations=True)  # 250
    XTERM_GREY_70 = ColorIndexed(0xb2b2b2, IntCodes.XTERM_GREY_70, use_for_approximations=True)  # 249
    XTERM_GREY_69 = ColorIndexed(0xafafaf, IntCodes.XTERM_GREY_69, use_for_approximations=True)  # 145
    XTERM_GREY_66 = ColorIndexed(0xa8a8a8, IntCodes.XTERM_GREY_66, use_for_approximations=True)  # 248
    XTERM_GREY_63 = ColorIndexed(0xaf87af, IntCodes.XTERM_GREY_63, use_for_approximations=True)  # 139
    XTERM_GREY_62 = ColorIndexed(0x9e9e9e, IntCodes.XTERM_GREY_62, use_for_approximations=True)  # 247
    XTERM_GREY_58 = ColorIndexed(0x949494, IntCodes.XTERM_GREY_58, use_for_approximations=True)  # 246
    XTERM_GREY_54 = ColorIndexed(0x8a8a8a, IntCodes.XTERM_GREY_54, use_for_approximations=True)  # 245
    XTERM_GREY_53 = ColorIndexed(0x878787, IntCodes.XTERM_GREY_53, use_for_approximations=True)  # 102
    XTERM_GREY = ColorIndexed(0x808080, IntCodes.XTERM_GREY)  # 8
    XTERM_GREY_50 = ColorIndexed(0x808080, IntCodes.XTERM_GREY_50, use_for_approximations=True)  # 244
    XTERM_GREY_46 = ColorIndexed(0x767676, IntCodes.XTERM_GREY_46, use_for_approximations=True)  # 243
    XTERM_GREY_42 = ColorIndexed(0x6c6c6c, IntCodes.XTERM_GREY_42, use_for_approximations=True)  # 242
    XTERM_GREY_39 = ColorIndexed(0x626262, IntCodes.XTERM_GREY_39, use_for_approximations=True)  # 241
    XTERM_GREY_37 = ColorIndexed(0x5f5f5f, IntCodes.XTERM_GREY_37, use_for_approximations=True)  # 59
    XTERM_GREY_35 = ColorIndexed(0x585858, IntCodes.XTERM_GREY_35, use_for_approximations=True)  # 240
    XTERM_GREY_30 = ColorIndexed(0x4e4e4e, IntCodes.XTERM_GREY_30, use_for_approximations=True)  # 239
    XTERM_GREY_27 = ColorIndexed(0x444444, IntCodes.XTERM_GREY_27, use_for_approximations=True)  # 238
    XTERM_GREY_23 = ColorIndexed(0x3a3a3a, IntCodes.XTERM_GREY_23, use_for_approximations=True)  # 237
    XTERM_GREY_19 = ColorIndexed(0x303030, IntCodes.XTERM_GREY_19, use_for_approximations=True)  # 236
    XTERM_GREY_15 = ColorIndexed(0x262626, IntCodes.XTERM_GREY_15, use_for_approximations=True)  # 235
    XTERM_GREY_11 = ColorIndexed(0x1c1c1c, IntCodes.XTERM_GREY_11, use_for_approximations=True)  # 234
    XTERM_GREY_7 = ColorIndexed(0x121212, IntCodes.XTERM_GREY_7, use_for_approximations=True)  # 233
    XTERM_GREY_3 = ColorIndexed(0x080808, IntCodes.XTERM_GREY_3, use_for_approximations=True)  # 232
    XTERM_GREY_0 = ColorIndexed(0x000000, IntCodes.XTERM_GREY_0, use_for_approximations=True)  # 16
    XTERM_HONEYDEW_2 = ColorIndexed(0xd7ffd7, IntCodes.XTERM_HONEYDEW_2, use_for_approximations=True)  # 194
    XTERM_HOT_PINK = ColorIndexed(0xff5fd7, IntCodes.XTERM_HOT_PINK, use_for_approximations=True)  # 206
    XTERM_HOT_PINK_2 = ColorIndexed(0xff5faf, IntCodes.XTERM_HOT_PINK_2, use_for_approximations=True)  # 205 (orig. HotPink)
    XTERM_HOT_PINK_3 = ColorIndexed(0xd75faf, IntCodes.XTERM_HOT_PINK_3, use_for_approximations=True)  # 169 (orig. HotPink2)
    XTERM_HOT_PINK_4 = ColorIndexed(0xd75f87, IntCodes.XTERM_HOT_PINK_4, use_for_approximations=True)  # 168 (orig. HotPink3)
    XTERM_HOT_PINK_5 = ColorIndexed(0xaf5f87, IntCodes.XTERM_HOT_PINK_5, use_for_approximations=True)  # 132 (orig. HotPink3)
    XTERM_INDIAN_RED_2 = ColorIndexed(0xff5f87, IntCodes.XTERM_INDIAN_RED_2, use_for_approximations=True)  # 204 (orig. IndianRed1)
    XTERM_INDIAN_RED_1 = ColorIndexed(0xff5f5f, IntCodes.XTERM_INDIAN_RED_1, use_for_approximations=True)  # 203
    XTERM_INDIAN_RED_3 = ColorIndexed(0xd75f5f, IntCodes.XTERM_INDIAN_RED_3, use_for_approximations=True)  # 167 (orig. IndianRed)
    XTERM_INDIAN_RED_4 = ColorIndexed(0xaf5f5f, IntCodes.XTERM_INDIAN_RED_4, use_for_approximations=True)  # 131 (orig. IndianRed)
    XTERM_KHAKI_1 = ColorIndexed(0xffff87, IntCodes.XTERM_KHAKI_1, use_for_approximations=True)  # 228
    XTERM_KHAKI_3 = ColorIndexed(0xd7d75f, IntCodes.XTERM_KHAKI_3, use_for_approximations=True)  # 185
    XTERM_LIGHT_CORAL = ColorIndexed(0xff8787, IntCodes.XTERM_LIGHT_CORAL, use_for_approximations=True)  # 210
    XTERM_LIGHT_CYAN_1 = ColorIndexed(0xd7ffff, IntCodes.XTERM_LIGHT_CYAN_1, use_for_approximations=True)  # 195
    XTERM_LIGHT_CYAN_3 = ColorIndexed(0xafd7d7, IntCodes.XTERM_LIGHT_CYAN_3, use_for_approximations=True)  # 152
    XTERM_LIGHT_GOLDENROD_2 = ColorIndexed(0xffd787, IntCodes.XTERM_LIGHT_GOLDENROD_2, use_for_approximations=True)  # 222
    XTERM_LIGHT_GOLDENROD_1 = ColorIndexed(0xffff5f, IntCodes.XTERM_LIGHT_GOLDENROD_1, use_for_approximations=True)  # 227
    XTERM_LIGHT_GOLDENROD_3 = ColorIndexed(0xd7d787, IntCodes.XTERM_LIGHT_GOLDENROD_3, use_for_approximations=True)  # 186 (orig. LightGoldenrod2)
    XTERM_LIGHT_GOLDENROD_4 = ColorIndexed(0xffd75f, IntCodes.XTERM_LIGHT_GOLDENROD_4, use_for_approximations=True)  # 221 (orig. LightGoldenrod2)
    XTERM_LIGHT_GOLDENROD_5 = ColorIndexed(0xd7af5f, IntCodes.XTERM_LIGHT_GOLDENROD_5, use_for_approximations=True)  # 179 (orig. LightGoldenrod3)
    XTERM_LIGHT_GREEN = ColorIndexed(0x87ff87, IntCodes.XTERM_LIGHT_GREEN, use_for_approximations=True)  # 120
    XTERM_LIGHT_GREEN_2 = ColorIndexed(0x87ff5f, IntCodes.XTERM_LIGHT_GREEN_2, use_for_approximations=True)  # 119 (orig. LightGreen)
    XTERM_LIGHT_PINK_1 = ColorIndexed(0xffafaf, IntCodes.XTERM_LIGHT_PINK_1, use_for_approximations=True)  # 217
    XTERM_LIGHT_PINK_2 = ColorIndexed(0xd78787, IntCodes.XTERM_LIGHT_PINK_2, use_for_approximations=True)  # 174 (orig. LightPink3)
    XTERM_LIGHT_PINK_3 = ColorIndexed(0x875f5f, IntCodes.XTERM_LIGHT_PINK_3, use_for_approximations=True)  # 95 (orig. LightPink4)
    XTERM_LIGHT_SALMON_1 = ColorIndexed(0xffaf87, IntCodes.XTERM_LIGHT_SALMON_1, use_for_approximations=True)  # 216
    XTERM_LIGHT_SALMON_2 = ColorIndexed(0xd7875f, IntCodes.XTERM_LIGHT_SALMON_2, use_for_approximations=True)  # 173 (orig. LightSalmon3)
    XTERM_LIGHT_SALMON_3 = ColorIndexed(0xaf875f, IntCodes.XTERM_LIGHT_SALMON_3, use_for_approximations=True)  # 137
    XTERM_LIGHT_SEA_GREEN = ColorIndexed(0x00afaf, IntCodes.XTERM_LIGHT_SEA_GREEN, use_for_approximations=True)  # 37
    XTERM_LIGHT_SKY_BLUE_1 = ColorIndexed(0xafd7ff, IntCodes.XTERM_LIGHT_SKY_BLUE_1, use_for_approximations=True)  # 153
    XTERM_LIGHT_SKY_BLUE_2 = ColorIndexed(0x87afd7, IntCodes.XTERM_LIGHT_SKY_BLUE_2, use_for_approximations=True)  # 110 (orig. LightSkyBlue3)
    XTERM_LIGHT_SKY_BLUE_3 = ColorIndexed(0x87afaf, IntCodes.XTERM_LIGHT_SKY_BLUE_3, use_for_approximations=True)  # 109
    XTERM_LIGHT_SLATE_BLUE = ColorIndexed(0x8787ff, IntCodes.XTERM_LIGHT_SLATE_BLUE, use_for_approximations=True)  # 105
    XTERM_LIGHT_SLATE_GREY = ColorIndexed(0x8787af, IntCodes.XTERM_LIGHT_SLATE_GREY, use_for_approximations=True)  # 103
    XTERM_LIGHT_STEEL_BLUE_1 = ColorIndexed(0xd7d7ff, IntCodes.XTERM_LIGHT_STEEL_BLUE_1, use_for_approximations=True)  # 189
    XTERM_LIGHT_STEEL_BLUE_2 = ColorIndexed(0xafafff, IntCodes.XTERM_LIGHT_STEEL_BLUE_2, use_for_approximations=True)  # 147 (orig. LightSteelBlue)
    XTERM_LIGHT_STEEL_BLUE_3 = ColorIndexed(0xafafd7, IntCodes.XTERM_LIGHT_STEEL_BLUE_3, use_for_approximations=True)  # 146
    XTERM_LIGHT_YELLOW_3 = ColorIndexed(0xd7d7af, IntCodes.XTERM_LIGHT_YELLOW_3, use_for_approximations=True)  # 187
    XTERM_LIME = ColorIndexed(0x00ff00, IntCodes.XTERM_LIME)  # 10
    XTERM_MAGENTA_1 = ColorIndexed(0xff00ff, IntCodes.XTERM_MAGENTA_1, use_for_approximations=True)  # 201
    XTERM_MAGENTA_4 = ColorIndexed(0xd700ff, IntCodes.XTERM_MAGENTA_4, use_for_approximations=True)  # 165 (orig. Magenta2)
    XTERM_MAGENTA_2 = ColorIndexed(0xff00d7, IntCodes.XTERM_MAGENTA_2, use_for_approximations=True)  # 200
    XTERM_MAGENTA_5 = ColorIndexed(0xd700d7, IntCodes.XTERM_MAGENTA_5, use_for_approximations=True)  # 164 (orig. Magenta3)
    XTERM_MAGENTA_3 = ColorIndexed(0xd700af, IntCodes.XTERM_MAGENTA_3, use_for_approximations=True)  # 163
    XTERM_MAGENTA_6 = ColorIndexed(0xaf00af, IntCodes.XTERM_MAGENTA_6, use_for_approximations=True)  # 127 (orig. Magenta3)
    XTERM_MAROON = ColorIndexed(0x800000, IntCodes.XTERM_MAROON)  # 1
    XTERM_MEDIUM_ORCHID_1 = ColorIndexed(0xff5fff, IntCodes.XTERM_MEDIUM_ORCHID_1, use_for_approximations=True)  # 207
    XTERM_MEDIUM_ORCHID_2 = ColorIndexed(0xd75fff, IntCodes.XTERM_MEDIUM_ORCHID_2, use_for_approximations=True)  # 171 (orig. MediumOrchid1)
    XTERM_MEDIUM_ORCHID_3 = ColorIndexed(0xaf5fd7, IntCodes.XTERM_MEDIUM_ORCHID_3, use_for_approximations=True)  # 134 (orig. MediumOrchid)
    XTERM_MEDIUM_ORCHID_4 = ColorIndexed(0xaf5faf, IntCodes.XTERM_MEDIUM_ORCHID_4, use_for_approximations=True)  # 133 (orig. MediumOrchid3)
    XTERM_MEDIUM_PURPLE_1 = ColorIndexed(0xaf87ff, IntCodes.XTERM_MEDIUM_PURPLE_1, use_for_approximations=True)  # 141
    XTERM_MEDIUM_PURPLE_2 = ColorIndexed(0xaf5fff, IntCodes.XTERM_MEDIUM_PURPLE_2, use_for_approximations=True)  # 135
    XTERM_MEDIUM_PURPLE_3 = ColorIndexed(0xaf87d7, IntCodes.XTERM_MEDIUM_PURPLE_3, use_for_approximations=True)  # 140 (orig. MediumPurple2)
    XTERM_MEDIUM_PURPLE_4 = ColorIndexed(0x8787d7, IntCodes.XTERM_MEDIUM_PURPLE_4, use_for_approximations=True)  # 104 (orig. MediumPurple)
    XTERM_MEDIUM_PURPLE_5 = ColorIndexed(0x875fd7, IntCodes.XTERM_MEDIUM_PURPLE_5, use_for_approximations=True)  # 98 (orig. MediumPurple3)
    XTERM_MEDIUM_PURPLE_6 = ColorIndexed(0x875faf, IntCodes.XTERM_MEDIUM_PURPLE_6, use_for_approximations=True)  # 97 (orig. MediumPurple3)
    XTERM_MEDIUM_PURPLE_7 = ColorIndexed(0x5f5f87, IntCodes.XTERM_MEDIUM_PURPLE_7, use_for_approximations=True)  # 60 (orig. MediumPurple4)
    XTERM_MEDIUM_SPRING_GREEN = ColorIndexed(0x00ffaf, IntCodes.XTERM_MEDIUM_SPRING_GREEN, use_for_approximations=True)  # 49
    XTERM_MEDIUM_TURQUOISE = ColorIndexed(0x5fd7d7, IntCodes.XTERM_MEDIUM_TURQUOISE, use_for_approximations=True)  # 80
    XTERM_MEDIUM_VIOLET_RED = ColorIndexed(0xaf0087, IntCodes.XTERM_MEDIUM_VIOLET_RED, use_for_approximations=True)  # 126
    XTERM_MISTY_ROSE_1 = ColorIndexed(0xffd7d7, IntCodes.XTERM_MISTY_ROSE_1, use_for_approximations=True)  # 224
    XTERM_MISTY_ROSE_3 = ColorIndexed(0xd7afaf, IntCodes.XTERM_MISTY_ROSE_3, use_for_approximations=True)  # 181
    XTERM_NAVAJO_WHITE_1 = ColorIndexed(0xffd7af, IntCodes.XTERM_NAVAJO_WHITE_1, use_for_approximations=True)  # 223
    XTERM_NAVAJO_WHITE_3 = ColorIndexed(0xafaf87, IntCodes.XTERM_NAVAJO_WHITE_3, use_for_approximations=True)  # 144
    XTERM_NAVY = ColorIndexed(0x000080, IntCodes.XTERM_NAVY)  # 4
    XTERM_NAVY_BLUE = ColorIndexed(0x00005f, IntCodes.XTERM_NAVY_BLUE, use_for_approximations=True)  # 17
    XTERM_OLIVE = ColorIndexed(0x808000, IntCodes.XTERM_OLIVE)  # 3
    XTERM_ORANGE_1 = ColorIndexed(0xffaf00, IntCodes.XTERM_ORANGE_1, use_for_approximations=True)  # 214
    XTERM_ORANGE_2 = ColorIndexed(0xd78700, IntCodes.XTERM_ORANGE_2, use_for_approximations=True)  # 172 (orig. Orange3)
    XTERM_ORANGE_3 = ColorIndexed(0x875f00, IntCodes.XTERM_ORANGE_3, use_for_approximations=True)  # 94 (orig. Orange4)
    XTERM_ORANGE_4 = ColorIndexed(0x5f5f00, IntCodes.XTERM_ORANGE_4, use_for_approximations=True)  # 58
    XTERM_ORANGE_RED_1 = ColorIndexed(0xff5f00, IntCodes.XTERM_ORANGE_RED_1, use_for_approximations=True)  # 202
    XTERM_ORCHID_1 = ColorIndexed(0xff87ff, IntCodes.XTERM_ORCHID_1, use_for_approximations=True)  # 213
    XTERM_ORCHID_2 = ColorIndexed(0xff87d7, IntCodes.XTERM_ORCHID_2, use_for_approximations=True)  # 212
    XTERM_ORCHID_3 = ColorIndexed(0xd75fd7, IntCodes.XTERM_ORCHID_3, use_for_approximations=True)  # 170 (orig. Orchid)
    XTERM_PALE_GREEN_1 = ColorIndexed(0x87ffaf, IntCodes.XTERM_PALE_GREEN_1, use_for_approximations=True)  # 121
    XTERM_PALE_GREEN_2 = ColorIndexed(0xafff87, IntCodes.XTERM_PALE_GREEN_2, use_for_approximations=True)  # 156 (orig. PaleGreen1)
    XTERM_PALE_GREEN_3 = ColorIndexed(0x87d787, IntCodes.XTERM_PALE_GREEN_3, use_for_approximations=True)  # 114
    XTERM_PALE_GREEN_4 = ColorIndexed(0x5fd75f, IntCodes.XTERM_PALE_GREEN_4, use_for_approximations=True)  # 77 (orig. PaleGreen3)
    XTERM_PALE_TURQUOISE_1 = ColorIndexed(0xafffff, IntCodes.XTERM_PALE_TURQUOISE_1, use_for_approximations=True)  # 159
    XTERM_PALE_TURQUOISE_4 = ColorIndexed(0x5f8787, IntCodes.XTERM_PALE_TURQUOISE_4, use_for_approximations=True)  # 66
    XTERM_PALE_VIOLET_RED_1 = ColorIndexed(0xff87af, IntCodes.XTERM_PALE_VIOLET_RED_1, use_for_approximations=True)  # 211
    XTERM_PINK_1 = ColorIndexed(0xffafd7, IntCodes.XTERM_PINK_1, use_for_approximations=True)  # 218
    XTERM_PINK_3 = ColorIndexed(0xd787af, IntCodes.XTERM_PINK_3, use_for_approximations=True)  # 175
    XTERM_PLUM_1 = ColorIndexed(0xffafff, IntCodes.XTERM_PLUM_1, use_for_approximations=True)  # 219
    XTERM_PLUM_2 = ColorIndexed(0xd7afff, IntCodes.XTERM_PLUM_2, use_for_approximations=True)  # 183
    XTERM_PLUM_3 = ColorIndexed(0xd787d7, IntCodes.XTERM_PLUM_3, use_for_approximations=True)  # 176
    XTERM_PLUM_4 = ColorIndexed(0x875f87, IntCodes.XTERM_PLUM_4, use_for_approximations=True)  # 96
    XTERM_PURPLE = ColorIndexed(0xaf00ff, IntCodes.XTERM_PURPLE, use_for_approximations=True)  # 129
    XTERM_PURPLE_2 = ColorIndexed(0x8700ff, IntCodes.XTERM_PURPLE_2, use_for_approximations=True)  # 93 (orig. Purple)
    XTERM_PURPLE_3 = ColorIndexed(0x5f00d7, IntCodes.XTERM_PURPLE_3, use_for_approximations=True)  # 56
    XTERM_PURPLE_4 = ColorIndexed(0x5f00af, IntCodes.XTERM_PURPLE_4, use_for_approximations=True)  # 55
    XTERM_PURPLE_5 = ColorIndexed(0x800080, IntCodes.XTERM_PURPLE_5)  # 5 (orig. Purple)
    XTERM_PURPLE_6 = ColorIndexed(0x5f0087, IntCodes.XTERM_PURPLE_6, use_for_approximations=True)  # 54 (orig. Purple4)
    XTERM_RED = ColorIndexed(0xff0000, IntCodes.XTERM_RED)  # 9
    XTERM_RED_1 = ColorIndexed(0xff0000, IntCodes.XTERM_RED_1, use_for_approximations=True)  # 196
    XTERM_RED_3 = ColorIndexed(0xd70000, IntCodes.XTERM_RED_3, use_for_approximations=True)  # 160
    XTERM_RED_4 = ColorIndexed(0xaf0000, IntCodes.XTERM_RED_4, use_for_approximations=True)  # 124 (orig. Red3)
    XTERM_ROSY_BROWN = ColorIndexed(0xaf8787, IntCodes.XTERM_ROSY_BROWN, use_for_approximations=True)  # 138
    XTERM_ROYAL_BLUE_1 = ColorIndexed(0x5f5fff, IntCodes.XTERM_ROYAL_BLUE_1, use_for_approximations=True)  # 63
    XTERM_SALMON_1 = ColorIndexed(0xff875f, IntCodes.XTERM_SALMON_1, use_for_approximations=True)  # 209
    XTERM_SANDY_BROWN = ColorIndexed(0xffaf5f, IntCodes.XTERM_SANDY_BROWN, use_for_approximations=True)  # 215
    XTERM_SEA_GREEN_1 = ColorIndexed(0x5fffaf, IntCodes.XTERM_SEA_GREEN_1, use_for_approximations=True)  # 85
    XTERM_SEA_GREEN_2 = ColorIndexed(0x5fff87, IntCodes.XTERM_SEA_GREEN_2, use_for_approximations=True)  # 84 (orig. SeaGreen1)
    XTERM_SEA_GREEN_3 = ColorIndexed(0x5fd787, IntCodes.XTERM_SEA_GREEN_3, use_for_approximations=True)  # 78
    XTERM_SEA_GREEN_4 = ColorIndexed(0x5fff5f, IntCodes.XTERM_SEA_GREEN_4, use_for_approximations=True)  # 83 (orig. SeaGreen2)
    XTERM_SILVER = ColorIndexed(0xc0c0c0, IntCodes.XTERM_SILVER)  # 7
    XTERM_SKY_BLUE_1 = ColorIndexed(0x87d7ff, IntCodes.XTERM_SKY_BLUE_1, use_for_approximations=True)  # 117
    XTERM_SKY_BLUE_2 = ColorIndexed(0x87afff, IntCodes.XTERM_SKY_BLUE_2, use_for_approximations=True)  # 111
    XTERM_SKY_BLUE_3 = ColorIndexed(0x5fafd7, IntCodes.XTERM_SKY_BLUE_3, use_for_approximations=True)  # 74
    XTERM_SLATE_BLUE_1 = ColorIndexed(0x875fff, IntCodes.XTERM_SLATE_BLUE_1, use_for_approximations=True)  # 99
    XTERM_SLATE_BLUE_2 = ColorIndexed(0x5f5fd7, IntCodes.XTERM_SLATE_BLUE_2, use_for_approximations=True)  # 62 (orig. SlateBlue3)
    XTERM_SLATE_BLUE_3 = ColorIndexed(0x5f5faf, IntCodes.XTERM_SLATE_BLUE_3, use_for_approximations=True)  # 61
    XTERM_SPRING_GREEN_1 = ColorIndexed(0x00ff87, IntCodes.XTERM_SPRING_GREEN_1, use_for_approximations=True)  # 48
    XTERM_SPRING_GREEN_6 = ColorIndexed(0x00d787, IntCodes.XTERM_SPRING_GREEN_6, use_for_approximations=True)  # 42 (orig. SpringGreen2)
    XTERM_SPRING_GREEN_2 = ColorIndexed(0x00ff5f, IntCodes.XTERM_SPRING_GREEN_2, use_for_approximations=True)  # 47
    XTERM_SPRING_GREEN_3 = ColorIndexed(0x00d75f, IntCodes.XTERM_SPRING_GREEN_3, use_for_approximations=True)  # 41
    XTERM_SPRING_GREEN_5 = ColorIndexed(0x00af5f, IntCodes.XTERM_SPRING_GREEN_5, use_for_approximations=True)  # 35 (orig. SpringGreen3)
    XTERM_SPRING_GREEN_4 = ColorIndexed(0x00875f, IntCodes.XTERM_SPRING_GREEN_4, use_for_approximations=True)  # 29
    XTERM_STEEL_BLUE_1 = ColorIndexed(0x5fd7ff, IntCodes.XTERM_STEEL_BLUE_1, use_for_approximations=True)  # 81
    XTERM_STEEL_BLUE_2 = ColorIndexed(0x5fafff, IntCodes.XTERM_STEEL_BLUE_2, use_for_approximations=True)  # 75 (orig. SteelBlue1)
    XTERM_STEEL_BLUE_3 = ColorIndexed(0x5f87d7, IntCodes.XTERM_STEEL_BLUE_3, use_for_approximations=True)  # 68
    XTERM_STEEL_BLUE = ColorIndexed(0x5f87af, IntCodes.XTERM_STEEL_BLUE, use_for_approximations=True)  # 67
    XTERM_TAN = ColorIndexed(0xd7af87, IntCodes.XTERM_TAN, use_for_approximations=True)  # 180
    XTERM_TEAL = ColorIndexed(0x008080, IntCodes.XTERM_TEAL)  # 6
    XTERM_THISTLE_1 = ColorIndexed(0xffd7ff, IntCodes.XTERM_THISTLE_1, use_for_approximations=True)  # 225
    XTERM_THISTLE_3 = ColorIndexed(0xd7afd7, IntCodes.XTERM_THISTLE_3, use_for_approximations=True)  # 182
    XTERM_TURQUOISE_2 = ColorIndexed(0x00d7ff, IntCodes.XTERM_TURQUOISE_2, use_for_approximations=True)  # 45
    XTERM_TURQUOISE_4 = ColorIndexed(0x008787, IntCodes.XTERM_TURQUOISE_4, use_for_approximations=True)  # 30
    XTERM_VIOLET = ColorIndexed(0xd787ff, IntCodes.XTERM_VIOLET, use_for_approximations=True)  # 177
    XTERM_WHEAT_1 = ColorIndexed(0xffffaf, IntCodes.XTERM_WHEAT_1, use_for_approximations=True)  # 229
    XTERM_WHEAT_4 = ColorIndexed(0x87875f, IntCodes.XTERM_WHEAT_4, use_for_approximations=True)  # 101
    XTERM_WHITE = ColorIndexed(0xffffff, IntCodes.XTERM_WHITE)  # 15
    XTERM_YELLOW = ColorIndexed(0xffff00, IntCodes.XTERM_YELLOW)  # 11
    XTERM_YELLOW_1 = ColorIndexed(0xffff00, IntCodes.XTERM_YELLOW_1, use_for_approximations=True)  # 226
    XTERM_YELLOW_2 = ColorIndexed(0xd7ff00, IntCodes.XTERM_YELLOW_2, use_for_approximations=True)  # 190
    XTERM_YELLOW_3 = ColorIndexed(0xd7d700, IntCodes.XTERM_YELLOW_3, use_for_approximations=True)  # 184
    XTERM_YELLOW_5 = ColorIndexed(0xafd700, IntCodes.XTERM_YELLOW_5, use_for_approximations=True)  # 148 (orig. Yellow3)
    XTERM_YELLOW_4 = ColorIndexed(0x87af00, IntCodes.XTERM_YELLOW_4, use_for_approximations=True)  # 106
    XTERM_YELLOW_6 = ColorIndexed(0x878700, IntCodes.XTERM_YELLOW_6, use_for_approximations=True)  # 100 (orig. Yellow4)
