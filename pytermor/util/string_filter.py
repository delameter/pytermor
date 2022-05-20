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

import abc
import re
from abc import abstractmethod
from functools import reduce
from typing import Generic, AnyStr, Type


def apply_filters(string: AnyStr, *args: StringFilter[AnyStr]|Type[StringFilter[AnyStr]]) -> AnyStr:
    """
    Method for applying dynamic filter list to a target str/bytes.
    Example (will replace all `\\\\x1b` control characters to `E` and
    make SGR params visible):

        ``>>> apply_filters(span.red('test'), ReplaceSGR(r'E\\2\\3\\5'))``

        ``'E[31mtestE[39m'``

    Note that type of ``string`` argument must correspond to `StringFilter's`
    types, i.e. ``ReplaceNonAsciiBytes`` is `StringFilter[bytes]` type, so
    you can apply it only to bytes-type strings.

    :param AnyStr string:
        String for filter application (str or bytes-type).

    :param args:
        `StringFilter` instances or `StringFilter` types.

    :return:
        String with applied filters.
    """
    filters = map(lambda t: t() if isinstance(t, type) else t, args)
    return reduce(lambda s, f: f.apply(s), filters, string)


class StringFilter(Generic[AnyStr], metaclass=abc.ABCMeta):
    """
    Common string modifier interface.
    """
    def __init__(self, repl: AnyStr):
        self._repl: AnyStr = repl

    def __call__(self, s: AnyStr) -> AnyStr:
        return self.apply(s)

    @abstractmethod
    def apply(self, s: AnyStr) -> AnyStr: raise NotImplementedError


class ReplaceSGR(StringFilter[str]):
    """
    Find all SGR seqs (e.g. 'ESC[1;4m') and replace with given string.

    More specific version of ``ReplaceCSI``.

    :param repl:
        Replacement, can contain regexp groups (see `apply_filters`).
    """
    def __init__(self, repl: AnyStr = ''):
        super().__init__(repl)

    def apply(self, s: str) -> str:
        return re.sub(r'(\x1b)(\[)(([0-9;])*)(m)', self._repl, s)


class ReplaceCSI(StringFilter[str]):
    """
    Find all CSI seqs (i.e. 'ESC[\*') and replace with given string.

    Less specific version of ``ReplaceSGR``, as CSI consists of SGR
    and many other sequence subtypes.

    :param repl:
        Replacement, can contain regexp groups (see `apply_filters`).
    """

    def __init__(self, repl: AnyStr = ''):
        super().__init__(repl)

    def apply(self, s: str) -> str:
        return re.sub(r'(\x1b)(\[)(([0-9;:<=>?])*)([@A-Za-z])', self._repl, s)


class ReplaceNonAsciiBytes(StringFilter[bytes]):
    """
    Keep 7-bit ASCII bytes `[0x00 - 0x7f]`,
    replace other to '?' (by default).

    :param repl:
        Replacement bytes. To delete non-ASCII bytes define it as b''.
    """
    def __init__(self, repl: AnyStr = b''):
        super().__init__(repl)

    def apply(self, s: bytes) -> bytes:
        return re.sub(b'[\x80-\xff]', self._repl, s)
