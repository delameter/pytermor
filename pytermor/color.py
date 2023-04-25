# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
"""
Color main classes and helper functions.
"""
from __future__ import annotations

import dataclasses
import math
import re
import typing as t
from abc import abstractmethod, ABCMeta

from .utilmisc import hex_to_rgb, hex_to_hsv
from .ansi import (
    SequenceSGR,
    NOOP_SEQ,
    HI_COLORS,
    BG_HI_COLORS,
    make_color_256,
    make_color_rgb,
    SeqIndex,
)
from .common import LogicError, HSV, RGB
from .config import get_config


CDT = t.TypeVar("CDT", int, str)
"""
:abbr:`CDT (Color descriptor type)` represents a RGB color value. Primary handler 
is `resolve_color()`. Valid values include:

    - *str* with a color name in any form distinguishable by the color resolver;
      the color lists can be found at: `guide.ansi-presets` and `guide.es7s-colors`;
    - *str* starting with a "#" and consisting of 6 more hexadecimal characters, case
      insensitive (RGB regular form), e.g. ":hex:`#0B0CCA`";
    - *str* starting with a "#" and consisting of 3 more hexadecimal characters, case
      insensitive (RGB short form), e.g. ":hex:`#666`";
    - *int* in a [:hex:`0`; :hex:`0xFFFFFF`] range.
"""

CT = t.TypeVar("CT", bound="IColor")
""" 
Any non-abstract ``IColor`` type.

:meta public:
 """


class _ColorRegistry(t.Generic[CT], t.Sized, t.Iterable):
    _TOKEN_SEPARATOR = "-"
    _QUERY_SPLIT_REGEX = re.compile(r"[\W_]+|(?<=[a-z])(?=[A-Z0-9])")

    def __init__(self):
        self._map: t.Dict[t.Tuple[str], CT] = {}
        self._list: t.Set[CT] = set()

    def register(self, color: CT, name: str):
        primary_tokens = tuple(self._QUERY_SPLIT_REGEX.split(name))
        self._register_pair(color, primary_tokens)

        if not isinstance(color, ColorRGB):
            return
        for variation in color.variations.values():
            variation_tokens: t.Tuple[str, ...] = (
                *primary_tokens,
                *(self._QUERY_SPLIT_REGEX.split(variation.name)),
            )
            self._register_pair(variation, variation_tokens)

    def _register_pair(self, color: CT, tokens: t.Tuple[str, ...]):
        self._list.add(color)

        if tokens not in self._map.keys():
            self._map[tokens] = color
            return

        existing_color = self._map.get(tokens)
        if color.hex_value == existing_color.hex_value:
            return  # skipping the duplicate with the same name and value
        raise ColorNameConflictError(tokens, existing_color, color)

    def resolve(self, name: str) -> CT:
        query_tokens = (*(qt.lower() for qt in self._QUERY_SPLIT_REGEX.split(name)),)
        if color := self._map.get(query_tokens, None):
            return color
        raise LookupError(f"Color '{name}' does not exist")

    def __len__(self) -> int:
        return len(self._map)

    def __bool__(self) -> bool:
        return len(self) > 0

    def __iter__(self) -> t.Iterator[CT]:
        return iter(self._list)

    def names(self) -> t.Iterable[t.Tuple[str]]:
        return self._map.keys()


class _ColorIndex(t.Generic[CT], t.Sized):
    def __init__(self):
        self._map: t.Dict[int, _ColorChannels[CT]] = {}

    def add(self, color: CT, code: int = None):
        if code is None:
            code = len(self._map)
        if code not in self._map.keys():
            self._map[code] = _ColorChannels(color)
            return

        existing_color = self._map.get(code).color
        if color.hex_value == existing_color.hex_value:
            return  # skipping the duplicate with the same code and value
        raise ColorCodeConflictError(code, existing_color, color)

    def get(self, code: int) -> CT:
        if channels := self._map.get(code, None):
            return channels.color
        raise KeyError(f"Color #{code} does not exist")

    def __len__(self) -> int:
        return len(self._map)

    def __bool__(self) -> bool:
        return len(self) > 0

    def __iter__(self) -> t.Iterator[_ColorChannels[CT]]:
        return iter(self._map.values())


