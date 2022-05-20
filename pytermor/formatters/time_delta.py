# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""
Module for time difference formatting (e.g. "4 days 15 hours", "8h 59m").

Supports several output lengths and can be customized even more.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import floor, trunc, isclose
from typing import List, Dict


def format_time_delta(seconds: float, max_len: int = None) -> str:
    """
    Format time delta using suitable format (which depends on
    ``max_len`` argument). Key feature of this formatter is
    ability to combine two units and display them simultaneously,
    e.g. print "3h 48min" instead of "228 mins" or "3 hours",

    Formatters are defined for max_len= 3, 4, 6 and 10. Therefore,
    you can pass in any value from 3 incl. and it's guarenteed
    that result's length will be less or equal to required
    length. If omitted longest registred will be used.

    Example output:
      -  max_len=3: "10s", "5m", "4h", "5d"
      -  max_len=4: "10 s", "5 m", "4 h", "5 d"
      -  max_len=6: "10 sec", "5 min", "4h 15m", "5d 22h"
      - max_len=10: "10 secs", "5 mins", "4h 15min", "5d 22h"

    :param seconds: Value to format
    :param max_len: Maximum output string length (total)
    :return:        Formatted string
    """
    if max_len is None:
        formatter = registry.get_longest()
    else:
        formatter = registry.find_matching(max_len)

    if formatter is None:
        raise ValueError(f'No settings defined for max length = {max_len} (or less)')

    return formatter.format(seconds)


@dataclass
class TimeUnit:
    name: str
    in_next: int = None
    custom_short: str = None
    collapsible_after: int = None
    overflow_afer: int = None


@dataclass
class TimeDeltaFormatter:
    """
    Formatter for time intervals. Key feature of this formatter is
    ability to combine two units and display them simultaneously,
    e.g. print "3h 48min" instead of "228 mins" or "3 hours",

    Example output:
        "10 secs", "5 mins", "4h 15min", "5d 22h"
    """
    max_len: int
    units: List[TimeUnit]
    allow_negative: bool
    unit_separator: str|None = None
    plural_suffix: str|None = None
    overflow_msg: str|None = 'OVERFLOW'

    def format(self, seconds: float) -> str:
        num = abs(seconds)
        unit_idx = 0
        prev_frac = ''

        negative = self.allow_negative and seconds < 0
        sign = '-' if negative else ''
        result = None

        while result is None and unit_idx < len(self.units):
            unit = self.units[unit_idx]
            if unit.overflow_afer and num > unit.overflow_afer:
                result = self.overflow_msg[0:self.max_len]
                break

            unit_name = unit.name
            unit_name_suffixed = unit_name
            if self.plural_suffix and trunc(num) != 1:
                unit_name_suffixed += self.plural_suffix

            short_unit_name = unit_name[0]
            if unit.custom_short:
                short_unit_name = unit.custom_short

            next_unit_ratio = unit.in_next
            unit_separator = self.unit_separator or ''

            if abs(num) < 1:
                if negative:
                    result = f'~0{unit_separator}{unit_name_suffixed:s}'
                elif isclose(num, 0, abs_tol=1e-03):
                    result = f'0{unit_separator}{unit_name_suffixed:s}'
                else:
                    result = f'<1{unit_separator}{unit_name:s}'

            elif unit.collapsible_after is not None and num < unit.collapsible_after:
                result = f'{sign}{floor(num):d}{short_unit_name:s}{unit_separator}{prev_frac:<s}'

            elif not next_unit_ratio or num < next_unit_ratio:
                result = f'{sign}{floor(num):d}{unit_separator}{unit_name_suffixed:s}'

            else:
                next_num = floor(num / next_unit_ratio)
                prev_frac = '{:d}{:s}'.format(floor(num - (next_num * next_unit_ratio)), short_unit_name)
                num = next_num
                unit_idx += 1
                continue

        return result or ''


class TimeDeltaFormatterRegistry:
    """
    Simple registry for storing formatters and selecting
    the suitable one by max output length.
    """
    def __init__(self):
        self._formatters: Dict[int, TimeDeltaFormatter] = dict()

    def register(self, *formatters: TimeDeltaFormatter):
        for formatter in formatters:
            self._formatters[formatter.max_len] = formatter

    def find_matching(self, max_len: int) -> TimeDeltaFormatter|None:
        exact_match = self.get_by_max_len(max_len)
        if exact_match is not None:
            return exact_match

        suitable_max_len_list = sorted(
            [key for key in self._formatters.keys() if key <= max_len],
            key=lambda k: k,
            reverse=True,
        )
        if len(suitable_max_len_list) == 0:
            return None
        return self.get_by_max_len(suitable_max_len_list[0])

    def get_by_max_len(self, max_len: int) -> TimeDeltaFormatter|None:
        return self._formatters.get(max_len, None)

    def get_shortest(self) -> TimeDeltaFormatterRegistry|None:
        return self._formatters.get(min(self._formatters.keys() or [None]))

    def get_longest(self) -> TimeDeltaFormatterRegistry|None:
        return self._formatters.get(max(self._formatters.keys() or [None]))


# ---------------------------------------------------------------------------
# Formatter presets
# ---------------------------------------------------------------------------

registry = TimeDeltaFormatterRegistry()
registry.register(
    TimeDeltaFormatter(3, [
        TimeUnit('s', 60),
        TimeUnit('m', 60),
        TimeUnit('h', 24),
        TimeUnit('d', overflow_afer=99),
    ], allow_negative=False,
       unit_separator=None,
       plural_suffix=None,
       overflow_msg='ERR',
    ),

    TimeDeltaFormatter(4, [
        TimeUnit('s', 60),
        TimeUnit('m', 60),
        TimeUnit('h', 24),
        TimeUnit('d', 30),
        TimeUnit('M', 12),
        TimeUnit('y', overflow_afer=99),
    ], allow_negative=False,
       unit_separator=' ',
       plural_suffix=None,
       overflow_msg='ERRO',
    ),

    TimeDeltaFormatter(6, [
        TimeUnit('sec', 60),
        TimeUnit('min', 60),
        TimeUnit('hr', 24, collapsible_after=10),
        TimeUnit('day', 30, collapsible_after=10),
        TimeUnit('mon', 12),
        TimeUnit('yr', overflow_afer=99),
    ], allow_negative=False,
       unit_separator=' ',
       plural_suffix=None,
    ),

    TimeDeltaFormatter(10, [
        TimeUnit('sec', 60),
        TimeUnit('min', 60, custom_short='min'),
        TimeUnit('hour', 24, collapsible_after=24),
        TimeUnit('day', 30, collapsible_after=10),
        TimeUnit('month', 12),
        TimeUnit('year', overflow_afer=999),
    ], allow_negative=True,
       unit_separator=' ',
       plural_suffix='s',
    ),
)
