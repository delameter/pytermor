# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

import enum
import inspect
from typing import Type, Callable, TypeVar, Union
import logging

logger = logging.getLogger(__package__)
logger.addHandler(logging.NullHandler())

### catching library logs "from the outside":
# logger = logging.getLogger('pytermor')
# handler = logging.StreamHandler(sys.stderr)
# formatter = logging.Formatter('[%(levelname)5.5s][%(name)s][%(module)s] %(message)s')
# handler.setFormatter(formatter)
# logger.addHandler(handler)
# logger.setLevel('DEBUG')
########

FT = TypeVar("FT", int, str, "IColor", "Style", None)
"""
F
"""

RT = TypeVar("RT", str, "IRenderable")
"""
E
"""

CRT = TypeVar("CRT", bound=Union[str, "IRenderable"])
""" 
`CRT` in a method signature usually means that regular strings as well as 
`IRenderable` implementations are supported, can be intermixed, and:

    - return type will be *str* if and only if the type of all arguments is *str*;
    - otherwise return type will be `Text` -- *str* arguments, if any, will
      be transformed into IRenderable` and concatenated. `Text` type is used because
      it's the only IRenderable` that is mutable.

"""


class UserCancel(Exception):
    pass


class UserAbort(Exception):
    pass


class LogicError(Exception):
    pass


class ConflictError(Exception):
    pass


class ArgTypeError(Exception):
    """ """

    def __init__(self, actual_type: Type, arg_name: str = None, fn: Callable = None):
        arg_name_str = f'"{arg_name}"' if arg_name else "argument"
        # @todo suggestion
        # f = inspect.currentframe()
        # fp = f.f_back
        # fn = getattr(fp.f_locals['self'].__class__, fp.f_code.co_name)
        # argspec = inspect.getfullargspec(fn)
        if fn is None:
            try:
                stacks = inspect.stack()
                method_name = stacks[0].function
                outer_frame = stacks[1].frame
                fn = outer_frame.f_locals.get(method_name)
            except Exception:
                pass

        if fn is not None:
            expected_type = inspect.getfullargspec(fn).annotations[arg_name]
            actual_type = actual_type.__qualname__
            msg = f"Expected {arg_name_str} type: <{expected_type}>, got: <{actual_type}>"
        else:
            msg = f"Unexpected {arg_name_str} type: <{actual_type}>"

        super().__init__(msg)


class ArgCountError(Exception):
    """ """

    def __init__(self, actual: int, *expected: int) -> None:
        expected_str = ", ".join(str(e) for e in expected)
        msg = f"Invalid arguments amount, expected one of: ({expected_str}), got: {actual}"
        super().__init__(msg)


class Align(str, enum.Enum):
    """
    Align type for `FixedString` enum.
    """

    LEFT = "<"
    """ """
    RIGHT = ">"
    """ """
    CENTER = "^"
    """ """


