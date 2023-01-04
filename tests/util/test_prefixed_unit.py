# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------

import pytest

from pytermor.utilnum import (
    format_si,
    format_si_binary,
    StaticBaseFormatter,
    formatter_si,
)


# fmt: off
@pytest.mark.parametrize(
    "expected,value",
    [
        [   "0 B", -.01],
        [   "0 B",  -.1],
        [   "0 B",  -.0],
        [   "0 B",   -0],
        [   "0 B",    0],
        [   "0 B",   .0],
        [   "0 B",   .1],
        [   "0 B",  .01],
        [   "1 B",    1],
        [  "10 B",   10],
        [  "43 B",   43],
        [ "180 B",  180],
        [ "631 B",  631],
        ["1010 B", 1010],
        ["1023 B", 1023],
        ["1.00 KiB",    1024],
        ["1.05 KiB",    1080],
        ["6.08 KiB",    6230],
        ["14.6 KiB",   15000],
        ["44.1 KiB",   45200],
        [ "130 KiB",  133300],
        ["1.00 MiB",  1024**2-1],
        ["1.00 GiB",  1024**3-1],
        ["1.00 TiB",  1024**4-1],
        ["1.00 PiB",  1024**5-1],
        ["1.00 EiB",  1024**6-1],
        ["1.00 ZiB",  1024**7-1],
        ["1.00 YiB",  1024**8-1],
        ["1.00 RiB",  1024**9-1],
        ["1.00 QiB", 1024**10-1],
        ["1.00 ??B", 1024**11-1],
        ["1.00 MiB",  1024**2],
        ["1.00 GiB",  1024**3],
        ["1.00 TiB",  1024**4],
        ["1.00 PiB",  1024**5],
        ["1.00 EiB",  1024**6],
        ["1.00 ZiB",  1024**7],
        ["1.00 YiB",  1024**8],
        ["1.00 RiB",  1024**9],
        ["1.00 QiB", 1024**10],
        ["1.00 ??B", 1024**11],
    ],
)
# fmt: on
def test_format_si_binary(expected: str, value: float):
    assert format_si_binary(value) == expected


# fmt: off
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
        [ "123 P", 1.23456789e17],
        ["12.3 P", 1.23456789e16],
        ["1.24 P", 1.23456789e15],
        [ "123 T", 1.23456789e14],
        ["12.3 T", 1.23456789e13],
        ["1.24 T", 1.23456789e12],
        [ "123 G", 1.23456789e11],
        ["12.3 G", 1.23456789e10],
        ["1.24 G", 1.23456789e9],
        [ "123 M", 1.23456789e8],
        ["12.3 M", 1.23456789e7],
        ["1.24 M", 1.23456789e6],
        [ "123 k", 1.23456789e5],
        ["12.3 k", 1.23456789e4],
        ["1.24 k", 1.23456789e3],
        [   "123", 1.23456789e2],
        [  "12.3", 1.23456789e1],
        [  "1.24", 1.23456789],
        [ "123 m", 0.123456789],
        ["12.3 m", 1.23456789e-2],
        ["1.24 m", 1.23456789e-3],
        [ "123 μ", 1.23456789e-4],
        ["12.3 μ", 1.23456789e-5],
        ["1.24 μ", 1.23456789e-6],
        [ "123 n", 1.23456789e-7],
        ["12.3 n", 1.23456789e-8],
        ["1.24 n", 1.23456789e-9],
        [ "123 p", 1.23456789e-10],
        ["12.3 p", 1.23456789e-11],
        ["1.24 p", 1.23456789e-12],
        [ "123 f", 1.23456789e-13],
        ["12.3 f", 1.23456789e-14],
        ["1.24 f", 1.23456789e-15],
        [ "123 a", 1.23456789e-16],
        ["12.3 a", 1.23456789e-17],
        ["1.24 a", 1.23456789e-18],
        [ "123 z", 1.23456789e-19],
        [ "123 y", 1.23456789e-22],
        [ "123 r", 1.23456789e-25],
        [ "123 q", 1.23456789e-28],
        [ "123 ?", 1.23456789e-31],

    ],
)
# fmt: on
def test_format_si_no_unit(expected: str, value: float):
    assert format_si(value) == expected


# fmt: off
@pytest.mark.parametrize(
    "expected,value",
    [
        [ "100 ?m",  1e-31],
        ["1.00 qm",  1e-30],
        ["10.0 qm",  1e-29],
        [ "100 qm",  1e-28],
        ["1.00 rm",  1e-27],
        ["10.0 rm",  1e-26],
        [ "100 rm",  1e-25],
        ["1.00 ym",  1e-24],
        ["10.0 ym",  1e-23],
        [ "100 ym",  1e-22],
        ["1.00 zm",  1e-21],
        ["10.0 zm",  1e-20],
        [ "100 zm",  1e-19],
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
        ["1.00 RV",   1e27],
        ["10.0 RV",   1e28],
        [ "100 RV",   1e29],
        ["1.00 QV",   1e30],
        ["10.0 QV",   1e31],
        [ "100 QV",   1e32],
        ["1.00 ?V",   1e33],
    ],
)
# fmt: on
def test_format_si_with_unit(expected: str, value: float):
    assert format_si(value, unit="m" if abs(value) <= 1 else "V") == expected


@pytest.mark.parametrize(
    argnames="value,legacy_rounding,expected",
    argvalues=[(0.2, False, "200m"), (0.2, True, "0.20")],
    ids=["legacy OFF", "legacy ON"],
)
def test_legacy_rounding_works(value: float, legacy_rounding: bool, expected: str):
    formatter = StaticBaseFormatter(
        formatter_si, unit_separator="", legacy_rounding=legacy_rounding
    )
    assert formatter.format(value) == expected


@pytest.mark.parametrize(
    "value,expected", [(10 - 1e-15, "10.0")]  # on the 64-bit float precision limit
)
def test_edge_cases(value: float, expected: str):
    assert format_si(value) == expected


VALUES = [0.076 * pow(11, x) * (1 - 2 * (x % 2)) for x in range(-20, 20)]


@pytest.mark.parametrize("value", VALUES)
def test_default_si_metric_result_len_is_le_than_6(value: float):
    assert len(format_si(value, unit="")) <= 6


@pytest.mark.parametrize("value", VALUES)
def test_si_with_unit_result_len_is_le_than_6(value: float):
    formatter = StaticBaseFormatter(
        max_value_len=4, allow_fractional=False, allow_negative=False, unit="m"
    )
    result = formatter.format(value)
    assert len(result) <= 6, f"Expected len <= 6, got {len(result)} for '{result}'"


@pytest.mark.parametrize("value", VALUES)
def test_si_with_unit_result_len_is_le_than_10(value: float):
    formatter = StaticBaseFormatter(max_value_len=9, allow_fractional=False)
    assert len(formatter.format(value)) <= 10
