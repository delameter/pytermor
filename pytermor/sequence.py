# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""
Module contains definitions for working with ANSI escape sequences as classes
and instances.

Each preset defined below is a valid argument for ``autocomplete()`` and
``build()`` methods.
"""
from __future__ import annotations

from abc import ABCMeta, abstractmethod, abstractproperty
from typing import List, Any

from . import intcode


class _AbstractSequence(metaclass=ABCMeta):
    """
    Common ancestor of all possible escape sequenes.
    """
    def __init__(self, *params: int):
        self._params: List[int] = [max(0, int(p)) for p in params]

    @property
    def params(self) -> List[int]:
        """ Return internal params as array. """
        return self._params

    @abstractmethod
    def print(self) -> str:
        """
        Build up actual byte sequence and return
        as an ASCII-encoded string.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def _short_class_name(cls): raise NotImplementedError

    def __eq__(self, other: _AbstractSequence):
        if type(self) != type(other):
            return False
        return self._params == other._params

    def __repr__(self):
        return f'{self._short_class_name()}[{";".join([str(p) for p in self._params])}]'


class _AbstractSequenceCSI(_AbstractSequence, metaclass=ABCMeta):
    """
    Class representing CSI-type ANSI escape sequence. All subtypes of this
    sequence have something in common - they all start with ``\\e[``.
    """
    _CONTROL_CHARACTER = '\x1b'
    _INTRODUCER = '['
    _SEPARATOR = ';'

    @classmethod
    def regexp(cls) -> str:
        return f'\\x1b\\[[0-9;]*{cls._terminator()}'

    def __init__(self, *params: int):
        super(_AbstractSequenceCSI, self).__init__(*params)

    def __str__(self) -> str:
        return self.print()

    @classmethod
    @abstractmethod
    def _terminator(cls) -> str: raise NotImplementedError


class SequenceSGR(_AbstractSequenceCSI, metaclass=ABCMeta):
    """
    Class representing SGR-type escape sequence with varying amount of parameters.

    It's possible to add of one SGR sequence to another:
       ``SequenceSGR(31) + SequenceSGR(1)``,
    which is equivalent to:
      ``SequenceSGR(31, 1)``
    """
    _TERMINATOR = 'm'

    def print(self) -> str:
        if len(self._params) == 0:  # noop
            return ''

        params = self._params
        if params == [0]:  # \e[0m <=> \em, saving 1 byte
            params = []

        return f'{self._CONTROL_CHARACTER}' \
               f'{self._INTRODUCER}' \
               f'{self._SEPARATOR.join([str(param) for param in params])}' \
               f'{self._TERMINATOR}'

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

    @classmethod
    def _terminator(cls) -> str:
        return cls._TERMINATOR

    @classmethod
    def _short_class_name(cls) -> str:
        return 'SGR'


def build(*args: str | int | SequenceSGR) -> SequenceSGR:
    """
    Create new ``SequenceSGR`` with specified ``args`` as params.

    Resulting sequence param order is same as an argument order.

    Each sequence param can be specified as:
      - string key (see `pytermor.span`)
      - integer param value (see `pytermor.intcode`)
      - existing `SequenceSGR` instance (params will be extracted).
    """

    result: List[int] = []

    for arg in args:
        if isinstance(arg, str):
            arg_mapped = arg.upper()
            resolved_param = getattr(intcode, arg_mapped, None)
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


def color_indexed(color: int, bg: bool = False) -> SequenceSGR:
    """
    Wrapper for creation of `SequenceSGR` that sets foreground
    (or background) to one of 256-color pallete value.

    :param color: Index of color in the pallete, from *0* to *255* incl.
    :param bg:    Set to *true* to change the background color
                  (default is foreground).
    :return:      SequenceSGR with required params.
    """

    _validate_extended_color(color)
    key_code = intcode.BG_COLOR_EXTENDED if bg else intcode.COLOR_EXTENDED
    return SequenceSGR(key_code, intcode.EXTENDED_MODE_256, color)


def color_rgb(r: int, g: int, b: int, bg: bool = False) -> SequenceSGR:
    """
    Wrapper for creation of `SequenceSGR` operating in TrueColor mode (16M).

    For example, sequence with ``#FF3300`` color can be created as:
        ``color_rgb(255, 51, 0)``

    :param r:  Red channel value, from *0* to *255* incl.
    :param g:  Blue channel value, from *0* to *255* incl.
    :param b:  Green channel value, from *0* to *255* incl.
    :param bg: Set to *true* to change the background color
               (default is foreground).
    :return:   SequenceSGR with required params.
    """

    [_validate_extended_color(color) for color in [r, g, b]]
    key_code = intcode.BG_COLOR_EXTENDED if bg else intcode.COLOR_EXTENDED
    return SequenceSGR(key_code, intcode.EXTENDED_MODE_RGB, r, g, b)


def _validate_extended_color(value: int):
    if value < 0 or value > 255:
        raise ValueError(f'Invalid color value: {value}; valid values are 0-255 inclusive')


# ---------------------------------------------------------------------------
# SequenceSGR presets
# ---------------------------------------------------------------------------

