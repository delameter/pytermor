# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

import typing as t
import logging

logger = logging.getLogger(__package__)
logger.addHandler(logging.NullHandler())

### catching library logs "from the outside":
# logger = logging.getLogger('pytermor')
# handler = logging.StreamHandler(sys.stderr)
# logging.Formatter('[%(levelname)5.5s][%(name)s][%(module)s] %(message)s')
# handler.setFormatter(formatter)
# logger.addHandler(handler)
# logger.setLevel('DEBUG')
########

T = t.TypeVar("T")
""" `t.Any` """

StrType = t.TypeVar("StrType", bound=t.Union[str, "Renderable"])
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


class EmptyColorMapError(RuntimeError):
    def __init__(self, is_rgb: bool) -> None:
        msg = "Class color map is empty, cannot proceed."
        if is_rgb:
            msg += (
                "\nIf you want to approximate color in RGB mode, first you need to "
                "manually load colors to the map; the library does this for you "
                "only for Color16 and Color256 classes in order to minify memory "
                "consumption and speed up imports. See: pytermor.index_rgb.load()"
            )
        super().__init__(msg)
