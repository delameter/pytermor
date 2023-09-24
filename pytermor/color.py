# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
"""
Abstractions for color definitions in three primary modes: 4-bit, 8-bit and
24-bit (``xterm-16``, ``xterm-256`` and ``True Color/RGB``, respectively).
Provides a global registry for color searching by names and codes, as well as
approximation algorithms, which are used for output devices with limited
advanced color modes support. Renderers do that automatically and transparently
for the developer, but the manual control over this process is also an option.

Supports 4 different color spaces: `RGB`, `HSV`, `XYZ` and `LAB`, and also
provides methods to covert colors from any space to any other.

"""
from __future__ import annotations

import dataclasses
import math
import re
import typing as t
from abc import ABCMeta, abstractmethod
from collections.abc import Iterable
from functools import cached_property
from math import sqrt
from typing import TypeVar, OrderedDict

from .ansi import BG_HI_COLORS, ColorTarget, HI_COLORS, NOOP_SEQ, SequenceSGR
from .common import CDT
from .common import get_qname
from .config import get_config
from .exception import (
    ColorCodeConflictError,
    ColorNameConflictError,
    LogicError,
    NotInitializedError,
)
from .term import make_color_256, make_color_rgb

_T = t.TypeVar("_T", bound=object)
ExtractorT = t.Union[str, t.Callable[[_T], "Color"], None]

_RCT = t.TypeVar("_RCT", bound="ResolvableColor")
_CVT = t.TypeVar("_CVT", bound="IColorValue")
_VT = TypeVar("_VT", int, float)

Color = TypeVar("Color", "Color16", "Color256", "ColorRGB")


class _ConstrainedValue(t.Generic[_VT]):
    def __init__(
        self,
        val: _VT,
        min_val: t.Optional[_VT] = 0,
        max_val: t.Optional[_VT] = None,
    ):
        if min_val is not None and max_val is not None and max_val < min_val:
            raise ValueError(
                f"No value can satisfy specified constraints: "
                f"{max_val} <= {val} <= {min_val})"
            )
        self._max_val: t.Optional[_VT] = max_val
        self._min_val: t.Optional[_VT] = min_val
        self._value: _VT = self._normalize(val)

    def _normalize(self, value: _VT) -> _VT:
        if self._min_val is not None:
            value = max(self._min_val, value)
        if self._max_val is not None:
            value = min(self._max_val, value)
        return value

    @property
    def value(self) -> _VT:
        return self._value


class IColorValue(metaclass=ABCMeta):
    @classmethod
    def diff(cls, c1: _CVT, c2: _CVT) -> float:
        ...

    def __int__(self) -> int:
        return self.int

    def __eq__(self, other) -> bool:
        try:
            return self.int == int(other)
        except (ValueError, LogicError):  # pragma: no cover
            return False

    @property
    @abstractmethod
    def int(self) -> int:
        """
        Color value in RGB space (24-bit integer within
        [0; :hex:`0xFFFFFF`] range)
        """
        # >>> RGB.from_channels(0, 128, 0).int
        # 32768
        # >>> hex(HSV(270, 2/3, 0.75).int)
        # '0x8040c0'

    @property
    @abstractmethod
    def rgb(self) -> RGB:
        """Color value in RGB space (3 × 8-bit ints)"""
        # >>> RGB(0x80ff80).red
        # 128
        # >>> [*RGB(0x80ff00)]
        # [128, 255, 0]

    @property
    @abstractmethod
    def hsv(self) -> HSV:
        """Color value in HSV space (three floats)"""

    @property
    @abstractmethod
    def xyz(self) -> XYZ:
        """Color value in XYZ space (three floats)"""

    @property
    @abstractmethod
    def lab(self) -> LAB:
        """Color value in LAB space (three floats)"""


_CIE_E: float = 216.0 / 24389.0  # 0.008856451679035631  # see http://brucelindbloom.com/

_REF_X: float = 95.047  # Observer= 2°, Illuminant= D65
_REF_Y: float = 100.000
_REF_Z: float = 108.883


class RGB(IColorValue):
    """
    Color value stored internally as an 24-bit integer.
    Base for more complex color classes.
    """

    @classmethod
    def diff(cls, c1: RGB, c2: RGB) -> float:
        """
        RGB euclidean distance.
        """
        if not isinstance(c1, RGB):
            c1 = getattr(c1, "rgb")
        if not isinstance(c2, RGB):
            c2 = getattr(c2, "rgb")
        r1, g1, b1 = c1
        r2, g2, b2 = c2
        dr = r2 - r1
        dg = g2 - g1
        db = b2 - b1
        return sqrt(dr**2 + dg**2 + db**2)

    @classmethod
    def from_channels(cls, red: int, green: int, blue: int) -> RGB:
        """

        :param red:
        :type red:
        :param green:
        :type green:
        :param blue:
        :type blue:
        :return:
        :rtype:
        """
        chans = (red, green, blue)
        return RGB(sum(int(ch) << 8 * (2 - idx) for (idx, ch) in enumerate(chans)))

    @classmethod
    def from_ratios(cls, rr: float, gr: float, br: float) -> RGB:
        """
        d
        :param rr:
        :param gr:
        :param br:
        """
        return cls.from_channels(round(rr * 255), round(gr * 255), round(br * 255))

    def __init__(self, value: int):
        self._int = _ConstrainedValue[int](value, max_val=0xFFFFFF)

    def __iter__(self) -> t.Iterator[int]:
        return iter((self.red, self.green, self.blue))

    def __str__(self) -> str:  # RGB(R=128, G=0, B=0)
        def _format_channel(attr: str) -> str:
            return f"{attr.upper()[0]}={getattr(self, attr):d}"

        attrs = [
            _format_channel("red"),
            _format_channel("green"),
            _format_channel("blue"),
        ]
        return f"{get_qname(self)}[#{self.int:06X}][{' '.join(attrs)}]"

    __repr__ = __str__

    @cached_property
    def red(self) -> int:
        """Red channel value [0;255]"""
        return (self._int.value & 0xFF0000) >> 16

    @cached_property
    def green(self) -> int:
        """Green channel value [0;255]"""
        return (self._int.value & 0xFF00) >> 8

    @cached_property
    def blue(self) -> int:
        """Blue channel value [0;255]"""
        return self._int.value & 0xFF

    @cached_property
    def int(self) -> int:
        return self._int.value

    @property
    def rgb(self) -> RGB:
        return self

    @cached_property
    def hsv(self) -> HSV:
        # https://en.wikipedia.org/wiki/HSL_and_HSV#From_RGB
        r, g, b = self

        rn, gn, bn = r / 255, g / 255, b / 255
        vmax = max(rn, gn, bn)
        vmin = min(rn, gn, bn)
        c = vmax - vmin
        v = vmax

        h = 0.0
        if c == 0:
            pass
        elif v == rn:
            h = 60 * (0 + (gn - bn) / c)
        elif v == gn:
            h = 60 * (2 + (bn - rn) / c)
        else:  # v == bn:
            h = 60 * (4 + (rn - gn) / c)

        if v == 0:
            s = 0
        else:
            s = c / v

        if h < 0:
            h += 360

        return HSV(hue=h, saturation=s, value=v)

    @cached_property
    def xyz(self) -> XYZ:
        def f(v) -> float:
            if v <= 0.04045:
                return v / 12.92
            return ((v + 0.055) / 1.055) ** 2.4

        r, g, b = self
        rn, gn, bn = (100.0 * f(v / 255) for v in (r, g, b))

        x: float = 0.4124 * rn + 0.3576 * gn + 0.1805 * bn  # sRGB D65 -> XYZ D50
        y: float = 0.2126 * rn + 0.7152 * gn + 0.0722 * bn
        z: float = 0.0193 * rn + 0.1192 * gn + 0.9503 * bn

        return XYZ(x, y, z)

    @cached_property
    def lab(self) -> LAB:
        return self.xyz.lab


