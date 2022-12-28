# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from datetime import timedelta

import pytest

from pytermor.utilnum import (
    format_time_delta,
    TimeDeltaFormatter,
    TimeUnit,
    tdf_registry,
)


def deltastr(val):
    if isinstance(val, (timedelta,)):
        args = []
        if val.days:
            args += ["%dd" % val.days]
        if val.seconds:
            args += ["%ds" % val.seconds]
        if val.microseconds:
            args += ["%dus" % val.microseconds]
        return "%s(%s)" % ("", ' '.join(args))


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


@pytest.mark.parametrize("expected,delta", TIMEDELTA_TEST_SET, ids=deltastr)
def test_output_has_expected_format_for_max_len(expected: str, delta: timedelta):
    longest = tdf_registry.get_longest().max_len
    assert format_time_delta(delta.total_seconds(), longest) == expected


@pytest.mark.parametrize("_,delta", TIMEDELTA_TEST_SET, ids=deltastr)
@pytest.mark.parametrize("max_len", [3, 4, 6, 10, 9, 1000])
def test_output_fits_in_required_length(max_len: int, _, delta: timedelta):
    actual_output = format_time_delta(delta.total_seconds(), max_len)
    assert len(actual_output) <= max_len


@pytest.mark.parametrize("max_len", [-5, 0, 1, 2], ids=deltastr)
@pytest.mark.xfail(raises=ValueError)
def test_invalid_max_length_fails(max_len: int):
    format_time_delta(100, max_len)


def test_formatter_registration():  # @TODO more
    formatter = TimeDeltaFormatter(
        units=[TimeUnit("s", 60), TimeUnit("m", 60), TimeUnit("h", 24)]
    )
    tdf_registry.register(formatter)

    assert formatter.max_len in tdf_registry._formatters
    assert tdf_registry.get_by_max_len(formatter.max_len)
