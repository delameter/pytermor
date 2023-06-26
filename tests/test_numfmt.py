# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

from datetime import timedelta

import pytest

from pytermor import Fragment, OutputMode, Style, Text, render
from pytermor.numfmt import (
    DualBaseUnit,
    DualFormatter,
    DualFormatterRegistry,
    StaticFormatter,
    dual_registry,
    format_auto_float,
    format_bytes_human,
    format_si,
    format_si_binary,
    format_time,
    format_time_delta,
    format_time_delta_longest,
    format_time_delta_shortest,
    format_time_ms,
    formatter_si,
    highlight,
)
from tests import format_test_params


@pytest.mark.setup(force_output_mode=OutputMode.TRUE_COLOR)
class TestHighlighter:
    DIM = Style(dim=True)

    @pytest.mark.parametrize(
        "input, expected",
        [
            ("0", [Fragment("0", Style(fg="gray"))]),
            ("-0", ["-" + Fragment("0", Style(fg="gray"))]),
            (
                "0.000",
                [
                    Fragment("0", Style(fg="gray")),
                    Fragment(".000", Style(fg="gray", dim=True)),
                ],
            ),
            (
                "0.0001",
                [
                    Fragment("0.000"),
                    Fragment("1", Style(dim=True)),
                ],
            ),
            (
                "890.789",
                [
                    Fragment("890"),
                    Fragment(".789"),
                ],
            ),
            (
                "8456.78901",
                [
                    Fragment("8", Style(fg="blue", bold=True)),
                    Fragment("456"),
                    Fragment(".789"),
                    Fragment("01", DIM),
                ],
            ),
            (
                "567890",
                [
                    Fragment("567", Style(fg="blue", bold=True)),
                    Fragment("890"),
                ],
            ),
            (
                "234567890",
                [
                    Fragment("234", Style(fg="cyan", bold=True)),
                    Fragment("567", DIM),
                    Fragment("890"),
                ],
            ),
            (
                "890123456.78901234567890",
                [
                    Fragment("890", Style(fg="cyan", bold=True)),
                    Fragment("123", DIM),
                    Fragment("456"),
                    Fragment(".789"),
                    Fragment("012", DIM),
                    Fragment("345"),
                    Fragment("678", DIM),
                    Fragment("90"),
                ],
            ),
            (
                "901234567890",
                [
                    Fragment("901", Style(fg="green", bold=True)),
                    Fragment("234"),
                    Fragment("567", DIM),
                    Fragment("890"),
                ],
            ),
            (
                "678901234567890",
                [
                    Fragment("678", Style(fg="yellow", bold=True)),
                    Fragment("901", DIM),
                    Fragment("234"),
                    Fragment("567", DIM),
                    Fragment("890"),
                ],
            ),
            (
                "-345678901234567890",
                [
                    Fragment("-"),
                    Fragment("345", Style(fg="red", bold=True)),
                    Fragment("678"),
                    Fragment("901", DIM),
                    Fragment("234"),
                    Fragment("567", DIM),
                    Fragment("890"),
                ],
            ),
        ],
        ids=format_test_params,
    )
    def test_multiapplying(self, input, expected):
        assert render(highlight(input)) == render(Text(*expected))


# -- format_auto_float --------------------------------------------------------