class _ColorChannels(t.Generic[CT]):
    def __init__(self, color: CT):
        self.color: CT = color
        self.r, self.g, self.b = self.color.to_rgb()


@dataclasses.dataclass(frozen=True)
class ApxResult(t.Generic[CT]):
    """
    Approximation result.
    """

    color: CT
    """ Found ``IColor`` instance. """
    distance: int
    """ Squared sRGB distance from this instance to the approximation target. """

    @property
    def distance_real(self) -> float:
        """
        Actual distance from instance to target:

            :math:`distance_{real} = \\sqrt{distance}`
        """
        return math.sqrt(self.distance)


class _ColorMeta(ABCMeta):
    def __new__(mcls, name, bases, namespace, **kwargs):
        cls = super().__new__(mcls, name, bases, namespace, **kwargs)

        cls._registry = _ColorRegistry[cls]()
        cls._index = _ColorIndex[cls]()
        cls._approx_cache = dict()
        return cls

    def __iter__(self) -> t.Iterator[CT]:
        return iter(self._registry)


class IColor(metaclass=_ColorMeta):
    """
    Abstract superclass for other ``Colors``.

    :meta private:
    """

    _registry: _ColorRegistry
    _index: _ColorIndex
    _approx_cache: t.Dict[int, CT]

    def __init__(self, hex_value: int, name: str = None):
        if hex_value < 0 or hex_value > 0xFFFFFF:
            raise ValueError(
                f"Out of bounds hex value {hex_value:06X}, "
                + "should be: 0x0 <= hex_value <= 0xFFFFFF"
            )
        self._hex_value: int = hex_value
        self._name: str | None = name
        self._base: CT | None = None

    def _register(
        self: CT, code: int | None, register: bool, index: bool, aliases: t.List[str]
    ):
        if register:
            self._register_names(aliases)
        if index:
            self._index.add(self, code)

    def _register_names(self: CT, aliases: t.List[str] = None):
        if not self.name:
            return
        self._registry.register(self, self.name)

        if not aliases:
            return
        for alias in aliases:
            self._registry.register(self, alias)

    def _make_variations(self: CT, variation_map: t.Dict[int, str] = None):
        if not variation_map:
            return
        for vari_hex_value, vari_name in variation_map.items():
            variation = type(self)(
                hex_value=vari_hex_value, name=vari_name, register=False, index=True
            )
            variation._base = self
            self._variations[vari_name] = variation

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._hex_value == other._hex_value

    def __hash__(self) -> int:
        return self._hex_value + hash(self._name)

    def format_value(self, prefix: str = "0x") -> str:
        """
        Format color value as ":hex:`0xRRGGBB`".

        :param prefix: Can be customized.
        """
        return f"{prefix:s}{self._hex_value:06X}"

    @property
    def hex_value(self) -> int:
        """Color value, e.g. :hex:`0x3AEB0C`."""
        return self._hex_value

    @property
    def name(self) -> str | None:
        """Color name, e.g. "navy-blue"."""
        return self._name

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}[{self.repr_attrs()}]>"

    @abstractmethod
    def repr_attrs(self, verbose: bool = True) -> str:
        raise NotImplementedError

    def to_hsv(self) -> HSV | t.Tuple[float, float, float]:
        """
        Wrapper around `hex_to_hsv()` for concrete instance.

        :see: hex_to_hsv() for the details
        """
        return hex_to_hsv(self._hex_value)

    def to_rgb(self) -> RGB | t.Tuple[int, int, int]:
        """
        Wrapper around `to_rgb()` for concrete instance.

        :see: to_rgb() for the details
        """
        return hex_to_rgb(self._hex_value)

    @abstractmethod
    def to_sgr(self, bg: bool, upper_bound: t.Type[IColor] = None) -> SequenceSGR:
        """
        Make an `SGR sequence<SequenceSGR>` out of ``IColor``. Used by `SgrRenderer`.

        :param bg: Set to *True* if required SGR should change the background color, or
                   *False* for the foreground (=text) color.
        :param upper_bound: Required result ``IColor`` type upper boundary, i.e., the
                            maximum acceptable color class, which will be the basis for
                            SGR being made. See `Color256.to_sgr()` for the details.
        """
        raise NotImplementedError

    @abstractmethod
    def to_tmux(self, bg: bool) -> str:
        """
        Make a tmux markup directive, which will change the output color to
        this color's value (after tmux processes and prints it). Used by `TmuxRenderer`.

        :param bg: Set to *True* if required tmux directive should change the background
                   color, or *False* for the foreground (=text) color.
        """
        raise NotImplementedError

    @classmethod
    def names(cls) -> t.Iterable[t.Tuple[str]]:
        return cls._registry.names()

    @classmethod
    def resolve(cls, name: str) -> CT:
        """
        Case-insensitive search through registry contents.

        :see: `resolve_color()` for the details
        :param name:  ``IColor`` name to search for.
        """
        if not hasattr(cls, "_registry"):
            raise LogicError(
                "Registry is empty. Did you call an abstract class' method?"
            )
        return cls._registry.resolve(name)

    @classmethod
    def find_closest(cls, hex_value: int) -> CT:
        """
        Search and return nearest to ``hex_value`` color instance.

        :see: `color.find_closest()` for the details
        :param hex_value: Target RGB value.
        """
        if not hasattr(cls, "_index"):
            raise LogicError("Index is empty. Did you call an abstract class' method?")

        if hex_value in cls._approx_cache.keys():
            return cls._approx_cache.get(hex_value)

        closest = cls._find_neighbours(hex_value)[0].color
        cls._approx_cache[hex_value] = closest
        return closest

    @classmethod
    def approximate(cls, hex_value: int, max_results: int = 1) -> t.List[ApxResult[CT]]:
        """
        Search for the colors nearest to ``hex_value`` and return the first ``max_results``.

        :see: `color.approximate()` for the details
        :param hex_value:   Target RGB value.
        :param max_results: Result limit.
        """
        if not hasattr(cls, "_index"):
            raise LogicError("Index is empty. Did you call an abstract class' method?")
        return cls._find_neighbours(hex_value)[:max_results]

    @classmethod
    def _find_neighbours(cls: t.Type[CT], hex_value: int) -> t.List[ApxResult[CT]]:
        """
        Iterate the registered colors table and compute the squared euclidean distance
        from argument to each color of the palette. Sort the results and return them.

        **sRGB euclidean distance**
            https://en.wikipedia.org/wiki/Color_difference#sRGB
            https://stackoverflow.com/a/35114586/5834973

        :param hex_value: Target RGB value.
        """
        input_r, input_g, input_b = hex_to_rgb(hex_value)
        result: t.List[ApxResult[CT]] = list()

        for channels in cls._index:
            distance_sq: int = (
                pow(channels.r - input_r, 2)
                + pow(channels.g - input_g, 2)
                + pow(channels.b - input_b, 2)
            )
            result.append(ApxResult(channels.color, distance_sq))
        return sorted(result, key=lambda r: r.distance)


