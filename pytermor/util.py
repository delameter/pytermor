# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

import re
from functools import reduce
from typing import Callable, AnyStr, Type, Generic


class StringFilter(Generic[AnyStr]):
    def __init__(self, fn: Callable[[AnyStr], AnyStr]):
        self._fn = fn

    def apply(self, s: AnyStr) -> AnyStr:
        return self._fn(s)


class ReplaceSGR(StringFilter[str]):
    """Find all SGR seqs (e.g. '\\e[1;4m') and replace with given string.
    More specific version of ReplaceCSI()."""
    def __init__(self, repl: str = ''):
        super().__init__(lambda s: re.sub(r'(\033)(\[)(([0-9;])*)(m)', repl, s))


class ReplaceCSI(StringFilter[str]):
    """Find all CSI seqs (e.g. '\\e[*') and replace with given string.
    Less specific version of ReplaceSGR(), as CSI consists of SGR and many other seq subtypes."""
    def __init__(self, repl: str = ''):
        super().__init__(lambda s: re.sub(r'(\033)(\[)(([0-9;:<=>?])*)([@A-Za-z])', repl, s))


class ReplaceNonAsciiBytes(StringFilter[bytes]):
    """Keep [0x00 - 0x7f], replace if greater than 0x7f."""
    def __init__(self, repl: bytes = b'?'):
        super().__init__(lambda s: re.sub(b'[\x80-\xff]', repl, s))


def apply_filters(string: AnyStr, *args: StringFilter|Type[StringFilter]) -> AnyStr:
    filters = map(lambda t: t() if isinstance(t, type) else t, args)
    return reduce(lambda s, f: f.apply(s), filters, string)


def ljust_fmtd(s: str, width: int, fillchar: str = ' ') -> str:
    sanitized = ReplaceSGR().apply(s)
    return s + fillchar * max(0, width - len(sanitized))


def rjust_fmtd(s: str, width: int, fillchar: str = ' ') -> str:
    sanitized = ReplaceSGR().apply(s)
    return fillchar * max(0, width - len(sanitized)) + s


def center_fmtd(s: str, width: int, fillchar: str = ' ') -> str:
    sanitized = ReplaceSGR().apply(s)
    fill_len = max(0, width - len(sanitized))
    if fill_len == 0:
        return s
    right_fill_len = fill_len // 2
    left_fill_len = fill_len - right_fill_len
    return (fillchar * left_fill_len) + s + (fillchar * right_fill_len)
