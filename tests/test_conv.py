# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import itertools
from dataclasses import dataclass

import pytest
import typing as t
import pytermor as pt
from pytermor import HSV, LAB, RGB, XYZ, hex_to_rgb, IColorType
from tests import assert_close, format_test_params


@dataclass
class Value:
    hex: int
    rgb: RGB
    hsv: HSV
    xyz: XYZ
    lab: LAB

    def __str__(self):
        return f"0x{self.hex:06x}-{self.rgb}"


# fmt: off
VALUES = [ # _hex_      _r_  _g_  _b_        __h__ __s__ __v__        __x__   __y__   __z__        __l__    __a__    __b__     # noqa
    Value(0x000000, RGB(  0,   0,   0), HSV(  0.00, 0.00, 0.00), XYZ(  0.00,   0.00,   0.00), LAB(  0.00,    0.00,    0.00)),  # noqa
    Value(0xFFFFFF, RGB(255, 255, 255), HSV(  0.00, 0.00, 1.00), XYZ( 95.05,  100.0, 108.88), LAB( 100.0, 0.00526, 0.00184)),  # noqa
    Value(0xFF0000, RGB(255,   0,   0), HSV(  0.00, 1.00, 1.00), XYZ( 41.24,  21.26,  1.930), LAB(53.232,  80.109,   67.22)),  # noqa
    Value(0x00FF00, RGB(  0, 255,   0), HSV( 120.0, 1.00, 1.00), XYZ( 35.76,  71.52,  11.92), LAB(87.737, -86.184,  83.181)),  # noqa
    Value(0x0000FF, RGB(  0,   0, 255), HSV( 240.0, 1.00, 1.00), XYZ( 18.05,   7.22,  95.03), LAB(32.302,  79.197, -107.85)),  # noqa
    Value(0x100000, RGB( 16,   0,   0), HSV(  0.00, 1.00, 1/16), XYZ(0.2137,   0.11,   0.01), LAB( 0.995,   4.464,  1.5726)),  # noqa
    Value(0xc02040, RGB(192,  32,  64), HSV( 348.0,  5/6,  3/4), XYZ(23.180,  12.61,  6.062), LAB(42.169,   61.66,  23.924)),  # noqa
    Value(0x00ff80, RGB(  0, 255, 128), HSV(150.11, 1.00, 1.00), XYZ(39.656,  73.08,  32.43), LAB(88.485, -76.749,  46.577)),  # noqa
    Value(0x000080, RGB(  0,   0, 128), HSV( 240.0, 1.00,  1/2), XYZ( 3.896,  1.558,  20.51), LAB(12.975,  47.508, -64.704)),  # noqa
    Value(0xffccab, RGB(255, 204, 171), HSV( 23.57,  1/3, 1.00), XYZ(70.183,  67.39,  47.83), LAB(85.698,  13.572,  23.309)),  # noqa
    Value(0x406080, RGB( 64,  96, 128), HSV( 210.0,  1/2,  1/2), XYZ(10.194, 11.014,  22.01), LAB(39.601, -2.1089, -21.501)),  # noqa
    Value(0x20181c, RGB( 32,  24,  28), HSV( 330.0,  1/4,  1/8), XYZ(1.1319, 1.0442, 1.2403), LAB(9.3542,  4.8953,  -1.286)),  # noqa
    Value(0x2d0a50, RGB( 45,  10,  80), HSV( 270.0,  7/8, 5/16), XYZ(2.6387, 1.3542, 7.7101), LAB(11.649, 32.2209, -35.072)),  # noqa
]
# fmt: on

SPACES = [*VALUES[-1].__dict__.keys()]


class TestColorDTOs:
    @pytest.mark.parametrize("cls", [RGB, HSV, XYZ, LAB], ids=format_test_params)
    def test_to_str(self, cls: t.Type[IColorType]):
        col = cls(1, 1, 1)
        col_str = str(col)
        assert str(cls.__name__) in col_str
        assert col_str.count('=') == 3

class TestColorTransform:
    @pytest.mark.parametrize("value", VALUES, ids=lambda val: str(val))
    @pytest.mark.parametrize(
        "spaces",
        itertools.permutations(SPACES, 2),
        ids=lambda val: f"[{val[0]}->{val[1]}]",
    )
    def test_transforms(self, value: Value, spaces: tuple[str, str]):
        s_from, s_to = spaces
        fname = f"{s_from}_to_{s_to}"
        if not hasattr(pt.conv, fname):
            return
        input = getattr(value, s_from)
        expected_output = getattr(value, s_to)
        actual_output: IColorType|int = getattr(pt.conv, fname)(input)
        if isinstance(actual_output, IColorType):
            actual_output.apply_thresholds()
        assert_close(actual_output, expected_output)

    def test_rgb_from_ratios(self):
        assert_close(RGB.from_ratios(0, 0.5, 1.0), RGB(0, 128, 255))

    @pytest.mark.xfail(raises=TypeError)
    def test_hex_to_rgb_fails_on_invalid_arg(self):
        # noinspection PyTypeChecker
        hex_to_rgb("123")
