# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

from dataclasses import dataclass
from math import floor, trunc, isclose
from typing import List


@dataclass
class TimeUnit:
    name: str
    in_next: int = None
    custom_short: str = None
    collapsible_after: int = None
    overflow_afer: int = None


@dataclass
class TimeDeltaPreset:
    units: List[TimeUnit]
    allow_negative: bool
    unit_separator: str|None
    plural_suffix: str|None
    overflow_msg: str|None


FMT_PRESET_DEFAULT_KEY = 10

FMT_PRESETS = {
    3: TimeDeltaPreset([
        TimeUnit('s', 60),
        TimeUnit('m', 60),
        TimeUnit('h', 24),
        TimeUnit('d', overflow_afer=99),
    ], allow_negative=False,
        unit_separator=None,
        plural_suffix=None,
        overflow_msg='ERR',
    ),

    4: TimeDeltaPreset([
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

    6: TimeDeltaPreset([
        TimeUnit('sec', 60),
        TimeUnit('min', 60),
        TimeUnit('hr', 24, collapsible_after=10),
        TimeUnit('day', 30, collapsible_after=10),
        TimeUnit('mon', 12),
        TimeUnit('yr', overflow_afer=99),
    ], allow_negative=False,
        unit_separator=' ',
        plural_suffix=None,
        overflow_msg='OVERFL',
    ),

    FMT_PRESET_DEFAULT_KEY: TimeDeltaPreset([
        TimeUnit('sec', 60),
        TimeUnit('min', 60, custom_short='min'),
        TimeUnit('hour', 24, collapsible_after=24),
        TimeUnit('day', 30, collapsible_after=10),
        TimeUnit('month', 12),
        TimeUnit('year', overflow_afer=999),
    ], allow_negative=True,
        unit_separator=' ',
        plural_suffix='s',
        overflow_msg='OVERFLOW',
    ),
}


def format_time_delta(seconds: float, max_len: int = None) -> str:
    """
    Format time delta using suitable format (which depends on
    *max_len* argument). Key feature of this formatter is
    ability to combine two units and display them simultaneously,
    i.e. print "3h 48min" instead of "228 mins" or "3 hours",

    Presets are defined for max_len= 3, 4, 6 and 10. Therefore,
    you can pass in any value from 3 incl. to anything reasonable and
    it's guarenteed that result's length will be less or equal to required
    length. If omitted **10** will be used.

    Example outputs:
      - max_len=3: 10s | 5m | 4h | 5d
      - max_len=4: 10 s | 5 m | 4 h | 5 d
      - max_len=6: 10 sec | 5 min | 4h 15m | 5d 22h
      - max_len=10: 10 secs | 5 mins | 4h 15min | 5d 22h

    :param seconds: value to format
    :param max_len: maximum output string length (total)
    :return: formatted string
    """
    preset = None
    if max_len is None:
        preset = FMT_PRESETS[FMT_PRESET_DEFAULT_KEY]
    else:
        fmt_preset_list = sorted(
            [key for key in FMT_PRESETS.keys() if key <= max_len],
            key=lambda k: k,
            reverse=True,
        )
        if len(fmt_preset_list) > 0:
            preset = FMT_PRESETS[fmt_preset_list[0]]

    if not preset:
        raise ValueError(f'No settings defined for max length = {max_len} (or less)')

    num = abs(seconds)
    unit_idx = 0
    prev_frac = ''

    negative = preset.allow_negative and seconds < 0
    sign = '-' if negative else ''
    result = None

    while result is None and unit_idx < len(preset.units):
        unit = preset.units[unit_idx]
        if unit.overflow_afer and num > unit.overflow_afer:
            result = preset.overflow_msg[0:max_len]
            break

        unit_name = unit.name
        unit_name_suffixed = unit_name
        if preset.plural_suffix and trunc(num) != 1:
            unit_name_suffixed += preset.plural_suffix

        short_unit_name = unit_name[0]
        if unit.custom_short:
            short_unit_name = unit.custom_short

        next_unit_ratio = unit.in_next
        unit_separator = preset.unit_separator or ''

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
