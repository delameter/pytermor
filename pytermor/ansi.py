# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
"""
Classes for working with ANSI escape sequences on a lower level.
Can be used for creating a variety of sequences including:

    - :abbr:`SGR (Select Graphic Rendition)` sequences (text and background
      coloring, other text formatting and effects);
    - :abbr:`CSI (Control Sequence Introducer)` sequences (cursor management,
      selective screen clearing);
    - :abbr:`OSC (Operating System Command)` sequences (various system commands).

Provides a bunch of ready-to-use sequence makers, as well as core method
`get_closing_seq()` that queries SGR pairs registry and composes "counterpart"
sequence for a specified one: every attribute that the latter modifies, will be
changed back by the one that's being created, while keeping the other attributes
untouched. This method is used by `SgrRenderer` and is essential for nested style
processing, as regular `RESET` sequence cancels all the formatting applied to
the output at the moment it's getting introduced to a terminal emulator, and
is near to impossible to use because of that (at least when there is a need to
perform partial attribute termination, e.g. for overlapping styles rendering).
"""
from __future__ import annotations

import enum
import re
import typing as t
from abc import ABCMeta, abstractmethod
from copy import copy
from enum import unique
from functools import lru_cache, total_ordering
from typing import Any

from .common import get_qname
from .exception import ConflictError, LogicError, ParseError

COLORS = list(range(30, 39))
BG_COLORS = list(range(40, 49))
HI_COLORS = list(range(90, 98))
BG_HI_COLORS = list(range(100, 108))
ALL_COLORS = COLORS + BG_COLORS + HI_COLORS + BG_HI_COLORS


class _ClassMap(t.Dict[str, t.Type["ISequence"]]):
    def add(
        self,
        cls: t.Type[ISequence],
        parents: t.Tuple[type],
        introducer: t.Iterable[str | int],
    ):
        for i in introducer:
            c = i if isinstance(i, str) else chr(i)
            if (existing := self.get(c)) in parents or not existing:
                self[c] = cls
            else:  # pragma: no cover
                raise LogicError(
                    f"Mapping ('{c}' -> {get_qname(existing)}) is already defined. "
                    f"Overwriting of class' mappings is allowed to its' descendants "
                    f"only, while {cls} is not."
                )

    def from_dict(self, groupdict: dict) -> ISequence:
        classifier = (
            groupdict.get("nf_classifier")
            or groupdict.get("st_classifier")
            or groupdict.get("osc_classifier")
            or groupdict.get("csi_classifier")
            or groupdict.get("fe_classifier")
            or groupdict.get("fp_classifier")
            or groupdict.get("fs_classifier")
        )
        if cls := self.get(classifier):
            return cls.from_dict(groupdict)
        raise LogicError(f"Unknown classifier in {groupdict}")  # pragma: no cover


_CLASSMAP = _ClassMap()


def seq_from_dict(groupdict: dict) -> "ISequence":
    return _CLASSMAP.from_dict(groupdict)


class _SequenceMeta(ABCMeta):
    def __new__(
        __mcls: t.Type[t.Type[ISequence]],
        __name: str,
        __bases: t.Tuple[type, ...],
        __namespace: t.Dict[str, Any],
        **kwargs: Any,
    ) -> _SequenceMeta:
        new = super().__new__(__mcls, __name, __bases, __namespace, **kwargs)
        if classifier := getattr(new, "_CLASSIFIER", None):
            _CLASSMAP.add(new, __bases, [classifier])
        elif classifier_range := getattr(new, "_CLASSIFIER_RANGE", None):
            _CLASSMAP.add(new, __bases, [*classifier_range])
        return new


class ISequence(t.Sized, metaclass=_SequenceMeta):
    """
    Abstract ancestor of all escape sequences.
    """

    ESC_CHARACTER = "\x1b"
    PARAM_SEPARATOR = ";"

    def __init__(
        self,
        classifier: str = None,
        interm: str = None,
        final: str = None,
        abbr: str = "ESC*",
    ):
        self._classifier: str | None = classifier
        self._interm: str | None = interm
        self._final: str | None = final

        self._params: list[int] | list[str] | None = None
        self._abbr: str = abbr

    def _assign_params(self, *params: int | str):
        self._params = []
        for param in params:
            if isinstance(param, IntCode):
                self._params.append(param.value)
                continue
            self._params.append(param)

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict) -> ISequence:
        raise NotImplementedError

    @classmethod
    def cast_params(
        cls, data: dict, key: str, require_int: bool
    ) -> t.Iterable[str | int, ...]:
        if not (params_raw := data.get(key)):
            return
        for param_spl in params_raw.split(cls.PARAM_SEPARATOR):
            try:
                yield int(param_spl)
            except ValueError:
                if require_int:
                    raise ParseError(data)
                yield param_spl

    def assemble(self) -> str:
        return (
            self.ESC_CHARACTER
            + (self._classifier or "")
            + self._assemble_params()
            + (self._interm or "")
            + (self._final or "")
        )

    def _assemble_params(self) -> str:
        if not self._params:
            return ""
        return self.PARAM_SEPARATOR.join(map(str, self._params))

    @property
    def params(self) -> list[int] | list[str]:
        return self._params or []

    def __str__(self) -> str:
        return self.assemble()

    def __len__(self) -> int:
        return 0

    def __eq__(self, other: ISequence):
        if type(self) != type(other):  # pragma: no cover
            return False
        return self._params == other._params

    def __repr__(self) -> str:
        params = self.PARAM_SEPARATOR.join(map(str, self._params or []))
        return f"<{self._abbr}[{params}{self._interm or ''}{self._final or ''}]>"


