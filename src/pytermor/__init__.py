# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

from functools import reduce
from typing import AnyStr, Union, Type

from . import preset
from .format import Format
from .preset import MODE8_START, BG_MODE8_START
from .sequence import SequenceSGR
from .string_filter import StringFilter


def build(*args: Union[str, int, SequenceSGR]) -> SequenceSGR:
    result = SequenceSGR()
    for arg in args:
        if isinstance(arg, str):
            arg_mapped = arg.upper()
            resolved_seq = getattr(preset, arg_mapped, None)
            if resolved_seq is None:
                raise KeyError(f'Preset "{arg_mapped}" not found in registry')
            if not isinstance(resolved_seq, SequenceSGR):
                raise ValueError(f'Attribute is not instance of SGR sequence: {resolved_seq}')
            result += resolved_seq

        elif isinstance(arg, int):
            result += SequenceSGR(arg)
        elif isinstance(arg, SequenceSGR):
            result += arg
        else:
            raise TypeError(f'Invalid argument type: {arg} ({type(arg)})')

    return result


def build_c256(color: int, bg: bool = False) -> SequenceSGR:
    return (MODE8_START if not bg else BG_MODE8_START) + SequenceSGR(color)


def apply_filters(string: AnyStr, *args: StringFilter | Type[StringFilter]) -> AnyStr:
    filters = map(lambda t: t() if isinstance(t, type) else t, args)
    return reduce(lambda s, f: f(s), filters, string)
