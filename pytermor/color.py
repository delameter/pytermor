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

import logging
from abc import abstractmethod, ABCMeta
from typing import Dict, Tuple, Generic, TypeVar, List, Optional

from .common import LogicError
from .ansi import SequenceSGR, NOOP_SEQ


class Color(metaclass=ABCMeta):
    """
    Abstract superclass for other ``Colors``.
    """
    _approx_initialized: bool = False
    _approx: Approximator[Color]

    def __init__(self, hex_value: int = None, use_for_approximations: bool = True):
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

    def format_value(self, prefix: str|None = '0x', noop_str: str = '^') -> str:
        if self._hex_value is None:
            return noop_str
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
        from . import Colors
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
    _index: Dict[int, ColorIndexed] = dict()  # @TODO get color by int code. replace 0-15 ColorIndexed with ColorDefault? or keep them separated

    def __init__(self, hex_value: int, code: int, use_for_approximations=True):
        self._code = code
        super().__init__(hex_value, use_for_approximations)

        if not self._index.get(self._code):
            self._index[self._code] = self
        else:
            logging.warning(f'Indexed color duplicate by code {self._code} '
                            f'detected: {self}. It was NOT added to the index.')

    @classmethod
    def get_default(cls) -> ColorIndexed:
        from . import Colors
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
        from . import Colors
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
            be returned. Another option is to use special "color" named `NOOP_COLOR`.

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


NOOP_COLOR = ColorRGB()
"""
Special instance of `Color` class always rendering into empty string.
"""