class SequenceNf(ISequence):
    """
    Escape sequences mostly used for ANSI/ISO code-switching mechanisms.

    All **nF**-class sequences start with ``ESC`` plus ASCII byte from
    the range :hex:`0x20-0x2F` (space, ``!``, ``"``, ``#``, ``$``, ``%``,
    ``&``, ``'``, ``(``, ``)``, ``*``, ``+``, ``,``, ``-``, ``.``, ``/``).
    """

    _CLASSIFIER_RANGE = range(0x20, 0x30)

    def __init__(
        self, classifier: str, final: str, interm: str = None, abbr: str = "nF"
    ):
        """
        :param interm: intermediate bytes :hex:`0x20-0x2F`
        """
        super().__init__(classifier, interm, final, abbr)

    def assemble(self) -> str:
        """
        Build up actual byte sequence and return as an ASCII-encoded string.
        """
        return (
            self.ESC_CHARACTER + self._classifier + (self._interm or None) + self._final
        )

    @classmethod
    def from_dict(cls, data: dict) -> SequenceNf:
        return SequenceNf(
            data.get("nf_classifier"),
            data.get("nf_final"),
            data.get("nf_interm") or None,
        )


class SequenceFp(ISequence):
    """
    Sequence class representing private control functions.

    All **Fp**-class sequences start with ``ESC`` plus ASCII byte in the
    range :hex:`0x30-0x3F` (``0``-``9``, ``:``, ``;``, ``<``, ``=``, ``>``,
    ``?``).
    """

    _CLASSIFIER_RANGE = range(0x30, 0x40)

    def __init__(self, classifier: str, abbr="Fp"):
        """
        .
        """
        super().__init__(classifier, abbr=abbr)

    @classmethod
    def from_dict(cls, data: dict) -> SequenceFp:
        return SequenceFp(data.get("fp_classifier"))


class SequenceFs(ISequence):
    """
    Sequences referred by ECMA-48 as "independent control functions".

    All **Fs**-class sequences start with ``ESC`` plus a byte in the range
    :hex:`0x60-0x7E` (``\u0060``, ``a``-``z``, ``{``, ``|``, ``}``).
    """

    _CLASSIFIER_RANGE = range(0x60, 0x7F)

    def __init__(self, classifier: str, abbr="Fs"):
        """
        .
        """
        super().__init__(classifier, abbr=abbr)

    @classmethod
    def from_dict(cls, data: dict) -> SequenceFs:
        return SequenceFs(data.get("fs_classifier"))


class SequenceFe(ISequence):
    """
    C1 set sequences -- a wide range of sequences that includes
    `CSI <SequenceCSI>`, `OSC <SequenceOSC>` and more.

    All **Fe**-class sequences start with ``ESC`` plus ASCII byte
    from :hex:`0x40` to :hex:`0x5F` (``@``, ``[``, ``\\``, ``]``, ``_``, ``^``
    and capital letters ``A``-``Z``).
    """

    _CLASSIFIER_RANGE = range(0x40, 0x60)

    def __init__(
        self,
        classifier: str,
        *params: int | str,
        interm: str = None,
        final: str = None,
        abbr="Fe",
    ):
        """
        .
        """
        super().__init__(classifier, interm, final, abbr)
        self._assign_params(*params)

    @classmethod
    def from_dict(cls, data: dict) -> SequenceFe:
        return SequenceFe(
            data.get("fe_classifier"),
            *cls.cast_params(data, "fe_param", False),
            interm=data.get("fe_interm") or None,
            final=data.get("fe_final") or None,
        )


class SequenceST(SequenceFe):
    """
    String Terminator sequence (ST). Terminates strings in other control
    sequences. Encoded as ``ESC \\`` (:hex:`0x1B 0x5C`).
    """

    _CLASSIFIER = "\\"

    def __init__(self):
        super().__init__(self._CLASSIFIER, abbr="ST")

    @classmethod
    def from_dict(cls, data: dict) -> SequenceFe:
        return SequenceST()


