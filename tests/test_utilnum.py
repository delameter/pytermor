# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

import typing as t
from datetime import timedelta

import pytest

from pytermor.utilnum import (
    format_thousand_sep,
    format_auto_float,
    format_time_delta,
    DynamicBaseFormatter,
    CustomBaseUnit,
    tdf_registry,
    format_si,
    format_si_binary,
    format_bytes_human,
    StaticBaseFormatter,
    FORMATTER_SI,
)


class TestFormatThousandSep:
    def test_output_has_expected_format(self):
        assert format_thousand_sep(1234567890) == "1 234 567 890"


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
            ["9.9e13", 98765432109876, 6],  #     significant digit), but decided that
            ["1.2e14", 123456789012345, 6],  #     the more normalizing — the better
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
            ["9", 9.9, 1],  # ints tight fit (rounding up cases)
            ["10", 9.9, 2],
            ["99", 99.9, 2],
            ["100", 99.9, 3],
            ["99.9", 99.9, 4],
            ["-9", -9.9, 2],
            ["-10", -9.9, 3],
        ],
    )
    def test_format_auto_float(self, expected: str, value: float, max_len: int):
        assert max_len == len(expected)
        assert format_auto_float(value, max_len) == expected

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
        assert format_auto_float(value, max_len, allow_exp_form=False) == expected


# -- DynamicBaseFormatter -----------------------------------------------------


def delta_str(val) -> str | None:
    if isinstance(val, timedelta):
        args = []
        if val.days:
            args += ["%dd" % val.days]
        if val.seconds:
            args += ["%ds" % val.seconds]
        if val.microseconds:
            args += ["%dus" % val.microseconds]
        return "%s(%s)" % ("", " ".join(args))
    return None


class TestDynamicBaseFormatter:
    TIMEDELTA_TEST_SET = [
        ["OVERFLOW", timedelta(days=-700000)],
        ["-2 years", timedelta(days=-1000)],
        ["-10 months", timedelta(days=-300)],
        ["-3 months", timedelta(days=-100)],
        ["-9d 23h", timedelta(days=-9, hours=-23)],
        ["-5d 0h", timedelta(days=-5)],
        ["-13h 30min", timedelta(days=-1, hours=10, minutes=30)],
        ["-45 mins", timedelta(hours=-1, minutes=15)],
        ["-5 mins", timedelta(minutes=-5)],
        ["-2.0s", timedelta(seconds=-2.01)],
        ["-2.0s", timedelta(seconds=-2)],
        ["-2.0s", timedelta(seconds=-2, microseconds=1)],
        ["-1.9s", timedelta(seconds=-1.9)],
        ["-1.1s", timedelta(seconds=-1.1)],
        ["-1.0s", timedelta(seconds=-1.0)],
        ["-500ms", timedelta(seconds=-0.5)],
        ["- 50ms", timedelta(milliseconds=-50)],
        ["-100μs", timedelta(microseconds=-100)],
        ["-1.0μs", timedelta(microseconds=-1)],
        ["0s", timedelta()],
        ["500μs", timedelta(microseconds=500)],
        ["25.0ms", timedelta(milliseconds=25)],
        ["100ms", timedelta(seconds=0.1)],
        ["900ms", timedelta(seconds=0.9)],
        ["1.00s", timedelta(seconds=1)],
        ["1.00s", timedelta(seconds=1.0)],
        ["1.10s", timedelta(seconds=1.1)],
        ["1.90s", timedelta(seconds=1.9)],
        ["2.00s", timedelta(seconds=2, microseconds=-1)],
        ["2.00s", timedelta(seconds=2)],
        ["2.00s", timedelta(seconds=2.0)],
        ["2.50s", timedelta(seconds=2.5)],
        ["10.0s", timedelta(seconds=10)],
        ["1 min", timedelta(minutes=1)],
        ["5 mins", timedelta(minutes=5)],
        ["15 mins", timedelta(minutes=15)],
        ["45 mins", timedelta(minutes=45)],
        ["1h 30min", timedelta(hours=1, minutes=30)],
        ["4h 15min", timedelta(hours=4, minutes=15)],
        ["8h 59min", timedelta(hours=8, minutes=59, seconds=59)],
        ["12h 30min", timedelta(hours=12, minutes=30)],
        ["18h 45min", timedelta(hours=18, minutes=45)],
        ["23h 50min", timedelta(hours=23, minutes=50)],
        ["1d 0h", timedelta(days=1)],
        ["3d 4h", timedelta(days=3, hours=4)],
        ["5d 22h", timedelta(days=5, hours=22, minutes=51)],
        ["6d 23h", timedelta(days=7, minutes=-1)],
        ["9d 0h", timedelta(days=9)],
        ["12 days", timedelta(days=12, hours=18)],
        ["16 days", timedelta(days=16, hours=2)],
        ["1 month", timedelta(days=30)],
        ["1 month", timedelta(days=55)],
        ["2 months", timedelta(days=70)],
        ["2 months", timedelta(days=80)],
        ["6 months", timedelta(days=200)],
        ["11 months", timedelta(days=350)],
        ["1 year", timedelta(days=390)],
        ["2 years", timedelta(days=810)],
        ["27 years", timedelta(days=10000)],
        ["277 years", timedelta(days=100000)],
        ["OVERFLOW", timedelta(days=400000)],
    ]

    @pytest.mark.parametrize("expected,delta", TIMEDELTA_TEST_SET, ids=delta_str)
    def test_output_has_expected_format_for_max_len(
        self, expected: str, delta: timedelta
    ):
        longest = tdf_registry.get_longest().max_len
        assert format_time_delta(delta.total_seconds(), longest) == expected

    @pytest.mark.parametrize("_,delta", TIMEDELTA_TEST_SET, ids=delta_str)
    @pytest.mark.parametrize("max_len", [3, 4, 6, 10, 9, 1000])
    def test_output_fits_in_required_length(self, max_len: int, _, delta: timedelta):
        actual_output = format_time_delta(delta.total_seconds(), max_len)
        assert len(actual_output) <= max_len

    # -------------------------------------------------------------------------

    @pytest.mark.parametrize("max_len", [-5, 0, 1, 2], ids=delta_str)
    @pytest.mark.xfail(raises=ValueError)
    def test_invalid_max_length_fails(self, max_len: int):
        format_time_delta(100, max_len)

    # -------------------------------------------------------------------------

    def test_formatter_registration(self):  # @TODO more
        formatter = DynamicBaseFormatter(
            units=[
                CustomBaseUnit("s", 60),
                CustomBaseUnit("m", 60),
                CustomBaseUnit("h", 24),
            ]
        )
        tdf_registry.register(formatter)

        assert formatter.max_len in tdf_registry._formatters
        assert tdf_registry.get_by_max_len(formatter.max_len)


