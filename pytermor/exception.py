# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import typing as t

from .common import get_qname


class LogicError(Exception):
    pass


class ParseError(Exception):
    def __init__(self, groupdict: dict):
        self.groupdict = groupdict
        msg = f"Failed to match sequence class for: '{self.groupdict}'"
        super().__init__(msg)


class ConflictError(Exception):
    pass


class ArgTypeError(Exception):
    """."""

    MESSAGE_TPL = "Argument '%s': expected %s, got %s"

    def __init__(
        self,
        arg_value: t.Any,
        arg_name: str,
        *expected_type: t.Type | None,
        suggestion: str = None,
    ):
        msg = self.MESSAGE_TPL % (
            arg_name,
            "|".join(get_qname(etype) for etype in expected_type),
            get_qname((arg_value)),
        )
        if suggestion:
            msg += f". Suggestion: {suggestion}"
        super().__init__(msg)


class ArgCountError(Exception):
    def __init__(self, actual: int, *expected: int) -> None:
        expected_str = ", ".join(str(e) for e in expected)
        msg = f"Invalid arguments amount, expected one of: ({expected_str}), got: {actual}"
        super().__init__(msg)


class UserCancel(Exception):
    pass


class UserAbort(Exception):
    pass


class ColorNameConflictError(Exception):
    def __init__(self, tokens: t.Tuple[str], existing_color, new_color):
        msg = f"Color '{new_color.name}' -> {tokens} already exists"
        super().__init__(msg, [existing_color, new_color])


class ColorCodeConflictError(Exception):
    def __init__(self, code: int, existing_color, new_color):
        msg = f"Color #{code} already exists"
        super().__init__(msg, existing_color, new_color)
