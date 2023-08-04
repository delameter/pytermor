# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import enum
import itertools
import typing as t
from collections.abc import Iterable
from functools import lru_cache

_T = t.TypeVar("_T")

_TT = t.TypeVar("_TT", bound=type)


CDT = t.TypeVar("CDT", int, str)
"""
:abbr:`CDT (Color descriptor type)` represents a RGB color value. Primary handler 
is `resolve_color()`. Valid values include:

    - *str* with a color name in any form distinguishable by the color resolver;
      the color lists can be found at: `guide.ansi-presets` and `guide.es7s-colors`;
    - *str* starting with a "#" and consisting of 6 more hexadecimal characters, case
      insensitive (RGB regular form), e.g. ":hex:`#0b0cca`";
    - *str* starting with a "#" and consisting of 3 more hexadecimal characters, case
      insensitive (RGB short form), e.g. ":hex:`#666`";
    - *int* in a [:hex:`0`; :hex:`0xffffff`] range.
"""

CT = t.TypeVar("CT", bound="IColor")
""" 
Any non-abstract ``IColor`` type.

:meta public:
 """

FT = t.TypeVar("FT", int, str, "IColor", "Style", None)
"""
:abbr:`FT (Format type)` is a style descriptor. Used as a shortcut precursor for actual 
styles. Primary handler is `make_style()`.
"""

RT = t.TypeVar("RT", str, "IRenderable")
"""
:abbr:`RT (Renderable type)` includes regular *str*\\ s as well as `IRenderable` 
implementations.
"""


class ExtendedEnum(enum.Enum):
    """
    Standard `Enum` with a few additional methods on top.


    """

    @classmethod
    @lru_cache
    def list(cls: t.Type[_T]) -> t.List[_T]:
        """
        Return all enum values as list.

        :example:    [1, 10]
        """
        return list(map(lambda c: c.value, cls))

    @classmethod
    @lru_cache
    def dict(cls: t.Type[_T]) -> t.Dict[str, _T]:
        """
        Return mapping of all enum keys to corresponding enum values.

        :example:   {<ExampleEnum.VAL1: 1>: 1, <ExampleEnum.VAL2: 10>: 10}
        """
        return dict(map(lambda c: (c, c.value), cls))

    @classmethod
    @lru_cache
    def rdict(cls: t.Type[_T]) -> t.Dict[_T, str]:
        return {v: k for k, v in cls.dict().items()}

    @classmethod
    @lru_cache
    def resolve_by_value(cls: t.Type[_T], val: _T) -> ExtendedEnum:
        if val in (rdict := cls.rdict()).keys():
            return rdict[val]
        msg = f"Invalid value {val!r}, should be one of: "
        msg += ", ".join(map(str, rdict.keys()))
        raise LookupError(msg)


class Align(str, ExtendedEnum):
    """
    Align type.
    """

    LEFT = "<"
    RIGHT = ">"
    CENTER = "^"

    @classmethod
    def resolve(cls, input: str | Align | None, fallback: Align = LEFT) -> Align | str:
        if input is None:
            return fallback
        if isinstance(input, cls):
            return input
        for k, v in cls.dict().items():
            if v == input:
                return k
        try:
            return cls[str(input).upper()]
        except KeyError as e:  # pragma: no cover
            raise KeyError(f"Invalid align name: {input}") from e


def only(cls: t.Type, inp: Iterable[_T]) -> t.List[_T]:
    return [*(a for a in inp if isinstance(a, cls))]


def but(cls: t.Type, inp: Iterable[_T]) -> t.List[_T]:
    return [*(a for a in inp if not isinstance(a, cls))]


def ours(cls: t.Type, inp: Iterable[_T]) -> t.List[_T]:
    return [*(a for a in inp if issubclass(type(a), cls))]


def others(cls: t.Type, inp: Iterable[_T]) -> t.List[_T]:
    return [*(a for a in inp if not issubclass(type(a), cls))]