class HSV(IColorValue):
    """
    Initially HSV is a transformation of RGB color space; color is stored as 3
    floats representing Hue channel, Saturation channel and Value channel
    correspondingly. Supports direct (fast) transformation to RGB and indirect
    (=slow) to all other spaces through using more than one conversion with
    HSV → RGB being the first one.
    """

    @classmethod
    def diff(cls, c1: HSV, c2: HSV) -> float:
        """
        HSV euclidean distance.
        """
        if not isinstance(c1, HSV):
            c1 = getattr(c1, "hsv")
        if not isinstance(c2, HSV):
            c2 = getattr(c2, "hsv")

        h1, s1, v1 = c1
        h2, s2, v2 = c2
        dh = min(abs(h2 - h1), 360 - abs(h2 - h1)) / 180.0
        ds = s2 - s1
        dv = v2 - v1

        return float(sqrt(dh**2 + ds**2 + dv**2))

    def __init__(self, hue: float, saturation: float, value: float):
        self._hue = _ConstrainedValue[float](hue, max_val=360.0)
        self._saturation = _ConstrainedValue[float](saturation, max_val=1.0)
        self._value = _ConstrainedValue[float](value, max_val=1.0)

    def __iter__(self) -> t.Iterator[float]:
        return iter((self.hue, self.saturation, self.value))

    def __str__(self):  # HSV(H=0° S=100% V=50%)
        attrs = [
            f"H={self.hue:.0f}°",
            f"S={100*self.saturation:.0f}%",
            f"V={100*self.value:.0f}%",
        ]
        return f"{self.__class__.__name__}[{' '.join(attrs)}]"

    __repr__ = __str__

    @property
    def hue(self) -> float:
        """Hue channel value [0;360]"""
        return self._hue.value

    @property
    def saturation(self) -> float:
        """Saturation channel value [0;1]"""
        return self._saturation.value

    @property
    def value(self) -> float:
        """Value channel value [0;1]"""
        return self._value.value

    @cached_property
    def int(self) -> int:
        return self.rgb.int

    @cached_property
    def rgb(self) -> RGB:
        # >>> HSV(270, 2/3, 0.75).rgb
        # RGB[#8040C0][R=128 G=64 B=192]
        # >>> HSV(hue=120, saturation=0.5, value=0.77).rgb
        # RGB[#63C563][R=99 G=197 B=99]
        h, s, v = self

        h = 0.0 if h == 360.0 else h / 60.0
        fract = h - math.floor(h)

        pv = v * (1.0 - s)
        qv = v * (1.0 - s * fract)
        tv = v * (1.0 - s * (1.0 - fract))

        if 0.0 <= h < 1.0:
            r, g, b = v, tv, pv
        elif 1.0 <= h < 2.0:
            r, g, b = qv, v, pv
        elif 2.0 <= h < 3.0:
            r, g, b = pv, v, tv
        elif 3.0 <= h < 4.0:
            r, g, b = pv, qv, v
        elif 4.0 <= h < 5.0:
            r, g, b = tv, pv, v
        else:
            r, g, b = v, pv, qv

        return RGB.from_channels(
            math.ceil(255 * r), math.ceil(255 * g), math.ceil(255 * b)
        )

    @property
    def hsv(self) -> HSV:
        return self

    @cached_property
    def xyz(self) -> XYZ:
        return self.rgb.xyz

    @cached_property
    def lab(self) -> LAB:
        return self.rgb.lab


class XYZ(IColorValue):
    """
    Color in XYZ space is represented by three floats: Y is the luminance, Z is
    quasi-equal to blue (of CIE RGB), and X is a mix of the three CIE RGB curves
    chosen to be nonnegative. CIE 1931 XYZ color space was one of the first
    attempts to produce a color space based on measurements of human color
    perception. Setting Y as luminance has the useful result that for any given
    Y value, the XZ plane will contain all possible chromaticities at that
    luminance.

    .. note ::

        `x` and `z` values can be above 100.

    """

    @classmethod
    def diff(cls, c1: XYZ, c2: XYZ) -> float:  # pragma: no cover
        """
        .. note ::

            This one is written on the analogy of other diffs, therefore
            it can be actually a little bit incorrect or outright wrong.

        """
        if not isinstance(c1, XYZ):
            c1 = getattr(c1, "xyz")
        if not isinstance(c2, XYZ):
            c2 = getattr(c2, "xyz")

        x1, y1, z1 = c1
        x2, y2, z2 = c2
        dx = x2 - x1
        dy = y2 - y1
        dz = z2 - z1

        return sqrt(dx**2 + dy**2 + dz**2)

    def __init__(self, x: float, y: float, z: float):
        self._x = _ConstrainedValue[float](x)
        self._y = _ConstrainedValue[float](y, max_val=100.00)
        self._z = _ConstrainedValue[float](z)

    def __iter__(self) -> t.Iterator[float]:
        return iter((self.x, self.y, self.z))

    def __str__(self):  # XYZ(X=0.95 Y=1.00 Z=1.08)
        attrs = [
            f"X={self.x:.2f}",
            f"Y={self.y:.2f}%",
            f"Z={self.z:.2f}",
        ]
        return f"{self.__class__.__name__}[{' '.join(attrs)}]"

    __repr__ = __str__

    @property
    def x(self) -> float:
        """X channel value [0;100)"""
        return self._x.value

    @property
    def y(self) -> float:
        """Luminance [0;100]"""
        return self._y.value

    @property
    def z(self) -> float:
        """Quasi-equal to blue [0;100)"""
        return self._z.value

    @cached_property
    def int(self) -> int:
        return self.rgb.int

    @cached_property
    def rgb(self) -> RGB:
        def f(v) -> float:
            if v <= 0.0031308:
                return 12.92 * v
            return 1.055 * (v ** (1 / 2.4)) - 0.055

        x, y, z = self
        xn, yn, zn = (v / 100.0 for v in (x, y, z))

        rr: float = f(xn * 3.2406 + yn * -1.5372 + zn * -0.4986)  # sRGB
        gr: float = f(xn * -0.9689 + yn * 1.8758 + zn * 0.0415)
        br: float = f(xn * 0.0557 + yn * -0.2040 + zn * 1.0570)

        return RGB.from_ratios(rr, gr, br)

    @cached_property
    def hsv(self) -> HSV:
        return self.rgb.hsv

    @property
    def xyz(self) -> XYZ:
        return self

    @cached_property
    def lab(self) -> LAB:
        def f(v: float) -> float:
            if v > _CIE_E:
                return math.pow(v, 1 / 3)
            else:
                return (7.787 * v) + (16.0 / 116.0)

        x, y, z = self

        x /= _REF_X
        y /= _REF_Y
        z /= _REF_Z

        fx, fy, fz = (f(v) for v in (x, y, z))

        lv = (116.0 * fy) - 16.0
        a = 500.0 * (fx - fy)
        b = 200.0 * (fy - fz)

        return LAB(lv, a, b)


