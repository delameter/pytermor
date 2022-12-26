# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------

import pytest

from pytermor.utilnum import (
    format_si_metric,
    format_si_binary,
    PrefixedUnitFormatter,
    formatter_si_metric,
)


# fmt: off
@pytest.mark.parametrize(
    "expected,value",
    [
        [   "0 b", -.01],
        [   "0 b",  -.1],
        [   "0 b",  -.0],
        [   "0 b",   -0],
        [   "0 b",    0],
        [   "0 b",   .0],
        [   "0 b",   .1],
        [   "0 b",  .01],
        [   "1 b",    1],
        [  "10 b",   10],
        [  "43 b",   43],
        [ "180 b",  180],
        [ "631 b",  631],
        ["1010 b", 1010],
        [  "1 kb", 1024],
        [  "1 kb", 1080],
        [  "6 kb", 6230],
        [ "14 kb",      15000],
        [ "44 kb",      45200],
        ["130 kb",     133300],
        [  "1 Mb",    1257800],
        [ "41 Mb",   43106100],
        ["668 Mb",  700500000],
        [  "2 Gb", 2501234567],
        [ "13 Gb",     14.53041e9],
        ["142 Tb",  156.530231e12],
        [  "1 Pb",    1.602989e15],
        [  "1 Eb", 1.641669584e18],
        [  "1 Zb",   1.8719334e21],
        [  "1 Yb", 1.921267334e24],
        ["191 Yb",  2.31487598e26],
        [ "20 ?b", 2.543258343e28],

    ],
)
# fmt: on
def test_format_si_binary(expected: str, value: float):
    assert format_si_binary(value) == expected


# fmt: off
@pytest.mark.parametrize(
    "expected,value",
    [
        ["12.3 ?", 1.23456789e28],
        ["12.3 Y", 1.23456789e25],
        ["12.3 Z", 1.23456789e22],
        ["12.3 E", 1.23456789e19],
        ["1.23 E", 1.23456789e18],
        [ "123 P", 1.23456789e17],
        ["12.3 P", 1.23456789e16],
        ["1.23 P", 1.23456789e15],
        [ "123 T", 1.23456789e14],
        ["12.3 T", 1.23456789e13],
        ["1.23 T", 1.23456789e12],
        [ "123 G", 1.23456789e11],
        ["12.3 G", 1.23456789e10],
        ["1.23 G", 1.23456789e9],
        [ "123 M", 1.23456789e8],
        ["12.3 M", 1.23456789e7],
        ["1.23 M", 1.23456789e6],
        [ "123 k", 1.23456789e5],
        ["12.3 k", 1.23456789e4],
        ["1.23 k", 1.23456789e3],
        [   "123", 1.23456789e2],
        [  "12.3", 1.23456789e1],
        [  "1.23", 1.23456789],
        [ "123 m", 0.123456789],
        ["12.3 m", 1.23456789e-2],
        ["1.23 m", 1.23456789e-3],
        [ "123 μ", 1.23456789e-4],
        ["12.3 μ", 1.23456789e-5],
        ["1.23 μ", 1.23456789e-6],
        [ "123 n", 1.23456789e-7],
        ["12.3 n", 1.23456789e-8],
        ["1.23 n", 1.23456789e-9],
        [ "123 p", 1.23456789e-10],
        ["12.3 p", 1.23456789e-11],
        ["1.23 p", 1.23456789e-12],
        [ "123 f", 1.23456789e-13],
        ["12.3 f", 1.23456789e-14],
        ["1.23 f", 1.23456789e-15],
        [ "123 a", 1.23456789e-16],
        ["12.3 a", 1.23456789e-17],
        ["1.23 a", 1.23456789e-18],
        [ "123 z", 1.23456789e-19],
        [ "123 y", 1.23456789e-22],
        [ "123 ?", 1.23456789e-25],
        [ "123 ?", 1.23456789e-28],

    ],
)
# fmt: on
def test_format_si_metric_no_unit(expected: str, value: float):
    assert format_si_metric(value, unit="") == expected


