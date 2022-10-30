# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

import json
import typing as t
from os.path import dirname, join

from .ansi import SequenceSGR, NOOP_SEQ, IntCode
from .common import LogicError, logger

ColorIndexed = t.TypeVar("ColorIndexed", "ColorIndexed16", "ColorIndexed256")


class Color:
    """
    Abstract superclass for other ``Colors``.
    """

    def __init__(self, hex_value: int):
        self._hex_value: int = hex_value

    def to_sgr(
        self, bg: bool = False, allow_index256: bool = True, allow_rgb: bool = False
    ) -> SequenceSGR:
        raise NotImplementedError

    def to_hsv_channels(self) -> t.Tuple[int, float, float]:
        """

        :return:
        """
        return hex_value_to_hsv_channels(self._hex_value)

    def to_rgb_channels(self) -> t.Tuple[int, int, int]:
        """

        :return:
        """
        return hex_value_to_rgb_channels(self._hex_value)

    @property
    def hex_value(self) -> int:
        """

        :return:
        """
        return self._hex_value

    def format_value(self, prefix: str = "0x") -> str:
        """

        :param prefix:
        :return:
        """
        return f"{prefix:s}{self._hex_value:06x}"


class ColorIndexed16(Color):
    _mapping_index: _ColorCodeMapping[ColorIndexed16]

    def __init__(self, hex_value: int, code_fg: int, code_bg: int):
        super().__init__(hex_value)
        self._code_fg: int = code_fg
        self._code_bg: int = code_bg

    def to_sgr(
        self, bg: bool = False, allow_index256: bool = True, allow_rgb: bool = False
    ) -> SequenceSGR:
        if bg:
            return SequenceSGR(self._code_bg)
        return SequenceSGR(self._code_fg)

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


class ColorIndexed256(Color):
    def __init__(
        self, hex_value: int, code: int = None, index16_equiv: ColorIndexed16 = None
    ):
        super().__init__(hex_value)
        self._code: int | None = code
        self._index16_equiv: ColorIndexed16 | None = index16_equiv

    def to_sgr(
        self, bg: bool = False, allow_index256: bool = True, allow_rgb: bool = False
    ) -> SequenceSGR:
        if allow_index256:
            return SequenceSGR.init_color_index256(self._code, bg=bg)

        if allow_rgb:
            # `allow_rgb=True` usually means that terminal also supports all
            # indexed colors, so we shouldn't be here... oh well, for the
            # sake of completeness:
            return SequenceSGR.init_color_rgb(*self.to_rgb_channels())

        if self._index16_equiv:
            return self._index16_equiv.to_sgr(bg=bg)

        color_indexed16 = find_closest(self.hex_value, allow_index256=False)
        return color_indexed16.to_sgr(bg=bg)

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
    def to_sgr(
        self, bg: bool = False, allow_index256: bool = True, allow_rgb: bool = False
    ) -> SequenceSGR:
        if allow_rgb:
            return SequenceSGR.init_color_rgb(*self.to_rgb_channels(), bg)
        color = find_closest(self.hex_value, allow_index256)
        return color.to_sgr(bg, allow_index256, allow_rgb)

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._hex_value == other._hex_value

    def __repr__(self):
        return f"{self.__class__.__name__}[{self.format_value()}]"


class _NoopColor(Color):
    def __init__(self):
        super().__init__(-1)

    def to_sgr(
        self, bg: bool = False, allow_index256: bool = True, allow_rgb: bool = False
    ) -> SequenceSGR:
        return NOOP_SEQ

    @property
    def hex_value(self) -> int:
        raise ValueError("No color for NO-OP instance")

    def format_value(self, prefix: str = "0x") -> str:
        return "~"


NOOP_COLOR = _NoopColor()
"""
Special `Color` instance always rendering into empty string.
"""

# -------------------------------------------------------------------------------------


