# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""
Module contains definitions for low-level ANSI escape sequences handling.

Each preset defined below is a valid argument for :class:`.Span` and
:class:`.SequenceSGR` default constructors (case-insensitive)::

    Span(sequence.BG_GREEN, sequence.UNDERLINED)

.. testsetup:: *

    from pytermor.sequence import build, SequenceSGR, NOOP, HI_CYAN, UNDERLINED

"""
from __future__ import annotations

from abc import ABCMeta, abstractmethod
from copy import copy
from typing import List, Any, Dict, Tuple

from . import intcode


def build(*args: str | int | SequenceSGR) -> SequenceSGR:
    """
    Create new `SequenceSGR` with specified ``args`` as params.

    Resulting sequence param order is same as an argument order.

    Each sequence param can be specified as:
      - string key (see :mod:`.span`)
      - integer param value (from :mod:`.intcode`)
      - existing ``SequenceSGR`` instance (params will be extracted).

    Examples:

    .. doctest::

        >>> build('yellow', 'bold')
        SGR[33;1]
        >>> build(91, 7)
        SGR[91;7]
        >>> build(HI_CYAN, UNDERLINED)
        SGR[96;4]
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

    :param color: Index of the color in the pallete, 0 -- 255.
    :param bg:    Set to *True* to change the background color
                  (default is foreground).
    :return:      `SequenceSGR` with required params.
    """

    _validate_extended_color(color)
    key_code = intcode.BG_COLOR_EXTENDED if bg else intcode.COLOR_EXTENDED
    return SequenceSGR(key_code, intcode._EXTENDED_MODE_256, color)


def color_rgb(r: int, g: int, b: int, bg: bool = False) -> SequenceSGR:
    """
    Wrapper for creation of `SequenceSGR` operating in True Color mode (16M).
    Valid values for *r*, *g* and *b* are in range [0; 255]. This range
    linearly translates into [``0x00``; ``0xFF``] for each channel. The result
    value is composed as ``#RRGGBB``. For example, sequence with color of
    ``#FF3300`` can be created with::

        color_rgb(255, 51, 0)

    :param r:  Red channel value, 0 -- 255.
    :param g:  Blue channel value, 0 -- 255.
    :param b:  Green channel value, 0 -- 255.
    :param bg: Set to *True* to change the background color
               (default is foreground).
    :return:   `SequenceSGR` with required params.
    """

    [_validate_extended_color(color) for color in [r, g, b]]
    key_code = intcode.BG_COLOR_EXTENDED if bg else intcode.COLOR_EXTENDED
    return SequenceSGR(key_code, intcode._EXTENDED_MODE_RGB, r, g, b)


def _validate_extended_color(value: int):
    if value < 0 or value > 255:
        raise ValueError(f'Invalid color value: {value}; valid values are 0-255 inclusive')


class _Sequence(metaclass=ABCMeta):
    """
    Common ancestor of all possible escape sequenes.
    """
    def __init__(self, *params: int):
        self._params: List[int] = [max(0, int(p)) for p in params]

    @abstractmethod
    def encode(self) -> str:
        """
        Build up actual byte sequence and return
        as an ASCII-encoded string.
        """
        raise NotImplementedError

    @property
    def params(self) -> List[int]:
        """ Return internal params as array. """
        return self._params

    @classmethod
    @abstractmethod
    def _short_class_name(cls): raise NotImplementedError

    def __eq__(self, other: _Sequence):
        if type(self) != type(other):
            return False
        return self._params == other._params

    def __repr__(self):
        return f'{self._short_class_name()}[{";".join([str(p) for p in self._params])}]'


class _SequenceCSI(_Sequence, metaclass=ABCMeta):
    """
    Class representing CSI-type ANSI escape sequence. All subtypes of this
    sequence have something in common -- all of them start with :kbd:`\\e[`.
    """
    _CONTROL_CHARACTER = '\x1b'
    _INTRODUCER = '['
    _SEPARATOR = ';'

    def __init__(self, *params: int):
        super(_SequenceCSI, self).__init__(*params)

    def __str__(self) -> str:
        return self.encode()

    @classmethod
    def regexp(cls) -> str:
        return f'\\x1b\\[[0-9;]*{cls._terminator()}'

    @classmethod
    @abstractmethod
    def _terminator(cls) -> str: raise NotImplementedError


class SequenceSGR(_SequenceCSI, metaclass=ABCMeta):
    """
    Class representing SGR-type escape sequence with varying amount of parameters.

    `SequenceSGR` with zero params was specifically implemented to
    translate into empty string and not into :kbd:`\e[m`, which would have
    made sense, but also would be very entangling, as this sequence is
    equivalent of :kbd:`\e[0m` -- hard reset sequence. The empty-string-sequence
    is predefined as :data:`.NOOP`.

    It's possible to add of one SGR sequence to another:

    .. doctest::

        >>> SequenceSGR(31) + SequenceSGR(1) == SequenceSGR(31, 1)
        True

    """
    _TERMINATOR = 'm'

    def encode(self) -> str:
        if len(self._params) == 0:  # NOOP
            return ''

        params = self._params
        if params == [0]:  # \e[0m <=> \em, saving 1 byte
            params = []

        return (self._CONTROL_CHARACTER +
                self._INTRODUCER +
                self._SEPARATOR.join([str(param) for param in params]) +
                self._TERMINATOR)

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


class _SgrPairityRegistry:
    def __init__(self):
        self._code_to_breaker_map: Dict[int|Tuple[int, ...], SequenceSGR] = dict()
        self._complex_code_def: Dict[int|Tuple[int, ...], int] = dict()
        self._complex_code_max_len: int = 0

    def register_single(self, starter_code: int | Tuple[int, ...], breaker_code: int):
        if starter_code in self._code_to_breaker_map:
            raise RuntimeError(f'Conflict: SGR code {starter_code} already has a registered breaker')

        self._code_to_breaker_map[starter_code] = SequenceSGR(breaker_code)

    def register_complex(self, starter_codes: Tuple[int, ...], param_len: int, breaker_code: int):
        self.register_single(starter_codes, breaker_code)

        if starter_codes in self._complex_code_def:
            raise RuntimeError(f'Conflict: SGR complex {starter_codes} already has a registered breaker')

        self._complex_code_def[starter_codes] = param_len
        self._complex_code_max_len = max(self._complex_code_max_len, len(starter_codes) + param_len)

    def get_closing_seq(self, opening_seq: SequenceSGR) -> SequenceSGR:
        closing_seq_params: List[int] = []
        opening_params = copy(opening_seq.params)

        while len(opening_params):
            key_params: int|Tuple[int, ...]|None = None

            for complex_len in range(1, min(len(opening_params), self._complex_code_max_len + 1)):
                opening_complex_suggestion = tuple(opening_params[:complex_len])

                if opening_complex_suggestion in self._complex_code_def:
                    key_params = opening_complex_suggestion
                    complex_total_len = complex_len + self._complex_code_def[opening_complex_suggestion]
                    opening_params = opening_params[complex_total_len:]
                    break

            if key_params is None:
                key_params = opening_params.pop(0)
            if key_params not in self._code_to_breaker_map:
                continue

            closing_seq_params.extend(self._code_to_breaker_map[key_params].params)

        return build(*closing_seq_params)


# -- SequenceSGR presets ------------------------------------------------------

NOOP = SequenceSGR()
"""
Special sequence in case where you *have to* provide one or
another SGR, but do not want any control sequence to be actually included. 