class LAB(IColorValue):
    """
    Color value in a *uniform* color space, CIELAB, which expresses color as
    three values: L* for perceptual lightness and a* and b* for the four unique
    colors of human vision: red, green, blue and yellow. CIELAB was intended as
    a perceptually uniform space, where a given numerical change corresponds to
    a similar perceived change in color. Like the CIEXYZ space it derives from,
    CIELAB color space is a device-independent, "standard observer" model.
    """

    @classmethod
    def diff(cls, c1: LAB, c2: LAB) -> float:
        """
        CIE76 \u0394E\\* color difference.
        """
        if not isinstance(c1, LAB):
            c1 = getattr(c1, "lab")
        if not isinstance(c2, LAB):
            c2 = getattr(c2, "lab")

        l1, a1, b1 = c1
        l2, a2, b2 = c2
        dl = l2 - l1
        da = a2 - a1
        db = b2 - b1

        return sqrt(dl**2 + da**2 + db**2)

    def __init__(self, lum: float, a: float, b: float):
        self._lum = _ConstrainedValue[float](lum, max_val=100.00)
        self._a = _ConstrainedValue[float](a, min_val=None)
        self._b = _ConstrainedValue[float](b, min_val=None)

    def __iter__(self) -> t.Iterator[float]:
        return iter((self.lum, self.a, self.b))

    def __str__(self):  # LAB(L=100% a=100 b=-100)
        attrs = [
            f"L={self.lum:.3f}%",
            f"a={self.a:.3f}",
            f"b={self.b:.3f}",
        ]
        return f"{self.__class__.__name__}[{' '.join(attrs)}]"

    __repr__ = __str__

    @property
    def lum(self) -> float:
        """Luminance [0;100]"""
        return self._lum.value

    @property
    def a(self) -> float:
        """Green–magenta axis, [-100;100] in general, but can be less/more"""
        return self._a.value

    @property
    def b(self) -> float:
        """Blue–yellow axis, [-100;100] in general, but can be less/more"""
        return self._b.value

    @cached_property
    def int(self) -> int:
        return self.xyz.rgb.int

    @cached_property
    def rgb(self) -> RGB:
        return self.xyz.rgb

    @cached_property
    def hsv(self) -> HSV:
        return self.xyz.rgb.hsv

    @cached_property
    def xyz(self) -> XYZ:
        def f(v: float) -> float:
            if (v3 := v**3) > _CIE_E:
                return v3
            else:
                return (v - 16.0 / 116.0) / 7.787

        l, a, b = self

        fy: float = (l + 16.0) / 116.0
        fx: float = (a / 500.0) + fy
        fz: float = fy - (b / 200.0)

        x, y, z = (f(v) for v in (fx, fy, fz))

        x *= _REF_X
        y *= _REF_Y
        z *= _REF_Z

        return XYZ(x, y, z)

    @property
    def lab(self) -> LAB:
        return self


# ---------------------------------------------------------------------------------------