class Color16(IColor):
    """
    Variant of a ``IColor`` operating within the most basic color set
    -- **xterm-16**. Represents basic color-setting SGRs with primary codes
    30-37, 40-47, 90-97 and 100-107 (see `guide.ansi-presets.color16`).

    .. note ::

        Arguments ``register``, ``index`` and ``aliases``
        are *kwonly*-type args.

    :param int hex_value:  Color RGB value, e.g. :hex:`0x800000`.
    :param int code_fg:    Int code for a foreground color setup, e.g. 30.
    :param int code_bg:    Int code for a background color setup. e.g. 40.
    :param str name:       Name of the color, e.g. "red".
    :param bool register:  If *True*, add color to registry for resolving by name.
    :param bool index:     If *True*, add color to approximation index.
    :param list[str] aliases:
                            Alternative color names (used in `resolve_color()`).
    """

    __hash__ = IColor.__hash__

    def __init__(
        self,
        hex_value: int,
        code_fg: int,
        code_bg: int,
        name: str = None,
        *,
        register: bool = False,
        index: bool = False,
        aliases: t.List[str] = None,
    ):
        super().__init__(hex_value, name)
        self._code_fg: int = code_fg
        self._code_bg: int = code_bg
        self._register(self._code_fg, register, index, aliases)

    @property
    def code_fg(self) -> int:
        """Int code for a foreground color setup, e.g. 30."""
        return self._code_fg

    @property
    def code_bg(self) -> int:
        """Int code for a background color setup. e.g. 40."""
        return self._code_bg

    @classmethod
    def get_by_code(cls, code: int) -> Color16:
        """
        Get a `Color16` instance with specified code. Only *foreground* (=text) colors
        are indexed, therefore it is impossible to look up for a `Color16` with
        given background color.

        :param code:      Foreground integer code to look up for (see
                          `guide.ansi-presets.color16`).
        :raises KeyError: If no color with specified code is found.
        """
        return cls._index.get(code)

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return (
            self._hex_value == other._hex_value
            and self._code_bg == other._code_bg
            and self._code_fg == other._code_fg
        )

    def repr_attrs(self, verbose: bool = True) -> str:
        # question mark after color value indicates that we cannot be 100% sure
        # about the exact value of xterm-16 colors, as they are configurable and
        # depend on terminal theme and settings. that's not the case for xterm-256,
        # though -- it's almost guaranteed to have the same color nearly everywhere.
        # the exceptions are rare and include color mapping at low level, e.g.,
        # ``tmux`` with specifically configured terminal capability overrides.
        # that's not something that you'd expect from a regular user, anyway.
        code = f"#{self._code_fg}"
        value = f"{self.format_value('')}?"

        params = [self._name]
        if verbose:
            params = [code, value] + params
        return ",".join(str(s) for s in filter(None, params))

    def to_sgr(self, bg: bool, upper_bound: t.Type[IColor] = None) -> SequenceSGR:
        if bg:
            return SequenceSGR(self._code_bg)
        return SequenceSGR(self._code_fg)

    def to_tmux(self, bg: bool) -> str:
        if self._name is None:
            raise LogicError("Translation to tmux format failed: color name required")
        code = self._code_bg if bg else self._code_fg
        is_hi = code in HI_COLORS or code in BG_HI_COLORS
        tmux_name = ("bright" if is_hi else "") + self._name.lower().replace("hi-", "")
        return tmux_name


