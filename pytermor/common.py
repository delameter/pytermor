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

_T = t.TypeVar("_T")
_TT = t.TypeVar("_TT", bound=type)


class ExtendedEnum(enum.Enum):
    """
    Standard `Enum` with a few additional methods on top.


    """

    @classmethod
    def list(cls):
        """
        Return all enum values as list.

        :example:    [1, 10]
        """
        return list(map(lambda c: c.value, cls))

    @classmethod
    def dict(cls):
        """
        Return mapping of all enum keys to corresponding enum values.

        :example:   {<ExampleEnum.VAL1: 1>: 1, <ExampleEnum.VAL2: 10>: 10}
        """
        return dict(map(lambda c: (c, c.value), cls))


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
    if i1 < 0xd800 and i2 > 0xdfff:
        irange = (*range(i1, 0xd800), *range(0xe000, i2))
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
    if isinstance(obj, type):
        return "<" + obj.__name__ + ">"
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
