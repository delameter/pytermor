# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

import typing as t
from collections import namedtuple
from math import isclose

import pytest

import pytermor as pt
from pytermor.common import RGB, HSV


def print_test_formatting_args(val) -> str | None:
    if isinstance(val, int):
        return f'0x{val:06x}'
    elif isinstance(val, tuple):
        return str(val)
    return str(val)


class TestColorTransform:
    @pytest.mark.parametrize('expected_hsv, input_hex', [
        [HSV(0, 0, 0.0), 0x000000],
        [HSV(0, 0, 1.0), 0xFFFFFF],
        [HSV(0, 1, 1.0), 0xFF0000],
        [HSV(120, 1, 1.0), 0x00FF00],
        [HSV(240, 1, 1.0), 0x0000FF],
        [HSV(60, 1, 0.0), 0x010100],
        [HSV(240, 1, 0.5), 0x000080],
        [HSV(0, 0, 0), 0x1000000],
    ], ids=print_test_formatting_args)
    def test_hex_to_hsv(self, expected_hsv: HSV, input_hex: int):
        actual_hsv = pt.utilmisc.hex_to_hsv(input_hex)
        for idx in range(0, len(expected_hsv)):
            assert isclose(expected_hsv[idx], actual_hsv[idx], abs_tol=0.01)

    @pytest.mark.parametrize('expected_rgb, input_hex', [
        [RGB(0, 0, 0), 0x000000],
        [RGB(255, 255, 255), 0xFFFFFF],
        [RGB(255, 0, 0), 0xFF0000],
        [RGB(0, 255, 0), 0x00FF00],
        [RGB(0, 0, 255), 0x0000FF],
        [RGB(1, 1, 0), 0x010100],
        [RGB(0, 0, 128), 0x000080],
        [RGB(0, 0, 0), 0x1000000],
    ], ids=print_test_formatting_args)
    def test_hex_to_rgb(self, expected_rgb: RGB, input_hex: int):
        actual_rgb = pt.utilmisc.hex_to_rgb(input_hex)
        assert actual_rgb == expected_rgb