class TestFormatAutoFloat:
    @pytest.mark.parametrize(
        "expected,value,max_len",
        [
            ["5.3e10", 5.251505e10, 6],  # fixed max length = 6
            ["5.25e7", 5.251505e7, 6],
            ["5.25e6", 5.251505e6, 6],
            ["525150", 5.251505e5, 6],
            [" 52515", 5.251505e4, 6],
            ["5251.5", 5.251505e3, 6],
            ["525.15", 5.251505e2, 6],
            ["52.515", 5.251505e1, 6],
            ["5.2515", 5.251505e0, 6],
            ["0.5252", 5.251505e-1, 6],
            ["0.0525", 5.251505e-2, 6],
            ["5.3e-3", 5.251505e-3, 6],
            ["5.3e-4", 5.251505e-4, 6],
            ["5.3e-5", 5.251505e-5, 6],
            ["5.3e-6", 5.251505e-6, 6],
            ["5.3e-7", 5.251505e-7, 6],
            ["-5e-10", -5.251505e-10, 6],
            ["- 5e10", -5.251505e10, 6],
            ["-5.3e7", -5.251505e7, 6],
            ["-5.3e6", -5.251505e6, 6],
            ["-5.3e5", -5.251505e5, 6],
            ["-52515", -5.251505e4, 6],
            ["- 5252", -5.251505e3, 6],
            ["-525.2", -5.251505e2, 6],
            ["-52.52", -5.251505e1, 6],
            ["-5.252", -5.251505e0, 6],
            ["-0.525", -5.251505e-1, 6],
            ["-0.053", -5.251505e-2, 6],
            ["- 5e-3", -5.251505e-3, 6],
            ["- 5e-4", -5.251505e-4, 6],
            ["- 5e-5", -5.251505e-5, 6],
            ["- 5e-6", -5.251505e-6, 6],
            ["- 5e-7", -5.251505e-7, 6],
            ["-5e-10", -5.251505e-10, 6],
            ["", 0.12345, 0],  # values with e = -1
            ["0", 0.12345, 1],
            [" 0", 0.12345, 2],
            ["0.1", 0.12345, 3],
            ["0.12", 0.12345, 4],
            ["0.123", 0.12345, 5],
            ["0.12345000", 0.12345, 10],
            ["", -0.12345, 0],
            ["!", -0.12345, 1],
            ["-0", -0.12345, 2],
            ["- 0", -0.12345, 3],
            ["-0.1", -0.12345, 4],
            ["-0.12", -0.12345, 5],
            ["-0.1234500", -0.12345, 10],
            ["", 1.23456789e9, 0],  # values with 0 <= e <= 10
            ["!", 1.23456789e9, 1],
            ["e9", 1.23456789e9, 2],
            ["1e9", 1.23456789e9, 3],
            [" 1e9", 1.23456789e9, 4],
            ["1.2e9", 1.23456789e9, 5],
            ["1.23e9", 1.23456789e9, 6],
            ["1.235e9", 1.23456789e9, 7],
            ["1.2346e9", 1.23456789e9, 8],
            ["1.23457e9", 1.23456789e9, 9],
            ["1234567890", 1.23456789e9, 10],
            ["", -9.87654321e8, 0],
            ["!", -9.87654321e8, 1],
            ["!!", -9.87654321e8, 2],
            ["-e8", -9.87654321e8, 3],
            ["-9e8", -9.87654321e8, 4],
            ["-10e8", -9.87654321e8, 5],
            ["-9.9e8", -9.87654321e8, 6],
            ["-9.88e8", -9.87654321e8, 7],
            ["-9.877e8", -9.87654321e8, 8],
            ["-9.8765e8", -9.87654321e8, 9],
            ["-987654321", -9.87654321e8, 10],
            ["!!", 123456789012345, 2],  # values with e > 10
            ["e14", 123456789012345, 3],
            ["1e14", 123456789012345, 4],
            ["10e13", 98765432109876, 5],
            [" 1e14", 123456789012345, 5],  # <-- 12e13 would be better than " 1e14" (+1
            ["9.9e13", 98765432109876, 6],  # significant digit), but decided that
            ["1.2e14", 123456789012345, 6],  # the more normalizing — the better
            ["9.88e13", 98765432109876, 7],
            ["1.23e14", 123456789012345, 7],
            ["9.877e13", 98765432109876, 8],
            ["1.235e14", 123456789012345, 8],
            ["9.8765e13", 98765432109876, 9],
            ["!!", -98765432109876, 2],
            ["!!!", -98765432109876, 3],
            ["-e13", -98765432109876, 4],
            ["-e14", -123456789012345, 4],
            ["-9e13", -98765432109876, 5],
            ["-1e14", -123456789012345, 5],
            ["-10e13", -98765432109876, 6],
            ["-9.9e13", -98765432109876, 7],
            ["-9.88e13", -98765432109876, 8],
            ["-9.877e13", -98765432109876, 9],
            ["", 0, 0],  # ints tight fit (overflow cases)
            ["", 0.0, 0],
            ["", 1.0, 0],
            ["", -1.0, 0],
            ["0", 0, 1],
            ["0", 0.0, 1],
            ["2", 2.0, 1],
            ["!", -2.0, 1],
            ["-2", -2.0, 2],
            [" 0", 0, 2],
            [" 0", 0.0, 2],
            [" 2", 2.0, 2],
            ["24", 24.0, 2],
            ["!!", -24.0, 2],
            ["-24", -24.0, 3],
            ["  0", 0, 3],
            ["  0", 0.0, 3],
            [" 24", 24.0, 3],
            ["9", 9.0, 1],  # ints tight fit (rounding up cases)
            [" 9", 9.0, 2],
            ["9.0", 9.0, 3],
            ["9.00", 9.0, 4],
            ["9", 9.9, 1],
            ["10", 9.9, 2],
            ["9.9", 9.9, 3],
            ["9.90", 9.9, 4],
            ["9", 9.99, 1],
            ["10", 9.99, 2],
            [" 10", 9.99, 3],
            ["9.99", 9.99, 4],
            ["9", 9.999, 1],
            ["10", 9.999, 2],
            [" 10", 9.999, 3],
            ["10.0", 9.999, 4],
            ["!", 99.999, 1],
            ["99", 99.999, 2],
            ["100", 99.999, 3],
            [" 100", 99.999, 4],
            ["100.0", 99.999, 5],
            ["!", -9.999, 1],
            ["-9", -9.999, 2],
            ["-10", -9.999, 3],
            ["- 10", -9.999, 4],
            ["-10.0", -9.999, 5],
            ["-9.99", -9.990, 5],
            ["-9.99", -9.989, 5],
            pytest.param("", 9.9, -1, marks=pytest.mark.xfail(raises=ValueError)),
        ],
    )
    def test_format_auto_float(self, expected: str, value: float, max_len: int):
        assert format_auto_float(value, max_len) == expected
        assert max_len == len(expected)

    @pytest.mark.parametrize(
        "expected,value",
        [
            ["0.00", 1e-5],
            ["0.00", 1e-4],
            ["0.00", 1e-3],
            ["0.01", 1e-2],
            ["0.10", 1e-1],
            ["1.00", 1e0],
            ["10.0", 1e1],
            [" 100", 1e2],
            ["1000", 1e3],
            pytest.param("1000", 1e4, marks=pytest.mark.xfail(raises=ValueError)),
        ],
    )
    def test_with_disallowed_exp_form(self, expected: str, value: float, max_len=4):
        assert max_len == len(expected)
        assert format_auto_float(value, max_len, allow_exp_form=False) == expected


# -- static ------------------------------------------------------


