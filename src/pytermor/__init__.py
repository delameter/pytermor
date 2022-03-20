# ------------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
from __future__ import annotations
import re
from functools import reduce
from typing import AnyStr, Union, Type

from pytermor.format import Format
from pytermor.sequence import SGRSequence
from pytermor.preset import RESET, MODE8_START, BG_MODE8_START
from pytermor.string_filter import StringFilter


def build(*args: Union[int, str]):
    # @TODO
    return Format(SGRSequence(*args), RESET)


def build_text256_seq(arg3: int) -> SGRSequence:
    return MODE8_START + SGRSequence(arg3)


def build_background256_seq(arg3: int) -> SGRSequence:
    return BG_MODE8_START + SGRSequence(arg3)


def sanitize(inp: AnyStr, ansi_control_seqs=True):
    if ansi_control_seqs:
        inp = re.sub('\033\\[([0-9;:<=>?]*)([@A-Za-z])', '', inp)
    return inp


def apply_filters(string: AnyStr, *args: StringFilter | Type[StringFilter]) -> AnyStr:
    filters = map(lambda t: t() if isinstance(t, type) else t, args)
    return reduce(lambda s, f: f(s), filters, string)
