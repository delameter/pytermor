# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import os.path
from datetime import timedelta
from inspect import isclass
from math import isclose
from typing import cast, overload, TypeVar, AnyStr
import typing as t
from pytermor import (
    IFilter,
    Style,
    apply_filters,
    SgrStringReplacer,
    NonPrintsOmniVisualizer,
    RGB,
    HSV,
    LAB,
    XYZ,
    ISequence,
    get_qname,
)
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
        return str(val).replace("°", "")
    if isinstance(val, (list, tuple)):
        return "(" + ",".join(map(str, val)) + ")"
    if isinstance(val, dict):
        return f"(" + (" ".join((k + "=" + str(v)) for k, v in val.items())) + ")"
    if isinstance(val, timedelta):
        return format_timedelta(val)
    if isinstance(val, Style):
        return "%s(%s)" % (get_qname(val), val.repr_attrs(False))
    if isinstance(val, ISequence):
        return repr(val)
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
def assert_close(a: float | int, b: float | int):
    ...


def assert_close(a, b):
    def get_base_type(v) -> type:
        if isinstance(v, int):
            return int
        elif isinstance(v, float):
            return float
        elif isinstance(v, tuple):
            return tuple
        return type(v)

    types = {get_base_type(a), get_base_type(b)}
    if types == {float} or types == {int, float}:
        assert isclose(a, b, abs_tol=0.01), f"{a:.3f} !≈ {b:.3f}"
    elif types == {int}:
        assert a == b, f"0x{a:06x} != 0x{b:06x}"
    elif types == {tuple}:
        for (pa, pb) in zip(a, b):
            try:
                assert_close(pa, pb)
            except AssertionError as e:
                raise AssertionError(a, b) from e
    else:
        raise TypeError(f"Cannot compare {a} and {b} ({', '.join(map(str, types))})")


def load_data_file(data_filename: str) -> AnyStr:
    data_filepath = os.path.join(os.path.dirname(__file__), "data", data_filename)
    try:
        with open(data_filepath, "rt") as f:
            return f.read()
    except UnicodeError:
        with open(data_filepath, "rb") as f:
            return f.read()
