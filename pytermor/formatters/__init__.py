# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

from .auto_float import format_auto_float
from .prefixed_unit import format_si_metric, format_prefixed_unit, PrefixedUnitPreset, PRESET_SI_METRIC, PRESET_SI_BINARY
from .time_delta import format_time_delta, TimeUnit, TimeDeltaFormatter, TimeDeltaFormatterRegistry


def format_thousand_sep(value: int | float, separator=' '):
    """
    A
    :param value:
    :param separator:
    :return:
    """
    return f'{value:_}'.replace('_', separator)
