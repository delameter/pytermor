# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

from typing import AnyStr

from .sequence import SequenceSGR


class Format:
    def __init__(self, opening_seq: SequenceSGR, closing_seq: SequenceSGR = None, reset_after: bool = False):
        self._opening_seq: SequenceSGR = opening_seq
        self._closing_seq: SequenceSGR|None = SequenceSGR(0) if reset_after else closing_seq

    def __call__(self, text: AnyStr = None) -> AnyStr:
        result = str(self._opening_seq)
        if text is not None:
            result += text
        if self._closing_seq is not None:
            result += str(self._closing_seq)
        return result

    @property
    def open(self) -> AnyStr:
        return str(self._opening_seq)

    @property
    def close(self) -> AnyStr:
        return str(self._closing_seq) if self._closing_seq else ''
