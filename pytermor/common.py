# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import enum
import itertools
import typing as t

T = t.TypeVar("T")
TT = t.TypeVar("TT", bound=type)


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


def chunk(items: t.Iterable[T], size: int) -> t.Iterator[t.Tuple[T, ...]]:
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


def flatten1(items: t.Iterable[t.Iterable[T]]) -> t.List[T]:
    """
    Take a list of nested lists and unpack all nested elements one level up.

    >>> flatten1([[1, 2, 3], [4, 5, 6], [[10, 11, 12]]])
    [1, 2, 3, 4, 5, 6, [10, 11, 12]]

    :param items:  Input lists.
    """
    return list(itertools.chain.from_iterable(items))


def flatten(items: t.Iterable[t.Iterable[T]]) -> t.List[T]:
    """
    @TODO @DRAFT didnt test it yet
    """
    return [*(flatten(f) for f in flatten1(items))]


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
    return str(obj)


def get_subclasses(cls: TT) -> t.Iterable[TT]:
    visited: t.Set[TT] = set()

    def fn(cls: TT):
        if cls in visited:
            return
        visited.add(cls)

        for subcls in cls.__subclasses__():
            fn(subcls)

    fn(cls)
    return visited