class TestStaticFormatter:
    @pytest.mark.parametrize(
        argnames="value,legacy_rounding,expected",
        argvalues=[(0.2, False, "200m"), (0.2, True, "0.20")],
        ids=["legacy OFF", "legacy ON"],
    )
    def test_legacy_rounding_works(
        self, value: float, legacy_rounding: bool, expected: str
    ):
        formatter = StaticFormatter(
            fallback=formatter_si, unit_separator="", legacy_rounding=legacy_rounding
        )
        assert formatter.format(value) == expected

    @pytest.mark.parametrize(
        "expected,value", [("10.0", 10 - 1e-15)]  # near 64-bit float precision limit
    )
    def test_edge_cases(self, expected: str, value: float):
        assert format_si(value) == expected

    @pytest.mark.parametrize(
        "expected,value",
        [
            [
                "\x1b[1;33m" + "9" + "\x1b[22;39m"
                "\x1b[1;2;33m" + ".80" + "\x1b[22;22;39m" + " "
                "\x1b[2;33m" + "p" + "\x1b[22;39m"
                "\x1b[2;33m" + "m" + "\x1b[22;39m",
                9.8e-12,
            ],
            [
                "\x1b[1;32m" + "9" + "\x1b[22;39m"
                "\x1b[1;2;32m" + ".80" + "\x1b[22;22;39m" + " "
                "\x1b[2;32m" + "n" + "\x1b[22;39m"
                "\x1b[2;32m" + "m" + "\x1b[22;39m",
                9.8e-9,
            ],
            [
                "\x1b[1;36m" + "9" + "\x1b[22;39m"
                "\x1b[1;2;36m" + ".80" + "\x1b[22;22;39m" + " "
                "\x1b[2;36m" + "µ" + "\x1b[22;39m"
                "\x1b[2;36m" + "m" + "\x1b[22;39m",
                9.8e-6,
            ],
            [
                "\x1b[1;34m" + "4" + "\x1b[22;39m"
                "\x1b[1;2;34m" + ".00" + "\x1b[22;22;39m" + " "
                "\x1b[2;34m" + "m" + "\x1b[22;39m"
                "\x1b[2;34m" + "m" + "\x1b[22;39m",
                0.004,
            ],
            [
                "\x1b[1;34m" + "200" + "\x1b[22;39m" + " "
                "\x1b[2;34m" + "m" + "\x1b[22;39m"
                "\x1b[2;34m" + "m" + "\x1b[22;39m",
                0.2,
            ],
            ["\x1b[90m" "0" "\x1b[39m" " " "\x1b[2;90m" "m" "\x1b[22;39m", 0.0],
            [
                "\x1b[1;34m" + "20" + "\x1b[22;39m"
                "\x1b[1;2;34m" + ".0" + "\x1b[22;22;39m" + " "
                "\x1b[2;34m" + "m" + "\x1b[22;39m",
                20.0,
            ],
            [
                "\x1b[1;34m" + "3" + "\x1b[22;39m"
                "\x1b[1;2;34m" + ".42" + "\x1b[22;22;39m" + " "
                "\x1b[2;34m" + "k" + "\x1b[22;39m"
                "\x1b[2;34m" + "m" + "\x1b[22;39m",
                3421.3,
            ],
            [
                "\x1b[1;34m" + "891" + "\x1b[22;39m" + " "
                "\x1b[2;34m" + "k" + "\x1b[22;39m"
                "\x1b[2;34m" + "m" + "\x1b[22;39m",
                891_233.433,
            ],
            [
                "\x1b[1;36m" + "189" + "\x1b[22;39m" + " "
                "\x1b[2;36m" + "M" + "\x1b[22;39m"
                "\x1b[2;36m" + "m" + "\x1b[22;39m",
                189_233_792.11,
            ],
            [
                "\x1b[1;33m" + "1" + "\x1b[22;39m"
                "\x1b[1;2;33m" + ".10" + "\x1b[22;22;39m" + " "
                "\x1b[2;33m" + "T" + "\x1b[22;39m"
                "\x1b[2;33m" + "m" + "\x1b[22;39m",
                1.1e12,
            ],
            [
                "\x1b[1;31m" + "1" + "\x1b[22;39m"
                "\x1b[1;2;31m" + ".10" + "\x1b[22;22;39m" + " "
                "\x1b[2;31m" + "P" + "\x1b[22;39m"
                "\x1b[2;31m" + "m" + "\x1b[22;39m",
                1.1e15,
            ],
        ],
        ids=format_test_params,
    )
    @pytest.mark.setup(force_output_mode=OutputMode.TRUE_COLOR)
    def test_colorizing(self, expected: str, value: float):
        assert format_si(value, unit="m", auto_color=True).render() == expected