NOOP = SequenceSGR()
"""
Special sequence in case where you *have to* provide one or
another SGR, but do not want anything to be actually printed. 

- ``NOOP.print()`` returns empty string.
- ``NOOP.params()`` returns empty list.

.. versionadded:: 1.8
"""

RESET = SequenceSGR(intcode.RESET)  #:

# attributes
BOLD = SequenceSGR(intcode.BOLD)  #:
DIM = SequenceSGR(intcode.DIM)  #:
ITALIC = SequenceSGR(intcode.ITALIC)  #:
UNDERLINED = SequenceSGR(intcode.UNDERLINED)  #:
BLINK_SLOW = SequenceSGR(intcode.BLINK_SLOW)  #:
BLINK_FAST = SequenceSGR(intcode.BLINK_FAST)  #:
INVERSED = SequenceSGR(intcode.INVERSED)  #:
HIDDEN = SequenceSGR(intcode.HIDDEN)  #:
CROSSLINED = SequenceSGR(intcode.CROSSLINED)  #:
DOUBLE_UNDERLINED = SequenceSGR(intcode.DOUBLE_UNDERLINED)  #:
OVERLINED = SequenceSGR(intcode.OVERLINED)  #:

NO_BOLD_DIM = SequenceSGR(intcode.NO_BOLD_DIM)  #:
ITALIC_OFF = SequenceSGR(intcode.ITALIC_OFF)  #:
UNDERLINED_OFF = SequenceSGR(intcode.UNDERLINED_OFF)  #:
BLINK_OFF = SequenceSGR(intcode.BLINK_OFF)  #:
INVERSED_OFF = SequenceSGR(intcode.INVERSED_OFF)  #:
HIDDEN_OFF = SequenceSGR(intcode.HIDDEN_OFF)  #:
CROSSLINED_OFF = SequenceSGR(intcode.CROSSLINED_OFF)  #:
OVERLINED_OFF = SequenceSGR(intcode.OVERLINED_OFF)  #:

# text colors
BLACK = SequenceSGR(intcode.BLACK)  #:
RED = SequenceSGR(intcode.RED)  #:
GREEN = SequenceSGR(intcode.GREEN)  #:
YELLOW = SequenceSGR(intcode.YELLOW)  #:
BLUE = SequenceSGR(intcode.BLUE)  #:
MAGENTA = SequenceSGR(intcode.MAGENTA)  #:
CYAN = SequenceSGR(intcode.CYAN)  #:
WHITE = SequenceSGR(intcode.WHITE)  #:
# code.COLOR_EXTENDED is handled by color_indexed()  #:
COLOR_OFF = SequenceSGR(intcode.COLOR_OFF)  #:

# background colors
BG_BLACK = SequenceSGR(intcode.BG_BLACK)  #:
BG_RED = SequenceSGR(intcode.BG_RED)  #:
BG_GREEN = SequenceSGR(intcode.BG_GREEN)  #:
BG_YELLOW = SequenceSGR(intcode.BG_YELLOW)  #:
BG_BLUE = SequenceSGR(intcode.BG_BLUE)  #:
BG_MAGENTA = SequenceSGR(intcode.BG_MAGENTA)  #:
BG_CYAN = SequenceSGR(intcode.BG_CYAN)  #:
BG_WHITE = SequenceSGR(intcode.BG_WHITE)  #:
# code.BG_COLOR_EXTENDED is handled by color_indexed()  #:
BG_COLOR_OFF = SequenceSGR(intcode.BG_COLOR_OFF)  #:

# high intensity text colors
GRAY = SequenceSGR(intcode.GRAY)  #:
HI_RED = SequenceSGR(intcode.HI_RED)  #:
HI_GREEN = SequenceSGR(intcode.HI_GREEN)  #:
HI_YELLOW = SequenceSGR(intcode.HI_YELLOW)  #:
HI_BLUE = SequenceSGR(intcode.HI_BLUE)  #:
HI_MAGENTA = SequenceSGR(intcode.HI_MAGENTA)  #:
HI_CYAN = SequenceSGR(intcode.HI_CYAN)  #:
HI_WHITE = SequenceSGR(intcode.HI_WHITE)  #:

# high intensity background colors
BG_GRAY = SequenceSGR(intcode.BG_GRAY)  #:
BG_HI_RED = SequenceSGR(intcode.BG_HI_RED)  #:
BG_HI_GREEN = SequenceSGR(intcode.BG_HI_GREEN)  #:
BG_HI_YELLOW = SequenceSGR(intcode.BG_HI_YELLOW)  #:
BG_HI_BLUE = SequenceSGR(intcode.BG_HI_BLUE)  #:
BG_HI_MAGENTA = SequenceSGR(intcode.BG_HI_MAGENTA)  #:
BG_HI_CYAN = SequenceSGR(intcode.BG_HI_CYAN)  #:
BG_HI_WHITE = SequenceSGR(intcode.BG_HI_WHITE)  #:

# rarely supported
# 10-20: font selection
#    50: disable proportional spacing
#    51: framed
#    52: encircled
#    54: neither framed nor encircled
# 58-59: underline color
# 60-65: ideogram attributes
# 73-75: superscript and subscript
