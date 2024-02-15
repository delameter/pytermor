# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
"""
Functions and classes commonly used throughout the library.
"""
from __future__ import annotations

import builtins
import enum
import itertools
import typing as t
from collections import OrderedDict
from collections.abc import Iterable
from dataclasses import dataclass
from functools import lru_cache, partial
from math import ceil

_T = t.TypeVar("_T")
_KT = t.TypeVar("_KT")
_VT = t.TypeVar("_VT")
_TT = t.TypeVar("_TT", bound=type)


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


@dataclass
class CacheStats:
    hits: int = 0
    misses: int = 0
    cursize: int = 0
    maxsize: int = 0

    @property
    def hit_ratio(self) -> float:
        return self.hits / ((self.hits + self.misses) or 1)

    def format(self) -> str:
        from .numfmt import format_thousand_sep

        return "%s hits, %s misses (%3.1f%% ratio), size %d/%d" % (
            format_thousand_sep(self.hits),
            format_thousand_sep(self.misses),
            100 * self.hit_ratio,
            self.cursize,
            self.maxsize,
        )


# -----------------------------------------------------------------------------
# strings

OVERFLOW_CHAR = "‥"


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


def pad(n: int = 1) -> str:
    """
    Convenient method to use instead of ``\"\".ljust(n)``.
    """
    return " " * n


def padv(n: int = 1) -> str:
    """
    Convenient method to use instead of ``"\\n\" * n``.
    """
    return "\n" * n


def cut(
    string: str,
    max_len: int,
    align: Align | str = Align.LEFT,
    *,
    keep: Align | str = Align.LEFT,
    overflow=OVERFLOW_CHAR,
) -> str:
    """
    cut

    :param string:
    :param max_len:
    :param align:
    :param keep:
    :param overflow:
    """
    if len(string) <= max_len:
        return string
    return fit(string, max_len, align, keep=keep, overflow=overflow)


def fit(
    string: str,
    max_len: int,
    align: Align | str = Align.LEFT,
    *,
    keep: Align | str = Align.LEFT,
    overflow: str = OVERFLOW_CHAR,
    fill: str = " ",
) -> str:
    """
    fit
    :param string:
    :param max_len:
    :param align:
    :param keep:
    :param overflow:
    :param fill:
    """
    align = Align.resolve(align)
    keep = Align.resolve(keep, fallback=Align.LEFT)

    if max_len <= 0:
        return ""
    if len(fill) == 0:  # pragma: no cover
        raise ValueError("Fill cannot be an empty string")

    max_len = max(0, max_len)
    ov_len = len(overflow)
    if max_len <= ov_len and max_len < len(string):
        return fit("", max_len, align, keep=keep, overflow="", fill=overflow)

    # excessive space or tight fit
    if (fill_len := max_len - len(string)) >= 0:
        fill_pnum = ceil(fill_len / len(fill))
        fill_full = fit(fill * fill_pnum, fill_len, align, keep=keep, overflow="")

        if align == Align.LEFT:
            return string + fill_full
        if align == Align.RIGHT:
            return fill_full + string
        fillmid = len(fill_full) // 2
        return fill_full[:fillmid] + string + fill_full[fillmid:]

    # not enough space
    if keep == Align.LEFT:
        return string[: max_len - ov_len] + overflow
    if keep == Align.RIGHT:
        return overflow + string[-max_len + ov_len :]
    s_chars = max_len - ov_len
    left_part = s_chars // 2
    right_part = s_chars - left_part
    return string[:left_part] + overflow + string[-right_part:]


# -----------------------------------------------------------------------------
# types