class RenderColor:
    """
    Abstract superclass for other ``Colors``. Provides interfaces for
    transforming RGB values to SGRs for different terminal modes.
    """

    @abstractmethod
    def to_sgr(
        self, target: ColorTarget = ColorTarget.FG, upper_bound: t.Type[Color] = None
    ) -> SequenceSGR:
        """
        Make an `SGR sequence<SequenceSGR>` out of ``Color``. Used by `SgrRenderer`.

        :param target:      Sequence context (FG, BG, UNDERLINE).
        :param upper_bound: Required result ``Color`` type upper boundary, i.e., the
                            maximum acceptable color class, which will be the basis for
                            SGR being made. See `Color256.to_sgr()` for the details.
        """
        raise NotImplementedError

    @abstractmethod
    def to_tmux(self, target: ColorTarget = ColorTarget.FG) -> str:
        """
        Make a tmux markup directive, which will change the output color to
        this color's value (after tmux processes and prints it). Used by `TmuxRenderer`.

        :param target:      Sequence context (FG, BG, UNDERLINE).
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"<{get_qname(self)}[{self.repr_attrs()}]>"

    @abstractmethod
    def repr_attrs(self, verbose: bool = True) -> str:
        raise NotImplementedError


class RealColor(IColorValue):
    def __init__(self, value: IColorValue | int | None):
        if isinstance(value, IColorValue):
            self.__value: RGB = value.rgb
        elif isinstance(value, int):
            self.__value: RGB = RGB(value)
        else:  # pragma: no cover
            pass  # dynamic via _value() property override

    def __hash__(self) -> int:  # pragma: no cover
        return hash(self.int)

    @property
    def _value(self) -> RGB:
        return self.__value

    def format_value(self, prefix: str = "0x") -> str:
        """Format color value as ":hex:`0xRRGGBB`"."""
        return f"{prefix:s}{self.int:06x}"

    @property
    def int(self) -> int:
        return self._value.int

    @property
    def rgb(self) -> RGB:
        return self._value.rgb

    @property
    def hsv(self) -> HSV:
        return self._value.hsv

    @property
    def xyz(self) -> XYZ:
        return self._value.xyz

    @property
    def lab(self) -> LAB:
        return self._value.lab


# ---------------------------------------------------------------------------------------


class _ResolvableColorMeta(ABCMeta):
    def __new__(mcls, name, bases, namespace, **kwargs):
        cls = super().__new__(mcls, name, bases, namespace, **kwargs)

        cls._registry = _ColorRegistry[cls]()
        cls._index = _ColorIndex[cls]()
        cls._approx_cache = dict()
        return cls

    def __iter__(self) -> t.Iterator[_RCT]:
        return iter(self._registry)


class _ColorRegistry(t.Generic[_RCT], t.Sized, t.Iterable):
    # Colors hashed by name parts

    _TOKEN_SEPARATOR = "-"
    _QUERY_SPLIT_REGEX = re.compile(r"[\W_]+|(?<=[a-z])(?=[A-Z0-9])")

    def __init__(self):
        self._map: t.Dict[t.Tuple[str], _RCT] = {}
        self._set: t.Set[_RCT] = set()

    def register(self, color: _RCT, name: str):
        primary_tokens = tuple(filter(None, self._QUERY_SPLIT_REGEX.split(name)))
        self._register_pair(color, primary_tokens)

        if not isinstance(color, ColorRGB):
            return
        for variation in color.variations.values():
            variation_tokens: t.Tuple[str, ...] = (
                *primary_tokens,
                *(self._QUERY_SPLIT_REGEX.split(variation.name)),
            )
            self._register_pair(variation, variation_tokens)

    def _register_pair(self, color: _RCT, tokens: t.Tuple[str, ...]):
        self._set.add(color)

        if tokens not in self._map.keys():
            self._map[tokens] = color
            return

        existing_color = self._map.get(tokens)
        if color.int == existing_color.int:
            return  # skipping the duplicate with the same name and value
        raise ColorNameConflictError(tokens, existing_color, color)

    def find_by_name(self, name: str) -> _RCT:
        query_tokens = (*(qt.lower() for qt in self._QUERY_SPLIT_REGEX.split(name)),)
        if color := self._map.get(query_tokens, None):
            return color
        raise LookupError(f"Color '{name}' does not exist")

    def __len__(self) -> int:
        return len(self._map)

    def __bool__(self) -> bool:
        return len(self) > 0

    def __iter__(self) -> t.Iterator[_RCT]:
        return iter(self._set)

    def names(self) -> t.Iterable[t.Tuple[str]]:
        return self._map.keys()


class _ColorIndex(t.Generic[_RCT], t.Sized):
    # Colors indexed by CODE (not RGB value)

    def __init__(self):
        self._map: t.OrderedDict[int, _RCT] = OrderedDict[int, _RCT]()

    def add(self, color: _RCT, code: int | None):
        if code is None:
            code = len(self._map)
        if code not in self._map.keys():
            self._map[code] = color
            return

        existing_color = self._map.get(code)
        if color.int == existing_color.int:
            return  # skipping the duplicate with the same code and value
        raise ColorCodeConflictError(code, existing_color, color)

    def get(self, code: int) -> _RCT:
        if color := self._map.get(code, None):  # pragma: no cover
            return color
        raise LookupError(f"Color #{code} does not exist")

    def __len__(self) -> int:
        return len(self._map)

    def __bool__(self) -> bool:
        return len(self) > 0

    def __iter__(self) -> t.Iterator[_RCT]:
        return iter(self._map.values())


class ResolvableColor(t.Generic[_RCT], metaclass=_ResolvableColorMeta):
    """
    Mixin for other ``Colors``. Implements color search by name.
    """

    _registry: _ColorRegistry[_RCT]
    _index: _ColorIndex[_RCT]
    _approx_cache: t.Dict[int, _RCT]
    _color_diff_fn: t.ClassVar[_ColorDiffFn]

    @classmethod
    def names(cls) -> t.Iterable[t.Tuple[str]]:
        """All registried colors' names of this type."""
        cls._ensure_loaded()
        return cls._registry.names()

    @classmethod
    def find_by_name(cls: t.Type[_RCT], name: str) -> _RCT:
        """
        Case-insensitive search through registry contents.

        .. seealso:: `resolve_color()` for the details

        :param name:  Name to search for.
        """
        if not hasattr(cls, "_registry"):  # pragma: no cover
            raise LogicError(
                "Registry not found. Did you call an abstract class' method?"
            )
        cls._ensure_loaded()
        return cls._registry.find_by_name(name)

    @classmethod
    def find_closest(cls: type[_RCT], value: IColorValue | int) -> _RCT:
        """
        Search and return color instance nearest to ``value``.

        .. seealso:: `color.find_closest()` for the details

        :param value: Target color/color value.
        """
        if not hasattr(cls, "_index"):  # pragma: no cover
            raise LogicError("Index not found. Did you call an abstract class' method?")

        if not isinstance(value, IColorValue):
            value = RGB(value)

        if value.int in cls._approx_cache.keys():
            return cls._approx_cache.get(value.int)

        closest = cls._find_neighbours(value)[0].color
        cls._approx_cache[value.int] = closest
        return closest

    @classmethod
    def approximate(
        cls: type[_RCT],
        value: IColorValue | int,
        max_results: int = 1,
    ) -> t.List[ApxResult[_RCT]]:
        """
        Search for the colors nearest to ``value`` and return the first ``max_results``.

        .. seealso:: `color.approximate()` for the details

        :param value:       Target color/color value.
        :param max_results: Result limit.
        """
        if not hasattr(cls, "_index"):  # pragma: no cover
            raise LogicError("Index is empty. Did you call an abstract class' method?")

        if not isinstance(value, IColorValue):
            value = RGB(value)

        return cls._find_neighbours(value)[:max_results]

    @classmethod
    def _find_neighbours(cls: type[_RCT], value: IColorValue) -> t.List[ApxResult[_RCT]]:
        """
        Iterate the registered colors table and compute CIE76 \u0394E\\* (color difference)
        between argument and each color of the palette. Sort the results and return them.

        **CIELAB \u0394E\\***
            https://en.wikipedia.org/wiki/Color_difference#CIE76

        :param value: Target color/color value.
        """
        cls._ensure_loaded()
        return sorted(cls._color_diff_fn(value), key=lambda r: r.distance)

    @classmethod
    def _ensure_loaded(cls):
        if not cls._registry or not cls._index:
            cls._load()

    @classmethod
    def _load(cls):
        ...

    @classmethod
    def _calc_lab_cie76_delta_e(
        cls: type[_RCT], value: _CVT
    ) -> Iterable[ApxResult[_RCT]]:
        for el in cls._index:
            yield ApxResult(el, LAB.diff(value, el))

    def __new__(cls: t.Type[_RCT], *args, **kwargs) -> _RCT:
        cls._color_diff_fn = cls._calc_lab_cie76_delta_e
        return super().__new__(cls)

    def __init__(
        self,
        name: str,
        register: bool,
        code: int | None,
        aliases: t.List[str],
        variation_map: t.Dict[int, str] = None,
    ):
        self._name: str | None = name
        self._base: _RCT | None = None
        self._variations: t.Dict[str, _RCT] = {}

        if code is not None:
            self._index.add(self, code)
        if variation_map:
            self._make_variations(variation_map)
        if register:
            self._register(aliases)

    def __hash__(self) -> int:  # pragma: no cover
        return hash(self._name)

    def _register(self: _RCT, aliases: t.List[str] = None):
        if not self.name:
            return
        self._registry.register(self, self.name)

        if not aliases:
            return
        for alias in aliases:
            self._registry.register(self, alias)

    def _make_variations(self: _RCT, variation_map: t.Dict[int, str] = None):
        for vari_value, vari_name in variation_map.items():
            args = dict(value=vari_value, name=vari_name, register=False)
            variation = type(self)(**args)
            variation._base = self
            self._index.add(variation, None)
            self._variations[vari_name] = variation

    @property
    def name(self) -> str | None:
        """Color name, e.g. "navy-blue"."""
        return self._name