class SequenceOSC(SequenceFe):
    """
    :abbr:`OSC (Operating System Command)`-type sequence. Starts a control
    string for the operating system to use. Encoded as ``ESC ]``, plus params
    separated by ``;``. The control string can contain bytes from ranges
    :hex:`0x08-0x0D`, `0x20-0x7E` and are usually terminated by
    `ST <SequenceST>`.
    """

    _CLASSIFIER = "]"

    def __init__(self, *params: int | str, interm: str = None):
        super().__init__(self._CLASSIFIER, interm=interm, abbr="OSC")
        self._assign_params(*params)

    @classmethod
    def from_dict(cls, data: dict) -> SequenceFe:
        return SequenceOSC(
            *cls.cast_params(data, "osc_param", False), interm=data.get("osc_interm")
        )


class SequenceCSI(SequenceFe):
    """
    Class representing :abbr:`CSI (Control Sequence Introducer)`-type ANSI
    escape sequence. All subtypes of this sequence start with ``ESC [``.

    Sequences of this type are used to control text formatting,
    change cursor position, erase screen and more.

    >>> from pytermor import *
    >>> make_clear_line().assemble()
    '\x1b[2K'

    """

    _CLASSIFIER = "["

    def __init__(
        self, final: str = None, *params: int, interm: str = None, abbr: str = "CSI"
    ):
        """
        .
        """
        super().__init__(
            self._CLASSIFIER, *params, interm=interm, final=final, abbr=abbr
        )

    def assemble(self) -> str:
        return (
            self.ESC_CHARACTER
            + (self._classifier or "")
            + (self._interm or "")
            + self._assemble_params()
            + (self._final or "")
        )

    @classmethod
    def from_dict(cls, data: dict) -> SequenceFe:
        return SequenceCSI(
            data.get("csi_final") or None,
            *cls.cast_params(data, "csi_param", True),
            interm=data.get("csi_interm") or None,
        )

    @staticmethod
    def validate_column_abs_value(column: int):
        if column <= 0:
            raise ValueError(f"Invalid column value: expected > 0, got: {column}")

    @staticmethod
    def validate_line_abs_value(line: int):
        if line <= 0:
            raise ValueError(f"Invalid line value: expected > 0, got: {line}")

    @staticmethod
    def validate_column_rel_value(columns: int):
        if columns <= 0:
            raise ValueError(f"Invalid column shift value: expected > 0, got: {columns}")

    @staticmethod
    def validate_line_rel_value(lines: int):
        if lines <= 0:
            raise ValueError(f"Invalid line shift value: expected > 0, got: {lines}")