class Color256(IColor):
    """
    Variant of a ``IColor`` operating within relatively modern **xterm-256**
    indexed color table. Represents SGR complex codes ``38;5;*`` and ``48;5;*``
    (see `guide.ansi-presets.color256`).

    .. note ::

        Arguments ``register``, ``index``, ``aliases`` and ``color16_equiv``
        are *kwonly*-type args.

    :param hex_value: Color RGB value, e.g. :hex:`0x5f0000`.
    :param code:      Int code for a color setup, e.g. 52.
    :param name:      Name of the color, e.g. "dark-red".
    :param register:  If *True*, add color to registry for resolving by name.
    :param index:     If *True*, add color to approximation index.
    :param aliases:   Alternative color names (used in `resolve_color()`).
    :param color16_equiv:
                      `Color16` counterpart (applies only to codes 0-15).
    """

    __hash__ = IColor.__hash__

    def __init__(
        self,
        hex_value: int,
        code: int,
        name: str = None,
        *,
        register: bool = False,
        index: bool = False,
        aliases: t.List[str] = None,
        color16_equiv: Color16 = None,
    ):
        super().__init__(hex_value, name)
        self._code: int | None = code
        self._color16_equiv: Color16 | None = None
        if color16_equiv:
            self._color16_equiv = Color16.get_by_code(color16_equiv.code_fg)
        self._register(self._code, register, index, aliases)

    def to_sgr(self, bg: bool, upper_bound: t.Type[IColor] = None) -> SequenceSGR:
        """
        Make an `SGR sequence<SequenceSGR>` out of ``IColor``. Used by `SgrRenderer`.

        Each ``IColor`` type represents one SGR type in the context of colors. For
        example, if ``upper_bound`` is set to `Color16`, the resulting SGR will always
        be one of 16-color index table, even if the original color was of different
        type -- it will be approximated just before the SGR assembling.

        The reason for this is the necessity to provide a similar look for all users
        with different terminal settings/ capabilities. When the library sees that
        user's output device supports 256 colors only, it cannot assemble True Color
        SGRs, because they will be ignored (if we are lucky), or displayed in a
        glitchy way, or mess up the output completely. The good news is that the
        process is automatic and in most cases the library will manage the
        transformations by itself. If it's not the case, the developer can correct the
        behaviour by overriding the renderers' output mode. See `SgrRenderer` and
        `OutputMode` docs.

        :param bg: Set to *True* if required SGR should change the background color, or
                   *False* for the foreground (=text) color.
        :param upper_bound: Required result ``IColor`` type upper boundary, i.e., the
                            maximum acceptable color class, which will be the basis for
                            SGR being made.
        """
        if upper_bound is ColorRGB:
            if get_config().prefer_rgb:
                return make_color_rgb(*self.to_rgb(), bg)
            return make_color_256(self._code, bg)

        if upper_bound is Color256 or upper_bound is None:
            return make_color_256(self._code, bg)

        if self._color16_equiv:
            return self._color16_equiv.to_sgr(bg, upper_bound)

        return Color16.find_closest(self.hex_value).to_sgr(bg, upper_bound)

    def to_tmux(self, bg: bool) -> str:
        return f"colour{self._code}"

    @property
    def code(self) -> int:
        """Int code for a color setup, e.g. 52."""
        return self._code

    @classmethod
    def get_by_code(cls, code: int) -> Color256:
        """
        Get a `Color256` instance with specified code (=position in the index).

        :param code:      Color code to look up for (see `guide.ansi-presets.color256`).
        :raises KeyError: If no color with specified code is found.
        """
        return cls._index.get(code)

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._hex_value == other._hex_value and self._code == other._code

    def repr_attrs(self, verbose: bool = True) -> str:
        code = f"X{self._code}"
        value = self.format_value("")

        params = [code + f"[{value}]"]
        if verbose:
            params = [code, value, self._name]
        return ",".join(str(s) for s in filter(None, params))