# fmt: off
@pytest.mark.parametrize(
    "expected,value",
    [
        ["1.00 am",  1e-18],
        ["10.0 am",  1e-17],
        [ "100 am",  1e-16],
        ["1.00 fm",  1e-15],
        ["10.0 fm",  1e-14],
        [ "100 fm",  1e-13],
        ["1.00 pm",  1e-12],
        ["10.0 pm",  1e-11],
        [ "100 pm",  1e-10],
        ["1.00 nm",  1e-09],
        ["10.0 nm",  1e-08],
        [ "100 nm",  1e-07],
        ["5.00 μm",  5e-06],
        ["1.00 μm",  1e-06],
        ["10.0 μm",  1e-05],
        ["- 50 μm", -5e-05],
        ["50.0 μm",  5e-05],
        [ "500 μm",  5e-04],
        ["-500 μm", -5e-04],
        [ "100 μm",  1e-04],
        ["-100 μm", -1e-04],
        ["1.00 mm",  1e-03],
        ["5.00 mm",  5e-03],
        ["50.0 mm",  5e-02],
        ["10.0 mm",  1e-02],
        [ "500 mm",  5e-01],
        [ "100 mm",  1e-01],
        ["99.0 mm",  0.099],
        [ "1.00 m",      1],
        [    "0 m",     -0],
        [    "0 m",   -0.0],
        [    "0 m",      0],
        [    "0 m",    0.0],
        [ "5.00 V",      5],
        [ "10.0 V",   1e01],
        [ "50.0 V",   5e01],
        [  "100 V",   1e02],
        [  "500 V",   5e02],
        ["1.00 kV",   1e03],
        ["5.00 kV",   5e03],
        ["10.0 kV",   1e04],
        ["50.0 kV",   5e04],
        [ "100 kV",   1e05],
        [ "500 kV",   5e05],
        ["1.00 MV",   1e06],
        ["-100 kV",  -1e05],
        ["-500 kV",  -5e05],
        ["-1.0 MV",  -1e06],
        ["10.0 MV",   1e07],
        [ "100 MV",   1e08],
        ["1.00 GV",   1e09],
        ["10.0 GV",   1e10],
        [ "100 GV",   1e11],
        ["1.00 TV",   1e12],
        ["10.0 TV",   1e13],
        [ "100 TV",   1e14],
        ["1.00 PV",   1e15],
        ["10.0 PV",   1e16],
        [ "100 PV",   1e17],
        ["1.00 EV",   1e18],
        ["10.0 EV",   1e19],
        [ "100 EV",   1e20],
        ["1.00 ZV",   1e21],
        ["10.0 ZV",   1e22],
        [ "100 ZV",   1e23],
        ["1.00 YV",   1e24],
        ["10.0 YV",   1e25],
        [ "100 YV",   1e26],
        ["1.00 ?V",   1e27],
        ["10.0 ?V",   1e28],
        [ "100 ?V",   1e29],
    ],
)
# fmt: on
def test_format_si_metric_with_unit(expected: str, value: float):
    assert format_si_metric(value, unit="m" if abs(value) <= 1 else "V") == expected


@pytest.mark.parametrize(
    argnames="value,legacy_rounding,expected",
    argvalues=[(0.2, False, "200m"), (0.2, True, "0.20")],
    ids=["legacy OFF", "legacy ON"],
)
def test_legacy_rounding_works(value: float, legacy_rounding: bool, expected: str):
    formatter = PrefixedUnitFormatter(
        4,
        unit_separator="",
        unit="",
        parent=formatter_si_metric,
        legacy_rounding=legacy_rounding,
    )
    assert formatter.format(value) == expected


VALUES = [0.076 * pow(11, x) * (1 - 2 * (x % 2)) for x in range(-20, 20)]


@pytest.mark.parametrize("value", VALUES)
def test_default_si_metric_result_len_is_le_than_6(value: float):
    assert len(format_si_metric(value, unit="")) <= 6


@pytest.mark.parametrize("value", VALUES)
def test_si_with_unit_result_len_is_le_than_6(value: float):
    formatter = PrefixedUnitFormatter(
        max_value_len=4, truncate_frac=False, mcoef=1000.0, unit="m", unit_separator=None
    )
    assert len(formatter.format(value)) <= 6


@pytest.mark.parametrize("value", VALUES)
def test_si_with_unit_result_len_is_le_than_10(value: float):
    formatter = PrefixedUnitFormatter(
        max_value_len=9,
        truncate_frac=False,
        mcoef=1000.0,
        unit=None,
        unit_separator=None,
    )
    assert len(formatter.format(value)) <= 10