def chunk(items: Iterable[_T], size: int) -> t.Iterator[t.Tuple[_T, ...]]:
    """
    Split item list into chunks of size ``size`` and return these
    chunks as *tuples*.

    >>> for c in chunk(range(5), 2):
    ...     print(c)
    (0, 1)
    (2, 3)
    (4,)

    :param items:  Input elements.
    :param size:   Chunk size.
    """
    arr_range = iter(items)
    return iter(lambda: tuple(itertools.islice(arr_range, size)), ())


def isiterable(arg) -> bool:  # pragma: no cover
    return isinstance(arg, Iterable) and not isinstance(arg, (str, bytes))


def flatten1(items: Iterable[Iterable[_T]]) -> t.List[_T]:
    """
    Take a list of nested lists and unpack all nested elements one level up.

    >>> flatten1([1, 2, [3, 4], [[5, 6]]])
    [1, 2, 3, 4, [5, 6]]

    """
    return flatten(items, level_limit=1)


def flatten(items: Iterable[_T | Iterable[_T]], level_limit: int = None) -> t.List[_T]:
    """
    Unpack a list with any amount of nested lists to 1d-array, or flat list,
    eliminating all the nesting. Note that nesting can be irregular, i.e. one part
    of initial list can have deepest elemenets on 3rd level, while the other --
    on 5th level.

    >>> flatten([1, 2, [3, [4, [[5]], [6, 7, [8]]]]])
    [1, 2, 3, 4, 5, 6, 7, 8]

    :param items:       An iterable to unpack.
    :param level_limit: Adjust how many levels deep can unpacking proceed, e.g.
                        if set to 1, only 2nd-level elements will be raised up
                        to level 1, but not the deeper ones. If set to 2, the
                        first two levels will be unpacked, while keeping the 3rd
                        and others. 0 or *None* disables the limit.
    """

    def _flatten(parent, lvl=0) -> Iterable[_T | Iterable[_T]]:
        if isiterable(parent):
            for child in parent:
                if isiterable(child):  # 2nd+ level, e.g. parent = [[1]]
                    if not level_limit or lvl < level_limit - 1:  # while below limit
                        yield from _flatten(child, lvl + 1)  # unpack recursively
                    else:  # keep the structure if limit exceeded
                        yield from child
                else:  # 1st level, e.g. parent = [1]
                    yield child
        else:  # 0th level, e.g. parent = 1
            yield parent

    return [*_flatten(items)]


def char_range(c1, c2):
    """
    Generates the characters from `c1` to `c2`, inclusive.
    """
    i1 = ord(c1)
    i2 = ord(c2) + 1

    # manually excluding UTF-16 surrogates from the range if there is
    # an intersection, as otherwise python will die with unicode error
    if i1 < 0xD800 and i2 > 0xDFFF:
        irange = (*range(i1, 0xD800), *range(0xE000, i2))
    else:
        irange = range(i1, i2)
    yield from map(chr, irange)


def get_qname(obj) -> str:
    """
    Convenient method for getting a class name for class instances
    as well as for the classes themselves.

    >>> get_qname("aaa")
    'str'
    >>> get_qname(ExtendedEnum)
    '<ExtendedEnum>'

    """
    if obj is None:
        return "None"
    if isinstance(obj, t.TypeVar) or hasattr(obj, "_typevar_types"):
        return f"<{obj!s}>"
    if isinstance(obj, type):
        return f"<{obj.__name__}>"
    if isinstance(obj, object):
        return obj.__class__.__qualname__
    return str(obj)  # pragma: no cover


def get_subclasses(cls: _TT) -> Iterable[_TT]:
    visited: t.Set[_TT] = set()

    def fn(cls: _TT):
        if cls in visited:  # pragma: no cover
            return
        visited.add(cls)

        for subcls in cls.__subclasses__():
            fn(subcls)

    fn(cls)
    return visited