class Index:
    _PRIMARY_CONFIG_FILENAMES = ["index16.json", "index256.json"]
    _SECONDARY_CONFIG_FILENAMES = ["rgb.json"]

    def __init__(self):
        self._mapping_index16 = _ColorCodeMapping[ColorIndexed16]()
        self._mapping_index256 = _ColorCodeMapping[ColorIndexed256]()

        self._name_map: t.Dict[str, ColorIndexed256 | int] = {}
        self._config_dir = join(dirname(__file__), "..", "config")  # @FIXME

        for primary_filename in self._PRIMARY_CONFIG_FILENAMES:
            self._load_config(primary_filename)

    def load_all_configs(self):
        for secondary_filename in self._SECONDARY_CONFIG_FILENAMES:
            self._load_config(secondary_filename)

    def get_by_code(self, color_class: type, code: int) -> ColorIndexed:
        return self._resolve_registry(color_class).get(code)

    def add_to_code_map(self, color: ColorIndexed, code: int):
        self._resolve_registry(type(color)).set(color, code)

    def resolve(self, name: str) -> ColorIndexed256 | ColorRGB:
        """
        Case-insensitive search through registry contents.

        :param name:      name of the color to look up for.
        :raises KeyError: if no color with specified name is registered.
        :returns:         `ColorIndexed256` or `ColorRGB`.
        """
        name_norm = name.lower()
        if (color := self._name_map.get(name_norm)) is not None:
            if isinstance(color, (ColorIndexed16, ColorIndexed256)):
                return color
            return ColorRGB(color)
        raise KeyError(f"No color named '{name_norm}' (<- '{name}') is found")

    def find_closest(self, hex_value: int, allow_index256: bool = True) -> ColorIndexed:
        """
        Search for color nearest to ``hex_value`` and return it. Is used to find
        applicable color alternatives if user's terminal is incapable of operating
        in more advanced mode.

        :param hex_value:          Color value in RGB format.
        :param allow_index256:     Operate with ``ColorIndexed256`` instances
                                   if True, otherwise -- with ``ColorIndexed16``.
        :return: Nearest to ``hex_value`` instance of ``ColorIndexed256`` or
                 ``ColorIndexed16`` found. Type depends on value of `allow_index256`.
        """
        return self._resolve_registry(allow_index256).find_closest(hex_value)

    def approximate(
        self, hex_value: int, allow_index256: bool = True, max_results: int = 1
    ) -> t.List[ColorIndexed]:
        """
        Search for colors nearest to ``hex_value`` and return the first
        ``<max_results>`` of them.

        :param hex_value:      Color RGB value.
        :param allow_index256: Operate with ``ColorIndexed256`` instances
                               if True, otherwise -- with ``ColorIndexed16``.
        :param max_results:    Maximum amount of values to return.
        :return: Closest `ColorIndexed` instance(s) found, sorted by color distance
                 descending, i.e., 0-th element is the closest to the input value.
        """
        registry = self._resolve_registry(allow_index256)
        sorted_result = registry.get_code_map_sorted_by_dist(hex_value)
        return [r[0] for r in sorted_result[:max_results]]

    @t.overload
    def _resolve_registry(self, allow_index256: bool) -> _ColorCodeMapping:
        ...

    @t.overload
    def _resolve_registry(self, color_class: type) -> _ColorCodeMapping:
        ...

    def _resolve_registry(self, criteria: bool | type) -> _ColorCodeMapping:
        if isinstance(criteria, type):
            if criteria is ColorIndexed256:
                return self._mapping_index256
            if criteria is ColorIndexed16:
                return self._mapping_index16
            raise KeyError(f"No registry found for class '{criteria}'")

        if isinstance(criteria, bool):
            return self._mapping_index256 if criteria else self._mapping_index16
        raise TypeError(
            f"Invalid argument type: {type(criteria)}, expected bool or type"
        )

    def _load_config(self, filename: str):
        with open(join(self._config_dir, filename), "rt") as f:
            data = json.load(f)
            color_class_str = data["class"]
            color_class = globals().get(color_class_str)
            if not color_class:
                logger.warning(
                    f"Failed to load color class '{color_class_str}', "
                    f"aborting loading of '{filename}'"
                )
                return

            for color_def in data["colors"]:
                self._add_color_def(color_def, color_class)

    def _add_color_def(self, color_def: t.Dict, color_class: type):
        registry = self._resolve_registry(color_class)
        names = [
            color_def.get("override_name", color_def.get("original_name")),
            *color_def.get("aliases", []),
        ]
        hex_value: int = int(color_def["hex_value"], 16)
        color: Color = None

        if (code := color_def.get("code", color_def.get("code_fg"))) is not None:
            if isinstance(code, str):
                code = getattr(IntCode, code)

            if registry.has(code):
                color = registry.get(code)
            else:
                args = [hex_value, code]
                if color_class is ColorIndexed16:
                    args.append(getattr(IntCode, color_def["code_bg"]))
                if color_class is ColorIndexed256 and (
                    index16_equiv_code := color_def.get("index16_equiv_code")
                ):
                    args.append(
                        self._mapping_index16.get(IntCode[index16_equiv_code])
                    )
                color = color_class(*args)

                # @TODO find a way to test it against ColorIndexed typevar:
                if isinstance(color, (ColorIndexed16, ColorIndexed256)):
                    registry.set(color, code)

        for name in names:
            name_norm = name.lower()
            if name_norm in self._name_map.keys():
                logger.warning(f"Color '{name_norm}' is already in registry, skipping")
                continue
            self._name_map[name_norm] = color or hex_value