def instantiate(bound: t.Type[_T], subject: str | t.Type[_T] | _T, default=None) -> _T | None:
    """
    Instantiate a class by a definition ``subject`` and ensure that it is
    an instance of ``bound`` argument or a subclass of it. ``subject`` can be
    either:

        - a qualified class name as a string, e.g. 'logging.StreamHandler'
        - a local class name as a string, e.g. 'SgrRenderer'
        - a type, e.g. `logging.StreamHandler` or `pytermor.SgrRenderer`
        - an instance, e.g. `logging.StreamHandler()` or
          `pytermor.SgrRenderer()`, in which case a function does not create
          any new instances, just performs the type check.

    The return value is guaranteed to be a subclass of ``bound``: either
    instantiated from ``subject`` definition, or, if that attempt fails for
    some reason, an instance provided as a ``default``. The only exception to
    this is when a ``default`` is not a subclass of ``bound`` itself, in which
    case **None** will be returned, should the instantiating OR type checking
    fail.

    :param subject:  required type of the instance defined as a *str* or *type*,
                     or already instantiated object of ``bound`` type
    :param bound:    type or supertype of the result
    :param default:  fallback result which is returned if an instantiating or
                     type, checking fail; must be an instance or a subclass of
                     ``bound``, or it will be replaced with **None**
    :return:         instance defined in ``subject`` or a ``default``
    :rtype:          ``bound`` or its subclass, or *None*
    """
    if default is not None:
        default = instantiate(bound, default)

    if isinstance(subject, bound):
        return subject

    cls = None
    if isinstance(subject, type) and issubclass(subject, bound):
        cls = subject
    elif isinstance(subject, str):
        if "." in subject:
            pkgname, _, clsname = subject.rpartition(".")
        else:
            pkgname, clsname = __package__, subject
        try:
            cls = getattr(__import__(pkgname), clsname)
        except AttributeError:
            return default

    if cls is not None:
        try:
            return cls()
        except TypeError:
            pass
    return default


def get_qname(obj: any, *, name_only=False) -> str:
    """
    Convenient method for getting a class name for the instances as well as
    for the classes themselves, in case where a variable in question can be both.

    >>> get_qname("aaa")
    'str'
    >>> get_qname(ExtendedEnum)
    '<ExtendedEnum>'

    """
    if obj is None:
        return "None"
    if isinstance(obj, t.TypeVar) or hasattr(obj, "_typevar_types"):
        return str(obj) if name_only else f"<{obj!s}>"
    if isinstance(obj, type):
        return obj.__name__ if name_only else f"<{obj.__name__}>"
    if isinstance(obj, object):
        if obj.__class__.__name__ == "method":
            return obj.__qualname__
        return obj.__class__.__qualname__
    return str(obj)  # pragma: no cover


def only(cls: t.Type, inp: Iterable[_T]) -> t.List[_T]:
    """Return all elements from `inp` that *are* instances of `cls`."""
    return [*(a for a in inp if isinstance(a, cls))]


def but(cls: t.Type, inp: Iterable[_T]) -> t.List[_T]:
    """Return all elements from `inp` *except* instances of `cls`."""
    return [*(a for a in inp if not isinstance(a, cls))]


def ours(cls: t.Type, inp: Iterable[_T]) -> t.List[_T]:
    """Return all elements from `inp` that *are* instances of `cls` or its children classes."""
    return [*(a for a in inp if issubclass(type(a), cls))]


def others(cls: t.Type, inp: Iterable[_T]) -> t.List[_T]:
    """Return all elements from `inp` *except* instances of `cls` and its children classes."""
    return [*(a for a in inp if not issubclass(type(a), cls))]


def chunk(items: Iterable[_T], size: int) -> t.Iterator[t.Tuple[_T, ...]]:
    """
    Split item list into chunks of size ``size`` and return these
    chunks as *tuples*.

    >>> ', '.join(map(str, chunk(range(10), 3)))
    '(0, 1, 2), (3, 4, 5), (6, 7, 8), (9,)'

    :param items:  Input elements.
    :param size:   Chunk size.
    """
    arr_range = iter(items)
    return iter(lambda: tuple(itertools.islice(arr_range, size)), ())


def get_subclasses(target: _T) -> Iterable[t.Type[_T]]:
    """
    Traverse the inheritance tree and return a flat list of
    all descendants of `cls` (full hierarchy).

    >>> from pytermor import SequenceCSI, Color16
    >>> get_subclasses(SequenceCSI())
    [<class 'pytermor.ansi.SequenceSGR'>, <class 'pytermor.ansi._NoOpSequenceSGR'>]

    >>> get_subclasses(Color16)
    []

    :param target:
    """
    if not isinstance(target, type):
        target = type(target)

    visited: t.OrderedDict[_TT] = OrderedDict()
    # using ordered dict keys as an *ordered set*

    def fn(_cls: _TT):
        if _cls in visited:  # pragma: no cover
            return
        visited.update({_cls: None})

        if not hasattr(_cls, "__subclasses__"):  # pragma: no cover
            return
        for sub in type.__subclasses__(_cls):
            fn(sub)

    fn(target)

    result = [*visited.keys()]
    result.remove(target)
    return result