class SequenceSGR(SequenceCSI):
    """
    Class representing :abbr:`SGR (Select Graphic Rendition)`-type escape sequence
    with varying amount of parameters. SGR sequences allow to change the color
    of text or/and terminal background (in 3 different color spaces) as well
    as set decorate text with italic style, underlining, overlining, cross-lining,
    making it bold or blinking etc.

        >>> SequenceSGR(IntCode.HI_CYAN, 'underlined', 1)
        <SGR[96;4;1m]>

    To encode into control sequence byte-string invoke `assemble()` method or cast
    the instance to *str*, which internally does the same (this actually applies
    to all children of `ISequence`):

        >>> SequenceSGR('blue', 'italic').assemble()
        '\x1b[34;3m'
        >>> str(SequenceSGR('blue', 'italic'))
        '\x1b[34;3m'

    The latter also allows fluent usage in f-strings:

        >>> f'{SeqIndex.RED}should be red{SeqIndex.RESET}'
        '\x1b[31mshould be red\x1b[0m'

    .. note ::
        `SequenceSGR` with zero params ``ESC [m`` is interpreted by terminal emulators
        as ``ESC [0m``, which is *hard* reset sequence. The empty-string-sequence is
        predefined at module level as `NOOP_SEQ`.

    .. note ::
        The module doesn't distinguish "single-instruction" sequences from several
        ones merged together, e.g. ``Style(fg='red', bold=True)`` produces only one
        opening SequenceSGR instance:

        >>> SequenceSGR(IntCode.BOLD, IntCode.RED).assemble()
        '\x1b[1;31m'

        ...although generally speaking it is two of them (``ESC [1m`` and
        ``ESC [31m``). However, the module can automatically match terminating
        sequences for any form of input SGRs and translate it to specified format.

    It is possible to add of one SGR sequence to another, resulting in a new one
    with merged params:

        >>> SequenceSGR('blue') + SequenceSGR('italic')
        <SGR[34;3m]>

    """

    _CLASSIFIER = SequenceCSI._CLASSIFIER
    _FINAL = "m"

    def __init__(self, *params: str | int | SubtypedParam | SequenceSGR):
        """
        :param args:  ..  ::

                    Sequence params. Resulting param order is the same as an
                    argument order. Each argument can be specified as:

                      * *str* -- any of `IntCode` names, case-insensitive;
                      * *int* -- `IntCode` instance or plain integer;
                      * *SubtypeParam*
                      * another `SequenceSGR` instance (params will be extracted).
        """
        super().__init__(final=self._FINAL, abbr="SGR")
        self._assign_params(*params)

    def _assign_params(self, *params: int | str | SubtypedParam | SequenceSGR):
        def process_params(*params) -> t.Iterable[int | SubtypedParam]:
            for param in params:
                if isinstance(param, SequenceSGR):
                    yield from process_params(*param.params)
                    continue
                yield max(0, process_param(param))

        def process_param(param) -> int | SubtypedParam:
            if isinstance(param, str):
                return IntCode.resolve(param).value
            elif isinstance(param, IntCode):
                return param.value
            elif isinstance(param, (int, SubtypedParam)):
                return param
            else:
                raise TypeError(f"Invalid param type: {param!r})")

        self._params: list[int | SubtypedParam] = [*(process_params(*params))]

    @property
    def params(self) -> t.List[int | SubtypedParam]:
        """
        :return: Sequence params as integers.
        """
        return super().params

    def __hash__(self) -> int:
        return int.from_bytes(self.assemble().encode(), byteorder="big")

    def __add__(self, other: SequenceSGR) -> SequenceSGR:
        try:
            self._ensure_sequence(other)
        except TypeError:
            return NotImplemented
        return SequenceSGR(*self._params, *other._params)

    def __iadd__(self, other: SequenceSGR) -> SequenceSGR:
        return self.__add__(other)

    @classmethod
    def from_dict(cls, data: dict) -> SequenceFe:
        if data.get("csi_final") == cls._FINAL:
            if not (csi_param := data.get("csi_param")):
                return SequenceSGR()
            params_raw: list[str] = csi_param.split(cls.PARAM_SEPARATOR)
            params: list[int | SubtypedParam] = []
            try:
                for param_raw in params_raw:
                    if (subsep := SubtypedParam._SEPARATOR) in param_raw:
                        params.append(SubtypedParam(*map(int, param_raw.split(subsep))))
                    else:
                        params.append(int(param_raw))
            except ValueError:
                raise ParseError(data)
            return SequenceSGR(*params)
        return super().from_dict(data)

    @staticmethod
    def _ensure_sequence(subject: t.Any):
        if not isinstance(subject, SequenceSGR):
            raise TypeError(f"Expected SequenceSGR, got {type(subject)}")

    @staticmethod
    def validate_extended_color(value: int):
        if value < 0 or value > 255:
            raise ValueError(
                f"Invalid color value: expected range [0-255], got: {value}"
            )


class _NoOpSequenceSGR(SequenceSGR):
    def __init__(self):
        super().__init__()

    def __bool__(self) -> bool:
        return False

    def __eq__(self, other: _NoOpSequenceSGR) -> bool:
        return isinstance(other, _NoOpSequenceSGR)

    def __repr__(self) -> str:
        return f"<SGR/NOP>"

    def __add__(self, other: SequenceSGR) -> SequenceSGR:
        try:
            self._ensure_sequence(other)
        except TypeError:
            return NotImplemented
        if params := [*self._params, *other._params]:
            return SequenceSGR(*params)
        return _NoOpSequenceSGR()

    def __iadd__(self, other: SequenceSGR) -> SequenceSGR:
        return self.__add__(other)

    def assemble(self) -> str:
        return ""

    @classmethod
    def from_dict(cls, data: dict) -> SequenceFe:
        return super().from_dict(data)  # no equivalent


@total_ordering
class SubtypedParam:
    _SEPARATOR = ":"

    def __init__(self, value: int, subtype: int) -> None:
        super().__init__()
        self._value = value
        self._subtype = subtype

    @property
    def value(self) -> int:
        return self._value

    @property
    def subtype(self) -> int:
        return self._subtype

    def __str__(self):
        return f"{self._value}{self._SEPARATOR}{self._subtype}"

    def __lt__(self, other: SubtypedParam | int) -> bool:
        if not isinstance(other, SubtypedParam):
            return self._value < other
        if self._value == other._value:
            return self._subtype < other._subtype
        return self._value < other._value

    def __eq__(self, other: SubtypedParam | int) -> bool:
        if not isinstance(other, SubtypedParam):
            return False
        return self._value == other._value and self._subtype == other._subtype


# -----------------------------------------------------------------------------

