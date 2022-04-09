# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

from abc import ABCMeta, abstractmethod

from . import build, code
from .registry import sgr_parity_registry
from .seq import SequenceSGR


class AbstractFormat(metaclass=ABCMeta):
    def __repr__(self):
        return f'{self.__class__.__name__}'

    def __call__(self, text: str = None) -> str:
        return self.wrap(text)

    @abstractmethod
    def wrap(self, text: str) -> str: raise NotImplementedError
    @property
    @abstractmethod
    def opening_str(self) -> str: raise NotImplementedError
    @property
    @abstractmethod
    def closing_str(self) -> str: raise NotImplementedError
    @property
    @abstractmethod
    def opening_seq(self) -> SequenceSGR|None: raise NotImplementedError
    @property
    @abstractmethod
    def closing_seq(self) -> SequenceSGR|None: raise NotImplementedError


class EmptyFormat(AbstractFormat):
    def wrap(self, text: str = None) -> str:
        if text is None:
            return ''
        return text

    @property
    def opening_str(self) -> str:
        return ''

    @property
    def closing_str(self) -> str:
        return ''

    @property
    def opening_seq(self) -> SequenceSGR|None:
        return None

    @property
    def closing_seq(self) -> SequenceSGR|None:
        return None


class Format(AbstractFormat):
    def __init__(self, opening_seq: SequenceSGR, closing_seq: SequenceSGR = None, hard_reset_after: bool = False):
        self._opening_seq: SequenceSGR = opening_seq
        self._closing_seq: SequenceSGR|None = SequenceSGR(0) if hard_reset_after else closing_seq

    def __repr__(self):
        return super().__repr__() + '[{!r}, {!r}]'.format(self._opening_seq, self._closing_seq)

    def wrap(self, text: str = None) -> str:
        result = str(self._opening_seq)
        if text is not None:
            result += text
        if self._closing_seq is not None:
            result += str(self._closing_seq)
        return result

    @property
    def opening_str(self) -> str:
        return str(self._opening_seq)

    @property
    def opening_seq(self) -> SequenceSGR:
        return self._opening_seq

    @property
    def closing_str(self) -> str:
        return str(self._closing_seq) if self._closing_seq else ''

    @property
    def closing_seq(self) -> SequenceSGR|None:
        return self._closing_seq


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
gray = autof(code.GRAY)

bg_red = autof(code.BG_RED)
bg_green = autof(code.BG_GREEN)
bg_yellow = autof(code.BG_YELLOW)
bg_blue = autof(code.BG_BLUE)
bg_magenta = autof(code.BG_MAGENTA)
bg_cyan = autof(code.BG_CYAN)
bg_gray = autof(code.BG_GRAY)