class TestStaticFormatterSi:
    @pytest.mark.parametrize(
        "expected,value",
        [
            ["12.3 ?", 1.23456789e34],
            ["12.3 Q", 1.23456789e31],
            ["12.3 R", 1.23456789e28],
            ["12.3 Y", 1.23456789e25],
            ["12.3 Z", 1.23456789e22],
            ["12.3 E", 1.23456789e19],
            ["1.24 E", 1.23456789e18],
            ["123 P", 1.23456789e17],
            ["12.3 P", 1.23456789e16],
            ["1.24 P", 1.23456789e15],
            ["123 T", 1.23456789e14],
            ["12.3 T", 1.23456789e13],
            ["1.24 T", 1.23456789e12],
            ["123 G", 1.23456789e11],
            ["12.3 G", 1.23456789e10],
            ["1.24 G", 1.23456789e9],
            ["123 M", 1.23456789e8],
            ["12.3 M", 1.23456789e7],
            ["1.24 M", 1.23456789e6],
            ["123 k", 1.23456789e5],
            ["12.3 k", 1.23456789e4],
            ["1.24 k", 1.23456789e3],
            ["123", 1.23456789e2],
            ["12.3", 1.23456789e1],
            ["1.24", 1.23456789],
            ["123 m", 0.123456789],
            ["12.3 m", 1.23456789e-2],
            ["1.24 m", 1.23456789e-3],
            ["123 µ", 1.23456789e-4],
            ["12.3 µ", 1.23456789e-5],
            ["1.24 µ", 1.23456789e-6],
            ["123 n", 1.23456789e-7],
            ["12.3 n", 1.23456789e-8],
            ["1.24 n", 1.23456789e-9],
            ["123 p", 1.23456789e-10],
            ["12.3 p", 1.23456789e-11],
            ["1.24 p", 1.23456789e-12],
            ["123 f", 1.23456789e-13],
            ["12.3 f", 1.23456789e-14],
            ["1.24 f", 1.23456789e-15],
            ["123 a", 1.23456789e-16],
            ["12.3 a", 1.23456789e-17],
            ["1.24 a", 1.23456789e-18],
            ["123 z", 1.23456789e-19],
            ["123 y", 1.23456789e-22],
            ["123 r", 1.23456789e-25],
            ["123 q", 1.23456789e-28],
            ["123 ?", 1.23456789e-31],
        ],
    )
    def test_format_si_no_unit(self, expected: str, value: float):
        assert format_si(value) == expected

    @pytest.mark.parametrize(
        "expected,value",
        [
            ["100 ?m", 1e-31],
            ["1.00 qm", 1e-30],
            ["10.0 qm", 1e-29],
            ["100 qm", 1e-28],
            ["1.00 rm", 1e-27],
            ["10.0 rm", 1e-26],
            ["100 rm", 1e-25],
            ["1.00 ym", 1e-24],
            ["10.0 ym", 1e-23],
            ["100 ym", 1e-22],
            ["1.00 zm", 1e-21],
            ["10.0 zm", 1e-20],
            ["100 zm", 1e-19],
            ["1.00 am", 1e-18],
            ["10.0 am", 1e-17],
            ["100 am", 1e-16],
            ["1.00 fm", 1e-15],
            ["10.0 fm", 1e-14],
            ["100 fm", 1e-13],
            ["1.00 pm", 1e-12],
            ["10.0 pm", 1e-11],
            ["100 pm", 1e-10],
            ["1.00 nm", 1e-09],
            ["10.0 nm", 1e-08],
            ["100 nm", 1e-07],
            ["5.00 µm", 5e-06],
            ["1.00 µm", 1e-06],
            ["10.0 µm", 1e-05],
            ["- 50 µm", -5e-05],
            ["50.0 µm", 5e-05],
            ["500 µm", 5e-04],
            ["-500 µm", -5e-04],
            ["100 µm", 1e-04],
            ["-100 µm", -1e-04],
            ["1.00 mm", 1e-03],
            ["5.00 mm", 5e-03],
            ["50.0 mm", 5e-02],
            ["10.0 mm", 1e-02],
            ["500 mm", 5e-01],
            ["100 mm", 1e-01],
            ["99.0 mm", 0.099],
            ["1.00 m", 1],
            ["0 m", -0],
            ["0 m", -0.0],
            ["0 m", 0],
            ["0 m", 0.0],
            ["5.00 V", 5],
            ["10.0 V", 1e01],
            ["50.0 V", 5e01],
            ["100 V", 1e02],
            ["500 V", 5e02],
            ["1.00 kV", 1e03],
            ["5.00 kV", 5e03],
            ["10.0 kV", 1e04],
            ["50.0 kV", 5e04],
            ["100 kV", 1e05],
            ["500 kV", 5e05],
            ["1.00 MV", 1e06],
            ["-100 kV", -1e05],
            ["-500 kV", -5e05],
            ["-1.0 MV", -1e06],
            ["10.0 MV", 1e07],
            ["100 MV", 1e08],
            ["1.00 GV", 1e09],
            ["10.0 GV", 1e10],
            ["100 GV", 1e11],
            ["1.00 TV", 1e12],
            ["10.0 TV", 1e13],
            ["100 TV", 1e14],
            ["1.00 PV", 1e15],
            ["10.0 PV", 1e16],
            ["100 PV", 1e17],
            ["1.00 EV", 1e18],
            ["10.0 EV", 1e19],
            ["100 EV", 1e20],
            ["1.00 ZV", 1e21],
            ["10.0 ZV", 1e22],
            ["100 ZV", 1e23],
            ["1.00 YV", 1e24],
            ["10.0 YV", 1e25],
            ["100 YV", 1e26],
            ["1.00 RV", 1e27],
            ["10.0 RV", 1e28],
            ["100 RV", 1e29],
            ["1.00 QV", 1e30],
            ["10.0 QV", 1e31],
            ["100 QV", 1e32],
            ["1.00 ?V", 1e33],
        ],
    )
    def test_format_si_with_unit(self, expected: str, value: float):
        assert format_si(value, unit="m" if abs(value) <= 1 else "V") == expected

    LENGTH_LIMIT_PARAMS = [
        (0.076 * pow(11, x) * (1 - 2 * (x % 2))) for x in range(-20, 20)
    ]

    @pytest.mark.parametrize("value", LENGTH_LIMIT_PARAMS)
    def test_default_si_metric_result_len_is_le_than_6(self, value: float):
        assert len(format_si(value, unit="")) <= 6

    @pytest.mark.parametrize("value", LENGTH_LIMIT_PARAMS)
    def test_si_with_unit_result_len_is_le_than_6(self, value: float):
        formatter = StaticFormatter(
            allow_fractional=False, allow_negative=False, unit="m"
        )
        result = formatter.format(value)
        assert len(result) <= 6, f"Expected len <= 6, got {len(result)} for '{result}'"

    @pytest.mark.parametrize("value", LENGTH_LIMIT_PARAMS)
    def test_si_with_unit_result_len_is_le_than_10(self, value: float):
        formatter = StaticFormatter(max_value_len=9, allow_fractional=False)
        assert len(formatter.format(value)) <= 10


