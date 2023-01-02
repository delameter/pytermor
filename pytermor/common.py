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
# handler = logging.StreamHandler()
# fmt = '[%(levelname)5.5s][%(name)s.%(module)s] %(message)s'
# handler.setFormatter(logging.Formatter(fmt))
# logger.addHandler(handler)
# logger.setLevel(logging.WARNING)
########


CDT = TypeVar("CDT", int, str)
"""
:abbr:`CDT (Color descriptor type)` represents a RGB color value. Primary handler 
is `resolve_color()`. Valid values include:

    - *str* with a color name in any form distinguishable by the color resolver;
      the color lists can be found at: `guide.ansi-presets` and `guide.es7s-colors`;
    - *str* starting with a "#" and consisting of 6 more hexadecimal characters, case
      insensitive (RGB regular form), e.g.: "#0B0CCA";
    - *str* starting with a "#" and consisting of 3 more hexadecimal characters, case
      insensitive (RGB short form), e.g.: "#666";
    - *int* in a [0; 0xFFFFFF] range.
"""

FT = TypeVar("FT", int, str, "IColor", "Style", None)
"""
:abbr:`FT (Format type)` is a style descriptor. Used as a shortcut precursor for actual 
styles. Primary handler is `make_style()`.
"""

RT = TypeVar("RT", str, "IRenderable")
"""
:abbr:`RT (Renderable type)` includes regular *str*\\ s as well as `IRenderable` 
implementations.
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