class IntCode(enum.IntEnum):
    """
    Complete or almost complete list of reliably working SGR param integer codes.
    Fully interchangeable with plain *int*. Suitable for `SequenceSGR`
    default constructor.

    .. note ::
        `IntCode` predefined constants are omitted from documentation to avoid
        useless repeats and save space, as most of the time "higher-level" class
        `SeqIndex` will be more appropriate, and on top of that, the constant
        names are literally the same for `SeqIndex` and `IntCode`.
    """

    @classmethod
    def resolve(cls, name: str) -> IntCode:
        """

        :param name:
        """
        name_norm = name.upper()
        try:
            instance = cls[name_norm]
        except KeyError as e:
            e.args = (f"Int code '{name_norm}' (<- '{name}') does not exist",)
            raise e
        return instance

    def __repr__(self) -> str:
        return f"<{self.value}|{self.name}>"

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
    FRAMED = 51
    OVERLINED = 53

    BOLD_DIM_OFF = 22  # no sequence to disable BOLD or DIM while keeping the other
    ITALIC_OFF = 23
    UNDERLINED_OFF = 24
    BLINK_OFF = 25
    INVERSED_OFF = 27
    HIDDEN_OFF = 28
    CROSSLINED_OFF = 29
    COLOR_OFF = 39
    BG_COLOR_OFF = 49
    FRAMED_OFF = 54  # with "encircled" off
    OVERLINED_OFF = 55

    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37
    COLOR_EXTENDED = 38

    BG_BLACK = 40
    BG_RED = 41
    BG_GREEN = 42
    BG_YELLOW = 43
    BG_BLUE = 44
    BG_MAGENTA = 45
    BG_CYAN = 46
    BG_WHITE = 47
    BG_COLOR_EXTENDED = 48

    UNDERLINE_COLOR_EXTENDED = 58
    UNDERLINE_COLOR_OFF = 59

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
    #    52: encircled
    # 60-65: ideogram attributes
    # 73-75: superscript and subscript

    EXTENDED_MODE_256 = 5
    EXTENDED_MODE_RGB = 2