class TestStaticFormatterSiBinary:
    @pytest.mark.parametrize(
        "expected,value",
        [
            ["0 B", -0.01],
            ["0 B", -0.1],
            ["0 B", -0.0],
            ["0 B", -0],
            ["0 B", 0],
            ["0 B", 0.0],
            ["0 B", 0.1],
            ["0 B", 0.01],
            ["1 B", 1],
            ["10 B", 10],
            ["43 B", 43],
            ["180 B", 180],
            ["631 B", 631],
            ["1010 B", 1010],
            ["1023 B", 1023],
            ["1.00 KiB", 1024],
            ["1.05 KiB", 1080],
            ["6.08 KiB", 6230],
            ["14.6 KiB", 15000],
            ["44.1 KiB", 45200],
            ["130 KiB", 133300],
            ["1.00 MiB", 1024**2 - 1],
            ["1.00 GiB", 1024**3 - 1],
            ["1.00 TiB", 1024**4 - 1],
            ["1.00 PiB", 1024**5 - 1],
            ["1.00 EiB", 1024**6 - 1],
            ["1.00 ZiB", 1024**7 - 1],
            ["1.00 YiB", 1024**8 - 1],
            ["1.00 RiB", 1024**9 - 1],
            ["1.00 QiB", 1024**10 - 1],
            ["1.00 ??B", 1024**11 - 1],
            ["1.00 MiB", 1024**2],
            ["1.00 GiB", 1024**3],
            ["1.00 TiB", 1024**4],
            ["1.00 PiB", 1024**5],
            ["1.00 EiB", 1024**6],
            ["1.00 ZiB", 1024**7],
            ["1.00 YiB", 1024**8],
            ["1.00 RiB", 1024**9],
            ["1.00 QiB", 1024**10],
            ["1.00 ??B", 1024**11],
        ],
    )
    def test_format_si_binary(self, expected: str, value: float):
        assert format_si_binary(value) == expected


class TestStaticFormatterBytesHuman:
    @pytest.mark.parametrize(
        "expected,value",
        [
            ["0", -0.01],
            ["0", -0.1],
            ["0", -0.0],
            ["0", -0],
            ["0", 0],
            ["0", 0.0],
            ["0", 0.1],
            ["0", 0.01],
            ["1", 1],
            ["10", 10],
            ["43", 43],
            ["180", 180],
            ["631", 631],
            ["1.01k", 1010],
            ["1.02k", 1023],
            ["1.02k", 1024],
            ["1.08k", 1080],
            ["6.23k", 6230],
            ["15.0k", 15000],
            ["45.2k", 45200],
            ["133k", 133_300],
            ["1.05M", 1_048_576],
            ["33.6M", 33_554_432],
            ["144M", 143_850_999],
            ["1.07G", 1_073_741_824],
            ["10.6G", 10_575_449_983],
            ["1.10T", 1_099_511_627_776],
            ["1.13P", 1_125_899_906_842_624],
        ],
    )
    def test_format_bytes_human(self, expected: str, value: int):
        assert format_bytes_human(value) == expected


# -- dynamic ------------------------------------------------------


