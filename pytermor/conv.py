# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
"""
A
"""

from __future__ import annotations

import math
import typing as t
from abc import ABCMeta, abstractmethod
from dataclasses import asdict, dataclass
from typing import overload


CIE_E: float = 216.0 / 24389.0  # 0.008856451679035631  # see http://brucelindbloom.com/

REF_X: float = 95.047  # Observer= 2°, Illuminant= D65
REF_Y: float = 100.000
REF_Z: float = 108.883


class IColorType(metaclass=ABCMeta):
    @abstractmethod
    def apply_thresholds(self) -> t.Self:
        ...


@dataclass
class RGB(IColorType):
    red: int
    """ Red channel value (0—255) """
    green: int
    """ Green channel value (0—255) """
    blue: int
    """ Blue channel value (0—255) """

    @classmethod
    def from_ratios(cls, rr: float, gr: float, br: float) -> RGB:
        """
        d
        :param rr:
        :param gr:
        :param br:
        """
        return RGB(round(rr * 255), round(gr * 255), round(br * 255)).apply_thresholds()

    def apply_thresholds(self) -> RGB:
        return RGB(**{k: _normalize(255, v) for k, v in asdict(self).items()})

    def __str__(self):  # RGB(R=128, G=0, B=0)
        attrs = map(self._format_channel, asdict(self).keys())
        return f"{self.__class__.__name__}({' '.join(attrs)})"

    def __iter__(self) -> t.Iterator[int]:
        return iter((self.red, self.green, self.blue))

    def _format_channel(self, attr: str) -> str:
        return f"{attr[0].upper()}={getattr(self, attr):d}"


@dataclass
class HSV(IColorType):
    hue: float
    """ Hue channel value (0—360) """
    saturation: float
    """ Saturation channel value (0.0—1.0) """
    value: float
    """ Value channel value (0.0—1.0) """

    def apply_thresholds(self):
        self.hue = _normalize(360.0, self.hue)
        self.saturation = _normalize(1.0, self.saturation)
        self.value = _normalize(1.0, self.value)

    def __str__(self):  # HSV(H=0° S=100% V=50%)
        attrs = [
            f"H={self.hue:.0f}°",
            f"S={100*self.saturation:.0f}%",
            f"V={100*self.value:.0f}%",
        ]
        return f"{self.__class__.__name__}({' '.join(attrs)})"

    def __iter__(self) -> t.Iterator[float]:
        return iter((self.hue, self.saturation, self.value))


@dataclass
class XYZ(IColorType):
    x: float
    """ X channel value (0—100+) """
    y: float
    """ Luminance (0—100) """
    z: float
    """ Quasi-equal to blue (0—100+) """

    def apply_thresholds(self):
        self.y = _normalize(100.00, self.y)

    def __str__(self):  # XYZ(X=0.95 Y=1.00 Z=1.08)
        attrs = [
            f"X={self.x:.2f}",
            f"Y={self.y:.2f}%",
            f"Z={self.z:.2f}",
        ]
        return f"{self.__class__.__name__}({' '.join(attrs)})"

    def __iter__(self) -> t.Iterator[float]:
        return iter((self.x, self.y, self.z))


@dataclass
class LAB(IColorType):
    L: float
    """ Luminance (0—100) """
    a: float
    """ Green–magenta axis (-100—100 in general, but can be less/more) """
    b: float
    """ Blue–yellow axis (-100—100 in general, but can be less/more) """

    def apply_thresholds(self):
        self.L = _normalize(100.00, self.L)

    def __str__(self):  # LAB(L=100% a=100 b=-100)
        attrs = [
            f"L={self.L:.3f}%",
            f"a={self.a:.3f}",
            f"b={self.b:.3f}",
        ]
        return f"{self.__class__.__name__}({' '.join(attrs)})"

    def __iter__(self) -> t.Iterator[float]:
        return iter((self.L, self.a, self.b))


@overload
def _normalize(max_val: int, val: float | int) -> int:
    ...


@overload
def _normalize(max_val: float, val: float | int) -> float:
    ...


def _normalize(max_val, val: float | int) -> int | float:
    if isinstance(max_val, int):
        val = round(val)
    return max(0, min(val, max_val))


# -----------------------------------------------------------------------------
# HEX <-> RGB


def hex_to_rgb(hex_value: int) -> RGB:
    """
    Transforms ``hex_value`` in *int* format into a tuple of three
    integers corresponding to **red**, **blue** and **green** channel value
    respectively. Values are within [0; 255] range.

        >>> hex_to_rgb(0x80ff80)
        RGB(red=128, green=255, blue=128)

    :param hex_value: RGB integer value.
    :returns: tuple with R, G, B channel values.
    """
    if not isinstance(hex_value, int):
        raise TypeError(f"Argument type should be 'int', got: {type(hex_value)}")

    return RGB(
        red=(hex_value & 0xFF0000) >> 16,
        green=(hex_value & 0xFF00) >> 8,
        blue=(hex_value & 0xFF),
    )