@dataclasses.dataclass(frozen=True)
class ApxResult(t.Generic[_RCT]):
    """
    Approximation result.
    """

    color: _RCT
    """ Found ``Color`` instance. """

    distance: float
    """ Color difference between this instance and the approximation target. """

    def __eq__(self, other: ApxResult) -> bool:  # pragma: no cover
        if not isinstance(other, ApxResult):
            return False
        if not isinstance(other.color, type(self)):
            return False
        return self.color == other.color and self.distance == other.distance


_ColorDiffFn = t.Callable[[IColorValue], Iterable[ApxResult[_RCT]]]

# ---------------------------------------------------------------------------------------


class Color16(RealColor, RenderColor, ResolvableColor["Color16"]):
    """
    Variant of a ``Color`` operating within the most basic color set
    -- **xterm-16**. Represents basic color-setting SGRs with primary codes
    30-37, 40-47, 90-97 and 100-107 (see `guide.ansi-presets.color16`).

    :param int|IColorValue value:
                           Color value as 24-bit integer in RGB space, or any
                           instance implementing color value interface (e.g. `HSV`).
    :param int code_fg:    Int code for a foreground color setup, e.g. 30.
    :param int code_bg:    Int code for a background color setup. e.g. 40.
    :param str name:       Name of the color, e.g. "red".
    :param bool register:  If *True*, add color to registry for resolving by name
                           and approximation.
    :param list[str] aliases:
                           Alternative color names (used in `resolve_color()`).
    """

    def __init__(
        self,
        value: IColorValue | int,
        code_fg: int,
        code_bg: int,
        name: str = None,
        *,
        register: bool = False,
        aliases: t.List[str] = None,
    ):
        self._code_fg: int = code_fg
        self._code_bg: int = code_bg
        self._color256_equiv: list[Color256] = []

        super(Color16, self).__init__(value)
        super(RenderColor, self).__init__(name, register, code_fg, aliases)

    def __hash__(self) -> int:  # pragma: no cover
        return hash(super(Color16, self)) + hash(super(RenderColor, self))

    @property
    def code_fg(self) -> int:
        """Int code for a foreground color setup, e.g. 30."""
        return self._code_fg

    @property
    def code_bg(self) -> int:
        """Int code for a background color setup. e.g. 40."""
        return self._code_bg

    @property
    def color256_equiv(self) -> Color256 | None:
        """..."""
        if not self._color256_equiv:  # pragma: no cover
            return None
        return self._color256_equiv[0]

    @classmethod
    def get_by_code(cls, code: int) -> Color16:
        """
        Get a `Color16` instance with specified code. Only *foreground* (=text)
        colors are indexed, therefore it is not possible to look up for a
        `Color16` with given background color (on second thought, it *is*
        actually possible using `find_closest()`).

        :param code:          Foreground integer code to look up for (see
                              `guide.ansi-presets.color16`).
        :raises LookupError:  If no color with specified code is found.
        """
        cls._load()
        return cls._index.get(code)

    @classmethod
    def _load(cls):
        from .cval import cv

        cv.load()

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return (
            self.int == other.int
            and self._code_bg == other._code_bg
            and self._code_fg == other._code_fg
        )

    def assign_color256_equiv(self, color256_equiv: Color256):
        self._color256_equiv.append(color256_equiv)

    def repr_attrs(self, verbose: bool = True) -> str:
        # question mark after color value indicates that we cannot be 100% sure
        # about the exact value of xterm-16 colors, as they are configurable and
        # depend on terminal theme and settings. that's not the case for xterm-256,
        # though -- it's almost guaranteed to have the same color nearly everywhere.
        # the exceptions are rare and include color mapping at low level, e.g.,
        # ``tmux`` with specifically configured terminal capability overrides.
        # that's not something that you'd expect from a regular user, anyway.
        if not verbose:
            return self._name

        code = f"c{getattr(self, '_code_fg', None)}"
        value = f"{self.format_value('#')}?"
        params = " ".join(map(str, filter(None, [value, self._name])))
        return f"{code}({params})"

    def to_sgr(
        self, target: ColorTarget = ColorTarget.FG, upper_bound: t.Type[Color] = None
    ) -> SequenceSGR:
        if code := self._target_to_code(target):
            return SequenceSGR(code)
        raise NotImplementedError(f"No color-16 equivalent for {target}")

    def to_tmux(self, target: ColorTarget = ColorTarget.FG) -> str:
        if self._name is None:
            raise LogicError("Translation to tmux format failed: color name required")
        if not (code := self._target_to_code(target)):
            raise NotImplementedError(f"No tmux equivalent for {target}")
        is_hi = code in HI_COLORS or code in BG_HI_COLORS
        tmux_name = ("bright" if is_hi else "") + self._name.lower().replace("hi-", "")
        return tmux_name

    def _target_to_code(self, target: ColorTarget) -> int | None:
        if target == ColorTarget.FG:
            return self._code_fg
        if target == ColorTarget.BG:
            return self._code_bg
        return None  # no equivalent for underline color


