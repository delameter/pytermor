# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""
.. testsetup:: *

    from pytermor.color import *

"""
from __future__ import annotations

import dataclasses
import math
import re
import typing as t
from abc import ABCMeta, abstractmethod

from .ansi import (
    SequenceSGR,
    NOOP_SEQ,
    HI_COLORS,
    BG_HI_COLORS,
    make_color_256,
    make_color_rgb,
)

ColorType = t.TypeVar("ColorType", "Color16", "Color256", "ColorRGB")
""" :meta public: """


class _ColorRegistry(t.Generic[ColorType], t.Sized):
    _TOKEN_SEPARATOR = "-"
    _QUERY_SPLIT_REGEX = re.compile(r"[\W_]+|(?<=[a-z])(?=[A-Z0-9])")

    def __init__(self):
        self._map: t.Dict[t.Tuple[str], ColorType] = {}

    def register(self, color: ColorType, name: str):
        primary_tokens = tuple(self._QUERY_SPLIT_REGEX.split(name))
        self._register_pair(color, primary_tokens)

        for variation in color.variations.values():
            variation_tokens: t.Tuple[str, ...] = (
                *primary_tokens,
                *(self._QUERY_SPLIT_REGEX.split(variation.name)),
            )
            self._register_pair(variation, variation_tokens)

    def _register_pair(self, color: ColorType, tokens: t.Tuple[str, ...]):
        if tokens not in self._map.keys():
            self._map[tokens] = color
            return

        existing_color = self._map.get(tokens)
        if color.hex_value == existing_color.hex_value:
            return  # skipping the duplicate with the same name and value
        raise ColorNameConflictError(tokens, existing_color, color)

    def resolve(self, name: str) -> ColorType:
        query_tokens = (*(qt.lower() for qt in self._QUERY_SPLIT_REGEX.split(name)),)
        if color := self._map.get(query_tokens, None):
            return color
        raise ValueError(f"Color '{name}' does not exist")

    def __len__(self) -> int:
        return len(self._map)


class _ColorIndex(t.Generic[ColorType], t.Sized):
    def __init__(self):
        self._map: t.Dict[int, _ColorChannels[ColorType]] = {}

    def add(self, color: ColorType, code: int = None):
        if code is None:
            code = len(self._map)
        if code not in self._map.keys():
            self._map[code] = _ColorChannels(color)
            return

        existing_color = self._map.get(code).color
        if color.hex_value == existing_color.hex_value:
            return  # skipping the duplicate with the same code and value
        raise ColorCodeConflictError(code, existing_color, color)

    def get(self, code: int) -> ColorType:
        if channels := self._map.get(code, None):
            return channels.color
        raise KeyError(f"Color #{code} does not exist")

    def __len__(self) -> int:
        return len(self._map)

    @property
    def values(self) -> t.Iterable[_ColorChannels[ColorType]]:
        return self._map.values()


class _ColorChannels(t.Generic[ColorType]):
    def __init__(self, color: ColorType):
        self.color: ColorType = color
        self.r, self.g, self.b = self.color.to_rgb()


@dataclasses.dataclass(frozen=True)
class ApproximationResult(t.Generic[ColorType]):
    """
    :param color:    `Color` instance.
    :param distance: Squared sRGB distance from this instance to
                     the approximation target.
    """
    color: ColorType
    distance: int

    @property
    def distance_real(self) -> float:
        """
        Actual distance from instance to target: Sqrt(distance).
        """
        return math.sqrt(self.distance)


class Color(metaclass=ABCMeta):
    """
    Abstract superclass for other ``Colors``.
    """

    # class vars #
    _registry: _ColorRegistry
    _index: _ColorIndex
    _approx_cache: t.Dict[int, ColorType]

    @classmethod
    def __new__(cls, *args, **kwargs):
        # fmt: off
        if not hasattr(cls, "_registry"):     cls._registry = _ColorRegistry[cls]()
        if not hasattr(cls, "_index"):        cls._index = _ColorIndex[cls]()
        if not hasattr(cls, "_approx_cache"): cls._approx_cache = dict()
        return super().__new__(cls)
        # fmt: on

    def __init__(self, hex_value: int, name: str = None):
        self._hex_value: int = hex_value
        self._name: str | None = name
        self._base: ColorType | None = None
        self._variations: t.Dict[str, ColorType] = {}

    def _post_init(
        self: ColorType,
        code: int | None,
        aliases: t.List[str],
        variation_map: t.Dict[int, str],
        register: bool,
        index: bool,
    ):
        self._make_variations(variation_map)
        if register:
            self._register_names(aliases)
        if index:
            self._index.add(self, code)

    def _register_names(self: ColorType, aliases: t.List[str] = None):
        if not self.name:
            return
        self._registry.register(self, self.name)

        if not aliases:
            return
        for alias in aliases:
            self._registry.register(self, alias)

    def _make_variations(self: ColorType, variation_map: t.Dict[int, str] = None):
        if not variation_map:
            return

        # @TODO rewrite this part later. don't like that entity relationship attributes
        #       are being set in some indistinct method, not in the constructor.
        for vari_hex_value, vari_name in variation_map.items():
            variation = type(self)(
                hex_value=vari_hex_value, name=vari_name, register=False, index=True
            )  # registration will be made by registry itself
            variation._base = self
            self._variations[vari_name] = variation

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._hex_value == other._hex_value

    def to_hsv(self) -> t.Tuple[float, float, float]:
        """

        :return:
        """
        return self.hex_to_hsv(self._hex_value)

    def to_rgb(self) -> t.Tuple[int, int, int]:
        """

        :return:
        """
        return self.hex_to_rgb(self._hex_value)

    def format_value(self, prefix: str = "0x") -> str:
        """

        :param prefix:
        :return:
        """
        return f"{prefix:s}{self._hex_value:06X}"

    @property
    def hex_value(self) -> int:
        """

        :return:
        """
        return self._hex_value

    @property
    def name(self) -> str | None:
        """
        
        :return:
        """
        return self._name

    @property
    def base(self) -> ColorType | None:
        """

        :return:
        """
        return self._base

    @property
    def variations(self) -> t.Dict[str, ColorType]:
        """

        :return:
        """
        return self._variations

    def _repr(self, *params: t.Any) -> str:  # pragma: no cover
        params_str = ",".join(str(s) for s in filter(None, params))
        return f"<{self.__class__.__name__}[{params_str}]>"

    @abstractmethod
    def to_sgr(self, bg: bool, upper_bound: t.Type[Color] = None) -> SequenceSGR:
        """

        :param bg:
        :param upper_bound:
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def to_tmux(self, bg: bool) -> str:
        """

        :param bg:
        :return:
        """
        raise NotImplementedError

    @classmethod
    def get_by_code(cls: t.Type[ColorType], code: int) -> ColorType:
        """

        :param code:
        :return:
        """
        if not hasattr(cls, "_index"):
            raise RuntimeError(
                "Unable to find color maps. Use concrete class instead of "
                "abstract Color, e.g.: Color16.get_by_code()"
            )
        return cls._index.get(code)

    @classmethod
    def resolve(cls: t.Type[ColorType], name: str) -> ColorType:
        """
        Case-insensitive search through registry contents. Type of the
        result depends on invoked class:

            - ``Color16.resolve(..)`` -> `Color16`
            - ``Color256.resolve(..)`` -> `Color256`
            - ``ColorRGB.resolve(..)`` -> `ColorRGB`

        .. note ::
            Invoking the method of `Color` itself is a special case. The search
            will be first performed in the registry of `Color16` class, then --
            in `Color256`, and, if previous two were unsuccessful, in the
            largest `ColorRGB` registry.

        :param name:        name of the color to look up for.
        :raises ValueError: if no color with specified name is registered.
        :returns:           `Color` instance.
        """
        if hasattr(cls, "_registry"):
            return cls._registry.resolve(name)

        for color_cls in [Color16, Color256, ColorRGB]:
            try:
                return color_cls.resolve(name)
            except ValueError:
                continue
        raise ValueError(f"Color '{name}' was not found in any of registries")

    @classmethod
    def find_closest(cls: t.Type[ColorType], hex_value: int) -> ColorType:
        """
        Search and return the nearset color to ``hex_value``. Depending on
        the desired result type and current color mode you might use either of:

            - ``Color16.find_closest(..)`` -> `Color16`
            - ``Color256.find_closest(..)`` -> `Color256`
            - ``ColorRGB.find_closest(..)`` -> `ColorRGB`

        .. note ::
            Invoking the method of `Color` itself is equivalent to
            calling ``Color256.find_closest()``.

        Method is useful for finding applicable color alternatives if user's
        terminal is incapable of operating in more advanced mode.

        This method caches the results, i.e., the same search query will from then
        onward result in the same return value without the necessity of iterating
        through the color index. If that's not applicable, use similar method
        `approximate()`, which is unaware of caching mechanism altogether.

        :param hex_value: Target color RGB value.
        :return: Nearest to ``hex_value`` instance of `Color` found. Type will
                 be the same as the class of called method.
        """
        if not hasattr(cls, "_index"):
            return Color256.find_closest(hex_value)

        if hex_value in cls._approx_cache.keys():
            return cls._approx_cache.get(hex_value)

        closest = cls._find_neighbours(hex_value)[0].color
        cls._approx_cache[hex_value] = closest
        return closest

    @classmethod
    def approximate(
        cls: t.Type[ColorType], hex_value: int, max_results: int = 1
    ) -> t.List[ApproximationResult[ColorType]]:
        """
        Search for nearest colors to ``hex_value`` and return the first
        ``max_results`` of them. This method is similar to the `find_closest()`,
        although they differ in some aspects:

            - `approximate()` can return more than one result;
            - `approximate()` returns not just `Color` instances, but also a
              number equal to squared distance to the target color for each of them;
            - `find_closest()` caches the results, while `approximate()` ignores
              the cache completely.

        The type of `Color` instances in the result will be the same as the
        `Color` class the called method is originating from (same as for method's
        sibling):

            - ``Color16.approximate(..)`` -> [ApproximationResult[`Color16`], ...]
            - ``Color256.approximate(..)`` -> [ApproximationResult[`Color256`], ...]
            - ``ColorRGB.approximate(..)`` -> [ApproximationResult[`ColorRGB`], ...]

        .. note ::
            Invoking the method of `Color` itself is equivalent to
            calling ``Color256.find_closest()``.

        :param hex_value:      Target color RGB value.
        :param max_results:    Return no more than ``max_results`` items.
        :return: Pairs of closest `Color` instance(s) found with their distances
                 to the target color, sorted by distance descending, i.e., element
                 at index 0 is the closest color found, paired with its distance
                 to the target; element with index 1 is second-closest color
                 (if any) and corresponding distance value, etc.
        """
        if hasattr(cls, "_index"):
            return cls._find_neighbours(hex_value)[:max_results]

        return Color256.approximate(hex_value)

    @classmethod
    def _find_neighbours(
        cls: t.Type[ColorType], hex_value: int
    ) -> t.List[ApproximationResult[ColorType]]:
        """
        Iterate the registered colors table and compute the squared euclidean distance
        from argument to each color of the palette. Sort the results and return them.

        **sRGB euclidean distance**
            https://en.wikipedia.org/wiki/Color_difference#sRGB
            https://stackoverflow.com/a/35114586/5834973

        :param hex_value:
        :return:
        """
        input_r, input_g, input_b = cls.hex_to_rgb(hex_value)
        result: t.List[ApproximationResult[ColorType]] = list()

        for channels in cls._index.values:
            distance_sq: int = (
                pow(channels.r - input_r, 2)
                + pow(channels.g - input_g, 2)
                + pow(channels.b - input_b, 2)
            )
            result.append(ApproximationResult(channels.color, distance_sq))

        return sorted(result, key=lambda r: r.distance)

    @staticmethod
    def hex_to_hsv(hex_value: int) -> t.Tuple[float, float, float]:
        """
        Transforms ``hex_value`` in 0xFFFFFF format into a tuple of three numbers
        corresponding to **hue**, **saturation** and **value** channel values respectively.
        Hue is within [0, 359] range, both saturation and value are within [0; 1] range.
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
        Transforms ``hex_value`` in 0xFFFFFF format into a tuple of three
        integers corresponding to **red**, **blue** and **green** channel value
        respectively. Values are within [0; 255] range.

        >>> Color.hex_to_rgb(0x80ff80)
        (128, 255, 128)

        :param hex_value: Color RGB value.
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
        """
        
        :param r:
        :param g:
        :param b:
        :return:
        """
        return (r << 16) + (g << 8) + b


class Color16(Color):
    """

    :param hex_value:
    :param code_fg:
    :param code_bg:
    :param name:
    :param aliases:
    :param variation_map:
    :param register:
    :param index:
    """
    def __init__(
        self,
        hex_value: int,
        code_fg: int,
        code_bg: int,
        name: str = None,
        aliases: t.List[str] = None,
        variation_map: t.Dict[int, str] = None,
        register: bool = False,
        index: bool = False,
    ):
        super().__init__(hex_value, name)
        self._code_fg: int = code_fg
        self._code_bg: int = code_bg
        self._post_init(self._code_fg, aliases, variation_map, register, index)

    def to_sgr(self, bg: bool, upper_bound: t.Type[Color] = None) -> SequenceSGR:
        if bg:
            return SequenceSGR(self._code_bg)
        return SequenceSGR(self._code_fg)

    def to_tmux(self, bg: bool) -> str:
        if self._name is None:
            raise ValueError("Translation to tmux format failed: color name required")
        code = self._code_bg if bg else self._code_fg
        is_hi = code in HI_COLORS or code in BG_HI_COLORS
        tmux_name = ("bright" if is_hi else "") + self._name.lower().replace("hi-", "")
        return tmux_name

    @property
    def code_fg(self) -> int:
        """

        :return:
        """
        return self._code_fg

    @property
    def code_bg(self) -> int:
        """
        
        :return:
        """
        return self._code_bg

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return (
            self._hex_value == other._hex_value
            and self._code_bg == other._code_bg
            and self._code_fg == other._code_fg
        )

    def __repr__(self):
        # question mark after color value indicates that we cannot be 100% sure
        # about the exact value of xterm-16 colors, as they are configurable and
        # depend on terminal theme and settings. that's not the case for xterm-256,
        # though -- it's almost guaranteed to have the same color nearly everywhere.
        # the exceptions are rare and include color mapping at low level, e.g.,
        # ``tmux`` with specifically configured terminal capability overrides.
        # that's not something that you'd expect from a regular user, anyway.
        code = f"#{self._code_fg}"
        value = f"{self.format_value('')}?"
        return self._repr(code, value, self._name)


class Color256(Color):
    """
    :param hex_value:
    :param code:
    :param name:
    :param aliases:
    :param variation_map:
    :param color16_equiv:
    :param register:
    :param index:
    """
    def __init__(
        self,
        hex_value: int,
        code: int,
        name: str = None,
        aliases: t.List[str] = None,
        variation_map: t.Dict[int, str] = None,
        color16_equiv: Color16 = None,
        register: bool = False,
        index: bool = False,
    ):
        super().__init__(hex_value, name)
        self._code: int | None = code
        self._color16_equiv: Color16 | None = None
        if color16_equiv:
            self._color16_equiv = Color16.get_by_code(color16_equiv.code_fg)
        self._post_init(self._code, aliases, variation_map, register, index)

    def to_sgr(self, bg: bool, upper_bound: t.Type[Color] = None) -> SequenceSGR:
        if upper_bound is ColorRGB:
            return make_color_rgb(*self.to_rgb(), bg)

        if upper_bound is Color256 or upper_bound is None:
            return make_color_256(self._code, bg)

        if self._color16_equiv:
            return self._color16_equiv.to_sgr(bg, upper_bound)

        return Color16.find_closest(self.hex_value).to_sgr(bg, upper_bound)

    def to_tmux(self, bg: bool) -> str:
        return f"colour{self._code}"

    @property
    def code(self) -> int:
        """

        :return:
        """
        return self._code

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._hex_value == other._hex_value and self._code == other._code

    def __repr__(self):
        code = f"#{self._code}"
        return self._repr(code, self.format_value(""), self._name)


class ColorRGB(Color):
    """

    :param hex_value:
    :param name:
    :param aliases:
    :param variation_map:
    :param register:
    :param index:
    """
    def __init__(
        self,
        hex_value: int,
        name: str = None,
        aliases: t.List[str] = None,
        variation_map: t.Dict[int, str] = None,
        register: bool = False,
        index: bool = False,
    ):
        super().__init__(hex_value, name)
        self._post_init(None, aliases, variation_map, register, index)

    def to_sgr(self, bg: bool, upper_bound: t.Type[Color] = None) -> SequenceSGR:
        if upper_bound is ColorRGB or upper_bound is None:
            return make_color_rgb(*self.to_rgb(), bg)

        return upper_bound.find_closest(self._hex_value).to_sgr(bg, upper_bound)

    def to_tmux(self, bg: bool) -> str:
        return self.format_value("#")

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._hex_value == other._hex_value

    def __repr__(self):
        return self._repr(self.format_value(""), self._name)


class _NoopColor(Color):
    def __init__(self):
        super().__init__(0)

    def to_sgr(self, bg: bool, upper_bound: t.Type[Color] = None) -> SequenceSGR:
        return NOOP_SEQ

    def to_tmux(self, bg: bool) -> str:
        return ""

    @property
    def hex_value(self) -> int:
        raise ValueError("No color for NO-OP instance")

    def format_value(self, prefix: str = "0x") -> str:
        return (prefix if "=" in prefix else "") + "NOP"

    def __repr__(self):
        return self._repr(self.format_value())


NOOP_COLOR = _NoopColor()
"""
Special `Color` instance always rendering into empty string.
"""


class ColorNameConflictError(Exception):
    def __init__(
        self, tokens: t.Tuple[str], existing_color: ColorType, new_color: ColorType
    ):
        msg = f"Color '{new_color.name}' -> {tokens} already exists"
        super().__init__(msg, [existing_color, new_color])


class ColorCodeConflictError(Exception):
    def __init__(self, code: int, existing_color: ColorType, new_color: ColorType):
        msg = f"Color #{code} already exists"
        super().__init__(msg, existing_color, new_color)
