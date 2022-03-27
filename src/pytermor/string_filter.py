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


# find all SGR seqs (e.g. '\e[1;4m') and replace with given string
# more specific version of ReplaceCSISequences
class ReplaceSGRSequences(StringFilter):
    def __init__(self, repl: AnyStr = ''):
        super().__init__(lambda s: re.sub(r'\033\[([0-9;]*)(m)', repl, s))


# less specific version of ReplaceSGRSequences,
# as CSI consists of SGR and many other seq sub-types
# find all CSI seqs (e.g. '\e[*') and replace with given string
class ReplaceCSISequences(StringFilter):
    def __init__(self, repl: AnyStr = ''):
        super().__init__(lambda s: re.sub(r'\033\[([0-9;:<=>?]*)([@A-Za-z])', repl, s))


# keep [0x00 - 0x7f], replace if greater than 0x7f
class ReplaceNonAsciiBytes(StringFilter):
    def __init__(self, repl: bytes = b'?'):
        super().__init__(lambda s: re.sub(b'[\x80-\xff]', repl, s))
