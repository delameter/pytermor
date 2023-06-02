# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import inspect
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
    """ . """

    def __init__(self, var_name: str, arg_name: str = None, suggestion: str = None):
        arg_name = arg_name or var_name
        self.suggestion = suggestion
        self.context = {
            "name": arg_name,
            "arg_val": None,
            "var_val": None,
            "fn": None,
            "fname": None,
            "expected_type": None,
        }
        try:
            fb = inspect.currentframe().f_back
            self.context.update(dict(
                arg_val=fb.f_locals.get(arg_name),
                var_val=fb.f_locals.get(var_name),
            ))

            ff = inspect.getframeinfo(fb)
            try:
                fn = fb.f_globals.get(ff.function)
                assert fn
            except:
                fn = getattr(fb.f_locals.get("self"), ff.function)
                assert fn
            self.context.update(dict(fn=fn, fname=fn.__name__))

            fas = inspect.getfullargspec(fn)
            expected_type = fas.annotations.get(arg_name, None)
            assert expected_type
            self.context.update(dict(expected_type=expected_type))
        except:
            pass

        params = {
            "type": "Argument",
            "name": arg_name,
            "fname": self.context["fname"],
            "expected_type": self.context['expected_type'],
            "actual_type": get_qname(self.context["var_val"]),
        }
        if var_name != arg_name:
            params.update({"type": "Var", "name": var_name})

        msg = "%(type)s '%(name)s'"
        if self.context["fname"]:
            msg += "of %(fname)s()"
        if self.context["expected_type"]:
            msg += ": expected <%(expected_type)s>, got <%(actual_type)s>"
        else:
            msg += ": unexpected <%(actual_type)s>"

        msg %= params
        if self.suggestion:
            msg += f". Suggestion: {suggestion}"
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