# -- StaticBaseFormatter ------------------------------------------------------


class TestStaticBaseFormatterSi:
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
            ["123 μ", 1.23456789e-4],
            ["12.3 μ", 1.23456789e-5],
            ["1.24 μ", 1.23456789e-6],
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

    # -------------------------------------------------------------------------

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
            ["5.00 μm", 5e-06],
            ["1.00 μm", 1e-06],
            ["10.0 μm", 1e-05],
            ["- 50 μm", -5e-05],
            ["50.0 μm", 5e-05],
            ["500 μm", 5e-04],
            ["-500 μm", -5e-04],
            ["100 μm", 1e-04],
            ["-100 μm", -1e-04],
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

    # -------------------------------------------------------------------------

    LENGTH_LIMIT_PARAMS = [
        (0.076 * pow(11, x) * (1 - 2 * (x % 2))) for x in range(-20, 20)
    ]

    @pytest.mark.parametrize("value", LENGTH_LIMIT_PARAMS)
    def test_default_si_metric_result_len_is_le_than_6(self, value: float):
        assert len(format_si(value, unit="")) <= 6

    @pytest.mark.parametrize("value", LENGTH_LIMIT_PARAMS)
    def test_si_with_unit_result_len_is_le_than_6(self, value: float):
        formatter = StaticBaseFormatter(
            allow_fractional=False, allow_negative=False, unit="m"
        )
        result = formatter.format(value)
        assert len(result) <= 6, f"Expected len <= 6, got {len(result)} for '{result}'"

    @pytest.mark.parametrize("value", LENGTH_LIMIT_PARAMS)
    def test_si_with_unit_result_len_is_le_than_10(self, value: float):
        formatter = StaticBaseFormatter(max_value_len=9, allow_fractional=False)
        assert len(formatter.format(value)) <= 10


class TestStaticBaseFormatterSiBinary:
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


class TestStaticBaseFormatterBytesHuman:
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


class TestStaticBaseFormatter:
    @pytest.mark.parametrize(
        argnames="value,legacy_rounding,expected",
        argvalues=[(0.2, False, "200m"), (0.2, True, "0.20")],
        ids=["legacy OFF", "legacy ON"],
    )
    def test_legacy_rounding_works(
        self, value: float, legacy_rounding: bool, expected: str
    ):
        formatter = StaticBaseFormatter(
            fallback=FORMATTER_SI,
            unit_separator="",
            legacy_rounding=legacy_rounding,
        )
        assert formatter.format(value) == expected

    @pytest.mark.parametrize(
        "value,expected", [(10 - 1e-15, "10.0")]  # on the 64-bit float precision limit
    )
    def test_edge_cases(self, value: float, expected: str):
        assert format_si(value) == expected