def ismutable(arg: any) -> bool:  # pragma: no cover
    """
    Test ``arg`` for mutability. Only build-in types are supported.
    Mutability is determined by trying to compute a hash of an argument.
    """
    return not isimmutable(arg)


def isimmutable(arg: any) -> bool:
    if not hasattr(builtins, type(arg).__name__):
        raise TypeError(f"Only built-in types are supported, got: {get_qname(arg)}")
    try:
        hash(arg)
        return True
    except TypeError:
        return False


isimmutable.__doc__ = ismutable.__doc__


def isiterable(arg: any) -> bool:  # pragma: no cover
    """
    Test if ``arg`` is an *Iterable*.

    .. important ::
        This method was designed for traversing sequences and was
        explicitly implemented not to count *str*, *bytes* and *bytearrays*
        as iterables to prevent breaking them down in a recursive descent
        algorithms.
    """
    return isinstance(arg, Iterable) and not isinstance(arg, (str, bytes, bytearray))


# -----------------------------------------------------------------------------
# iterables


def flatten1(items: Iterable[Iterable[_T]]) -> t.List[_T]:
    """
    Take a list of nested lists and unpack all nested elements one level up.

    >>> flatten1([1, 2, [3, 4], [[5, 6]]])
    [1, 2, 3, 4, [5, 6]]

    """
    return flatten(items, level_limit=1)


def flatten(
    items: Iterable[_T | Iterable[_T]],
    level_limit: int = 0,
    *,
    track=False,
    catch=False,
) -> t.List[_T]:
    """
    Unpack a list consisting of any amount of nested lists to 1d-array, or flat list,
    eliminating all the nesting. Note that nesting can be irregular, i.e. one part
    of initial list can have deepest elements on 3rd level, while the other --
    on 5th level.

    .. attention ::

        Tracking of visited objects is not performed by default, i.e., circular
        references and self-references will be unpacked again and again endlessly,
        until recursion limit is exceeded with a ``RecursionError``. The tracking
        can be enabled via setting ``track`` parameter to True.

        Another option is to set ``catch`` parameter to True, which makes the
        function stop and return upon receiveing a ``RecursionError`` instead of
        propagating it further.

    >>> flatten([1, 2, [3, [4, [[5]], [6, 7, [8]]]]])
    [1, 2, 3, 4, 5, 6, 7, 8]

    :param items:       N-dimensional iterable to unpack.
    :param level_limit: Adjust how many levels deep can unpacking proceed, e.g.
                        if set to 1, only 2nd-level elements will be raised up
                        to level 1, but not the deeper ones. If set to 2, the
                        first two levels will be unpacked, while keeping the 3rd
                        and others. 0 disables the limit.

                        Note that altering/disabling this limit doesn't affect
                        max recursion depth limiting mechanism, which will (sooner
                        or later) interrupt the attempt to descent on a hierarchy
                        with a self-referencing object or several objects forming
                        a circular reference(s).

    :param track:       Setting to *True* enables tracking mechanism which forbids
                        descending into already visited items for a second time,
                        thus allowing to flatten circular- and/or self-referencing
                        structures.
    :param catch:       Setting to *True* suppresses RecursionError, and instead
                        of raising an exception the function just stops descending
                        further.
    """
    _seen = set()

    def _iter(parent, lvl=0) -> Iterable[_T | Iterable[_T]]:
        if track:
            if (pid := id(parent)) in _seen:
                return
            _seen.add(pid)

        if isiterable(parent):
            if level_limit and lvl >= level_limit:
                yield from parent  # stop descending
            else:
                for child in parent:
                    try:
                        yield from _iter(child, lvl + 1)
                    except RecursionError:
                        if catch:
                            return
                        raise
        else:
            yield parent

    return [*_iter(items)]