- ``NOOP.encode()`` returns empty string.
- ``NOOP.params`` returns empty list.

.. doctest::

    >>> NOOP.encode()
    ''
    >>> NOOP.params
    []

.. versionadded:: 1.8
"""

RESET = SequenceSGR(intcode.RESET)
"""
Resets all attributes and colors.
"""

# attributes
BOLD = SequenceSGR(intcode.BOLD)
DIM = SequenceSGR(intcode.DIM)
ITALIC = SequenceSGR(intcode.ITALIC)
UNDERLINED = SequenceSGR(intcode.UNDERLINED)
BLINK_SLOW = SequenceSGR(intcode.BLINK_SLOW)
BLINK_FAST = SequenceSGR(intcode.BLINK_FAST)
INVERSED = SequenceSGR(intcode.INVERSED)
HIDDEN = SequenceSGR(intcode.HIDDEN)
CROSSLINED = SequenceSGR(intcode.CROSSLINED)
DOUBLE_UNDERLINED = SequenceSGR(intcode.DOUBLE_UNDERLINED)
OVERLINED = SequenceSGR(intcode.OVERLINED)

NO_BOLD_DIM = SequenceSGR(intcode.NO_BOLD_DIM)  # there is no separate sequence for disabling either of BOLD or DIM while keeping the other
ITALIC_OFF = SequenceSGR(intcode.ITALIC_OFF)
UNDERLINED_OFF = SequenceSGR(intcode.UNDERLINED_OFF)
BLINK_OFF = SequenceSGR(intcode.BLINK_OFF)
INVERSED_OFF = SequenceSGR(intcode.INVERSED_OFF)
HIDDEN_OFF = SequenceSGR(intcode.HIDDEN_OFF)
CROSSLINED_OFF = SequenceSGR(intcode.CROSSLINED_OFF)
OVERLINED_OFF = SequenceSGR(intcode.OVERLINED_OFF)

# text colors
BLACK = SequenceSGR(intcode.BLACK)
RED = SequenceSGR(intcode.RED)
GREEN = SequenceSGR(intcode.GREEN)
YELLOW = SequenceSGR(intcode.YELLOW)
BLUE = SequenceSGR(intcode.BLUE)
MAGENTA = SequenceSGR(intcode.MAGENTA)
CYAN = SequenceSGR(intcode.CYAN)
WHITE = SequenceSGR(intcode.WHITE)
# code.COLOR_EXTENDED is handled by color_indexed()
COLOR_OFF = SequenceSGR(intcode.COLOR_OFF)

# background colors
BG_BLACK = SequenceSGR(intcode.BG_BLACK)
BG_RED = SequenceSGR(intcode.BG_RED)
BG_GREEN = SequenceSGR(intcode.BG_GREEN)
BG_YELLOW = SequenceSGR(intcode.BG_YELLOW)
BG_BLUE = SequenceSGR(intcode.BG_BLUE)
BG_MAGENTA = SequenceSGR(intcode.BG_MAGENTA)
BG_CYAN = SequenceSGR(intcode.BG_CYAN)
BG_WHITE = SequenceSGR(intcode.BG_WHITE)
# code.BG_COLOR_EXTENDED is handled by color_indexed()
BG_COLOR_OFF = SequenceSGR(intcode.BG_COLOR_OFF)

# high intensity text colors
GRAY = SequenceSGR(intcode.GRAY)
HI_RED = SequenceSGR(intcode.HI_RED)
HI_GREEN = SequenceSGR(intcode.HI_GREEN)
HI_YELLOW = SequenceSGR(intcode.HI_YELLOW)
HI_BLUE = SequenceSGR(intcode.HI_BLUE)
HI_MAGENTA = SequenceSGR(intcode.HI_MAGENTA)
HI_CYAN = SequenceSGR(intcode.HI_CYAN)
HI_WHITE = SequenceSGR(intcode.HI_WHITE)

# high intensity background colors
BG_GRAY = SequenceSGR(intcode.BG_GRAY)
BG_HI_RED = SequenceSGR(intcode.BG_HI_RED)
BG_HI_GREEN = SequenceSGR(intcode.BG_HI_GREEN)
BG_HI_YELLOW = SequenceSGR(intcode.BG_HI_YELLOW)
BG_HI_BLUE = SequenceSGR(intcode.BG_HI_BLUE)
BG_HI_MAGENTA = SequenceSGR(intcode.BG_HI_MAGENTA)
BG_HI_CYAN = SequenceSGR(intcode.BG_HI_CYAN)
BG_HI_WHITE = SequenceSGR(intcode.BG_HI_WHITE)

# rarely supported
# 10-20: font selection
#    50: disable proportional spacing
#    51: framed
#    52: encircled
#    54: neither framed nor encircled
# 58-59: underline color
# 60-65: ideogram attributes
# 73-75: superscript and subscript


# -- Openinng <-> closing sequences matches -----------------------------------

sgr_parity_registry = _SgrPairityRegistry()

sgr_parity_registry.register_single(intcode.BOLD, intcode.NO_BOLD_DIM)
sgr_parity_registry.register_single(intcode.DIM, intcode.NO_BOLD_DIM)
sgr_parity_registry.register_single(intcode.ITALIC, intcode.ITALIC_OFF)
sgr_parity_registry.register_single(intcode.UNDERLINED, intcode.UNDERLINED_OFF)
sgr_parity_registry.register_single(intcode.DOUBLE_UNDERLINED, intcode.UNDERLINED_OFF)
sgr_parity_registry.register_single(intcode.BLINK_SLOW, intcode.BLINK_OFF)
sgr_parity_registry.register_single(intcode.BLINK_FAST, intcode.BLINK_OFF)
sgr_parity_registry.register_single(intcode.INVERSED, intcode.INVERSED_OFF)
sgr_parity_registry.register_single(intcode.HIDDEN, intcode.HIDDEN_OFF)
sgr_parity_registry.register_single(intcode.CROSSLINED, intcode.CROSSLINED_OFF)
sgr_parity_registry.register_single(intcode.OVERLINED, intcode.OVERLINED_OFF)

for c in [intcode.BLACK, intcode.RED, intcode.GREEN, intcode.YELLOW, intcode.BLUE, intcode.MAGENTA, intcode.CYAN, intcode.WHITE, intcode.GRAY,
          intcode.HI_RED, intcode.HI_GREEN, intcode.HI_YELLOW, intcode.HI_BLUE, intcode.HI_MAGENTA, intcode.HI_CYAN, intcode.HI_WHITE]:
    sgr_parity_registry.register_single(c, intcode.COLOR_OFF)

for c in [intcode.BG_BLACK, intcode.BG_RED, intcode.BG_GREEN, intcode.BG_YELLOW, intcode.BG_BLUE, intcode.BG_MAGENTA, intcode.BG_CYAN,
          intcode.BG_WHITE, intcode.BG_GRAY, intcode.BG_HI_RED, intcode.BG_HI_GREEN, intcode.BG_HI_YELLOW, intcode.BG_HI_BLUE,
          intcode.BG_HI_MAGENTA, intcode.BG_HI_CYAN, intcode.BG_HI_WHITE]:
    sgr_parity_registry.register_single(c, intcode.BG_COLOR_OFF)


sgr_parity_registry.register_complex((intcode.COLOR_EXTENDED, 5), 1, intcode.COLOR_OFF)
sgr_parity_registry.register_complex((intcode.COLOR_EXTENDED, 2), 3, intcode.COLOR_OFF)
sgr_parity_registry.register_complex((intcode.BG_COLOR_EXTENDED, 5), 1, intcode.BG_COLOR_OFF)
sgr_parity_registry.register_complex((intcode.BG_COLOR_EXTENDED, 2), 3, intcode.BG_COLOR_OFF)