class TestDynamicFormatter:
    @pytest.mark.parametrize(
        "expected,value",
        [
            ["-10.0 ms", -0.01],
            ["0.0 s", 1e-18],
            ["1.0 fs", 1e-15],
            ["1.0 ps", 1e-12],
            ["1.0 ns", 1e-9],
            ["1.0 µs", 1e-6],
            ["100.0 µs", 0.0001],
            ["1.0 ms", 0.001],
            ["10.0 ms", 0.01],
            ["100.0 ms", 0.1],
            ["0.0 s", 0.0],
            ["0.0 s", 0],
            ["0.0 s", -0],
            ["1.0 s", 1],
            ["10.0 s", 10],
            ["43.0 s", 43],
            ["3 m", 180],
            ["10 m", 631],
            ["16 m", 1010],
            ["17 m", 1023],
            ["18 m", 1080],
            ["1 h", 6230],
            ["4 h", 15000],
            ["12 h", 45200],
            ["1 d", 133_300],
            ["1 w", 1_048_576],
            ["5 M", 13_048_576],
            ["29 y", 932_048_576],
        ],
    )
    def test_format_time(self, expected: str, value: int):
        assert format_time(value) == expected

    @pytest.mark.parametrize(
        "expected,value",
        [
            ["-10µs", -0.01],
            ["0ms", -0],
            ["0ms", 0],
            ["0ms", 0.0],
            ["100µs", 0.1],
            ["10µs", 0.01],
            ["1µs", 0.001],
            ["100ns", 0.0001],
            ["1ms", 1],
            ["10ms", 10],
            ["43ms", 43],
            ["180ms", 180],
            ["631ms", 631],
            ["1s", 1010],
            ["1s", 1023],
            ["1s", 1024],
            ["1s", 1080],
            ["6s", 6230],
            ["15s", 15000],
            ["45s", 45200],
            ["2m", 133_300],
            ["17m", 1_048_576],
        ],
    )
    def test_format_time_ms(self, expected: str, value: int):
        assert format_time_ms(value) == expected

    @pytest.mark.parametrize(
        "expected,value",
        [
            [
                "\x1b[1;34m" + "-10" + "\x1b[22;39m"
                "\x1b[1;2;34m" + ".0" + "\x1b[22;22;39m" + " "
                "\x1b[2;34m" + "m" + "\x1b[22;39m"
                "\x1b[2;34m" + "s" + "\x1b[22;39m",
                -0.01,
            ],
            [
                "\x1b[90m" + "0" + "\x1b[39m"
                "\x1b[2;90m" + ".0" + "\x1b[22;39m" + " "
                "\x1b[2;90m" + "s" + "\x1b[22;39m",
                1e-18,
            ],
            [
                "1" + "\x1b[2m" + ".0" + "\x1b[22m" + " "
                "\x1b[2m" + "f" + "\x1b[22m"
                "\x1b[2m" + "s" + "\x1b[22m",
                1e-15,
            ],
            [
                "\x1b[1;33m" + "1" + "\x1b[22;39m"
                "\x1b[1;2;33m" + ".0" + "\x1b[22;22;39m" + " "
                "\x1b[2;33m" + "p" + "\x1b[22;39m"
                "\x1b[2;33m" + "s" + "\x1b[22;39m",
                1e-12,
            ],
            [
                "\x1b[1;32m" + "1" + "\x1b[22;39m"
                "\x1b[1;2;32m" + "." + "0\x1b[22;22;39m" + " "
                "\x1b[2;32m" + "n" + "\x1b[22;39m"
                "\x1b[2;32m" + "s" + "\x1b[22;39m",
                1e-9,
            ],
            [
                "\x1b[1;36m" + "1" + "\x1b[22;39m"
                "\x1b[1;2;36m" + "." + "0" + "\x1b[22;22;39m" + " "
                "\x1b[2;36m" + "µ" + "\x1b[22;39m"
                "\x1b[2;36m" + "s" + "\x1b[22;39m",
                1e-6,
            ],
            [
                "\x1b[1;34m" + "1" + "\x1b[22;39m"
                "\x1b[1;2;34m" + "." + "0\x1b[22;22;39m" + " "
                "\x1b[2;34m" + "m" + "\x1b[22;39m"
                "\x1b[2;34m" + "s" + "\x1b[22;39m",
                0.001,
            ],
            [
                "\x1b[90m" + "0" + "\x1b[39m"
                "\x1b[2;90m" + "." + "0\x1b[22;39m" + " "
                "\x1b[2;90m" + "s" + "\x1b[22;39m",
                0,
            ],
            [
                "\x1b[1;34m" + "3" + "\x1b[22;39m" + " "
                "\x1b[2;34m" + "m" + "\x1b[22;39m",
                180,
            ],
            [
                "\x1b[1;36m" + "1" + "\x1b[22;39m" + " "
                "\x1b[2;36m" + "h" + "\x1b[22;39m",
                6230,
            ],
            [
                "\x1b[1;32m" + "1" + "\x1b[22;39m" + " "
                "\x1b[2;32m" + "d" + "\x1b[22;39m",
                133_300,
            ],
            [
                "\x1b[1;33m" + "1" + "\x1b[22;39m" + " "
                "\x1b[2;33m" + "w" + "\x1b[22;39m",
                1_048_576,
            ],
            [
                "\x1b[1;93m" + "5" + "\x1b[22;39m" + " "
                "\x1b[2;93m" + "M" + "\x1b[22;39m",
                13_048_576,
            ],
            [
                "\x1b[1;31m" + "2" + "9\x1b[22;39m" + " "
                "\x1b[2;31m" + "y" + "\x1b[22;39m",
                932_048_576,
            ],
        ],
        ids=format_test_params,
    )
    @pytest.mark.setup(force_output_mode=OutputMode.TRUE_COLOR)
    def test_colorizing(self, expected: str, value: int):
        assert format_time(value, auto_color=True).render() == expected


# -- dual -----------------------------------------------------


def delta(d=0.0, s=0.0, us=0.0, ms=0.0, m=0.0, h=0.0, w=0.0) -> timedelta:
    return timedelta(d, s, us, ms, m, h, w)