class _ColorCodeMapping(t.Generic[ColorIndexed]):
    def __init__(self):
        self._code_map: t.Dict[int, ColorIndexed] = dict()
        self._query_cache: t.Dict[int, ColorIndexed] = dict()

    def has(self, code: int) -> bool:
        """

        :param code:
        :return:
        """
        return code in self._code_map.keys()

    def set(self, color: ColorIndexed, code: int):
        """

        :param color:
        :param code:
        :return:
        """
        if color.hex_value is None:
            return
        if self.has(code) and color.hex_value != self.get(code).hex_value:
            logger.warning(
                f"Color with {code} is already in {self!r}, skipping {color!r}"
            )
            return
        self._code_map[code] = color

    def get(self, code: int) -> ColorIndexed:
        """

        :param code:
        :return:
        """
        if self.has(code):
            return self._code_map[code]
        raise KeyError(f"Color with code {code} was not found in {self!r}")

    def find_closest(self, hex_value: int) -> ColorIndexed:
        if hex_value in self._query_cache.keys():
            return self._query_cache.get(hex_value)

        closest = self.get_code_map_sorted_by_dist(hex_value)[0][0]
        self._query_cache[hex_value] = closest
        return closest

    def get_code_map_sorted_by_dist(
        self, hex_value: int
    ) -> t.List[t.Tuple[ColorIndexed, float]]:
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
        input_r, input_g, input_b = hex_value_to_rgb_channels(hex_value)
        result: t.List[t.Tuple[ColorIndexed, float]] = list()

        for map_hex, map_color in self._code_map.items():
            map_r, map_g, map_b = hex_value_to_rgb_channels(map_hex)
            distance_sq = (
                pow(map_r - input_r, 2)
                + pow(map_g - input_g, 2)
                + pow(map_b - input_b, 2)
            )
            result.append((map_color, distance_sq))

        return sorted(result, key=lambda r: r[1])


index = Index()

# -------------------------------------------------------------------------------------


def find_closest(hex_value: int, allow_index256: bool = True) -> ColorIndexed:
    """Wrapper for `Index.find_closest`"""
    return index.find_closest(hex_value, allow_index256)


def approximate(
    hex_value: int, allow_index256: bool = True, max_results: int = 1
) -> t.List[ColorIndexed]:
    """Wrapper for  `Index.approximate`"""
    return index.approximate(hex_value, allow_index256, max_results)


