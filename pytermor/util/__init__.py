# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""
Utility package for removing some of the boilerplate code when
dealing with escape sequences. Also contains set of formatters for
prettier output.
"""
from __future__ import annotations

from .auto_float import format_auto_float
from .prefixed_unit import format_si_metric, format_si_binary, PrefixedUnitFormatter, PREFIXES_SI, PREFIX_ZERO_SI
from .time_delta import format_time_delta, TimeUnit, TimeDeltaFormatter, TimeDeltaStylesheet

from .string_filter import apply_filters, StringFilter, ReplaceSGR, ReplaceCSI, ReplaceNonAsciiBytes
from .stdlib_ext import ljust_sgr, rjust_sgr, center_sgr


def format_thousand_sep(value: int | float, separator=' '):
    return f'{value:_}'.replace('_', separator)
