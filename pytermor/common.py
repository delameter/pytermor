# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
"""
Shared code suitable for the package as well as any other.
"""
from __future__ import annotations

import enum
import inspect
import itertools
import logging
import math
import os
import re
import threading
import typing as t

F = t.TypeVar("F", bound=t.Callable[..., t.Any])


ESCAPE_SEQ_REGEX = re.compile(
    R"""
	(?P<escape_char>\x1b)
	(?P<data>
		(?P<nf_class_seq>
			(?P<nf_interm>[\x20-\x2f]+)
			(?P<nf_final>[\x30-\x7e])
		)|
		(?P<fp_class_seq>
			(?P<fp_classifier>[\x30-\x3f])
			(?P<fp_interm>[\x20-\x7e]*)
		)|
		(?P<fe_class_seq>
			(?P<fe_classifier>[\x40-\x5f])
			(?P<fe_param>[\x30-\x3f]*)
			(?P<fe_interm>[\x20-\x2f]*)
			(?P<fe_final>[\x40-\x7e]*)
		)|
		(?P<fs_class_seq>
			(?P<fs_classifier>[\x60-\x7e])
			(?P<fs_final>[\x20-\x7e])
		)  
	)
	""",
    flags=re.VERBOSE,
)
""" 
Regular expression that matches all classes of escape sequences.

More specifically, it recognizes **nF**, **Fp**, **Fe** and **Fs** [#]_ 
classes. Useful for removing the sequences as well as for granular search 
thanks to named match groups, which include:

    ``escape_byte``
        first byte of every sequence -- ``ESC``, or :hex:`0x1B`.
        
    ``data``
        remaining bytes of the sequence, excluding escape byte; contains
        no more than one of the following groups:
        
    ``nf_class_seq``, ``fp_class_seq``, ``fe_class_seq``, ``fs_class_seq``
        groups that contain ``data`` bytes. each of these is split to more
        specific groups including:
        
        - ``nf_interm`` and ``nf_final`` for **nF**-class sequences,
        - ``fp_classifier`` and ``fp_param`` for **Fp**-class sequences,
        - ``fe_classifier``, ``fe_param``, ``fe_interm`` and ``fe_terminator`` 
          for **Fe**-class sequences (including :term:`SGRs <SGR>`),
        - ``fs_classifier`` and ``fs_interm`` for **Fs**-class sequences.

.. [#] `ECMA-35 specification <https://ecma-international.org/publications-and-standards/standards/ecma-35/>`_

:meta hide-value:
"""

SGR_SEQ_REGEX = re.compile(r"(\x1b)(\[)([0-9;:]*)(m)")
"""
Regular expression that matches :term:`SGR` sequences. Group 3 can be used for 
sequence params extraction.

:meta hide-value:
"""

CSI_SEQ_REGEX = re.compile(r"(\x1b)(\[)(([0-9;:<=>?])*)([@A-Za-z])")
"""
Regular expression that matches CSI sequences (a superset which includes 
:term:`SGRs <SGR>`). 

:meta hide-value:
"""



class RGB(t.NamedTuple):
    red: int
    """ Red channel value (0—255) """
    green: int
    """ Green channel value (0—255) """
    blue: int
    """ Blue channel value (0—255) """

    def __str__(self):  # RGB(R=128, G=0, B=0)
        attrs = map(self._format_channel, ['red', 'green', 'blue'])
        return f"{self.__class__.__name__}({' '.join(attrs)})"

    def _format_channel(self, attr: str) -> str:
        return f'{attr[0].upper()}={getattr(self, attr):d}'


class HSV(t.NamedTuple):
    hue: float
    """ Hue channel value (0—360) """
    saturation: float
    """ Saturation channel value (0.0—1.0) """
    value: float
    """ Value channel value (0.0—1.0) """

    def __str__(self):  # HSV(H=0° S=100% V=50%)
        attrs = [
            f"H={self.hue:.0f}°",
            f"S={100*self.saturation:.0f}%",
            f"V={100*self.value:.0f}%",
        ]
        return f"{self.__class__.__name__}({' '.join(attrs)})"


class XYZ(t.NamedTuple):
    x: float
    """ X channel value (0.0—1.0+) """
    y: float
    """ Luminance (0.0—1.0) """
    z: float
    """ Quasi-equal to blue (0.0—1.0+) """

    def __str__(self):  # XYZ(X=0.95 Y=1.00 Z=1.08)
        attrs = [
            f"X={self.x:.3f}",
            f"Y={self.y:.3f}%",
            f"Z={self.z:.3f}",
        ]
        return f"{self.__class__.__name__}({' '.join(attrs)})"


class LAB(t.NamedTuple):
    L: float
    """ Luminance (0—100) """
    a: float
    """ Green–magenta axis (-100—100 in general, but can be less/more) """
    b: float
    """ Blue–yellow axis (-100—100 in general, but can be less/more) """

    def __str__(self):  # LAB(L=100% a=100 b=-100)
        attrs = [
            f"L={self.L:.3f}%",
            f"a={self.a:.3f}",
            f"b={self.b:.3f}",
        ]
        return f"{self.__class__.__name__}({' '.join(attrs)})"


LOGGING_TRACE = 5
logging.addLevelName(LOGGING_TRACE, "TRACE")