class SeqIndex:
    """
    Registry of static sequences that can be utilized without implementing
    an extra logic.
    """

    RESET = SequenceSGR(IntCode.RESET)
    """
    Hard reset sequence.
    """

    BOLD = SequenceSGR(IntCode.BOLD)
    """ Bold or increased intensity. """

    DIM = SequenceSGR(IntCode.DIM)
    """ Faint, decreased intensity. """

    ITALIC = SequenceSGR(IntCode.ITALIC)
    """ Italic *(not widely supported)*. """

    UNDERLINED = SequenceSGR(IntCode.UNDERLINED)
    """ Underline. """

    CURLY_UNDERLINED = SequenceSGR(SubtypedParam(IntCode.UNDERLINED, 3))
    """ Curly underline. """

    BLINK_SLOW = SequenceSGR(IntCode.BLINK_SLOW)
    """ Set blinking to < 150 cpm. """

    BLINK_FAST = SequenceSGR(IntCode.BLINK_FAST)
    """ Set blinking to 150+ cpm *(not widely supported)*. """

    INVERSED = SequenceSGR(IntCode.INVERSED)
    """ Swap foreground and background colors. """

    HIDDEN = SequenceSGR(IntCode.HIDDEN)
    """ Conceal characters *(not widely supported)*. """

    CROSSLINED = SequenceSGR(IntCode.CROSSLINED)
    """ Strikethrough. """

    DOUBLE_UNDERLINED = SequenceSGR(IntCode.DOUBLE_UNDERLINED)
    """ Double-underline. *On several terminals disables* `BOLD` *instead*. """

    FRAMED = SequenceSGR(IntCode.FRAMED)
    """ Rectangular border *(not widely supported, to say the least)*. """

    OVERLINED = SequenceSGR(IntCode.OVERLINED)
    """ Overline *(not widely supported)*. """

    BOLD_DIM_OFF = SequenceSGR(IntCode.BOLD_DIM_OFF)
    """
    Disable ``BOLD`` and ``DIM`` attributes.\n
    *Special aspects... It's impossible to reliably disable them on a separate basis.*
    """

    ITALIC_OFF = SequenceSGR(IntCode.ITALIC_OFF)
    """ Disable italic. """

    UNDERLINED_OFF = SequenceSGR(IntCode.UNDERLINED_OFF)
    """ Disable underlining. """

    BLINK_OFF = SequenceSGR(IntCode.BLINK_OFF)
    """ Disable blinking. """

    INVERSED_OFF = SequenceSGR(IntCode.INVERSED_OFF)
    """ Disable inversing. """

    HIDDEN_OFF = SequenceSGR(IntCode.HIDDEN_OFF)
    """ Disable conecaling. """

    CROSSLINED_OFF = SequenceSGR(IntCode.CROSSLINED_OFF)
    """ Disable strikethrough. """

    FRAMED_OFF = SequenceSGR(IntCode.FRAMED_OFF)
    """ Disable border. """

    OVERLINED_OFF = SequenceSGR(IntCode.OVERLINED_OFF)
    """ Disable overlining. """

    UNDERLINE_COLOR_OFF = SequenceSGR(IntCode.UNDERLINE_COLOR_OFF)
    """ Reset underline color. """

    # text colors

    BLACK = SequenceSGR(IntCode.BLACK)
    """ Set text color to :hex:`0x000000`. """

    RED = SequenceSGR(IntCode.RED)
    """ Set text color to :hex:`0x800000`. """

    GREEN = SequenceSGR(IntCode.GREEN)
    """ Set text color to :hex:`0x008000`. """

    YELLOW = SequenceSGR(IntCode.YELLOW)
    """ Set text color to :hex:`0x808000`. """

    BLUE = SequenceSGR(IntCode.BLUE)
    """ Set text color to :hex:`0x000080`. """

    MAGENTA = SequenceSGR(IntCode.MAGENTA)
    """ Set text color to :hex:`0x800080`. """

    CYAN = SequenceSGR(IntCode.CYAN)
    """ Set text color to :hex:`0x008080`. """

    WHITE = SequenceSGR(IntCode.WHITE)
    """ Set text color to :hex:`0xc0c0c0`. """

    COLOR_OFF = SequenceSGR(IntCode.COLOR_OFF)
    """ Reset foreground color. """

    # background colors

    BG_BLACK = SequenceSGR(IntCode.BG_BLACK)
    """ Set background color to :hex:`0x000000`. """

    BG_RED = SequenceSGR(IntCode.BG_RED)
    """ Set background color to :hex:`0x800000`. """

    BG_GREEN = SequenceSGR(IntCode.BG_GREEN)
    """ Set background color to :hex:`0x008000`. """

    BG_YELLOW = SequenceSGR(IntCode.BG_YELLOW)
    """ Set background color to :hex:`0x808000`. """

    BG_BLUE = SequenceSGR(IntCode.BG_BLUE)
    """ Set background color to :hex:`0x000080`. """

    BG_MAGENTA = SequenceSGR(IntCode.BG_MAGENTA)
    """ Set background color to :hex:`0x800080`. """

    BG_CYAN = SequenceSGR(IntCode.BG_CYAN)
    """ Set background color to :hex:`0x008080`. """

    BG_WHITE = SequenceSGR(IntCode.BG_WHITE)
    """ Set background color to :hex:`0xc0c0c0`. """

    BG_COLOR_OFF = SequenceSGR(IntCode.BG_COLOR_OFF)
    """ Reset background color. """

    # high intensity text colors

    GRAY = SequenceSGR(IntCode.GRAY)
    """ Set text color to :hex:`0x808080`. """
    HI_RED = SequenceSGR(IntCode.HI_RED)
    """ Set text color to :hex:`0xff0000`. """
    HI_GREEN = SequenceSGR(IntCode.HI_GREEN)
    """ Set text color to :hex:`0x00ff00`. """
    HI_YELLOW = SequenceSGR(IntCode.HI_YELLOW)
    """ Set text color to :hex:`0xffff00`. """
    HI_BLUE = SequenceSGR(IntCode.HI_BLUE)
    """ Set text color to :hex:`0x0000ff`. """
    HI_MAGENTA = SequenceSGR(IntCode.HI_MAGENTA)
    """ Set text color to :hex:`0xff00ff`. """
    HI_CYAN = SequenceSGR(IntCode.HI_CYAN)
    """ Set text color to :hex:`0x00ffff`. """
    HI_WHITE = SequenceSGR(IntCode.HI_WHITE)
    """ Set text color to :hex:`0xffffff`. """

    # high intensity background colors

    BG_GRAY = SequenceSGR(IntCode.BG_GRAY)
    """ Set background color to :hex:`0x808080`. """
    BG_HI_RED = SequenceSGR(IntCode.BG_HI_RED)
    """ Set background color to :hex:`0xff0000`. """
    BG_HI_GREEN = SequenceSGR(IntCode.BG_HI_GREEN)
    """ Set background color to :hex:`0x00ff00`. """
    BG_HI_YELLOW = SequenceSGR(IntCode.BG_HI_YELLOW)
    """ Set background color to :hex:`0xffff00`. """
    BG_HI_BLUE = SequenceSGR(IntCode.BG_HI_BLUE)
    """ Set background color to :hex:`0x0000ff`. """
    BG_HI_MAGENTA = SequenceSGR(IntCode.BG_HI_MAGENTA)
    """ Set background color to :hex:`0xff00ff`. """
    BG_HI_CYAN = SequenceSGR(IntCode.BG_HI_CYAN)
    """ Set background color to :hex:`0x00ffff`. """
    BG_HI_WHITE = SequenceSGR(IntCode.BG_HI_WHITE)
    """ Set background color to :hex:`0xffffff`. """


