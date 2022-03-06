from __future__ import annotations
import re
from typing import AnyStr, Union

from pytermor.format import Format
from pytermor.sequence import SGRSequence
from pytermor.preset import RESET, MODE8_START, BG_MODE8_START


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

