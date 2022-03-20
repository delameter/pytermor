# ------------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import re
from typing import Callable, AnyStr


class StringFilter:
    def __init__(self, fn: Callable):
        self._fn = fn

    def __call__(self, s: str):
        return self._fn(s)


class ReplaceSGRSequences(StringFilter):
    def __init__(self, repl: AnyStr = '.'):
        super().__init__(lambda s: re.sub(r'\033\[([0-9;:<=>?]*)([@A-Za-z])', repl, s))


class ReplaceNonAsciiCharacters(StringFilter):
    def __init__(self, repl: AnyStr = '.'):
        super().__init__(lambda s: re.sub(r'[^\x00-\x7f]', repl, s))