class _SgrPairityRegistry:
    """
    Internal class providing methods for mapping SGRs to a
    complement (closing) SGRs, also referred to as "resetters".
    """

    def __init__(self):
        self._code_to_resetter_map: t.Dict[int | t.Tuple[int, ...], SequenceSGR] = dict()
        self._resetter_codes: t.Set[int] = set()
        self._complex_code_def: t.Dict[int | t.Tuple[int, ...], int] = dict()
        self._complex_code_max_len: int = 0

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
            (IntCode.FRAMED, IntCode.FRAMED_OFF),
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
        self._bind_complex(
            (IntCode.UNDERLINE_COLOR_EXTENDED, 5), 1, IntCode.UNDERLINE_COLOR_OFF
        )
        self._bind_complex(
            (IntCode.UNDERLINE_COLOR_EXTENDED, 2), 3, IntCode.UNDERLINE_COLOR_OFF
        )

    def _bind_regular(self, starter_code: int | t.Tuple[int, ...], resetter_code: int):
        if starter_code in self._code_to_resetter_map:  # pragma: no cover
            raise ConflictError(f"SGR {starter_code} already has a registered resetter")

        self._code_to_resetter_map[starter_code] = SequenceSGR(resetter_code)
        self._resetter_codes.add(resetter_code)

    def _bind_complex(
        self, starter_codes: t.Tuple[int, ...], param_len: int, resetter_code: int
    ):
        self._bind_regular(starter_codes, resetter_code)

        if starter_codes in self._complex_code_def:  # pragma: no cover
            raise ConflictError(f"SGR {starter_codes} already has a registered resetter")

        self._complex_code_def[starter_codes] = param_len
        self._complex_code_max_len = max(
            self._complex_code_max_len, len(starter_codes) + param_len
        )

    def get_closing_seq(self, opening_seq: SequenceSGR) -> SequenceSGR:
        if not isinstance(opening_seq, SequenceSGR):
            raise TypeError(f"Not a SGR sequence: {opening_seq}")
        if isinstance(opening_seq, _NoOpSequenceSGR):
            return NOOP_SEQ
        closing_seq_params: t.List[int] = []
        opening_params = copy(opening_seq.params)

        while len(opening_params):
            key_params: int | SubtypedParam | t.Tuple[
                int | SubtypedParam, ...
            ] | None = None

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
            key_params = (*self.expand_subtypes(key_params),)
            if len(key_params) == 1:
                key_params = key_params[0]
            if key_params not in self._code_to_resetter_map:
                continue

            closing_seq_params.extend(self._code_to_resetter_map[key_params].params)

        if not closing_seq_params:
            return NOOP_SEQ
        return SequenceSGR(*closing_seq_params)

    def expand_subtypes(
        self, key_params: int | SubtypedParam | t.Tuple[int | SubtypedParam, ...] | None
    ) -> t.Iterable[int]:
        if not isinstance(key_params, t.Iterable):
            key_params = (key_params,)
        for kp in key_params:
            yield kp.value if isinstance(kp, SubtypedParam) else kp

    def get_resetter_codes(self) -> t.Set[int]:
        return self._resetter_codes



@unique
class ColorTarget(enum.Enum):
    FG = (IntCode.COLOR_EXTENDED, SeqIndex.COLOR_OFF)
    BG = (IntCode.BG_COLOR_EXTENDED, SeqIndex.BG_COLOR_OFF)
    UNDERLINE = (IntCode.UNDERLINE_COLOR_EXTENDED, SeqIndex.UNDERLINE_COLOR_OFF)

    def __init__(self, open_code: int, resetter: SequenceSGR = None):
        self.open_code = open_code
        self.resetter = resetter


_PAIRITY_REGISTRY = _SgrPairityRegistry()


def get_closing_seq(opening_seq: SequenceSGR) -> SequenceSGR:
    """

    :param opening_seq:
    :return:
    """
    return _PAIRITY_REGISTRY.get_closing_seq(opening_seq)


def enclose(opening_seq: SequenceSGR, string: str) -> str:
    """

    :param opening_seq:
    :param string:
    :return:
    """
    return f"{opening_seq}{string}{get_closing_seq(opening_seq)}"


def get_resetter_codes() -> t.Set[int]:
    return _PAIRITY_REGISTRY.get_resetter_codes()


# -----------------------------------------------------------------------------

NOOP_SEQ = _NoOpSequenceSGR()
"""
Special sequence in case one *has to* provide one or another SGR, but does 
not want any control sequences to be actually included in the output. 

``NOOP_SEQ.assemble()`` returns empty string, ``NOOP_SEQ.params`` 
returns empty list:

    >>> NOOP_SEQ.assemble()
    ''
    >>> NOOP_SEQ.params
    []

.. important ::
    Casting to *bool* results in **False** for all ``NOOP`` instances in the 
    library (`NOOP_SEQ`, `NOOP_COLOR` and `NOOP_STYLE`). This is intended. 

Can be safely added to regular `SequenceSGR` from any side, as internally
`SequenceSGR` always makes a new instance with concatenated params from both 
items, rather than modifies state of either of them:

    >>> NOOP_SEQ + SequenceSGR(1)
    <SGR[1m]>
    >>> SequenceSGR(3) + NOOP_SEQ
    <SGR[3m]>

"""


