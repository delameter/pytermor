# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

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

T = TypeVar("T")
""" `t.Any` """

StrType = TypeVar("StrType", bound=Union[str, "Renderable"])
""" 
`StrType` in a method signature usually means that regular strings as well as 
`Renderable` implementations are supported, can be intermixed, and:

    - return type will be *str* if and only if type of all arguments is *str*;
    - otherwise return type will be `Renderable` -- *str* arguments, if any, will
      be transformed into `Renderable` and concatenated.

"""


class LogicError(Exception):
    pass


class ConflictError(Exception):
    pass


class ArgTypeError(Exception):
    """

    """
    def __init__(self, actual_type: Type, arg_name: str = None, fn: Callable = None):
        arg_name_str = f'"{arg_name}"' if arg_name else "argument"
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