logger = logging.getLogger(__package__)
logger.addHandler(logging.NullHandler())

# _ catching library logs "from the outside" _______________________
#    logger = logging.getLogger('pytermor')
#    handler = logging.StreamHandler()
#    fmt = '[%(levelname)5.5s][%(name)s.%(module)s] %(message)s'
#    handler.setFormatter(logging.Formatter(fmt))
#    logger.addHandler(handler)
#    logger.setLevel(logging.WARNING)
# __________________________________________________________________


class ExtendedEnum(enum.Enum):
    """Standard `Enum` with a few additional methods on top."""

    @classmethod
    def list(cls):
        """
        Return all enum values as list.

        >>> Align.list()
        ['<', '>', '^']

        """
        return list(map(lambda c: c.value, cls))

    @classmethod
    def dict(cls):
        """
        Return mapping of all enum keys to corresponding enum values.

        >>> Align.dict()
        {<Align.LEFT: '<'>: '<', <Align.RIGHT: '>'>: '>', <Align.CENTER: '^'>: '^'}

        """
        return dict(map(lambda c: (c, c.value), cls))


class Align(str, ExtendedEnum):
    """
    Align type.
    """

    LEFT = "<"
    RIGHT = ">"
    CENTER = "^"

    @classmethod
    def resolve(cls, input: str | Align | None, fallback: Align = LEFT):
        if input is None:
            return fallback
        if isinstance(input, cls):
            return input
        for k, v in cls.dict().items():
            if v == input:
                return k
        try:
            return cls[input.upper()]
        except KeyError:
            logger.warning(f"Invalid align name: {input}")
            return fallback


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

    def __init__(self, actual_type: t.Type, arg_name: str = None, fn: t.Callable = None):
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
            signature = inspect.signature(fn)
            param_desc = signature.parameters.get(arg_name, None)
            expected_type = "?"
            if param_desc:
                expected_type = param_desc.annotation
            actual_type = actual_type.__qualname__
            msg = (
                f"Expected {arg_name_str} type: <{expected_type}>, got: <{actual_type}>"
            )
        else:
            msg = f"Unexpected {arg_name_str} type: <{actual_type}>"

        super().__init__(msg)


class ArgCountError(Exception):
    """ """

    def __init__(self, actual: int, *expected: int) -> None:
        expected_str = ", ".join(str(e) for e in expected)
        msg = (
            f"Invalid arguments amount, expected one of: ({expected_str}), got: {actual}"
        )
        super().__init__(msg)


ALIGN_LEFT = Align.LEFT
""" Left align (add padding on the right side, if necessary). """
ALIGN_RIGHT = Align.RIGHT
""" Right align (add padding on the left side, if necessary). """
ALIGN_CENTER = Align.CENTER
""" Center align (add paddings on both sides evenly, if necessary). """


def get_qname(obj: t.Any) -> str:
    """
    Convenient method for getting a class name for class instances
    as well as for the classes themselves. Suitable for debug output in
    ``__repr__`` methods, for example.

    >>> get_qname("aaa")
    'str'
    >>> get_qname(threading.Thread)
    'Thread'

    """
    if isinstance(obj, type):
        return obj.__qualname__
    if isinstance(obj, object):
        return obj.__class__.__qualname__
    return str(obj)


def get_terminal_width(fallback: int = 80, pad: int = 2) -> int:
    """
    Return current terminal width with an optional "safety buffer", which
    ensures that no unwanted line wrapping will happen.

    :param fallback: Default value when shutil is unavailable and environment
                     variable COLUMNS is unset.
    :param pad:      Additional safety space to prevent unwanted line wrapping.
    """
    try:
        import shutil as _shutil

        return _shutil.get_terminal_size().columns - pad
    except ImportError:
        pass

    try:
        return int(os.environ.get("COLUMNS", fallback))
    except ValueError:
        pass

    return fallback


def get_preferable_wrap_width(force_width: int = None) -> int:
    """
    Return preferable terminal width for comfort reading of wrapped text (max=120).

    :param force_width:
               Ignore current terminal width and use this value as a result.
    """
    if isinstance(force_width, int) and force_width > 1:
        return force_width
    return min(120, get_terminal_width())


T = t.TypeVar("T")


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
    .. todo ::
        recursrive
    """


def percentile(
    N: t.Sequence[float], percent: float, key: t.Callable[[float], float] = lambda x: x
) -> float:
    """
    Find the percentile of a list of values.

    :param N:        List of values. MUST BE already sorted.
    :param percent:  Float value from 0.0 to 1.0.
    :param key:      Optional key function to compute value from each element of N.
    """
    # origin: https://code.activestate.com/recipes/511478/

    if not N:
        raise ValueError("N should be a non-empty sequence of floats")
    k = (len(N) - 1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return key(N[int(k)])
    d0 = key(N[int(f)]) * (c - k)
    d1 = key(N[int(c)]) * (k - f)
    return d0 + d1


def median(N: t.Sequence[float], key: t.Callable[[float], float] = lambda x: x) -> float:
    """
    Find the median of a list of values.
    Wrapper around `percentile()` with fixed ``percent`` argument (=0.5).

    :param N:    List of values. MUST BE already sorted.
    :param key:  Optional key function to compute value from each element of N.
    """
    return percentile(N, percent=0.5, key=key)
