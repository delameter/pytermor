# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""

.. testsetup:: *

    from pytermor.utilstr import *
    from pytermor.ansi import SeqIndex

"""
from __future__ import annotations

import math
import re
import textwrap
import typing as t
from functools import reduce
from typing import Union

from .common import StrType

_PRIVATE_REPLACER = "\U000E5750"


def format_thousand_sep(value: int | float, separator: str = " ") -> str:
    """
    Returns input ``value`` with integer part split into groups of three digits,
    joined then with ``separator`` string.

    >>> format_thousand_sep(260341)
    '260 341'
    >>> format_thousand_sep(-9123123123.55, ',')
    '-9,123,123,123.55'

    :param value:
    :param separator:
    """
    return f"{value:_}".replace("_", separator)


def distribute_padded(
    values: t.List[StrType],
    max_len: int,
    pad_before: bool = False,
    pad_after: bool = False,
) -> StrType:
    """
    .. todo ::
        todo

    :param values:
    :param max_len:
    :param pad_before:
    :param pad_after:
    :return:
    """
    if pad_before:
        values.insert(0, "")
    if pad_after:
        values.append("")

    values_amount = len(values)
    gapes_amount = values_amount - 1
    values_len = sum(len(v) for v in values)
    spaces_amount = max_len - values_len
    if spaces_amount < gapes_amount:
        raise ValueError(f"There is not enough space for all values with padding")

    result = ""
    for value_idx, value in enumerate(values):
        gape_len = spaces_amount // (gapes_amount or 1)  # for last value
        result += value + " " * gape_len
        gapes_amount -= 1
        spaces_amount -= gape_len

    return result


"""
Some of the Python Standard Library methods rewritten
for correct work with strings containing control sequences.
"""


def ljust_sgr(s: str, width: int, fillchar: str = " ", actual_len: int = None) -> str:
    """
    SGR-formatting-aware implementation of ``str.ljust``.

    Return a left-justified string of length ``width``. Padding is done
    using the specified fill character (default is a space).
    """
    if actual_len is None:
        actual_len = len(SgrStringReplacer().apply(s))
    return s + fillchar * max(0, width - actual_len)


def rjust_sgr(s: str, width: int, fillchar: str = " ", actual_len: int = None) -> str:
    """
    SGR-formatting-aware implementation of ``str.rjust``.

    Return a right-justified string of length ``width``. Padding is done
    using the specified fill character (default is a space).
    """
    if actual_len is None:
        actual_len = len(SgrStringReplacer().apply(s))
    return fillchar * max(0, width - actual_len) + s


def center_sgr(s: str, width: int, fillchar: str = " ", actual_len: int = None) -> str:
    """
    SGR-formatting-aware implementation of ``str.center``.

    Return a centered string of length ``width``. Padding is done using the
    specified fill character (default is a space).

    .. todo ::

        поверить корректность работы в случае эмодзи (напр. 🔋)
        если алгоритм поедет -- можно заменить на f-стринги
    """
    if actual_len is None:
        actual_len = len(SgrStringReplacer().apply(s))

    fill_len = max(0, width - actual_len)
    if fill_len == 0:
        return s

    if actual_len % 2 == 1:
        right_fill_len = math.ceil(fill_len / 2)
    else:
        right_fill_len = math.floor(fill_len / 2)
    left_fill_len = fill_len - right_fill_len
    return (fillchar * left_fill_len) + s + (fillchar * right_fill_len)


def wrap_sgr(
    raw_input: str | list[str], width: int, indent_first: int = 0, indent_subseq: int = 0
) -> str:
    """
    A workaround to make standard library ``textwrap.wrap()`` more friendly
    to an SGR-formatted strings.

    The main idea is

    :param raw_input:
    :param width:
    :return:
    """
    # initially was written as a part of es7s/core
    # package, and transferred here later
    sgrs: list[str] = []

    def push(m: t.Match):
        sgrs.append(m.group())
        return _PRIVATE_REPLACER

    if isinstance(raw_input, str):  # input can be just one paragraph
        raw_input = [raw_input]

    input = "\n\n".join(raw_input).split("\n\n")
    result = ""
    for raw_line in input:
        # had an inspiration and wrote this; no idea how does it work exactly, it just does
        replaced_line = re.sub(r"(\s?\S?)((\x1b\[([0-9;]*)m)+)", push, raw_line)
        wrapped_line = f"\n".join(
            textwrap.wrap(
                replaced_line,
                width=width,
                initial_indent=(indent_first * " "),
                subsequent_indent=(indent_subseq * " "),
            )
        )
        final_line = re.sub(_PRIVATE_REPLACER, lambda _: sgrs.pop(0), wrapped_line)
        result += final_line + "\n"
    return result

# -----------------------------------------------------------------------------


SGR_SEQ_SREGEX = re.compile(r"(\x1b)(\[)([0-9;]*)(m)")
CONTROL_SREGEX = re.compile(r"([\x00-\x09\x0b-\x1f\x7f]+)")
NON_ASCII_BREGEX = re.compile(br"([\x80-\xff]+)")
CONTROL_AND_NON_ASCII_BREGEX = re.compile(br"([\x00-\x09\x0b-\x1f\x7f\x80-\xff]+)")

IT = t.TypeVar("IT", str, bytes)  # input type
OT = t.TypeVar("OT", str, bytes)  # output type
PT = Union[OT, t.Pattern[OT]]   # pattern type (=output)
RT = Union[OT, t.Callable[[t.Match[OT]], OT]]  # replacer type (=output)
FT = Union['OmniFilter[IT, OT]', t.Type['OmniFilter[IT, OT]']]  # filter type (any)


class OmniFilter(t.Generic[IT, OT]):
    """
    Main idea is to provide a common interface for string filtering, that can make
    possible working with filters like with objects rather than with functions/lambdas.
    """

    def __call__(self, s: IT) -> OT:
        """Can be used instead of `apply()`"""
        return self.apply(s)

    def apply(self, inp: IT) -> OT:
        """
        :param inp:
        :return:
        """
        raise NotImplementedError

    def _transcode(self, inp: IT, target: t.Type[OT]) -> OT:
        if isinstance(inp, target):
            return inp
        return inp.encode() if isinstance(inp, str) else inp.decode()


class NoopFilter(OmniFilter[IT, OT]):
    def apply(self, inp: IT) -> OT:
        return inp


class OmniDecoder(OmniFilter[IT, str]):
    def apply(self, inp: IT) -> str:
        return inp.decode() if isinstance(inp, bytes) else inp


class OmniEncoder(OmniFilter[IT, bytes]):
    def apply(self, inp: IT) -> bytes:
        return inp.encode() if isinstance(inp, str) else inp


class OmniReplacer(OmniFilter[IT, OT]):
    """."""

    def __init__(self, pattern: PT, repl: RT):
        if isinstance(pattern, (str, bytes)):
            self._pattern: t.Pattern[OT] = re.compile(pattern)
        else:
            self._pattern: t.Pattern[OT] = pattern
        self._repl = repl

    def apply(self, inp: IT) -> OT:
        """Apply filter to ``s`` string (or bytes)."""
        target: t.Type[OT] = type(self._pattern.pattern)
        inp_transcoded: OT = self._transcode(inp, target)
        return self._pattern.sub(self._repl, inp_transcoded)


class StringReplacer(OmniReplacer[str, str]):
    pass


class BytesReplacer(OmniReplacer[bytes, bytes]):
    pass


class SgrStringReplacer(StringReplacer):
    """
    Find all SGR seqs (e.g. |e|\ ``[1;4m``) and replace with given string. More
    specific version of :class:`CsiReplacer`.

    :param repl:
        Replacement, can contain regexp groups (see :meth:`apply_filters()`).
    """

    def __init__(self, repl: RT[str] = ""):
        super().__init__(SGR_SEQ_SREGEX, repl)


class CsiStringReplacer(StringReplacer):
    """
    Find all CSI seqs (i.e. starting with |e|\ ``[``) and replace with given
    string. Less specific version of :class:`SgrReplacer`, as CSI consists of SGR
    and many other sequence subtypes.

    :param repl:
        Replacement, can contain regexp groups (see :meth:`apply_filters()`).
    """

    def __init__(self, repl: RT[str] = ""):
        super().__init__(r"(\x1b)(\[)(([0-9;:<=>?])*)([@A-Za-z])", repl)


class WhitespacesStringReplacer(StringReplacer):
    """
    Replace every invisible character with ``repl`` (default is ``·``),
    except newlines. Newlines are kept and get prepneded with same string by
    default, but this behaviour can be disabled with ``keep_newlines`` = *False*.

    >>> WhitespacesStringReplacer("·").apply('A  B  C')
    'A··B··C'
    >>> apply_filters('1. D\\n2. L ', WhitespacesStringReplacer(keep_newlines=False))
    '1.D2.L'

    :param repl:
    :param keep_newlines:
    """

    def __init__(self, repl: RT[str] = "", keep_newlines: bool = True):
        if keep_newlines:
            super().__init__(r"(\n)|\s", rf"{repl}\1")
        else:
            super().__init__(r"\s", repl)


class ControlCharsStringReplacer(StringReplacer):
    """."""

    def __init__(self, repl: RT[str] = ""):
        super().__init__(CONTROL_SREGEX, repl)


class NonAsciiByteReplacer(BytesReplacer):
    """
    Keep 7-bit ASCII bytes [0x00-0x7f], replace or remove (this is a default) others.

    >>> inp = bytes((0x60, 0x70, 0x80, 0x90, 0x50))
    >>> NonAsciiByteReplacer().apply(inp)
    b'`pP'
    >>> NonAsciiByteReplacer(lambda m: b'?'*len(m.group())).apply(inp)
    b'`p??P'
    >>> NonAsciiByteReplacer(lambda m: f'[{m.group().hex()}]'.encode()).apply(inp)
    b'`p[8090]P'

    :param repl: Replacement byte-string.
    """

    def __init__(self, repl: RT[bytes] = b""):
        super().__init__(NON_ASCII_BREGEX, repl)


class OmniSanitizer(OmniReplacer[IT, bytes]):
    def __init__(self, repl: RT[bytes] = b""):
        super().__init__(CONTROL_AND_NON_ASCII_BREGEX, repl)

    def apply(self, inp: IT) -> bytes:
        if isinstance(inp, str):
            inp = inp.encode()
        return super().apply(inp)


def apply_filters(string: IT, *args: FT) -> OT:
    """
    Method for applying dynamic filter list to a target string/bytes.
    Example (will replace all ``ESC`` control characters to ``E`` and
    thus make SGR params visible):

    >>> apply_filters(f'{SeqIndex.RED}test{SeqIndex.COLOR_OFF}', SgrStringReplacer(r'E\\2\\3\\4'))
    'E[31mtestE[39m'

    Note that type of ``s`` argument must be same as ``StringFilter`` parameterized
    type, i.e. :class:`ReplaceNonAsciiBytes` is ``StringFilter`` type, so
    you can apply it only to bytes-type strings.

    :param string: String to filter.
    :param args:   `OmniFilter` instance(s) or ``OmniFilter`` type(s).
    :return:       Filtered ``s``.
    """
    return reduce(lambda s, f: f()(s) if isinstance(f, type) else f(s), args, string)
