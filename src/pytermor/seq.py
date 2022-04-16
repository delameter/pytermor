# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import List, Any

from . import code


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
        return f'{self.CONTROL_CHARACTER}' \
               f'{self.INTRODUCER}' \
               f'{self.SEPARATOR.join([str(param) for param in self._params])}' \
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
            resolved_param = getattr(code, arg_mapped, None)
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
    key_code = code.BG_COLOR_EXTENDED if bg else code.COLOR_EXTENDED
    return SequenceSGR(key_code, code.EXTENDED_MODE_256, color)


def build_rgb(r: int, g: int, b: int, bg: bool = False) -> SequenceSGR:
    [_validate_extended_color(color) for color in [r, g, b]]
    key_code = code.BG_COLOR_EXTENDED if bg else code.COLOR_EXTENDED
    return SequenceSGR(key_code, code.EXTENDED_MODE_RGB, r, g, b)


def _validate_extended_color(value: int):
    if value < 0 or value > 255:
        raise ValueError(f'Invalid color value: {value}; valid values are 0-255 inclusive')


RESET = SequenceSGR(0)  # 0

# attributes
BOLD = SequenceSGR(code.BOLD)  # 1
DIM = SequenceSGR(code.DIM)  # 2
ITALIC = SequenceSGR(code.ITALIC)  # 3
UNDERLINED = SequenceSGR(code.UNDERLINED)  # 4
BLINK_SLOW = SequenceSGR(code.BLINK_SLOW)  # 5
BLINK_FAST = SequenceSGR(code.BLINK_FAST)  # 6
INVERSED = SequenceSGR(code.INVERSED)  # 7
HIDDEN = SequenceSGR(code.HIDDEN)  # 8
CROSSLINED = SequenceSGR(code.CROSSLINED)  # 9
DOUBLE_UNDERLINED = SequenceSGR(code.DOUBLE_UNDERLINED)  # 21
OVERLINED = SequenceSGR(code.OVERLINED)  # 53

BOLD_DIM_OFF = SequenceSGR(code.BOLD_DIM_OFF)  # 22
ITALIC_OFF = SequenceSGR(code.ITALIC_OFF)  # 23
UNDERLINED_OFF = SequenceSGR(code.UNDERLINED_OFF)  # 24
BLINK_OFF = SequenceSGR(code.BLINK_OFF)  # 25
INVERSED_OFF = SequenceSGR(code.INVERSED_OFF)  # 27
HIDDEN_OFF = SequenceSGR(code.HIDDEN_OFF)  # 28
CROSSLINED_OFF = SequenceSGR(code.CROSSLINED_OFF)  # 29
OVERLINED_OFF = SequenceSGR(code.OVERLINED_OFF)  # 55

# text colors
BLACK = SequenceSGR(code.BLACK)  # 30
RED = SequenceSGR(code.RED)  # 31
GREEN = SequenceSGR(code.GREEN)  # 32
YELLOW = SequenceSGR(code.YELLOW)  # 33
BLUE = SequenceSGR(code.BLUE)  # 34
MAGENTA = SequenceSGR(code.MAGENTA)  # 35
CYAN = SequenceSGR(code.CYAN)  # 36
WHITE = SequenceSGR(code.WHITE)  # 37
# code.COLOR_EXTENDED is handled by build_c256()  # 38
COLOR_OFF = SequenceSGR(code.COLOR_OFF)  # 39

# background colors
BG_BLACK = SequenceSGR(code.BG_BLACK)  # 40
BG_RED = SequenceSGR(code.BG_RED)  # 41
BG_GREEN = SequenceSGR(code.BG_GREEN)  # 42
BG_YELLOW = SequenceSGR(code.BG_YELLOW)  # 43
BG_BLUE = SequenceSGR(code.BG_BLUE)  # 44
BG_MAGENTA = SequenceSGR(code.BG_MAGENTA)  # 45
BG_CYAN = SequenceSGR(code.BG_CYAN)  # 46
BG_WHITE = SequenceSGR(code.BG_WHITE)  # 47
# code.BG_COLOR_EXTENDED is handled by build_c256()  # 48
BG_COLOR_OFF = SequenceSGR(code.BG_COLOR_OFF)  # 49

# high intensity text colors
GRAY = SequenceSGR(code.GRAY)  # 90
HI_RED = SequenceSGR(code.HI_RED)  # 91
HI_GREEN = SequenceSGR(code.HI_GREEN)  # 92
HI_YELLOW = SequenceSGR(code.HI_YELLOW)  # 93
HI_BLUE = SequenceSGR(code.HI_BLUE)  # 94
HI_MAGENTA = SequenceSGR(code.HI_MAGENTA)  # 95
HI_CYAN = SequenceSGR(code.HI_CYAN)  # 96
HI_WHITE = SequenceSGR(code.HI_WHITE)  # 97

# high intensity background colors
BG_GRAY = SequenceSGR(code.BG_GRAY)  # 100
BG_HI_RED = SequenceSGR(code.BG_HI_RED)  # 101
BG_HI_GREEN = SequenceSGR(code.BG_HI_GREEN)  # 102
BG_HI_YELLOW = SequenceSGR(code.BG_HI_YELLOW)  # 103
BG_HI_BLUE = SequenceSGR(code.BG_HI_BLUE)  # 104
BG_HI_MAGENTA = SequenceSGR(code.BG_HI_MAGENTA)  # 105
BG_HI_CYAN = SequenceSGR(code.BG_HI_CYAN)  # 106
BG_HI_WHITE = SequenceSGR(code.BG_HI_WHITE)  # 107

# rarely supported
# 10-20: font selection
#    50: disable proportional spacing
#    51: framed
#    52: encircled
#    54: neither framed nor encircled
# 58-59: underline color
# 60-65: ideogram attributes
# 73-75: superscript and subscript