class ColorRGB(IColor):
    """
    Variant of a ``IColor`` operating within RGB color space. Presets include
    `es7s named colors <guide.es7s-colors>`, a unique collection of colors
    compiled from several known sources after careful selection. However,
    it's not limited to aforementioned color list and can be easily extended.

    .. note ::

        Arguments ``register``, ``index``, ``aliases`` and ``variation_map``
        are *kwonly*-type args.


    :param hex_value: Color RGB value, e.g. :hex:`0x73A9C2`.
    :param name:      Name of the color, e.g. "moonstone-blue".
    :param register:  If *True*, add color to registry for resolving by name.
    :param index:     If *True*, add color to approximation index.
    :param aliases:   Alternative color names (used in `resolve_color()`).
    :param variation_map: Mapping {*int*: *str*}, where keys are hex values,
                          and values are variation names.
    """

    __hash__ = IColor.__hash__

    def __init__(
        self,
        hex_value: int,
        name: str = None,
        *,
        register: bool = False,
        index: bool = False,
        aliases: t.List[str] = None,
        variation_map: t.Dict[int, str] = None,
    ):
        super().__init__(hex_value, name)
        self._base: CT | None = None
        self._variations: t.Dict[str, CT] = {}
        self._make_variations(variation_map)
        self._register(None, register, index, aliases)

    def to_sgr(self, bg: bool, upper_bound: t.Type[IColor] = None) -> SequenceSGR:
        if upper_bound is ColorRGB or upper_bound is None:
            return make_color_rgb(*self.to_rgb(), bg)

        return Color256.find_closest(self._hex_value).to_sgr(bg, upper_bound)

    def to_tmux(self, bg: bool) -> str:  # rgb hex format should be lower-cased!
        return self.format_value("#").lower()

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._hex_value == other._hex_value

    def repr_attrs(self, verbose: bool = True) -> str:
        value = self.format_value("")

        params = [value]
        if verbose:
            params += [self.name]
        return ",".join(str(s) for s in filter(None, params))

    @property
    def base(self) -> CT | None:
        """Parent color for color variations. Empty for regular colors."""
        return self._base

    @property
    def variations(self) -> t.Dict[str, CT]:
        """
        List of color variations. *Variation* of a color is a similar color with
        almost the same name, but with differing suffix. The main idea of variations
        is to provide a basis for fuzzy searching, which will return several results
        for one query; i.e., when the query matches a color with variations, the whole
        color family can be considered a match, which should increase searching speed.
        """
        return self._variations


