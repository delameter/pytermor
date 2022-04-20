# -----------------------------------------------------------------------------
# es7s/pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import List, Any

from . import sgr


class AbstractSequence(metaclass=ABCMeta):
    def __init__(self, *params: int):
        self._params: List[int] = [max(0, int(p)) for p in params]

    @abstractmethod
    def print(self) -> str:
        raise NotImplementedError

    @property
    def params(self) -> List[int]:
        return self._params

    def __eq__(self, other: AbstractSequence):
        if type(self) != type(other):
            return False
        return self._params == other._params

    def __repr__(self):
        return f'{self.__class__.__name__}[{";".join([str(p) for p in self._params])}]'


class AbstractSequenceCSI(AbstractSequence, metaclass=ABCMeta):
    CONTROL_CHARACTER = '\033'
    INTRODUCER = '['
    SEPARATOR = ';'

    def __init__(self, *params: int):
        super(AbstractSequenceCSI, self).__init__(*params)

    def __str__(self) -> str:
        return self.print()


class SequenceSGR(AbstractSequenceCSI, metaclass=ABCMeta):
    TERMINATOR = 'm'

    def print(self) -> str:
        if len(self._params) == 0:
            return ''

        params = self._params
        if params == [0]:  # \e[0m <=> \em, saving 1 byte
            params = []

        return f'{self.CONTROL_CHARACTER}' \
               f'{self.INTRODUCER}' \
               f'{self.SEPARATOR.join([str(param) for param in params])}' \
               f'{self.TERMINATOR}'

    def __add__(self, other: SequenceSGR) -> SequenceSGR:
        self._ensure_sequence(other)
        return SequenceSGR(*self._params, *other._params)

    def __radd__(self, other: SequenceSGR) -> SequenceSGR:
        return other.__add__(self)

    def __iadd__(self, other: SequenceSGR) -> SequenceSGR:
        return self.__add__(other)

    def __eq__(self, other: SequenceSGR):
        if type(self) != type(other):
            return False
        return self._params == other._params

    # noinspection PyMethodMayBeStatic
    def _ensure_sequence(self, subject: Any):
        if not isinstance(subject, SequenceSGR):
            raise TypeError(
                f'Expected SequenceSGR, got {type(subject)}'
            )


def build(*args: str | int | SequenceSGR) -> SequenceSGR:
    result: List[int] = []

    for arg in args:
        if isinstance(arg, str):
            arg_mapped = arg.upper()
            resolved_param = getattr(sgr, arg_mapped, None)
            if resolved_param is None:
                raise KeyError(f'Code "{arg}" -> "{arg_mapped}" not found in registry')
            if not isinstance(resolved_param, int):
                raise ValueError(f'Attribute is not valid SGR param: {resolved_param}')
            result.append(resolved_param)

        elif isinstance(arg, int):
            result.append(arg)

        elif isinstance(arg, SequenceSGR):
            result.extend(arg.params)

        else:
            raise TypeError(f'Invalid argument type: {arg!r})')

    return SequenceSGR(*result)


def build_c256(color: int, bg: bool = False) -> SequenceSGR:
    _validate_extended_color(color)
    key_code = sgr.BG_COLOR_EXTENDED if bg else sgr.COLOR_EXTENDED
    return SequenceSGR(key_code, sgr.EXTENDED_MODE_256, color)


def build_rgb(r: int, g: int, b: int, bg: bool = False) -> SequenceSGR:
    [_validate_extended_color(color) for color in [r, g, b]]
    key_code = sgr.BG_COLOR_EXTENDED if bg else sgr.COLOR_EXTENDED
    return SequenceSGR(key_code, sgr.EXTENDED_MODE_RGB, r, g, b)


def _validate_extended_color(value: int):
    if value < 0 or value > 255:
        raise ValueError(f'Invalid color value: {value}; valid values are 0-255 inclusive')


RESET = SequenceSGR(0)  # 0

# attributes
BOLD = SequenceSGR(sgr.BOLD)  # 1
DIM = SequenceSGR(sgr.DIM)  # 2
ITALIC = SequenceSGR(sgr.ITALIC)  # 3
UNDERLINED = SequenceSGR(sgr.UNDERLINED)  # 4
BLINK_SLOW = SequenceSGR(sgr.BLINK_SLOW)  # 5
BLINK_FAST = SequenceSGR(sgr.BLINK_FAST)  # 6
INVERSED = SequenceSGR(sgr.INVERSED)  # 7
HIDDEN = SequenceSGR(sgr.HIDDEN)  # 8
CROSSLINED = SequenceSGR(sgr.CROSSLINED)  # 9
DOUBLE_UNDERLINED = SequenceSGR(sgr.DOUBLE_UNDERLINED)  # 21
OVERLINED = SequenceSGR(sgr.OVERLINED)  # 53