class Color256(RealColor, RenderColor, ResolvableColor["Color256"]):
    """
    Variant of a ``Color`` operating within relatively modern **xterm-256**
    indexed color table. Represents SGR complex codes ``38;5;*`` and ``48;5;*``
    (see `guide.ansi-presets.color256`).

    :param int|IColorValue value:
                           Color value as 24-bit integer in RGB space, or any
                           instance implementing color value interface (e.g. `HSV`).
    :param code:      Int code for a color setup, e.g. 52.
    :param name:      Name of the color, e.g. "dark-red".
    :param register:  If *True*, add color to registry for resolving by name.
    :param aliases:   Alternative color names (used in `resolve_color()`).
    :param color16_equiv:
                      `Color16` counterpart (applies only to codes 0-15).
    """

    def __init__(
        self,
        value: IColorValue | int,
        code: int,
        name: str = None,
        *,
        register: bool = False,
        aliases: t.List[str] = None,
        color16_equiv: Color16 = None,
    ):
        self._code: int | None = code
        self._color16_equiv: Color16 | None = color16_equiv
        if self._color16_equiv:
            self._color16_equiv.assign_color256_equiv(self)

        super(Color256, self).__init__(value)
        super(RenderColor, self).__init__(name, register, code, aliases)

    def __hash__(self) -> int:  # pragma: no cover
        return hash(super(Color256, self)) + hash(super(RenderColor, self))

    def to_sgr(
        self, target: ColorTarget = ColorTarget.FG, upper_bound: t.Type[Color] = None
    ) -> SequenceSGR:
        """
        Make an `SGR sequence<SequenceSGR>` out of ``Color``. Used by `SgrRenderer`.

        Each ``Color`` type represents one SGR type in the context of colors. For
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

        :param target:
        :param upper_bound: Required result ``Color`` type upper boundary, i.e., the
                            maximum acceptable color class, which will be the basis for
                            SGR being made.
        """
        if upper_bound is ColorRGB:
            if get_config().prefer_rgb:
                return make_color_rgb(*self.rgb, target=target)
            return make_color_256(self._code, target)

        if upper_bound is Color256 or upper_bound is None:
            return make_color_256(self._code, target)

        # underline color can be defined as Color256 (58;5;x) or ColorRGB (58;2;r;g;b),
        # but not as Color16 (no equivalent SGR code);
        if target == ColorTarget.UNDERLINE:
            return NOOP_SEQ
            # that's why we should not raise NotImplemented here, as it will result in an
            # unpredictable behaviour depending on user's terminal mode, i.e., underlined
            # color working as expected in xterm-256color mode, but throwing an exception
            # in xterm-color mode; whereas Color16.to_sgr(target=UNDERLINE) will raise an
            # error regardless of terminal mode, which allows to detect and fix it early.

        if self._color16_equiv:
            return self._color16_equiv.to_sgr(target, upper_bound)

        return Color16.find_closest(self).to_sgr(target, upper_bound)

    def to_tmux(self, target: ColorTarget = ColorTarget.FG) -> str:
        if target in [ColorTarget.FG, ColorTarget.BG]:
            return f"colour{self._code}"
        raise NotImplementedError(f"No tmux equivalent for {target}")

    @property
    def code(self) -> int:
        """Int code for a color setup, e.g. 52."""
        return self._code

    @classmethod
    def get_by_code(cls, code: int) -> Color256:
        """
        Get a `Color256` instance with specified code (=position in the index).

        :param code:      Color code to look up for (see `guide.ansi-presets.color256`).
        :raises LookupError:
                         If no color with specified code is found.
        """
        cls._load()
        return cls._index.get(code)

    @classmethod
    def _load(cls):
        from .cval import cv

        cv.load()

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False

        values_match = self.int == other.int
        codes_match = self.code == other.code
        if not codes_match and self._color16_equiv and other._color16_equiv:
            # for cases when colors being compared have same value, same color16
            # equivalents, but different own codes, get primary reverse equivalents
            # (256 -> 16 -> 256) and compare the codes. this ensures that e.g.,
            # Color256._256A_16_WHITE == Color256.GRAY_100 is True.

            primary_reverse_equiv_self = self._color16_equiv.color256_equiv
            primary_reverse_equiv_other = other._color16_equiv.color256_equiv
            codes_match = (primary_reverse_equiv_self.code == primary_reverse_equiv_other.code)
        return values_match and codes_match

    def repr_attrs(self, verbose: bool = True) -> str:
        code = f"x{getattr(self, '_code', None)}"
        if not verbose:
            return code

        value = self.format_value("#")
        if getattr(self, "_color16_equiv", None):  # pragma: no cover
            value += "?"  # depends on end-user terminal setup
        params = " ".join(map(str, filter(None, [value, self._name])))
        return f"{code}({params})"


class ColorRGB(RealColor, RenderColor, ResolvableColor["ColorRGB"]):
    """
    Variant of a ``Color`` operating within RGB color space. Presets include
    `es7s named colors <guide.es7s-colors>`, a unique collection of colors
    compiled from several known sources after careful selection. However,
    it's not limited to aforementioned color list and can be easily extended.

    :param int|IColorValue value:
                      Color value as 24-bit integer in RGB space (e.g.
                      :hex:`0x73a9c2`), or any instance implementing color value
                      interface (e.g. `HSV`).
    :param name:      Name of the color, e.g. "moonstone-blue".
    :param register:  If *True*, add color to registry for resolving by name.
    :param aliases:   Alternative color names (used in `resolve_color()`).
    :param variation_map:
                      Mapping {*int*: *str*}, where keys are hex values,
                      and values are variation names.
    """

    def __init__(
        self,
        value: IColorValue | int,
        name: str = None,
        *,
        register: bool = False,
        aliases: t.List[str] = None,
        variation_map: t.Dict[int, str] = None,
    ):
        super(ColorRGB, self).__init__(value)
        super(RenderColor, self).__init__(name, register, None, aliases, variation_map)

    def __hash__(self) -> int:  # pragma: no cover
        return hash(super(ColorRGB, self)) + hash(super(RenderColor, self))

    def to_sgr(
        self, target: ColorTarget = ColorTarget.FG, upper_bound: t.Type[Color] = None
    ) -> SequenceSGR:
        if upper_bound is ColorRGB or upper_bound is None:
            return make_color_rgb(*self.rgb, target=target)
        return Color256.find_closest(self).to_sgr(target, upper_bound)

    def to_tmux(self, target: ColorTarget = ColorTarget.FG) -> str:
        if target in [ColorTarget.FG, ColorTarget.BG]:
            return self.format_value("#").lower()
        raise NotImplementedError(f"No tmux equivalent for {target}")

    @classmethod
    def _load(cls):
        from .cval import cvr

        cvr.load()

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.int == other.int

    def repr_attrs(self, verbose: bool = True) -> str:
        value = self.format_value("#")
        if not verbose or not self._name:
            return value
        return f"{value}({self._name})"

    @property
    def base(self) -> _RCT | None:
        """Parent color for color variations. Empty for regular colors."""
        return self._base

    @property
    def variations(self) -> t.Dict[str, _RCT]:
        """
        List of color variations. *Variation* of a color is a similar color with
        almost the same name, but with differing suffix. The main idea of
        variations is to provide a basis for fuzzy searching, which will return
        several results for one query; i.e., when the query matches a color with
        variations, the whole color family can be considered a match, which
        should increase searching speed.
        """
        return self._variations


