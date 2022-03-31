# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

from . import preset
from .format import Format
from .preset import MODE8_START, BG_MODE8_START
from .sequence import SequenceSGR
from .string_filter import StringFilter


def build(*args: str|int|SequenceSGR) -> SequenceSGR:
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


def autof(*args: str|int|SequenceSGR) -> Format:
    raise NotImplementedError