def flip_unpack(d: dict[_KT, Iterable[_VT]]) -> dict[_VT, _KT]:
    """
    Unpack each value of a dictionary and return a new dictionary with unpacked
    values mapped as keys and with corresponding keys as values.

    >>> flip_unpack({1: ['a', 'b', 'c'], 2: ['d', 'e', 'f']})
    {'a': 1, 'b': 1, 'c': 1, 'd': 2, 'e': 2, 'f': 2}

    :param d: dictionary in form {key1: [val1, val2, ...], key2: [val3, val4, ...], ...}
    :return:  dictionary in form  {val1: key1, val2: key1, ..., val3: key2, val4: key2, ...}
    """
    return {v: k for k, vv in d.items() for v in vv}


def char_range(start: str, stop: str):
    """
    Yields all the characters from range of [`c1`; `c2`], inclusive
    (end character `c2` is **also present**, in contrast with classic
    `range()`, which excludes ``stop`` value from the results).

    >>> ''.join(char_range('₁', '₉'))
    '₁₂₃₄₅₆₇₈₉'

    .. note ::

        In some cases the result will seem to be incorrect, i.e. this:
        `pt.char_range('¹', '⁴')` yields 8124 characters total. The reason
        is that the algoritm works with input characters as Unicode codepoints,
        and '¹', '⁴' are relatively distant from each other: "¹" :hex:`U+B9`,
        "⁴" :hex:`Ux2074`, which leads to an unexpected results. Character
        ranges in Python regular expessetions, e.g. `[¹-⁴]`, work the same way.

    :param start; Character to start from (inclusive)
    :param stop;  Character to stop at (**inclusive**)
    """
    start_code = ord(start)
    stop_code = ord(stop) + 1

    # manually excluding UTF-16 surrogates from the range if there is
    # an intersection, as otherwise python will die with unicode error
    if start_code < 0xD800 and stop_code > 0xDFFF:
        codes = (*range(start_code, 0xD800), *range(0xE000, stop_code))
    else:
        codes = range(start_code, stop_code)
    yield from map(chr, codes)


# -----------------------------------------------------------------------------
# none/false/empty handling

_isnotnone = lambda v: v is not None
_istruly = lambda v: bool(v)
_isfilled = lambda v: bool(v) and len(str(v).strip())


def _first(items: t.Iterable[_T]) -> _T | None:
    # can be a generator so we should not access length property
    for item in items:
        return item
    return None


filtern = partial(filter, _isnotnone)
"""Shortcut for filtering out Nones from sequences."""

filterf = partial(filter, _istruly)
"""Shortcut for filtering out falsy values from sequences."""

filtere = partial(filter, _isfilled)
"""Shortcut for filtering out falsy AND empty values from sequences."""


def filternv(mapping: dict[_KT, _VT]) -> dict[_KT, _VT]:
    """Shortcut for filtering out None values from mappings."""
    return dict(filter(lambda kv: _isnotnone(kv[1]), mapping.items()))


def filterfv(mapping: dict[_KT, _VT]) -> dict[_KT, _VT]:
    """Shortcut for filtering out falsy values from mappings."""
    return dict(filter(lambda kv: _istruly(kv[1]), mapping.items()))


def filterev(mapping: dict[_KT, _VT]) -> dict[_KT, _VT]:
    """Shortcut for filtering out falsy AND empty values from mappings."""
    return dict(filter(lambda kv: _isfilled(kv[1]), mapping.items()))


def coaln(*arg: _T) -> _T | None:
    """Return first ``arg`` that is not **None**"""
    return _first(filtern(arg))


def coalf(*arg: _T) -> _T | None:
    """Return first non-falsy ``arg``"""
    return _first(filterf(arg))


def coale(*arg: _T) -> _T | None:
    """Return first non-empty ``arg``"""
    return _first(filtere(arg))


def joinn(*arg: any, sep="") -> str:
    """Drop all *Nones* from ``args``, map the rest to *str* and join them with ``sep``."""
    return sep.join(map(str, filtern(arg)))


def joinf(*arg: any, sep="") -> str:
    """Drop all falsy values from ``args``, map the rest to *str* and join them with ``sep``."""
    return sep.join(map(str, filtern(arg)))


def joine(*arg: any, sep="") -> str:
    """Drop all empty valuues ``args``, map the rest to *str* and join them with ``sep``."""
    return sep.join(map(str, filtern(arg)))
