# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import re
from typing import Callable, AnyStr


class StringFilter:
    def __init__(self, fn: Callable):
        self._fn = fn

    def __call__(self, s: str):
        return self.invoke(s)

    def invoke(self, s: str):
        return self._fn(s)


class ReplaceSGRs(StringFilter):
    """Find all SGR seqs (e.g. '\\e[1;4m') and replace with given string.
    More specific version of ReplaceCSIs()."""
    def __init__(self, repl: AnyStr = ''):
        super().__init__(lambda s: re.sub(r'\033\[([0-9;]*)(m)', repl, s))


class ReplaceCSIs(StringFilter):
    """Find all CSI seqs (e.g. '\\e[*') and replace with given string.
    Less specific version of ReplaceSGRs(), as CSI consists of SGR and many other seq sub-types."""
    def __init__(self, repl: AnyStr = ''):
        super().__init__(lambda s: re.sub(r'\033\[([0-9;:<=>?]*)([@A-Za-z])', repl, s))


class ReplaceNonAsciiBytes(StringFilter):
    """Keep [0x00 - 0x7f], replace if greater than 0x7f."""
    def __init__(self, repl: bytes = b'?'):
        super().__init__(lambda s: re.sub(b'[\x80-\xff]', repl, s))
