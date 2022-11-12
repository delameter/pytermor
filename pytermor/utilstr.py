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
from functools import reduce
import typing as t
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
        actual_len = len(ReplaceSGR().apply(s))
    return s + fillchar * max(0, width - actual_len)


def rjust_sgr(s: str, width: int, fillchar: str = " ", actual_len: int = None) -> str:
    """
    SGR-formatting-aware implementation of ``str.rjust``.

    Return a right-justified string of length ``width``. Padding is done
    using the specified fill character (default is a space).
    """
    if actual_len is None:
        actual_len = len(ReplaceSGR().apply(s))
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
        actual_len = len(ReplaceSGR().apply(s))

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

    result = ""
    for raw_line in raw_input:
        # had an inspiration and wrote it; no idea how does it work exactly, it just does
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


"""
String filtering module.

Main idea is to provide a common interface for string filtering, that can make
possible working with filters like with objects rather than with functions/lambdas.
"""


SGR_REGEXP = re.compile(r"(\x1b)(\[)([0-9;]*)(m)")
ST = t.TypeVar("ST", str, bytes)


def apply_filters(s: ST, *args: StringFilter | t.Type[StringFilter]) -> ST:
    """
    Method for applying dynamic filter list to a target string/bytes.
    Example (will replace all ``ESC`` control characters to ``E`` and
    thus make SGR params visible):

    >>> apply_filters(f'{SeqIndex.RED}test{SeqIndex.COLOR_OFF}', ReplaceSGR(r'E\\2\\3\\4'))
    'E[31mtestE[39m'

    Note that type of ``s`` argument must be same as ``StringFilter`` parameterized
    type, i.e. :class:`ReplaceNonAsciiBytes` is ``StringFilter[bytes]`` type, so
    you can apply it only to bytes-type strings.

    :param s:     String to filter.
    :param args:  `StringFilter` instance(s) or ``StringFilter`` class(es).
    :return:      Filtered ``s``.
    """
    filters = map(lambda t: t() if isinstance(t, type) else t, args)
    return reduce(lambda s_, f: f.apply(s_), filters, s)


class StringFilter(t.Generic[ST]):
    """
    Common string modifier interface.
    """

    def __init__(
        self, pattern: ST | t.Pattern[ST], repl: ST | t.Callable[[ST | t.Match], ST]
    ):
        if isinstance(pattern, (str, bytes)):
            self._regexp = re.compile(pattern)
        else:
            self._regexp = pattern
        self._repl = repl

    def __call__(self, s: ST) -> ST:
        """Can be used instead of `apply()`"""
        return self.apply(s)

    def apply(self, s: ST) -> ST:
        """Apply filter to ``s`` string (or bytes)."""
        return self._regexp.sub(self._repl, s)


class VisualuzeWhitespace(StringFilter[str]):
    """
    Replace every invisible character with ``repl`` (default is ``·``),
    except newlines. Newlines are kept and get_by_code prepneded with same string.

    >>> VisualuzeWhitespace().apply('A  B  C')
    'A··B··C'
    >>> apply_filters('1. D\\n2. L ', VisualuzeWhitespace)
    '1.·D·\\n2.·L·'

    :param repl:
    """

    def __init__(self, repl: str = "·"):
        super().__init__(r"(\n)|\s", repl + "\\1")


class ReplaceSGR(StringFilter[str]):
    """
    Find all SGR seqs (e.g. ``ESC[1;4m``) and replace with given string. More
    specific version of :class:`ReplaceCSI`.

    :param repl:
        Replacement, can contain regexp groups (see :meth:`apply_filters()`).
    """

    def __init__(self, repl: str = ""):
        super().__init__(SGR_REGEXP, repl)


class ReplaceCSI(StringFilter[str]):
    """
    Find all CSI seqs (i.e. starting with ``ESC[``) and replace with given
    string. Less specific version of :class:`ReplaceSGR`, as CSI consists of SGR
    and many other sequence subtypes.

    :param repl:
        Replacement, can contain regexp groups (see :meth:`apply_filters()`).
    """

    def __init__(self, repl: str = ""):
        super().__init__(r"(\x1b)(\[)(([0-9;:<=>?])*)([@A-Za-z])", repl)


class ReplaceNonAsciiBytes(StringFilter[bytes]):
    """
    Keep 7-bit ASCII bytes [``0x00`` - ``0x7f``], replace other to ``?``.

    :param repl: Replacement byte-string.
    """

    def __init__(self, repl: bytes = b"?"):
        super().__init__(b"[\x80-\xff]", repl)
