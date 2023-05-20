# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import itertools
from dataclasses import dataclass

import pytest

import pytermor as pt
from pytermor import XYZ
from pytermor.common import RGB, HSV, LAB

from . import assert_close


@dataclass
class Value:
    hex: int
    rgb: RGB
    hsv: HSV
    xyz: XYZ
    lab: LAB

    def __str__(self):
        return f"0x{self.hex:06x}"


SPACES = ["hex", "rgb", "hsv", "xyz", "lab"]


# fmt: off
VALUES = [
Value(0x000000, RGB(0,   0,   0),   HSV(0.0,   0.0, 0.0),   XYZ(0.0000, 0.00,  0.00),     LAB(0.00, 0.00, 0.00)),
Value(0xFFFFFF, RGB(255, 255, 255), HSV(0.0,   0.0, 1.0),   XYZ(0.9505, 100.0, 1.089),      LAB(0.01, 0.00, 0.00)),
Value(0xFF0000, RGB(255, 0,   0),   HSV(0.0,   1.0, 1.0),   XYZ(0.4124, 21.26, 0.019),    LAB(0.532, 0.8011, 0.6722)),
Value(0x00FF00, RGB(0,   255, 0),   HSV(120.0, 1.0, 1.0),   XYZ(0.3576, 0.7152, 0.1192),   LAB(0.877, -0.8618, 0.8318)),
Value(0x0000FF, RGB(0,   0,   255), HSV(240.0, 1.0, 1.0),   XYZ(0.1805, 0.0722,  0.9505),   LAB(0.323, 0.7919, -1.0786)),
Value(0x010000, RGB(1,   0,   0),   HSV(0.0,   1.0, 1/256), XYZ(1.2e-4, 0.0000,  5.86e-5),  LAB(0.0006, 0.00261, 0.00092)),
Value(0x000080, RGB(0,   0,   128), HSV(240.0, 1.0, 0.5),   XYZ(0.0389, 0.0156,  0.2052),   LAB(0.1297, 0.4751, -0.6470)),
]  # noqa
# fmt: οn

VALUES_HEX = [v.hex for v in VALUES]
VALUES_RGB = [v.rgb for v in VALUES]
VALUES_HSV = [v.hsv for v in VALUES]
VALUES_XYZ = [v.xyz for v in VALUES]
VALUES_LAB = [v.lab for v in VALUES]


@pytest.mark.skip
class TestColorTransform:
    @pytest.mark.parametrize("value", VALUES, ids=lambda val: str(val))
    @pytest.mark.parametrize(
        'spaces',
        itertools.permutations(SPACES, 2),
        ids=lambda val: f"[{val[0]}->{val[1]}]"
    )
    def test_transforms(self, value: Value, spaces: tuple[str, str]):
        s_from, s_to = spaces
        fname = f'{s_from}_to_{s_to}'
        if not hasattr(pt.conv, fname):
            return
        input = getattr(value, s_from)
        expected_output = getattr(value, s_to)
        print(input, expected_output)
        assert_close(getattr(pt.conv, fname)(input), expected_output)