def hex_value_to_hsv_channels(hex_value: int) -> t.Tuple[int, float, float]:
    """
    Transforms ``hex_value`` in ``0xffffff`` format into tuple of three numbers
    corresponding to *hue*, *saturation* and *value* channel values respectively.
    *Hue* is within [0, 359] range, *saturation* and *value* are
    within [0; 1] range.
    """
    if not isinstance(hex_value, int):
        raise TypeError(f"Argument type should be 'int', got: {type(hex_value)}")

    # https://en.wikipedia.org/wiki/HSL_and_HSV#From_RGB
    r, g, b = hex_value_to_rgb_channels(hex_value)
    rn, gn, bn = r / 255, g / 255, b / 255

    vmax = max(rn, gn, bn)
    vmin = min(rn, gn, bn)
    c = vmax - vmin
    v = vmax

    if c == 0:
        h = 0
    elif v == rn:
        h = 60 * (0 + (gn - bn) / c)
    elif v == gn:
        h = 60 * (2 + (bn - rn) / c)
    elif v == bn:
        h = 60 * (4 + (rn - gn) / c)
    else:
        raise LogicError("Impossible if-branch")

    if v == 0:
        s = 0
    else:
        s = c / v

    if h < 0:
        h += 360

    return h, s, v


def hex_value_to_rgb_channels(hex_value: int) -> t.Tuple[int, int, int]:
    """
    Transforms ``hex_value`` in ``0xffffff`` format into tuple of three
    integers corresponding to *red*, *blue* and *green* channel value
    respectively. Values are within [0; 255] range.

    >>> col.hex_value_to_rgb_channels(0x80ff80)
    (128, 255, 128)
    >>> col.hex_value_to_rgb_channels(0x000001)
    (0, 0, 1)
    """
    if not isinstance(hex_value, int):
        raise TypeError(f"Argument type should be 'int', got: {type(hex_value)}")

    return (hex_value & 0xFF0000) >> 16, (hex_value & 0xFF00) >> 8, (hex_value & 0xFF)


def rgb_channels_to_hex_value(r: int, g: int, b: int) -> int:
    """
    .. todo ::

    :param r:
    :param g:
    :param b:
    :return:
    """
    return (r << 16) + (g << 8) + b

# -------------------------------------------------------------------------------------
# fmt: off


# ColorIndexed16
BLACK      = index.resolve('Black')
RED        = index.resolve('Red')
GREEN      = index.resolve('Green')
YELLOW     = index.resolve('Yellow')
BLUE       = index.resolve('Blue')
MAGENTA    = index.resolve('Magenta')
CYAN       = index.resolve('Cyan')
WHITE      = index.resolve('White')
GREY       = index.resolve('Grey')
HI_RED     = index.resolve('HiRed')
HI_GREEN   = index.resolve('HiGreen')
HI_YELLOW  = index.resolve('HiYellow')
HI_BLUE    = index.resolve('HiBlue')
HI_MAGENTA = index.resolve('HiMagenta')
HI_CYAN    = index.resolve('HiCyan')
HI_WHITE   = index.resolve('HiWhite')

# ColorIndexed256
GRAY_3     = index.resolve('Gray3')
GRAY_7     = index.resolve('Gray7')
GRAY_11    = index.resolve('Gray11')
GRAY_15    = index.resolve('Gray15')
GRAY_19    = index.resolve('Gray19')
GRAY_23    = index.resolve('Gray23')
GRAY_27    = index.resolve('Gray27')
GRAY_30    = index.resolve('Gray30')
GRAY_35    = index.resolve('Gray35')
GRAY_39    = index.resolve('Gray39')
GRAY_42    = index.resolve('Gray42')
GRAY_46    = index.resolve('Gray46')
GRAY_50    = index.resolve('Gray50')
GRAY_54    = index.resolve('Gray54')
GRAY_58    = index.resolve('Gray58')
GRAY_62    = index.resolve('Gray62')
GRAY_66    = index.resolve('Gray66')
GRAY_70    = index.resolve('Gray70')
GRAY_74    = index.resolve('Gray74')
GRAY_78    = index.resolve('Gray78')
GRAY_82    = index.resolve('Gray82')
GRAY_85    = index.resolve('Gray85')
GRAY_89    = index.resolve('Gray89')
GRAY_93    = index.resolve('Gray93')

# ColorIndexedRGB
TRUE_WHITE = ColorRGB(0xFFFFFF)
"""White power"""
TRUE_BLACK = ColorRGB(0x000000)

# fmt: on