# ---------------------------------------------------------------------------------------


class NoopColor(RenderColor):
    """
    Special ``Color`` class always rendering into empty string.

    .. important ::
        Casting to *bool* results in **False** for all ``NOOP`` instances in the
        library (`NOOP_SEQ`, `NOOP_COLOR` and `NOOP_STYLE`). This is intended.

    """

    def __init__(self):
        super().__init__()

    def __bool__(self) -> bool:
        return False

    def __eq__(self, other: Color) -> bool:
        return isinstance(other, NoopColor)

    def to_sgr(
        self, target: ColorTarget = ColorTarget.FG, upper_bound: t.Type[Color] = None
    ) -> SequenceSGR:
        return NOOP_SEQ

    def to_tmux(self, target: ColorTarget = ColorTarget.FG) -> str:
        if target in [ColorTarget.FG, ColorTarget.BG]:
            return ""
        raise NotImplementedError(f"No tmux equivalent for {target}")

    # noinspection PyMethodMayBeStatic
    def format_value(self, prefix: str = "") -> str:
        return prefix + "NOP"

    def repr_attrs(self, verbose: bool = True) -> str:
        return self.format_value()


class DefaultColor(RenderColor):
    """
    Special ``Color`` instance rendering to SGR sequence telling the terminal
    to reset fg or bg color; same for `TmuxRenderer`. Useful when you inherit
    some :class:`.Style` with fg or bg color that you don't need, but at the same
    time you don't actually want to set up any color whatsoever::

        >>> from pytermor import *
        >>> DEFAULT_COLOR.to_sgr(target=ColorTarget.BG)
        <SGR[49m]>


    `NOOP_COLOR` is treated like a placeholder for parent's attribute value and
    doesn't change the result::

        >>> from pytermor import SgrRenderer, render
        >>> sgr_renderer = SgrRenderer(OutputMode.XTERM_16)
        >>> render("MISMATCH", Style(Styles.INCONSISTENCY, fg=NOOP_COLOR), sgr_renderer)
        '\x1b[93;101mMISMATCH\x1b[39;49m'

    .. raw:: html

      <div class="highlight-adjacent highlight-output">
         <div class="highlight">
            <pre><span style="color: #ffff00; background-color: #d70000">MISMATCH</span></pre>
         </div>
      </div>


    While `DEFAULT_COLOR` is actually resetting the color to default (terminal) value::

        >>> render("MISMATCH", Style(Styles.INCONSISTENCY, fg=DEFAULT_COLOR), sgr_renderer)
        '\x1b[39;101mMISMATCH\x1b[49m'

    .. raw:: html

      <div class="highlight-adjacent highlight-output">
         <div class="highlight">
            <pre><span style="background-color: #d70000">MISMATCH</span></pre>
         </div>
      </div>

    """  # noqa

    def __init__(self):
        super().__init__()

    def __eq__(self, other: Color) -> bool:
        return isinstance(other, DefaultColor)

    def to_sgr(
        self,
        target: ColorTarget = ColorTarget.FG,
        upper_bound: t.Type[Color] = None,
    ) -> SequenceSGR:
        return target.resetter

    def to_tmux(self, target: ColorTarget = ColorTarget.FG) -> str:
        if target in [ColorTarget.FG, ColorTarget.BG]:
            return "default"
        raise NotImplementedError(f"No tmux equivalent for {target}")

    # noinspection PyMethodMayBeStatic
    def format_value(self, prefix: str = "") -> str:
        return prefix + "DEF"

    def repr_attrs(self, verbose: bool = True) -> str:
        return self.format_value()


class DynamicColor(RenderColor, t.Generic[_T], metaclass=ABCMeta):
    """
    Color that returns different values depending on internal class-level
    state that can be altered globally for all instances of a concrete
    implementation. Supposed usage is to make a subclass of `DynamicColor`
    and define state type, which will be shared between all instances of a
    new class. Also concrete implementation of `update()` method is required,
    which should contain logic for transforming some external parameters into
    the state. State can be of any type, from plain `RGB` value to complex
    dictionaries or custom classes.

    There is also an `extractor` parameter, which is not shared between
    instances of same subclass, rather being an instance attribute. This
    parameter represents the logic of transforming one shared state into
    several different colors, which therefore can be used as is, or be
    included as a `fg`/`bg` attributes of :class:`.Style` instances.

    Full usage example can be found at `guide.dynamic-deferred-colors` docs page.
    """

    _DEFERRED: t.ClassVar[bool] = False
    """
    Class variable responsible for enabling :def:`deferred` mode. In this
    mode there is a possibility to delay an initialization of the state of
    a concrete class and to create all dependant entities regardless. When
    state is still uninitialized, the return color will be `NOOP_COLOR`, which
    automatically updates to an actual color after state creation. See
    `guide.dynamic-deferred-colors` for the details.
    
    :meta public:
    """

    _state: _T

    @classmethod
    def __new__(cls, *args, **kwargs):
        inst = super().__new__(cls)
        if not (hasattr(cls, "_state")):
            cls.update()
        return inst

    @classmethod
    def update(cls, **kwargs) -> None:
        """Set new internal state for all instances of this class."""
        try:
            cls._state = cls._update_impl(**kwargs)
        except NotInitializedError:
            pass

    @classmethod
    @abstractmethod
    def _update_impl(cls, **kwargs) -> _T:
        raise NotImplementedError

    def __init__(self, extractor: ExtractorT[_T]):
        """
        :param extractor: Concrete implementation of "state" -> "color"
                          transformation logic. Can be a callable, which will be
                          invoked with a state variable as a first argument, or
                          can be a string, in which case it will be used to
                          extract the color value from the instance itself, with
                          this string as an attribute name, or it can be *None*,
                          in which case it implies that state variable is
                          instance of `Color` or it descendant and it can be
                          returned on extraction without transformation, as is.
        """
        self._extractor: ExtractorT[_T] = extractor
        super().__init__()

    @classmethod
    @property
    def _initialized(cls) -> bool:
        return hasattr(cls, "_state")

    @property
    def _value(self) -> RenderColor:
        if not self._initialized:
            if not self._DEFERRED:
                raise LogicError(f"{get_qname(self)} is uninitialized")
            self.__class__.update()
            if not self._initialized:  # pragma: no cover
                return NOOP_COLOR

        state = self.__class__._state
        if self._extractor is None:
            return t.cast(RenderColor, state)

        if isinstance(self._extractor, t.Callable):
            return self._extractor(state)

        return getattr(state, self._extractor, NOOP_COLOR)

    def __eq__(self, other: Color) -> bool:
        return self._value == other

    def to_sgr(
        self, target: ColorTarget = ColorTarget.FG, upper_bound: t.Type[Color] = None
    ) -> SequenceSGR:
        return self._value.to_sgr(target, upper_bound)

    def to_tmux(self, target: ColorTarget = ColorTarget.FG) -> str:
        return self._value.to_tmux(target)

    def repr_attrs(self, verbose: bool = True) -> str:
        return f"DYNAMIC|{self._value.repr_attrs(verbose)}"