@overload
def rgb_to_hex(rgb: RGB) -> int:
    """
    :param rgb: tuple with R, G, B channel values.
    :return: RGB value.
    """
    ...


@overload
def rgb_to_hex(r: int, g: int, b: int) -> int:
    """
    :param r: value of red channel.
    :param g: value of green channel.
    :param b: value of blue channel.
    :return: RGB value.
    """
    ...


def rgb_to_hex(*args) -> int:
    """
    Transforms RGB value in a three-integers form ([0; 255], [0; 255], [0; 255])
    to an one-integer form.

        >>> hex(rgb_to_hex(0, 128, 0))
        '0x8000'
        >>> hex(rgb_to_hex(RGB(red=16, green=16, blue=0)))
        '0x101000'

    """
    r, g, b = args if len(args) > 1 else args[0]
    return (r << 16) + (g << 8) + b


# -----------------------------------------------------------------------------
# RGB <-> HSV


@overload
def hsv_to_rgb(hsv: HSV) -> RGB:
    """
    :param hsv: tuple with H, S, V channel values.
    :return: tuple with R, G, B channel values.
    """
    ...


@overload
def hsv_to_rgb(h: float, s: float, v: float) -> RGB:
    """
    :param h: hue channel value.
    :param s: saturation channel value.
    :param v: value channel value.
    :return: tuple with R, G, B channel values.
    """
    ...


def hsv_to_rgb(*args) -> RGB:
    """
    Transforms HSV value in three-floats form (where 0 <= h < 360, 0 <= s <= 1,
    and 0 <= v <= 1) into RGB three-integer form ([0; 255], [0; 255], [0; 255]).

        >>> hsv_to_rgb(270, 2/3, 0.75)
        RGB(red=128, green=64, blue=192)
        >>> hsv_to_rgb(HSV(hue=120, saturation=0.5, value=0.77))
        RGB(red=99, green=197, blue=99)

    """
    h, s, v = args if len(args) > 1 else args[0]

    h = 0.0 if h == 360.0 else h / 60.0
    fract = h - math.floor(h)

    p = v * (1.0 - s)
    q = v * (1.0 - s * fract)
    t = v * (1.0 - s * (1.0 - fract))

    if 0.0 <= h < 1.0:
        r, g, b = v, t, p
    elif 1.0 <= h < 2.0:
        r, g, b = q, v, p
    elif 2.0 <= h < 3.0:
        r, g, b = p, v, t
    elif 3.0 <= h < 4.0:
        r, g, b = p, q, v
    elif 4.0 <= h < 5.0:
        r, g, b = t, p, v
    else:
        r, g, b = v, p, q

    return RGB(math.ceil(255 * r), math.ceil(255 * g), math.ceil(255 * b))


@overload
def rgb_to_hsv(rgb: RGB) -> HSV:
    ...


@overload
def rgb_to_hsv(r: int, g: int, b: int) -> HSV:
    ...


def rgb_to_hsv(*args) -> HSV:
    """
    Transforms RGB value in a three-integers form ([0; 255], [0; 255], [0; 255]) to an
    HSV in three-floats form such as (0 <= h < 360, 0 <= s <= 1, and 0 <= v <= 1).

        >>> rgb_to_hsv(0, 0, 255)
        HSV(hue=240.0, saturation=1.0, value=1.0)

    :param r: value of red channel.
    :param g: value of green channel.
    :param b: value of blue channel.
    :returns: H, S, V channel values correspondingly.
    """
    # fmt: off
    # https://en.wikipedia.org/wiki/HSL_and_HSV#From_RGB
    r, g, b = args if len(args) > 1 else args[0]

    rn, gn, bn = r / 255, g / 255, b / 255
    vmax = max(rn, gn, bn)
    vmin = min(rn, gn, bn)
    c = vmax - vmin
    v = vmax

    h = 0.0
    if c == 0: pass
    elif v == rn:  h = 60 * (0 + (gn - bn) / c)
    elif v == gn:  h = 60 * (2 + (bn - rn) / c)
    elif v == bn:  h = 60 * (4 + (rn - gn) / c)

    if v == 0:     s = 0
    else:          s = c / v

    if h < 0:      h += 360

    return HSV(hue=h, saturation=s, value=v)
    # fmt: on


# -----------------------------------------------------------------------------
# HEX <-<RGB>-> HSV
#


def hex_to_hsv(hex_value: int) -> HSV:
    """
    Transforms ``hex_value`` in *int* form into named tuple consisting of three floats
    corresponding to **hue**, **saturation** and **value** channel values respectively.
    Hue is within [0, 359] range, both saturation and value are within [0; 1] range.

        >>> hex_to_hsv(0x999999)
        HSV(hue=0.0, saturation=0.0, value=0.6)

    :param hex_value: RGB value.
    :returns: named tuple with H, S and V channel values
    """
    return rgb_to_hsv(hex_to_rgb(hex_value))