ESCAPE_SEQ_REGEX = re.compile(
    R"""
	(?P<escape_byte>\x1b)
	(?P<data>
		(?P<nf_class_seq>
			(?P<nf_classifier>[\x20-\x2f])
			(?P<nf_interm>[\x20-\x2f]*)
			(?P<nf_final>[\x30-\x7e])
		)|
		(?P<fp_class_seq>
			(?P<fp_classifier>[\x30-\x3f])
		)|
		(?P<fe_class_seq>
		    (?P<st_classifier>\\)
		    |
		    (?P<osc_classifier>\])
		    (?P<osc_param>[\x30-\x3f]*;;?)
		    |
		    (?P<csi_classifier>\[)
			(?P<csi_interm>[?!]?)
			(?P<csi_param>[\x30-\x3f]*)
			(?P<csi_final>[\x40-\x7e])
		    |
			(?P<fe_classifier>[\x40-\x5a\x5e\x5f])
			(?P<fe_param>[\x30-\x3f]*)
			(?P<fe_interm>[\x20-\x2f]?)
			(?P<fe_final>[\x40-\x7e]?)
		)|
		(?P<fs_class_seq>
			(?P<fs_classifier>[\x60-\x7e])
		)  
	)
	""",
    flags=re.VERBOSE,
)
""" 
Regular expression that matches all classes of escape sequences.

More specifically, it recognizes **nF**, **Fp**, **Fe** and **Fs** [#]_ 
classes. Useful for removing the sequences as well as for granular search 
thanks to named match groups, which include:

    ``escape_byte``
        first byte of every sequence -- ``ESC``, or :hex:`0x1B`.
        
    ``data``
        remaining bytes of the sequence (without escape byte) represented as 
        one of the following groups: ``nf_class_seq``, ``fp_class_seq``, 
        ``fe_class_seq`` or ``fs_class_seq``; each of these splits further to
        even more specific subgroups:
        
        - ``nf_classifier``, ``nf_interm`` and ``nf_final`` as parts of 
          **nF**-class sequences,
        - ``fp_classifier`` for **Fp**-class sequences,
        - ``st_classifier``, ``osc_classifier``, ``osc_param``,  ``csi_classifier``, 
          ``csi_interm``, ``csi_param``, ``csi_final``, ``fe_classifier``, ``fe_param``, 
          ``fe_interm`` and ``fe_final`` for **Fe**-class generic sequences and 
          subtypes (including :term:`SGRs <SGR>`),
        - ``fs_classifier`` for **Fs**-class sequences.

.. [#] `ECMA-35 specification <https://ecma-international.org/publications-and-standards/standards/ecma-35/>`_

:meta hide-value:
"""


@lru_cache
def _compile_contains_sgr_regex(*codes: int) -> re.Pattern:
    return re.compile(Rf'\x1b\[(?:|[\d;]*;)({";".join(map(str, codes))})(?:|;[\d;]*)m')


def contains_sgr(string: str, *codes: int) -> re.Match | None:
    """
    Return the first match of :term:`SGR` sequence in ``string`` with specified
    ``codes`` as params, strictly inside a single sequence in specified order,
    or *None* if nothing was found.

    The match object has one group (or, technically, two):

        - Group #0: the whole matched SGR sequence;
        - Group #1: the requested params bytes only.

    Example regex used for searching: :regexp:`\\x1b\\[(?:|[\\d;]*;)(48;5)(?:|;[\\d;]*)m`.

        >>> contains_sgr(make_color_256(128).assemble(), 38)
        <re.Match object; span=(0, 11), match='\x1b[38;5;128m'>
        >>> contains_sgr(make_color_256(84, ColorTarget.BG).assemble(), 48, 5)
        <re.Match object; span=(0, 10), match='\x1b[48;5;84m'>

    :param string: String to search the SGR in.
    :param codes:  Integer SGR codes to find.
    """
    if not string:
        return None
    return _compile_contains_sgr_regex(*codes).search(string)


def parse(string: str) -> t.Iterable[ISequence | str]:
    """
    parse
    :param string:
    """
    cursor = 0
    for match in ESCAPE_SEQ_REGEX.finditer(string):
        if (mstart := match.start()) > cursor:
            yield string[cursor:mstart]
        cursor = match.end()
        yield seq_from_dict(match.groupdict())
    if last_str := string[cursor:]:
        yield last_str
