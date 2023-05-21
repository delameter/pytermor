# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

from datetime import timedelta
from math import isclose
from typing import overload, TypeVar

from pytermor import Style, apply_filters, SgrStringReplacer, \
    NonPrintsOmniVisualizer, RGB, HSV, LAB, XYZ
from pytermor.log import get_qname
from .fixtures import *  # noqa


str_filters = [
    SgrStringReplacer(lambda m: "]" if "39" in m.group(3) else "["),
    NonPrintsOmniVisualizer,
]

def format_test_params(val) -> str | None:
    if isinstance(val, str):
        return apply_filters(val, *str_filters)
    if isinstance(val, int):
        return f"0x{val:06x}"
    if isinstance(val, (RGB, HSV, LAB, XYZ)):
        return str(val).replace('°', '')
    if isinstance(val, (list, tuple)):
        return "("+",".join(map(str, val))+")"
    if isinstance(val, dict):
        return f"(" + (" ".join((k + "=" + str(v)) for k, v in val.items())) + ")"
    if isinstance(val, timedelta):
        return format_timedelta(val)
    if isinstance(val, Style):
        return "%s(%s)" % (get_qname(val), val.repr_attrs(False))
    return None

def format_timedelta(val: timedelta) -> str:
    args = []
    if val.days:
        args += ["%dd" % val.days]
    if val.seconds:
        args += ["%ds" % val.seconds]
    if val.microseconds:
        args += ["%dus" % val.microseconds]
    return "%s(%s)" % ("", " ".join(args))


TT = TypeVar("TT", bound=tuple)

@overload
def assert_close(a: TT, b: TT):
    ...
@overload
def assert_close(a: float|int, b: float|int):
    ...
def assert_close(a, b):
    def are_instances(t):
        return isinstance(a, t) and isinstance(b, t)

    if are_instances((float, int)):
        assert isclose(a, b, abs_tol=0.01)
    elif are_instances(tuple):
        for (pa, pb) in zip(a, b):
            try:
                assert_close(pa, pb)
            except AssertionError as e:
                raise AssertionError(a, b) from e
    else:
        raise TypeError
