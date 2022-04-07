# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

from . import build, code
from .registry import sgr_parity_registry
from .seq import SequenceSGR


class Format:
    def __init__(self, opening_seq: SequenceSGR, closing_seq: SequenceSGR = None, hard_reset_after: bool = False):
        self._opening_seq: SequenceSGR = opening_seq
        self._closing_seq: SequenceSGR|None = SequenceSGR(0) if hard_reset_after else closing_seq

    def __repr__(self):
        return f'{self.__class__.__name__}[{self._opening_seq!r}, {self._closing_seq!r}]'

    def __call__(self, text: str = None) -> str:
        result = str(self._opening_seq)
        if text is not None:
            result += text
        if self._closing_seq is not None:
            result += str(self._closing_seq)
        return result

    def invoke(self, s: str) -> str:
        return self(s)

    @property
    def opening(self) -> str:
        return str(self._opening_seq)

    @property
    def opening_seq(self) -> SequenceSGR:
        return self._opening_seq

    @property
    def closing(self) -> str:
        return str(self._closing_seq) if self._closing_seq else ''

    @property
    def closing_seq(self) -> SequenceSGR|None:
        return self._closing_seq


class EmptyFormat(Format):
    def __init__(self):
        self._opening_seq = None
        self._closing_seq = None

    def __repr__(self):
        return f'{self.__class__.__name__}[]'

    def __call__(self, text: str = None) -> str:
        if text is None:
            return ''
        return text

    @property
    def opening(self) -> str:
        return ''


def autof(*args: str|int|SequenceSGR) -> Format:
    opening_seq = build(*args)
    closing_seq = sgr_parity_registry.get_closing_seq(opening_seq)
    return Format(opening_seq, closing_seq)


bold = autof(code.BOLD)
dim = autof(code.DIM)
italic = autof(code.ITALIC)
underlined = autof(code.UNDERLINED)
inversed = autof(code.INVERSED)
overlined = autof(code.OVERLINED)

red = autof(code.RED)
green = autof(code.GREEN)
yellow = autof(code.YELLOW)
blue = autof(code.BLUE)
magenta = autof(code.MAGENTA)
cyan = autof(code.CYAN)

bg_red = autof(code.BG_RED)
bg_green = autof(code.BG_GREEN)
bg_yellow = autof(code.BG_YELLOW)
bg_blue = autof(code.BG_BLUE)
bg_magenta = autof(code.BG_MAGENTA)
bg_cyan = autof(code.BG_CYAN)
