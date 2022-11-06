# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""
Module contains definitions for low-level ANSI escape sequences building.
Can be used for creating a variety of sequences including:

    - :abbr:`SGR (Select Graphic Rendition)` sequences (text coloring, background
    - :abbr:`CSI (Control Sequence Introducer)` sequences (cursor management,
      selective screen cleraing);
    - :abbr:`OSC (Operating System Command)` sequences (varoius system commands).

The module doesn't distinguish "single-instruction" sequences from several
ones merged together, e.g. ``Style(fg='red', bold=True)`` produces only one
opening SequenceSGR instance:

>>> SequenceSGR(IntCode.BOLD, IntCode.RED).assemble()
'\\x1b[1;31m'

...although generally speaking it is two of them (:kbd:`ESC[1m` and
:kbd:`ESC[31m`). However, the module can automatically match terminating
sequences for any form of input SGRs and translate it to specified format.

**XTerm Control Sequences**
    https://invisible-island.net/xterm/ctlseqs/ctlseqs.html

**ECMA-48 specification**
    https://www.ecma-international.org/publications-and-standards/standards/ecma-48/

.. testsetup:: *

    import typing as t
    from pytermor.ansi import *

"""
from __future__ import annotations

from abc import abstractmethod, ABC
from copy import copy
import enum
import typing as t

from .common import ConflictError


class Sequence(t.Sized, ABC):
    """
    Abstract ancestor of all escape sequences.
    """

    _ESC_CHARACTER: str = "\x1b"
    _SEPARATOR: str = ";"
    _INTRODUCER: str
    _TERMINATOR: str

    def __init__(self, *params: int | str):
        self._params: t.List[int | str] = [*params]

    def assemble(self) -> str:
        """
        Build up actual byte sequence and return
        as an ASCII-encoded string.
        """
        return self._ESC_CHARACTER + \
               self._INTRODUCER + \
               self._SEPARATOR.join([str(param) for param in self.params]) + \
               self._TERMINATOR

    @property
    def params(self) -> t.List[int | str]:
        """
        Return internal params as array.
        """
        return self._params

    @classmethod
    @abstractmethod
    def _short_class_name(cls):
        raise NotImplementedError

    def __str__(self) -> str:
        return self.assemble()

    def __len__(self) -> int:
        return 0

    def __eq__(self, other: Sequence):
        if type(self) != type(other):
            return False
        return self._params == other._params

    def __repr__(self):
        params = ",".join([str(p) for p in self._params])
        if len(self._params) == 0:
            params = "NOP"
        return f"<{self._short_class_name()} [{params}]>"


class SequenceFe(Sequence, ABC):
    """
    Wide range of sequence types that includes CSI, OSC and more.

    All subtypes of this sequence start with :kbd:`ESC` plus ASCII byte
    from ``0x40`` to ``0x5F`` (:kbd:`@[\\\\]_^` and capital letters
    :kbd:`A`-:kbd:`Z`).
    """


class SequenceST(SequenceFe):
    """
    String Terminator sequence (ST). Terminates strings in other control
    sequences. Encoded as :kbd:`ESC\\\\` (``0x1B`` ``0x5C``).
    """
    _INTRODUCER = '\\'

    def assemble(self) -> str:
        return self._ESC_CHARACTER + self._INTRODUCER

    @classmethod
    def _short_class_name(cls) -> str:
        return "ST"


class SequenceOSC(SequenceFe):
    """
    Operating System Command sequence (OSC). Starts a control string for the
    operating system to use. Encoded as :kbd:`ESC]` plus params separated by
    :kbd:`;`, and terminated with `SequenceST`.
    """
    _INTRODUCER = ']'
    _TERMINATOR = SequenceST().assemble()

    @classmethod
    def init_hyperlink(cls, url: str) -> SequenceOSC:
        return SequenceOSC(IntCode.HYPERLINK, "", url)

    @classmethod
    def _short_class_name(cls):
        return "OSC"


class SequenceCSI(SequenceFe):
    """
    Class representing CSI-type ANSI escape sequence. All subtypes
    of this sequence start with :kbd:`ESC[`.

    Sequences of this type are used to control text formatting,
    change cursor position, erase screen and more.
    """
    _INTRODUCER = '['

    def __init__(self, terminator: str, *params: int):
        """

        :param terminator:
        :param params:
        """
        self._terminator = terminator
        super().__init__(*params)

    @classmethod
    def init_cursor_horizontal_absolute(cls, column: int = 1) -> SequenceCSI:
        """
        Set cursor x-coordinate to ``column``.

        :param column:
        """
        return SequenceCSI("G", column)

    @classmethod
    def init_erase_in_line(cls, mode: int = 0) -> SequenceCSI:
        """
        Erase part of the line. If ``mode`` is 0, clear from cursor to the end
        of the line. If ``mode`` is 1, clear from cursor to beginning of the line.
        If ``mode`` is 2, clear the entire line. Cursor position does not change.
        """
        if not (0 <= mode <= 2):
            raise ValueError(f"Invalid mode: {mode}, expected [0;2]")
        return SequenceCSI("K", mode)

    def regexp(self) -> str:
        return f"\\x1b\\[[0-9;]*{self._terminator}"

    def assemble(self) -> str:
        return (
            self._ESC_CHARACTER
            + self._INTRODUCER
            + self._SEPARATOR.join([str(param) for param in self.params])
            + self._terminator
        )

    @classmethod
    def _short_class_name(cls):
        return "CSI"


class SequenceSGR(SequenceCSI):
    """
    Class representing SGR-type escape sequence with varying amount of parameters.
    SGR sequences allow to change the color of text or/and terminal background
    (in 3 different color spaces) as well as set decorate text with italic style,
    underlining, overlining, cross-lining, making it bold or blinking etc.

    .. note ::
        `SequenceSGR` with zero params was specifically implemented to
        translate into empty string and not into :kbd:`ESC[m`, which would have
        made sense, but also would be entangling, as this sequence is the equivalent
        of :kbd:`ESC[0m` -- hard reset sequence. The empty-string-sequence is
        predefined at module level as `NOOP_SEQ`.

    When cast to *str*, as all other sequences, invokes `assemble()` method
    and transforms into encoded control sequence string. It's possible to add
    of one SGR sequence to another, resulting in a new one with merged params
    (see examples).

        >>> SequenceSGR(91, SequenceSGR(7))
        SGR[91;7]
        >>> SequenceSGR(IntCode.HI_CYAN, 'underlined')
        SGR[96;4]
        >>> SequenceSGR(31) + SequenceSGR(1) == SequenceSGR(31, 1)
        True

    :param args:  Sequence params. Resulting param order is the same as an
                  argument order. Each argument can be specified as:

                     - *str* -- any of `IntCode` names, case-insensitive
                     - *int* -- `IntCode` instance or plain integer
                     - `SequenceSGR` instance (params will be extracted)
    """

    _TERMINATOR = "m"

    def __init__(self, *args: str | int | SequenceSGR):
        result: t.List[int] = []

        for arg in args:
            if isinstance(arg, str):
                result.append(IntCode.resolve(arg).value)
            elif isinstance(arg, IntCode):
                result.append(arg.value)  # to avoid casting it later in assemble()
            elif isinstance(arg, int):
                result.append(arg)
            elif isinstance(arg, SequenceSGR):
                result.extend(arg.params)
            else:
                raise TypeError(f"Invalid argument type: {arg!r})")

        result = [max(0, p) for p in result]
        super().__init__(self._TERMINATOR, *result)

    @classmethod
    def new_color_256(cls, code: int, bg: bool = False) -> SequenceSGR:
        """
        Wrapper for creation of `SequenceSGR` that sets foreground
        (or background) to one of 256-color palette value.

        :param code:  Index of the color in the palette, 0 -- 255.
        :param bg:    Set to *True* to change the background color
                      (default is foreground).
        :returns:     `SequenceSGR` with required params.
        """

        cls._validate_extended_color(code)
        key_code = IntCode.BG_COLOR_EXTENDED if bg else IntCode.COLOR_EXTENDED
        return SequenceSGR(key_code, IntCode.EXTENDED_MODE_256, code)

    @classmethod
    def new_color_rgb(cls, r: int, g: int, b: int, bg: bool = False) -> SequenceSGR:
        """
        Wrapper for creation of `SequenceSGR` operating in True Color mode (16M).
        Valid values for *r*, *g* and *b* are in range [0; 255]. This range
        linearly translates into [``0x00``; ``0xFF``] for each channel. The result
        value is composed as ``#RRGGBB``. For example, sequence with color of
        ``#FF3300`` can be created with::

            SequenceSGR.new_color_rgb(255, 51, 0)

        :param r:  Red channel value, 0 -- 255.
        :param g:  Blue channel value, 0 -- 255.
        :param b:  Green channel value, 0 -- 255.
        :param bg: Set to *True* to change the background color
                   (default is foreground).
        :return:   `SequenceSGR` with required params.
        """

        [cls._validate_extended_color(color) for color in [r, g, b]]
        key_code = IntCode.BG_COLOR_EXTENDED if bg else IntCode.COLOR_EXTENDED
        return SequenceSGR(key_code, IntCode.EXTENDED_MODE_RGB, r, g, b)

    def assemble(self) -> str:
        if len(self._params) == 0:  # NOOP
            return ""

        params = self._params
        if params == [0]:  # \x1b[0m <=> \x1b[m, saving 1 byte
            params = []

        return (
            self._ESC_CHARACTER
            + self._INTRODUCER
            + self._SEPARATOR.join([str(param) for param in params])
            + self._TERMINATOR
        )

    @property
    def params(self) -> t.List[int]:
        """
        :return: Sequence params as integers or `IntCode` instances.
        """
        return super().params

    def __hash__(self) -> int:
        return int.from_bytes(self.assemble().encode(), byteorder="big")

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

    @staticmethod
    def _ensure_sequence(subject: t.Any):
        if not isinstance(subject, SequenceSGR):
            raise TypeError(f"Expected SequenceSGR, got {type(subject)}")

    @staticmethod
    def _validate_extended_color(value: int):
        if value < 0 or value > 255:
            raise ValueError(
                f"Invalid color value: expected range [0-255], got: {value}"
            )

    @classmethod
    def _short_class_name(cls) -> str:
        return "SGR"


NOOP_SEQ = SequenceSGR()
"""
Special sequence in case you *have to* provide one or another SGR, but do 
not want any control sequences to be actually included in the output. 
``NOOP_SEQ.assemble()`` returns empty string, ``NOOP_SEQ.params`` 
returns empty list.

>>> pt.NOOP_SEQ.assemble()
''
>>> pt.NOOP_SEQ.params
[]
"""


class IntCode(enum.IntEnum):
    """
    Complete or almost complete list of reliably working SGR param integer codes.
    Fully interchangeable with plain *int*\-s. Suitable for `SequenceSGR`
    default constructor.
    """

    @classmethod
    def resolve(cls, name: str) -> IntCode:
        name_norm = name.upper()
        try:
            instance = cls[name_norm]
        except KeyError as e:
            e.args = (f"Int code '{name_norm}' (<- '{name}') does not exist",)
            raise e
        return instance

    def __repr__(self) -> str:
        return f"<{self.value}|{self.name}>"

    # -- SGR: default attributes and colors -----------------------------------

    RESET = 0  # hard reset code
    BOLD = 1
    DIM = 2
    ITALIC = 3
    UNDERLINED = 4
    BLINK_SLOW = 5
    BLINK_FAST = 6
    INVERSED = 7
    HIDDEN = 8
    CROSSLINED = 9
    DOUBLE_UNDERLINED = 21
    OVERLINED = 53
    BOLD_DIM_OFF = 22  # there is no separate sequence for disabling either
    ITALIC_OFF = 23  # of BOLD or DIM while keeping the other
    UNDERLINED_OFF = 24
    BLINK_OFF = 25
    INVERSED_OFF = 27
    HIDDEN_OFF = 28
    CROSSLINED_OFF = 29
    COLOR_OFF = 39
    BG_COLOR_OFF = 49
    OVERLINED_OFF = 55

    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37
    COLOR_EXTENDED = 38  # use new_color_256() and new_color_rgb() instead

    BG_BLACK = 40
    BG_RED = 41
    BG_GREEN = 42
    BG_YELLOW = 43
    BG_BLUE = 44
    BG_MAGENTA = 45
    BG_CYAN = 46
    BG_WHITE = 47
    BG_COLOR_EXTENDED = 48  # use new_color_256() and new_color_rgb() instead

    GRAY = 90
    HI_RED = 91
    HI_GREEN = 92
    HI_YELLOW = 93
    HI_BLUE = 94
    HI_MAGENTA = 95
    HI_CYAN = 96
    HI_WHITE = 97

    BG_GRAY = 100
    BG_HI_RED = 101
    BG_HI_GREEN = 102
    BG_HI_YELLOW = 103
    BG_HI_BLUE = 104
    BG_HI_MAGENTA = 105
    BG_HI_CYAN = 106
    BG_HI_WHITE = 107

    # RARELY SUPPORTED (thus excluded)
    # 10-20: font selection
    #    26: proportional spacing
    #    50: disable proportional spacing
    #    51: framed
    #    52: encircled
    #    54: neither framed nor encircled
    # 58-59: underline color
    # 60-65: ideogram attributes
    # 73-75: superscript and subscript

    # -- SGR: extended modifiers ----------------------------------------------

    EXTENDED_MODE_256 = 5
    EXTENDED_MODE_RGB = 2

    # -- Other sequence classes -----------------------------------------------

    HYPERLINK = 8


class SeqIndex:
    """
    Registry of sequence presets.
    """

    # == SGR ==================================================================

    RESET = SequenceSGR(IntCode.RESET)
    """
    Hard reset sequence.
    """

    # attributes
    BOLD = SequenceSGR(IntCode.BOLD)
    DIM = SequenceSGR(IntCode.DIM)
    ITALIC = SequenceSGR(IntCode.ITALIC)
    UNDERLINED = SequenceSGR(IntCode.UNDERLINED)
    BLINK_SLOW = SequenceSGR(IntCode.BLINK_SLOW)
    BLINK_FAST = SequenceSGR(IntCode.BLINK_FAST)
    BLINK_DEFAULT = BLINK_SLOW
    INVERSED = SequenceSGR(IntCode.INVERSED)
    HIDDEN = SequenceSGR(IntCode.HIDDEN)
    CROSSLINED = SequenceSGR(IntCode.CROSSLINED)
    DOUBLE_UNDERLINED = SequenceSGR(IntCode.DOUBLE_UNDERLINED)
    OVERLINED = SequenceSGR(IntCode.OVERLINED)

    BOLD_DIM_OFF = SequenceSGR(IntCode.BOLD_DIM_OFF)  # there is no separate sequence for
    ITALIC_OFF = SequenceSGR(IntCode.ITALIC_OFF)  # disabling either of BOLD or DIM
    UNDERLINED_OFF = SequenceSGR(IntCode.UNDERLINED_OFF)  # while keeping the other
    BLINK_OFF = SequenceSGR(IntCode.BLINK_OFF)
    INVERSED_OFF = SequenceSGR(IntCode.INVERSED_OFF)
    HIDDEN_OFF = SequenceSGR(IntCode.HIDDEN_OFF)
    CROSSLINED_OFF = SequenceSGR(IntCode.CROSSLINED_OFF)
    OVERLINED_OFF = SequenceSGR(IntCode.OVERLINED_OFF)

    # text colors
    BLACK = SequenceSGR(IntCode.BLACK)
    RED = SequenceSGR(IntCode.RED)
    GREEN = SequenceSGR(IntCode.GREEN)
    YELLOW = SequenceSGR(IntCode.YELLOW)
    BLUE = SequenceSGR(IntCode.BLUE)
    MAGENTA = SequenceSGR(IntCode.MAGENTA)
    CYAN = SequenceSGR(IntCode.CYAN)
    WHITE = SequenceSGR(IntCode.WHITE)
    # code.COLOR_EXTENDED is handled by color_indexed()
    COLOR_OFF = SequenceSGR(IntCode.COLOR_OFF)

    # background colors
    BG_BLACK = SequenceSGR(IntCode.BG_BLACK)
    BG_RED = SequenceSGR(IntCode.BG_RED)
    BG_GREEN = SequenceSGR(IntCode.BG_GREEN)
    BG_YELLOW = SequenceSGR(IntCode.BG_YELLOW)
    BG_BLUE = SequenceSGR(IntCode.BG_BLUE)
    BG_MAGENTA = SequenceSGR(IntCode.BG_MAGENTA)
    BG_CYAN = SequenceSGR(IntCode.BG_CYAN)
    BG_WHITE = SequenceSGR(IntCode.BG_WHITE)
    # code.BG_COLOR_EXTENDED is handled by color_indexed()
    BG_COLOR_OFF = SequenceSGR(IntCode.BG_COLOR_OFF)

    # high intensity text colors
    GRAY = SequenceSGR(IntCode.GRAY)
    HI_RED = SequenceSGR(IntCode.HI_RED)
    HI_GREEN = SequenceSGR(IntCode.HI_GREEN)
    HI_YELLOW = SequenceSGR(IntCode.HI_YELLOW)
    HI_BLUE = SequenceSGR(IntCode.HI_BLUE)
    HI_MAGENTA = SequenceSGR(IntCode.HI_MAGENTA)
    HI_CYAN = SequenceSGR(IntCode.HI_CYAN)
    HI_WHITE = SequenceSGR(IntCode.HI_WHITE)

    # high intensity background colors
    BG_GRAY = SequenceSGR(IntCode.BG_GRAY)
    BG_HI_RED = SequenceSGR(IntCode.BG_HI_RED)
    BG_HI_GREEN = SequenceSGR(IntCode.BG_HI_GREEN)
    BG_HI_YELLOW = SequenceSGR(IntCode.BG_HI_YELLOW)
    BG_HI_BLUE = SequenceSGR(IntCode.BG_HI_BLUE)
    BG_HI_MAGENTA = SequenceSGR(IntCode.BG_HI_MAGENTA)
    BG_HI_CYAN = SequenceSGR(IntCode.BG_HI_CYAN)
    BG_HI_WHITE = SequenceSGR(IntCode.BG_HI_WHITE)

    # == OSC ==================================================================

    HYPERLINK = SequenceOSC(IntCode.HYPERLINK)


COLORS = list(range(30, 39))
BG_COLORS = list(range(40, 49))
HI_COLORS = list(range(90, 98))
BG_HI_COLORS = list(range(100, 108))
ALL_COLORS = COLORS + BG_COLORS + HI_COLORS + BG_HI_COLORS


class _SgrPairityRegistry:
    """
    Internal class responsible for correct SGRs termination.
    """

    _code_to_breaker_map: t.Dict[int | t.Tuple[int, ...], SequenceSGR] = dict()
    _complex_code_def: t.Dict[int | t.Tuple[int, ...], int] = dict()
    _complex_code_max_len: int = 0

    def __init__(self):
        _regulars = [
            (IntCode.BOLD, IntCode.BOLD_DIM_OFF),
            (IntCode.DIM, IntCode.BOLD_DIM_OFF),
            (IntCode.ITALIC, IntCode.ITALIC_OFF),
            (IntCode.UNDERLINED, IntCode.UNDERLINED_OFF),
            (IntCode.DOUBLE_UNDERLINED, IntCode.UNDERLINED_OFF),
            (IntCode.BLINK_SLOW, IntCode.BLINK_OFF),
            (IntCode.BLINK_FAST, IntCode.BLINK_OFF),
            (IntCode.INVERSED, IntCode.INVERSED_OFF),
            (IntCode.HIDDEN, IntCode.HIDDEN_OFF),
            (IntCode.CROSSLINED, IntCode.CROSSLINED_OFF),
            (IntCode.OVERLINED, IntCode.OVERLINED_OFF),
        ]

        for c in _regulars:
            self._bind_regular(*c)

        for c in [*COLORS, *HI_COLORS]:
            self._bind_regular(c, IntCode.COLOR_OFF)

        for c in [*BG_COLORS, *BG_HI_COLORS]:
            self._bind_regular(c, IntCode.BG_COLOR_OFF)

        self._bind_complex((IntCode.COLOR_EXTENDED, 5), 1, IntCode.COLOR_OFF)
        self._bind_complex((IntCode.COLOR_EXTENDED, 2), 3, IntCode.COLOR_OFF)
        self._bind_complex((IntCode.BG_COLOR_EXTENDED, 5), 1, IntCode.BG_COLOR_OFF)
        self._bind_complex((IntCode.BG_COLOR_EXTENDED, 2), 3, IntCode.BG_COLOR_OFF)

    def _bind_regular(self, starter_code: int | t.Tuple[int, ...], breaker_code: int):
        if starter_code in self._code_to_breaker_map:
            raise ConflictError(
                f"SGR code {starter_code} already has a registered breaker"
            )

        self._code_to_breaker_map[starter_code] = SequenceSGR(breaker_code)

    def _bind_complex(
        self, starter_codes: t.Tuple[int, ...], param_len: int, breaker_code: int
    ):
        self._bind_regular(starter_codes, breaker_code)

        if starter_codes in self._complex_code_def:
            raise ConflictError(
                f"SGR complex {starter_codes} already has a registered breaker"
            )

        self._complex_code_def[starter_codes] = param_len
        self._complex_code_max_len = max(
            self._complex_code_max_len, len(starter_codes) + param_len
        )

    def get_closing_seq(self, opening_seq: SequenceSGR) -> SequenceSGR:
        closing_seq_params: t.List[int] = []
        opening_params = copy(opening_seq.params)

        while len(opening_params):
            key_params: int | t.Tuple[int, ...] | None = None

            for complex_len in range(
                1, min(len(opening_params), self._complex_code_max_len + 1)
            ):
                opening_complex_suggestion = tuple(opening_params[:complex_len])

                if opening_complex_suggestion in self._complex_code_def:
                    key_params = opening_complex_suggestion
                    complex_total_len = (
                        complex_len + self._complex_code_def[opening_complex_suggestion]
                    )
                    opening_params = opening_params[complex_total_len:]
                    break

            if key_params is None:
                key_params = opening_params.pop(0)
            if key_params not in self._code_to_breaker_map:
                continue

            closing_seq_params.extend(self._code_to_breaker_map[key_params].params)

        return SequenceSGR(*closing_seq_params)


_sgr_pairity_registry = _SgrPairityRegistry()


def get_closing_seq(opening_seq: SequenceSGR) -> SequenceSGR:
    return _sgr_pairity_registry.get_closing_seq(opening_seq)
