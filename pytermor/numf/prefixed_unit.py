# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

from dataclasses import dataclass
from math import trunc
from typing import List

from . import format_auto_float


@dataclass
class PrefixedUnitPreset:
    max_value_len: int
    integer_input: bool
    unit: str|None
    unit_separator: str|None
    mcoef: float
    prefixes: List[str|None]|None
    prefix_zero_idx: int|None


PREFIXES_SI = ['y', 'z', 'a', 'f', 'p', 'n', 'μ', 'm', None, 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
PREFIX_ZERO_SI = 8

"""
Suitable for formatting any SI unit with values
from approximately 10^-27 to 10^27 .

*max_value_len* must be at least `4`, because it's a
minimum requirement for displaying values from 999 to -999.
Next number to 999 is 1000, which will be displayed as 1k.
"""
PRESET_SI_METRIC = PrefixedUnitPreset(
    max_value_len=5,
    integer_input=False,
    unit='m',
    unit_separator=' ',
    mcoef=1000.0,
    prefixes=PREFIXES_SI,
    prefix_zero_idx=PREFIX_ZERO_SI,
)
PRESET_SI_BINARY = PrefixedUnitPreset(
    max_value_len=5,
    integer_input=True,
    unit='b',
    unit_separator=' ',
    mcoef=1024.0,
    prefixes=PREFIXES_SI,
    prefix_zero_idx=PREFIX_ZERO_SI,
)


def format_prefixed_unit(value: float, preset: PrefixedUnitPreset = None) -> str:
    """
    Format *value* using *preset* settings. The main idea of this method
    is to fit into specified string length as much significant digits as it's
    theoretically possible, using multipliers and unit prefixes to
    indicate them.

    Default *preset* is PRESET_SI_BINARY, PrefixedUnitPreset with base 1024
    made for binary sizes (bytes, kbytes, Mbytes).

    :param value: input value
    :param preset: formatter settings
    :return: formatted value
    :rtype: str
    """
    if preset is None:
        preset = PRESET_SI_BINARY

    prefixes = preset.prefixes or ['']
    unit_separator = preset.unit_separator or ''
    unit_idx = preset.prefix_zero_idx or ''

    while 0 <= unit_idx < len(prefixes):
        if 0.0 < abs(value) <= 1/preset.mcoef:
            value *= preset.mcoef
            unit_idx -= 1
            continue
        elif abs(value) >= preset.mcoef:
            value /= preset.mcoef
            unit_idx += 1
            continue

        unit_full = (prefixes[unit_idx] or '') + (preset.unit or '')

        if preset.integer_input and unit_idx == preset.prefix_zero_idx:
            num_str = f'{trunc(value)!s:.{preset.max_value_len}s}'
        else:
            num_str = format_auto_float(value, preset.max_value_len)

        return f'{num_str.strip()}{unit_separator}{unit_full}'

    # no more prefixes left
    return f'{value!r:{preset.max_value_len}.{preset.max_value_len}}{preset.unit_separator or ""}' + \
           '?' * max([len(p) for p in prefixes]) + \
           (preset.unit or "")