class TestDualFormatter:

    # fmt: off
    TIMEDELTA_TEST_SET = [
        [delta(d=-700000),        [  "ERR",  "ERRO", "ERROR",  "OVERFL",   "OVERFLOW"]],
        [delta(d=-1000),          [  "ERR",   "2 y",  "-2 y",    "2 yr",   "-2 years"]],
        [delta(d=-300),           [  "ERR",  "10 M", "-10 M",  "10 mon", "-10 months"]],
        [delta(d=-300, s=1),      [   "9M",   "9 M",  "-9 M",   "9 mon",  "-9 months"]],
        [delta(d=-100),           [   "3M",   "3 M",  "-3 M",   "3 mon",  "-3 months"]],
        [delta(d=-9, h=-23),      [   "9d",   "9 d",  "-9 d",  "9d 23h",    "-9d 23h"]],
        [delta(d=-5),             [   "5d",   "5 d",  "-5 d",   "5d 0h",     "-5d 0h"]],
        [delta(d=-1, h=10, m=30), [  "13h",  "13 h", "-13 h",   "13 hr", "-13h 30min"]],
        [delta(h=-1, m=15),       [  "45m",  "45 m", "-45 m",  "45 min",   "-45 mins"]],
        [delta(m=-5),             [   "5m",   "5 m",  "-5 m",   "5 min",    "-5 mins"]],
        [delta(s=-2.01),          [   "0s",    "0s", "-2.0s",      "0s",      "-2.0s"]],
        [delta(s=-2),             [   "0s",    "0s", "-2.0s",      "0s",      "-2.0s"]],
        [delta(s=-2, us=1),       [   "0s",    "0s", "-2.0s",      "0s",      "-2.0s"]],
        [delta(s=-1.9),           [   "0s",    "0s", "-1.9s",      "0s",      "-1.9s"]],
        [delta(s=-1.1),           [   "0s",    "0s", "-1.1s",      "0s",      "-1.1s"]],
        [delta(s=-1.0),           [   "0s",    "0s", "-1.0s",      "0s",      "-1.0s"]],
        [delta(us=-500),          [   "0s",    "0s",  "~0 s",      "0s",     "-500µs"]],
        [delta(s=-0.5),           [   "0s",    "0s",  "~0 s",      "0s",     "-500ms"]],
        [delta(ms=-50),           [   "0s",    "0s",  "~0 s",      "0s",     "- 50ms"]],
        [delta(us=-199.12345),    [   "0s",    "0s",  "~0 s",      "0s",     "-199µs"]],
        [delta(us=-100),          [   "0s",    "0s",  "~0 s",      "0s",     "-100µs"]],
        [delta(us=-1),            [   "0s",    "0s",  "~0 s",      "0s",     "-1.0µs"]],
        [delta(),                 [   "0s",    "0s",    "0s",      "0s",         "0s"]],
        [delta(us=500),           [   "0s",   "0 s", "500µs",   "500µs",      "500µs"]],
        [delta(ms=25),            [  "<1s",  "<1 s",  "<1 s",  "25.0ms",     "25.0ms"]],
        [delta(s=0.1),            [  "<1s",  "<1 s", "100ms",   "100ms",      "100ms"]],
        [delta(s=0.9),            [  "<1s",  "<1 s", "900ms",   "900ms",      "900ms"]],
        [delta(s=1),              [   "1s",   "1 s", "1.00s",   "1.00s",      "1.00s"]],
        [delta(s=1.0),            [   "1s",   "1 s", "1.00s",   "1.00s",      "1.00s"]],
        [delta(s=1.1),            [   "1s",   "1 s", "1.10s",   "1.10s",      "1.10s"]],
        [delta(s=1.9),            [   "1s",   "1 s", "1.90s",   "1.90s",      "1.90s"]],
        [delta(s=2, us=-1),       [   "1s",   "1 s", "2.00s",   "2.00s",      "2.00s"]],
        [delta(s=2),              [   "2s",   "2 s", "2.00s",   "2.00s",      "2.00s"]],
        [delta(s=2.0),            [   "2s",   "2 s", "2.00s",   "2.00s",      "2.00s"]],
        [delta(s=2.5),            [   "2s",   "2 s", "2.50s",   "2.50s",      "2.50s"]],
        [delta(s=10),             [  "10s",  "10 s", "10.0s",   "10.0s",      "10.0s"]],
        [delta(m=1),              [   "1m",   "1 m",   "1 m",   "1 min",      "1 min"]],
        [delta(m=5),              [   "5m",   "5 m",   "5 m",   "5 min",     "5 mins"]],
        [delta(m=15),             [  "15m",  "15 m",  "15 m",  "15 min",    "15 mins"]],
        [delta(m=45),             [  "45m",  "45 m",  "45 m",  "45 min",    "45 mins"]],
        [delta(h=1, m=30),        [   "1h",   "1 h",   "1 h",  "1h 30m",   "1h 30min"]],
        [delta(h=4, m=15),        [   "4h",   "4 h",   "4 h",  "4h 15m",   "4h 15min"]],
        [delta(h=8, m=59, s=59),  [   "8h",   "8 h",   "8 h",  "8h 59m",   "8h 59min"]],
        [delta(h=12, m=30),       [  "12h",  "12 h",  "12 h",   "12 hr",  "12h 30min"]],
        [delta(h=18, m=45),       [  "18h",  "18 h",  "18 h",   "18 hr",  "18h 45min"]],
        [delta(h=23, m=50),       [  "23h",  "23 h",  "23 h",   "23 hr",  "23h 50min"]],
        [delta(d=1),              [   "1d",   "1 d",   "1 d",   "1d 0h",      "1d 0h"]],
        [delta(d=3, h=4),         [   "3d",   "3 d",   "3 d",   "3d 4h",      "3d 4h"]],
        [delta(d=5, h=22, m=51),  [   "5d",   "5 d",   "5 d",  "5d 22h",     "5d 22h"]],
        [delta(d=7, m=-1),        [   "6d",   "6 d",   "6 d",  "6d 23h",     "6d 23h"]],
        [delta(d=9),              [   "9d",   "9 d",   "9 d",   "9d 0h",      "9d 0h"]],
        [delta(d=12, h=18),       [  "12d",  "12 d",  "12 d",  "12 day",    "12 days"]],
        [delta(d=16, h=2),        [  "16d",  "16 d",  "16 d",  "16 day",    "16 days"]],
        [delta(d=30),             [   "1M",   "1 M",   "1 M",   "1 mon",    "1 month"]],
        [delta(d=55),             [   "1M",   "1 M",   "1 M",   "1 mon",    "1 month"]],
        [delta(d=70),             [   "2M",   "2 M",   "2 M",   "2 mon",   "2 months"]],
        [delta(d=80),             [   "2M",   "2 M",   "2 M",   "2 mon",   "2 months"]],
        [delta(d=200),            [   "6M",   "6 M",   "6 M",   "6 mon",   "6 months"]],
        [delta(d=350),            [  "ERR",  "11 M",  "11 M",  "11 mon",  "11 months"]],
        [delta(d=390),            [  "ERR",   "1 y",   "1 y",    "1 yr",     "1 year"]],
        [delta(d=810),            [  "ERR",   "2 y",   "2 y",    "2 yr",    "2 years"]],
        [delta(d=10000),          [  "ERR",  "27 y",  "27 y",   "27 yr",   "27 years"]],
        [delta(d=100000),         [  "ERR",  "ERRO", "ERROR",  "OVERFL",  "277 years"]],
        [delta(d=400000),         [  "ERR",  "ERRO", "ERROR",  "OVERFL",   "OVERFLOW"]],
    ]
    # fmt: on

    @pytest.mark.parametrize(
        "delta,expected", TIMEDELTA_TEST_SET, ids=format_test_params
    )
    @pytest.mark.parametrize("max_len,column", [(3, 0), (4, 1), (5, 2), (6, 3), (10, 4)])
    def test_output(self, max_len: int, column: int, expected: str, delta: timedelta):
        assert format_time_delta(delta.total_seconds(), max_len) == expected[column]

    @pytest.mark.parametrize(
        "delta", [l[0] for l in TIMEDELTA_TEST_SET], ids=format_test_params
    )
    @pytest.mark.parametrize("max_len", [3, 4, 5, 6, 10, 9, 1000])
    def test_output_fits_in_required_length(self, max_len: int, delta: timedelta):
        actual_output = format_time_delta(delta.total_seconds(), max_len)
        assert len(actual_output) <= max_len

    @pytest.mark.parametrize(
        "expected,delta",
        [
            [
                "\x1b[1;34m" + "-" + "100" + "\x1b[22;39m"
                "\x1b[2;34m" + "m" + "\x1b[22;39m"
                "\x1b[2;34m" + "s" + "\x1b[22;39m",
                delta(s=-0.1),
            ],
            [
                "\x1b[1;36m" + "-1" + "\x1b[22;39m"
                "\x1b[1;2;36m" + ".0" + "\x1b[22;22;39m"
                "\x1b[2;36m" + "µ" + "\x1b[22;39m"
                "\x1b[2;36m" + "s" + "\x1b[22;39m",
                delta(us=-1),
            ],
            [
                "\x1b[90m" + "0" + "\x1b[39m" "\x1b[2;90m" + "s" + "\x1b[22;39m",
                delta(),
            ],
            [
                "\x1b[1;36m" + "500" + "\x1b[22;39m"
                "\x1b[2;36m" + "µ" + "\x1b[22;39m"
                "\x1b[2;36m" + "s" + "\x1b[22;39m",
                delta(us=500),
            ],
            [
                "\x1b[1;34m" + "25" + "\x1b[22;39m"
                "\x1b[1;2;34m" + ".0" + "\x1b[22;22;39m"
                "\x1b[2;34m" + "m" + "\x1b[22;39m"
                "\x1b[2;34m" + "s" + "\x1b[22;39m",
                delta(ms=25),
            ],
            [
                "\x1b[1;35m" + "1" + "\x1b[22;39m"
                "\x1b[1;2;35m" + ".90" + "\x1b[22;22;39m"
                "\x1b[2;35m" + "s" + "\x1b[22;39m",
                delta(s=1.9),
            ],
            [
                "\x1b[1;35m" + "15" + "\x1b[22;39m" + " "
                "\x1b[2;35m" + "mins" + "\x1b[22;39m",
                delta(m=15),
            ],
            [
                "\x1b[1;36m" + "18" + "\x1b[22;39m"
                "\x1b[2;36m" + "h" + "\x1b[22;39m" + " " + "45"
                "\x1b[2m" + "min" + "\x1b[22m",
                delta(h=18, m=45),
            ],
            [
                "\x1b[1;32m" + "9" + "\x1b[22;39m"
                "\x1b[2;32m" + "d" + "\x1b[22;39m" + " "
                "\x1b[1;36m" + "23" + "\x1b[22;39m"
                "\x1b[2;36m" + "h" + "\x1b[22;39m",
                delta(d=9, h=23),
            ],
            [
                "\x1b[1;35m" + "3" + "\x1b[22;39m" + " "
                "\x1b[2;35m" + "months" + "\x1b[22;39m",
                delta(d=100),
            ],
            ["\x1b[1;31m" "OVERFLOW" "\x1b[22;39m", delta(d=400000)],
        ],
        ids=format_test_params,
    )
    @pytest.mark.setup(force_output_mode=OutputMode.TRUE_COLOR)
    def test_colorizing(self, expected: str, delta: timedelta):
        formatter = dual_registry.find_matching(10)
        actual = formatter.format(delta.total_seconds(), auto_color=True)
        assert actual.render() == expected

    @pytest.mark.parametrize("max_len", [-5, 0, 1, 2], ids=format_test_params)
    @pytest.mark.xfail(raises=ValueError)
    def test_invalid_max_length_fails(self, max_len: int):
        format_time_delta(100, max_len)

    def test_formatter_registration(self):  # @TODO more
        registry = DualFormatterRegistry()
        formatter = DualFormatter(
            units=[
                DualBaseUnit("secondsverylong", 60),
                DualBaseUnit("minutesverylong", 60),
                DualBaseUnit("hoursverylong", 24),
            ]
        )
        registry.register(formatter)
        assert formatter.max_len in registry._formatters
        assert registry.get_by_max_len(formatter.max_len)

    def test_formatting_with_shortest(self):
        assert len(format_time_delta_shortest(234)) <= 3

    def test_formatting_with_longest(self):
        assert 3 < len(format_time_delta_longest(234)) <= 10
