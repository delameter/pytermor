# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""
String filtering module.

Main idea is to provide a common interface for string filtering, that can make
possible working with filters like with objects rather than with functions/lambdas.
"""
from __future__ import annotations

import re
from functools import reduce
from re import Match
from typing import Generic, AnyStr, Type, Callable

from .. import span


def apply_filters(string: AnyStr, *args: StringFilter[AnyStr]|Type[StringFilter[AnyStr]]) -> AnyStr:
    """
    Method for applying dynamic filter list to a target str/bytes.
    Example (will replace all :kbd:`ESC` control characters to :kbd:`E` and
    thus make SGR params visible)::

        >>> apply_filters(span.RED('test'), ReplaceSGR(r'E\\2\\3\\5'))
        'E[31mtestE[39m'

    Note that type of ``string`` argument must correspond to ``StringFilter``
    types, i.e. :class:`ReplaceNonAsciiBytes` is ``StringFilter[bytes]`` type, so
    you can apply it only to bytes-type strings.

    :param AnyStr string:
        String for filter application (str or bytes-type).

    :param args:
        `StringFilter` instances or ``StringFilter`` types.

    :return:
        String with applied filters.
    """
    filters = map(lambda t: t() if isinstance(t, type) else t, args)
    return reduce(lambda s, f: f.apply(s), filters, string)


class StringFilter(Generic[AnyStr]):
    """
    Common string modifier interface.
    """
    def __init__(self, pattern: AnyStr, repl: AnyStr|Callable[[AnyStr|Match], AnyStr]):
        self._regex = re.compile(pattern)
        self._repl = repl

    def __call__(self, s: AnyStr) -> AnyStr:
        return self.apply(s)

    def apply(self, s: AnyStr) -> AnyStr:
        return self._regex.sub(self._repl, s)


class VisualuzeWhitespace(StringFilter[str]):
    """
    Replace every invisible character with visible :kbd:`·`, execpt
    newlines. Newlines are kept and gets prepneded with same char.

    Example usages::

        output = VisualuzeWhitespace().apply(input)  # OR
        output = apply_filters(input, VisualuzeWhitespace)
    """
    def __init__(self):
        super().__init__(r'\s(\n|.)]', '·\\1')


class ReplaceSGR(StringFilter[str]):
    """
    Find all SGR seqs (e.g. :kbd:`ESC[1;4m`) and replace with given string. More
    specific version of :class:`ReplaceCSI`.

    :param repl:
        Replacement, can contain regexp groups (see :meth:`apply_filters()`).
    """
    def __init__(self, repl: AnyStr = ''):
        super().__init__(r'(\x1b)(\[)(([0-9;])*)(m)', repl)


class ReplaceCSI(StringFilter[str]):
    """
    Find all CSI seqs (i.e. :kbd:`ESC[*`) and replace with given string. Less
    specific version of :class:`ReplaceSGR`, as CSI consists of SGR and many other
    sequence subtypes.

    :param repl:
        Replacement, can contain regexp groups (see :meth:`apply_filters()`).
    """
    def __init__(self, repl: AnyStr = ''):
        super().__init__(r'(\x1b)(\[)(([0-9;:<=>?])*)([@A-Za-z])', repl)


class ReplaceNonAsciiBytes(StringFilter[bytes]):
    """
    Keep 7-bit ASCII bytes [:kbd:`0x00` - :kbd:`0x7f`], replace other to :kbd:`?`.

    :param repl: Replacement byte-string.
    """
    def __init__(self, repl: AnyStr = b'?'):
        super().__init__(b'[\x80-\xff]', repl)