BOLD_DIM_OFF = SequenceSGR(sgr.BOLD_DIM_OFF)  # 22
ITALIC_OFF = SequenceSGR(sgr.ITALIC_OFF)  # 23
UNDERLINED_OFF = SequenceSGR(sgr.UNDERLINED_OFF)  # 24
BLINK_OFF = SequenceSGR(sgr.BLINK_OFF)  # 25
INVERSED_OFF = SequenceSGR(sgr.INVERSED_OFF)  # 27
HIDDEN_OFF = SequenceSGR(sgr.HIDDEN_OFF)  # 28
CROSSLINED_OFF = SequenceSGR(sgr.CROSSLINED_OFF)  # 29
OVERLINED_OFF = SequenceSGR(sgr.OVERLINED_OFF)  # 55

# text colors
BLACK = SequenceSGR(sgr.BLACK)  # 30
RED = SequenceSGR(sgr.RED)  # 31
GREEN = SequenceSGR(sgr.GREEN)  # 32
YELLOW = SequenceSGR(sgr.YELLOW)  # 33
BLUE = SequenceSGR(sgr.BLUE)  # 34
MAGENTA = SequenceSGR(sgr.MAGENTA)  # 35
CYAN = SequenceSGR(sgr.CYAN)  # 36
WHITE = SequenceSGR(sgr.WHITE)  # 37
# code.COLOR_EXTENDED is handled by build_c256()  # 38
COLOR_OFF = SequenceSGR(sgr.COLOR_OFF)  # 39

# background colors
BG_BLACK = SequenceSGR(sgr.BG_BLACK)  # 40
BG_RED = SequenceSGR(sgr.BG_RED)  # 41
BG_GREEN = SequenceSGR(sgr.BG_GREEN)  # 42
BG_YELLOW = SequenceSGR(sgr.BG_YELLOW)  # 43
BG_BLUE = SequenceSGR(sgr.BG_BLUE)  # 44
BG_MAGENTA = SequenceSGR(sgr.BG_MAGENTA)  # 45
BG_CYAN = SequenceSGR(sgr.BG_CYAN)  # 46
BG_WHITE = SequenceSGR(sgr.BG_WHITE)  # 47
# code.BG_COLOR_EXTENDED is handled by build_c256()  # 48
BG_COLOR_OFF = SequenceSGR(sgr.BG_COLOR_OFF)  # 49

# high intensity text colors
GRAY = SequenceSGR(sgr.GRAY)  # 90
HI_RED = SequenceSGR(sgr.HI_RED)  # 91
HI_GREEN = SequenceSGR(sgr.HI_GREEN)  # 92
HI_YELLOW = SequenceSGR(sgr.HI_YELLOW)  # 93
HI_BLUE = SequenceSGR(sgr.HI_BLUE)  # 94
HI_MAGENTA = SequenceSGR(sgr.HI_MAGENTA)  # 95
HI_CYAN = SequenceSGR(sgr.HI_CYAN)  # 96
HI_WHITE = SequenceSGR(sgr.HI_WHITE)  # 97

# high intensity background colors
BG_GRAY = SequenceSGR(sgr.BG_GRAY)  # 100
BG_HI_RED = SequenceSGR(sgr.BG_HI_RED)  # 101
BG_HI_GREEN = SequenceSGR(sgr.BG_HI_GREEN)  # 102
BG_HI_YELLOW = SequenceSGR(sgr.BG_HI_YELLOW)  # 103
BG_HI_BLUE = SequenceSGR(sgr.BG_HI_BLUE)  # 104
BG_HI_MAGENTA = SequenceSGR(sgr.BG_HI_MAGENTA)  # 105
BG_HI_CYAN = SequenceSGR(sgr.BG_HI_CYAN)  # 106
BG_HI_WHITE = SequenceSGR(sgr.BG_HI_WHITE)  # 107

# rarely supported
# 10-20: font selection
#    50: disable proportional spacing
#    51: framed
#    52: encircled
#    54: neither framed nor encircled
# 58-59: underline color
# 60-65: ideogram attributes
# 73-75: superscript and subscript