@overload
def hsv_to_hex(hsv: HSV) -> int:
    ...


@overload
def hsv_to_hex(h: float, s: float, v: float) -> int:
    ...


def hsv_to_hex(*args) -> int:
    """
    Transforms HSV value in three-floats form (where 0 <= h < 360, 0 <= s <= 1,
    and 0 <= v <= 1) into an one-integer form.

        >>> hex(hsv_to_hex(90, 0.5, 0.5))
        '0x608040'

    :param h: hue channel value.
    :param s: saturation channel value.
    :param v: value channel value.
    :return: RGB value.
    """
    return rgb_to_hex(hsv_to_rgb(*args))


# -----------------------------------------------------------------------------
# RGB <-> XYZ


@overload
def rgb_to_xyz(rgb: RGB) -> XYZ:
    ...


@overload
def rgb_to_xyz(r: int, g: int, b: int) -> XYZ:
    ...


def rgb_to_xyz(*args) -> XYZ:
    def f(v):
        if v <= 0.04045:
            return v / 12.92
        return ((v + 0.055) / 1.055) ** 2.4

    r, g, b = args if len(args) > 1 else args[0]
    R, G, B = (100.0 * f(v / 255) for v in (r, g, b))

    x: float = 0.4124 * R + 0.3576 * G + 0.1805 * B  # sRGB D65 -> XYZ D50
    y: float = 0.2126 * R + 0.7152 * G + 0.0722 * B
    z: float = 0.0193 * R + 0.1192 * G + 0.9503 * B

    return XYZ(x, y, z)


@overload
def xyz_to_rgb(xyz: XYZ) -> RGB:
    ...


@overload
def xyz_to_rgb(x: float, y: float, z: float) -> RGB:
    ...


def xyz_to_rgb(*args) -> RGB:
    def f(v) -> float:
        if v <= 0.0031308:
            return 12.92 * v
        return 1.055 * (v ** (1 / 2.4)) - 0.055

    X, Y, Z = args if len(args) > 1 else args[0]
    x, y, z = (v / 100.0 for v in (X, Y, Z))

    r: int = round(255 * f(x * 3.2406 + y * -1.5372 + z * -0.4986))  # sRGB
    g: int = round(255 * f(x * -0.9689 + y * 1.8758 + z * 0.0415))
    b: int = round(255 * f(x * 0.0557 + y * -0.2040 + z * 1.0570))

    return RGB(r, g, b)


# -----------------------------------------------------------------------------
# XYZ <-> LAB


@overload
def lab_to_xyz(lab: LAB) -> XYZ:
    ...


@overload
def lab_to_xyz(L: float, a: float, b: float) -> XYZ:
    ...


def lab_to_xyz(*args) -> XYZ:
    def f(v: float) -> float:
        if (v3 := v**3) > CIE_E:
            return v3
        else:
            return (v - 16.0 / 116.0) / 7.787

    L, a, b = args if len(args) > 1 else args[0]

    fy: float = (L + 16.0) / 116.0
    fx: float = (a / 500.0) + fy
    fz: float = fy - (b / 200.0)

    x, y, z = (f(v) for v in (fx, fy, fz))

    x *= REF_X
    y *= REF_Y
    z *= REF_Z

    return XYZ(x, y, z)


@overload
def xyz_to_lab(xyz: XYZ) -> LAB:
    ...


@overload
def xyz_to_lab(x: float, y: float, z: float) -> LAB:
    ...


def xyz_to_lab(*args) -> LAB:
    def f(v: float) -> float:
        if v > CIE_E:
            return math.pow(v, 1 / 3)
        else:
            return (7.787 * v) + (16.0 / 116.0)

    x, y, z = args if len(args) > 1 else args[0]

    x /= REF_X
    y /= REF_Y
    z /= REF_Z

    fx, fy, fz = (f(v) for v in (x, y, z))

    L = (116.0 * fy) - 16.0
    a = 500.0 * (fx - fy)
    b = 200.0 * (fy - fz)

    return LAB(L, a, b)


# -----------------------------------------------------------------------------
# RGB <-<XYZ>-> LAB


@overload
def lab_to_rgb(lab: LAB) -> RGB:
    ...


@overload
def lab_to_rgb(L: float, a: float, b: float) -> RGB:
    ...


def lab_to_rgb(*args) -> RGB:
    """
    @TODO

    :param L:
    :param a:
    :param b:
    :return:
    """
    return xyz_to_rgb(lab_to_xyz(*args))


@overload
def rgb_to_lab(rgb: RGB) -> LAB:
    ...


@overload
def rgb_to_lab(r: int, g: int, b: int) -> LAB:
    ...


def rgb_to_lab(*args) -> LAB:
    return xyz_to_lab(rgb_to_xyz(*args))