class _NoopColor(IColor):
    def __init__(self):
        super().__init__(0)

    def __bool__(self) -> bool:
        return False

    def to_sgr(self, bg: bool, upper_bound: t.Type[IColor] = None) -> SequenceSGR:
        return NOOP_SEQ

    def to_tmux(self, bg: bool) -> str:
        return ""

    @property
    def hex_value(self) -> int:
        raise LogicError("No color for NO-OP instance")

    def format_value(self, prefix: str = "0x") -> str:
        return (prefix if "=" in prefix else "") + "NOP"

    def repr_attrs(self, verbose: bool = True) -> str:
        return self.format_value()


class DefaultColor(IColor):
    def __init__(self):
        super().__init__(0)

    def to_sgr(self, bg: bool, upper_bound: t.Type[IColor] = None) -> SequenceSGR:
        return SeqIndex.BG_COLOR_OFF if bg else SeqIndex.COLOR_OFF

    def to_tmux(self, bg: bool) -> str:
        return "default"

    @property
    def hex_value(self) -> int:
        raise LogicError("Default colors entirely depend on user terminal settings")

    def format_value(self, prefix: str = "0x") -> str:
        return (prefix if "=" in prefix else "") + "DEF"

    def repr_attrs(self, verbose: bool = True) -> str:
        return self.format_value()


NOOP_COLOR = _NoopColor()
"""
Special ``IColor`` instance always rendering into empty string.

.. important ::
    Casting to *bool* results in **False** for all ``NOOP`` instances of the 
    library (`NOOP_SEQ`, `NOOP_COLOR` and `NOOP_STYLE`). This is intended. 

"""

DEFAULT_COLOR = DefaultColor()
"""
Special ``IColor`` instance rendering to SGR sequence telling the terminal
to reset fg or bg color; same for `TmuxRenderer`. Useful when you inherit
some `Style` with fg or bg color which you don't need, but at the same time
you don't actually want to set up any color whatsoever (as using `NOOP_COLOR`
will result in an inheritance of parent style color instead of terminal default).

	>>> DEFAULT_COLOR.to_sgr(bg=False)
	<SGR[39]>

	>>> import pytermor as pt
	>>> pt.Style(pt.Styles.CRITICAL, fg=NOOP_COLOR)
	<Style[hi-white:X160[D70000]]>
	
	>>> pt.Style(pt.Styles.CRITICAL, fg=DEFAULT_COLOR)
	<Style[DEF:X160[D70000]]>
	
"""


