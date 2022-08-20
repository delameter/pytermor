# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""
.. testsetup:: *

    from pytermor.util import format_thousand_sep

"""
from __future__ import annotations

from typing import List

from .auto_float import format_auto_float
from .prefixed_unit import format_si_metric, format_si_binary, PrefixedUnitFormatter, PREFIXES_SI, PREFIX_ZERO_SI
from .time_delta import format_time_delta, TimeUnit, TimeDeltaFormatter, TimeDeltaStylesheet

from .string_filter import apply_filters, StringFilter, ReplaceSGR, ReplaceCSI, ReplaceNonAsciiBytes, VisualuzeWhitespace
from .stdlib_ext import ljust_sgr, rjust_sgr, center_sgr

from ..render import Text


def format_thousand_sep(value: int|float, separator=' '):
    """
    Returns input ``value`` with integer part splitted into groups of three digits,
    joined then with ``separator`` string.

    >>> format_thousand_sep(260341)
    '260 341'
    >>> format_thousand_sep(-9123123123.55, ',')
    '-9,123,123,123.55'

    """
    return f'{value:_}'.replace('_', separator)


def distribute_padded(values: List[str|Text], max_len: int, pad_before: bool = False,
                      pad_after: bool = False, ) -> str:
    if pad_before:
        values.insert(0, '')
    if pad_after:
        values.append('')

    values_amount = len(values)
    gapes_amount = values_amount - 1
    values_len = sum(len(v) for v in values)
    spaces_amount = max_len - values_len
    if spaces_amount < gapes_amount:
        raise ValueError(f'There is not enough space for all values with padding')

    result = ''
    for value_idx, value in enumerate(values):
        gape_len = spaces_amount // (gapes_amount or 1)  # for last value
        result += value + ' ' * gape_len
        gapes_amount -= 1
        spaces_amount -= gape_len

    return result
