# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import typing as t
from math import isclose

import pytest

import pytermor as pt
from pytermor.common import RGB, HSV


def assert_close(a: float, b: float):
    assert isclose(a, b, abs_tol=0.01)


def format_test_params(val) -> str | None:
    if isinstance(val, int):
        return f"0x{val:06x}"
    elif isinstance(val, tuple):
        return str(val)
    return str(val)


class TestColorTransform:
    @pytest.mark.parametrize(
        "expected_hsv, input_hex",
        [
            [HSV(0, 0, 0.0), 0x000000],
            [HSV(0, 0, 1.0), 0xFFFFFF],
            [HSV(0, 1, 1.0), 0xFF0000],
            [HSV(120, 1, 1.0), 0x00FF00],
            [HSV(240, 1, 1.0), 0x0000FF],
            [HSV(60, 1, 0.0), 0x010100],
            [HSV(240, 1, 0.5), 0x000080],
            [HSV(0, 0, 0), 0x1000000],
        ],
        ids=format_test_params,
    )
    def test_hex_to_hsv(self, expected_hsv: HSV, input_hex: int):
        actual_hsv = pt.utilmisc.hex_to_hsv(input_hex)
        for idx, val in enumerate(expected_hsv):
            assert_close(actual_hsv[idx], expected_hsv[idx])

    @pytest.mark.parametrize(
        "expected_rgb, input_hex",
        [
            [RGB(0, 0, 0), 0x000000],
            [RGB(255, 255, 255), 0xFFFFFF],
            [RGB(255, 0, 0), 0xFF0000],
            [RGB(0, 255, 0), 0x00FF00],
            [RGB(0, 0, 255), 0x0000FF],
            [RGB(1, 1, 0), 0x010100],
            [RGB(0, 0, 128), 0x000080],
            [RGB(0, 0, 0), 0x1000000],
        ],
        ids=format_test_params,
    )
    def test_hex_to_rgb(self, expected_rgb: RGB, input_hex: int):
        assert pt.utilmisc.hex_to_rgb(input_hex)    == expected_rgb

    @pytest.mark.parametrize(
        "expected_hex, input_args_rgb",
        [
            [0xFF0000, [RGB(255, 0, 0)]],
            [0x00FF00, [RGB(0, 255, 0)]],
            [0x000040, [RGB(0, 0, 64)]],
            [0x010100, [RGB(1, 1, 0)]],
            [0x000000, [0, 0, 0]],
            [0xFFFFFF, [255, 255, 255]],
            [0x808080, [(128, 128, 128)]],
        ],
        ids=format_test_params,
    )
    def test_rgb_to_hex(
        self, expected_hex: int, input_args_rgb: t.List[RGB | t.Tuple[int, int, int]]
    ):
        assert pt.utilmisc.rgb_to_hex(*input_args_rgb) == expected_hex