def resolve_color(subject: CDT, color_type: t.Type[CT] = None) -> CT:
    """
    Case-insensitive search through registry contents. Search is performed for
    ``IColor`` instance with name ``subject`` if the ``color_type`` registry.
    If ``color_type`` is omitted, all the registries will be requested in this
    order: [`Color16`, `Color256`, `ColorRGB`]. Should any registry return a match,
    the resolving is stopped and the result is returned.

        >>> resolve_color('red')
        <Color16[#31,800000?,red]>

    If ``color_type`` is `ColorRGB` or *None*, one more way to specify a color
    is supported. ``subject`` should be:

        1) in full hexadecimal form as *str*: ":hex:`#RRGGBB`",
        2) in short hexadecimal form as *str*: ":hex:`#RGB`",
        3) as an integer in [:hex:`0x000000`; :hex:`0xFFFFFF`] range.

    Note that '#' in the beginning of the string is essential, as it tells the
    resolver to parse a string instead of invoking the registry.

    .. important ::

        In this case no actual searching is performed, and a new nameless instance
        of `ColorRGB` is created and returned. This instance will be a "unbound" color,
        i.e. it does not end up in a registry or index, thus it can't be resolved by
        name and can't be used in approximation procedures.

    ::

        >>> resolve_color("#333")
        <ColorRGB[333333]>
        >>> resolve_color(0xfafef0)
        <ColorRGB[FAFEF0]>

    Color names are stored in registries as tokens, which allows to use any form of
    input and get the correct result regardless. The only requirement is to split the
    words in any matter, so that tokenizer could distinguish the words from each other:

        >>> resolve_color('deep-sky-blue-7')
        <Color256[X23,005F5F,deep-sky-blue-7]>
        >>> resolve_color('DEEP_SKY_BLUE_7')
        <Color256[X23,005F5F,deep-sky-blue-7]>
        >>> resolve_color('DeepSkyBlue7')
        <Color256[X23,005F5F,deep-sky-blue-7]>

        >>> resolve_color('deepskyblue7')
        Traceback (most recent call last):
        LookupError: Color 'deepskyblue7' was not found in any of registries

    :param str|int subject:
            ``IColor`` name or hex value to search for. See `CDT`.
    :param color_type:   Target color type (`Color16`, `Color256` or `ColorRGB`).
    :raises LookupError: If nothing was found in either of registries.
    :return:             ``IColor`` instance with specified name or value.
    """

    def as_hex(s: CDT):
        if isinstance(s, int):
            return s
        if re.fullmatch(r"#[\da-f]{3}([\da-f]{3})?", s, flags=re.IGNORECASE):
            s = s[1:]
            if len(s) == 3:
                # 3-digit hex notation, basically #RGB -> #RRGGBB
                # https://www.quackit.com/css/color/values/css_hex_color_notation_3_digits.cfm
                s = "".join(map(lambda c: 2 * c, s))
            return int(s, 16)
        return None

    if (hex_value := as_hex(subject)) is not None:
        if color_type is None or color_type == ColorRGB:
            return ColorRGB(hex_value)

    for ct in [color_type or Color16, Color256, ColorRGB]:
        try:
            return ct.resolve(str(subject))
        except LookupError:
            continue
    raise LookupError(f"Color '{subject}' was not found in any of registries")


def find_closest(hex_value: int, color_type: t.Type[CT] = None) -> CT:
    """
    Search and return nearest to ``hex_value`` instance of specified ``color_type``.
    If `color_type` is omitted, search for the closest `Color256` element.

    Method is useful for finding applicable color alternatives if user's
    terminal is incapable of operating in more advanced mode. Usually it is
    done by the library automatically and transparently for both the developer
    and the end-user.

    .. note ::

        This method caches the results, i.e., the same search query will from then
        onward result in the same return value without the necessity of iterating
        through the color index. If that's not applicable, use similar method
        `approximate()`, which is unaware of caching mechanism altogether.

    :param hex_value:   Target color RGB value.
    :param color_type:  Target color type (`Color16`, `Color256` or `ColorRGB`).
    :return:            Nearest to ``hex_value`` color instance of specified type.
    """
    return (color_type or Color256).find_closest(hex_value)


def approximate(
    hex_value: int, color_type: t.Type[CT] = None, max_results: int = 1
) -> t.List[ApxResult[CT]]:
    """
    Search for nearest to ``hex_value`` colors of specified ``color_type`` and
    return the first ``max_results`` of them. If `color_type` is omitted, search
    for the closest `Color256` elements. This method is similar to the
    `find_closest()`, although they differ in some aspects:

        - `approximate()` can return more than one result;
        - `approximate()` returns not just a ``IColor`` instance(s), but also a
          number equal to squared distance to the target color for each of them;
        - `find_closest()` caches the results, while `approximate()` ignores
          the cache completely.

    :param hex_value:    Target color RGB value.
    :param color_type:   Target color type (`Color16`, `Color256` or `ColorRGB`).
    :param max_results:  Return no more than ``max_results`` items.
    :return: Pairs of closest ``IColor`` instance(s) found with their distances
             to the target color, sorted by distance descending, i.e., element
             at index 0 is the closest color found, paired with its distance
             to the target; element with index 1 is second-closest color
             (if any) and corresponding distance value, etc.
    """
    return (color_type or Color256).approximate(hex_value, max_results)


class ColorNameConflictError(Exception):
    def __init__(self, tokens: t.Tuple[str], existing_color: CT, new_color: CT):
        msg = f"Color '{new_color.name}' -> {tokens} already exists"
        super().__init__(msg, [existing_color, new_color])


class ColorCodeConflictError(Exception):
    def __init__(self, code: int, existing_color: CT, new_color: CT):
        msg = f"Color #{code} already exists"
        super().__init__(msg, existing_color, new_color)
