# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from . import fmt_auto_float


@dataclass
class PrefixedUnitFmtPreset:
    """
    Default settings are suitable for formatting sizes in bytes (
    *mcoef* =1024, prefixes are k, M, G, T etc.)

    *max_value_len* cannot effectively be less than 3, at least
    as long as *prefix_coef* =1024, because there is no way for
    method to insert into output more digits than it can shift
    back using multiplier (/divider) coefficient and prefixed units.
    """
    max_value_len: int = 5
    expand_to_max: bool = False
    mcoef: float = 1024.0
    unit: str|None = 'b'
    unit_separator: str|None = ' '
    prefixes: List[str] = None


FMT_PRESET_DEFAULT_KEY = 8
FMT_PRESETS = {FMT_PRESET_DEFAULT_KEY: PrefixedUnitFmtPreset()}

FMT_PREFIXES_DEFAULT = ['', 'k', 'M', 'G', 'T', 'P', 'E', 'Z']


def fmt_prefixed_unit(value: int, preset: PrefixedUnitFmtPreset = None) -> str:
    """
    Format *value* using *preset* settings. The main idea of this method
    is to fit into specified string length as much significant digits as it's
    theoretically possible, using increasing coefficients and unit prefixes to
    indicate power.

    :param value: input value
    :param preset: formatter settings
    :return: formatted value
    """
    if preset is None:
        preset = FMT_PRESETS[FMT_PRESET_DEFAULT_KEY]
    value = max(0, value)

    def iterator(_value: float) -> str:
        prefixes = preset.prefixes if preset.prefixes else FMT_PREFIXES_DEFAULT
        for unit_idx, unit_prefix in enumerate(prefixes):
            unit = preset.unit if preset.unit else ""
            unit_separator = preset.unit_separator if preset.unit_separator else ""
            unit_full = f'{unit_prefix}{unit}'

            if _value >= preset.mcoef:
                _value /= preset.mcoef
                continue

            num_str = fmt_auto_float(_value, preset.max_value_len, (unit_idx == 0))
            return f'{num_str}{unit_separator}{unit_full}'

        # no more prefixes left
        return f'{_value!r:{preset.max_value_len}.{preset.max_value_len}}{preset.unit_separator or ""}' + \
               '?' * max([len(p) for p in prefixes]) + \
               (preset.unit or "")

    result = iterator(value)
    if not preset.expand_to_max:
        result = result.strip()
    return result