# ---------------------------------------------------------------------------------------


def resolve_color(
    subject: CDT,
    color_type: t.Type[_RCT | _RCT] = None,
    approx_cache=True,
) -> _RCT | _RCT:
    """
    Suggested usage is to transform the user input in a free form in an attempt
    to find any matching color. The method operates in three different modes depending
    on arguments: resolving by name, resolving by value and instantiating.

    **Resolving by name**\\ : If ``subject`` is a *str* starting with any character
    except `#`, case-insensitive search through the registry of ``color_type`` colors
    is performed. In this mode the algorithm looks for the instance which has all the
    words from ``subject`` as parts of its name (the order must be the same). Color
    names are stored in registries as sets of tokens, which allows to use any form
    of input and get the correct result regardless. The only requirement is to
    separate the words in any matter (see the example below), so that they could be
    split to tokens which will be matched with the registry keys.

    If ``color_type`` is omitted, all the registries will be requested in this order:
    [`Color16`, `Color256`, `ColorRGB`]. Should any registry find a full match, the
    resolving is stopped and the result is returned.

        >>> resolve_color('deep-sky-blue-7')
        <Color256[x23(#005f5f deep-sky-blue-7)]>
        >>> resolve_color('DEEP SKY BLUE 7')
        <Color256[x23(#005f5f deep-sky-blue-7)]>
        >>> resolve_color('DeepSkyBlue7')
        <Color256[x23(#005f5f deep-sky-blue-7)]>

        >>> resolve_color('deepskyblue7')
        Traceback (most recent call last):
        LookupError: Color 'deepskyblue7' was not found in any registry

    **Resolving by value** or **instantiating**\\ : if ``subject`` is specified as:

        1) *int* in [:hex:`0x000000`; :hex:`0xffffff`] range, or
        2) *str* in full hexadecimal form: ":hex:`#RRGGBB`", or
        3) *str* in short hexadecimal form: ":hex:`#RGB`",

    and ``color_type`` is **present** , the result will be the best ``subject``
    approximation to corresponding color index. Note that this value is expected
    to differ from the requested one (and sometimes differs a lot). If ``color_type``
    is **missing**, no searching is performed; instead a new nameless `ColorRGB`
    is instantiated and returned.

    .. note::
        The instance created this way is an "unbound" color, i.e. it does
        not end up in a registry or an index bound to its type, thus the resolver
        and approximation algorithms are unaware of its existence. The rationale
        for this is to keep the registries clean and stateless to ensure that
        the same input always resolves to the same output.

    ::

        >>> resolve_color("#333")
        <ColorRGB[#333333]>
        >>> resolve_color(0xfafef0)
        <ColorRGB[#fafef0]>

    :param str|int subject: ``Color`` name or hex value to search for. See `CDT`.
    :param color_type:      Target color type (`Color16`, `Color256` or `ColorRGB`).
    :param approx_cache:    Use the approximation cache for **resolving by value**
                            mode or ignore it. For the details see `find_closest` and
                            `approximate` which are actually invoked by this method
                            under the hood.
    :raises LookupError:    If nothing was found in either of registries.
    :return:               ``Color`` instance with specified name or value.
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

    if (value := as_hex(subject)) is not None:
        if color_type is None:
            return ColorRGB(value)
        if not issubclass(color_type, ResolvableColor):
            return ColorRGB(value)
        if approx_cache:
            return find_closest(value, color_type)
        return approximate(value, color_type)[0].color

    color_types: t.List[t.Type[Color]] = [Color16, Color256, ColorRGB]
    if color_type:
        color_types = [color_type]

    for ct in color_types:
        if not issubclass(ct, ResolvableColor):
            continue  # pragma: no cover
        try:
            return ct.find_by_name(str(subject))
        except LookupError:
            continue

    registry = str(color_type) if color_type else "any registry"
    raise LookupError(f"Color '{subject}' was not found in {registry}")


def find_closest(value: IColorValue | int, color_type: t.Type[_RCT] = None) -> _RCT:
    """
    Search and return nearest to ``value`` instance of specified ``color_type``.
    If `color_type` is omitted, search for the closest `Color256` element.

    .. note ::

        Distance between two colors is calculated using CIE76 \u0394E\\* color
        difference formula in LAB color space. This method is considered to be
        an acceptable tradeoff between sRGB euclidean distance, which doesn't
        account for differences in human color perception, and CIE94/CIEDE2000,
        which are more complex and in general excessive for this task.

    Method is useful for finding applicable color alternatives if user's
    terminal is incapable of operating in more advanced mode. Usually it is
    done by the library automatically and transparently for both the developer
    and the end-user.

    .. important ::

        This method caches the results, i.e., the same search query will from then
        onward result in the same return value without the necessity of iterating
        through the color index. If that's not applicable, use similar method
        `approximate()`, which is unaware of caching mechanism altogether.

    :param value:       Target color/color value.
    :param color_type:  Target color type (`Color16`, `Color256` or `ColorRGB`).
    :return:            Nearest to ``value`` color instance of specified type.
    """
    return (color_type or Color256).find_closest(value)


def approximate(
    value: IColorValue | int,
    color_type: t.Type[_RCT] = None,
    max_results: int = 1,
) -> t.List[ApxResult[_RCT]]:
    """
    Search for nearest to ``value`` colors of specified ``color_type`` and
    return the first ``max_results`` of them. If `color_type` is omitted, search
    for the closest `Color256` instances. This method is similar to the
    `find_closest()`, although they differ in some aspects:

        - `approximate()` can return more than one result;
        - `approximate()` returns not just a ``Color`` instance(s), but also a
          number equal to squared distance to the target color for each of them;
        - `find_closest()` caches the results, while `approximate()` ignores
          the cache completely.

    :param value:        Target color/color value.
    :param color_type:   Target color type (`Color16`, `Color256` or `ColorRGB`).
    :param max_results:  Return no more than ``max_results`` items.
    :return: Pairs of closest ``Color`` instance(s) found with their distances
             to the target color, sorted by distance descending, i.e., element
             at index 0 is the closest color found, paired with its distance
             to the target; element with index 1 is second-closest color
             (if any) and corresponding distance value, etc.
    """
    return (color_type or Color256).approximate(value, max_results)


NOOP_COLOR = NoopColor()
DEFAULT_COLOR = DefaultColor()
