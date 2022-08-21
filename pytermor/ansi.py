# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""
Module contains definitions for low-level ANSI escape sequences handling.

The key difference beetween ``Spans`` and ``Sequences`` is that sequence can
*open* text style and also *close*, or terminate it. As for ``Spans`` -- they
always do both; typical use-case of `Span` is to wrap some text in opening SGR
and closing one.

Each variable in `Seqs` and `Spans` below is a valid argument
for :class:`.Span` and :class:`.SequenceSGR` default constructors; furthermore,
it can be passed in a string form (case-insensitive):

.. testsetup:: *

    from pytermor import SequenceSGR, Spans, Span, Seqs, IntCodes, NOOP_SPAN, NOOP_SEQ

>>> Span('BG_GREEN')
Span[SGR[42], SGR[49]]

>>> Span(Seqs.BG_GREEN, Seqs.UNDERLINED)
Span[SGR[42;4], SGR[49;24]]

"""
from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import List, Any
from .registry import IntCodes


class Sequence(metaclass=ABCMeta):
    """
    Abstract ancestor of all escape sequences.
    """
    def __init__(self, *params: int):
        self._params: List[int] = [max(0, int(p)) for p in params]

    @abstractmethod
    def assemble(self) -> str:
        """
        Build up actual byte sequence and return
        as an ASCII-encoded string.
        """
        raise NotImplementedError

    @property
    def params(self) -> List[int]:
        """ Return internal params as array. """
        return self._params

    @classmethod
    @abstractmethod
    def _short_class_name(cls): raise NotImplementedError

    def __eq__(self, other: Sequence):
        if type(self) != type(other):
            return False
        return self._params == other._params

    def __repr__(self):
        params = ";".join([str(p) for p in self._params])
        if len(self._params) == 0:
            params = '^'
        return f'{self._short_class_name()}[{params}]'


class SequenceCSI(Sequence, metaclass=ABCMeta):
    """
    Abstract class representing CSI-type ANSI escape sequence. All subtypes
    of this sequence start with :kbd:`\\e[`.
    """
    _CONTROL_CHARACTER = '\x1b'
    _INTRODUCER = '['
    _SEPARATOR = ';'

    def __init__(self, *params: int):
        super(SequenceCSI, self).__init__(*params)

    def __str__(self) -> str:
        return self.assemble()

    @classmethod
    def regexp(cls) -> str:
        return f'\\x1b\\[[0-9;]*{cls._terminator()}'

    @classmethod
    @abstractmethod
    def _terminator(cls) -> str: raise NotImplementedError


class SequenceSGR(SequenceCSI, metaclass=ABCMeta):
    """
    Class representing SGR-type escape sequence with varying amount of parameters.

    `SequenceSGR` with zero params was specifically implemented to
    translate into empty string and not into :kbd:`\\e[m`, which would have
    made sense, but also would be very entangling, as this sequence is
    equivalent of :kbd:`\\e[0m` -- hard reset sequence. The empty-string-sequence
    is predefined as `NOOP_SEQ`.

    It's possible to add of one SGR sequence to another:

    >>> SequenceSGR(31) + SequenceSGR(1) == SequenceSGR(31, 1)
    True

    """
    _TERMINATOR = 'm'

    def __init__(self, *args: str|int|SequenceSGR):
        """
        Create new `SequenceSGR` with specified ``args`` as params.

        Resulting sequence param order is same as an argument order.

        Each sequence param can be specified as:
          - string key (name of any constant defined in `IntCodes`, case-insensitive)
          - integer param value (``IntCodes`` values)
          - existing ``SequenceSGR`` instance (params will be extracted).

        >>> SequenceSGR('yellow', 'bold')
        SGR[33;1]
        >>> SequenceSGR(91, 7)
        SGR[91;7]
        >>> SequenceSGR(IntCodes.HI_CYAN, IntCodes.UNDERLINED)
        SGR[96;4]
        """
        result: List[int] = []

        for arg in args:
            if isinstance(arg, str):
                resolved_param = IntCodes.resolve(arg)
                if not isinstance(resolved_param, int):
                    raise ValueError(f'Attribute is not valid SGR param: {resolved_param}')
                result.append(resolved_param)
            elif isinstance(arg, int):
                result.append(arg)
            elif isinstance(arg, SequenceSGR):
                result.extend(arg.params)
            else:
                raise TypeError(f'Invalid argument type: {arg!r})')

        super().__init__(*result)

    @classmethod
    def init_color_indexed(cls, idx: int, bg: bool = False) -> SequenceSGR:
        """
        Wrapper for creation of `SequenceSGR` that sets foreground
        (or background) to one of 256-color pallete value.

        :param idx:  Index of the color in the pallete, 0 -- 255.
        :param bg:    Set to *True* to change the background color
                      (default is foreground).
        :return:      `SequenceSGR` with required params.
        """

        cls._validate_extended_color(idx)
        key_code = IntCodes.BG_COLOR_EXTENDED if bg else IntCodes.COLOR_EXTENDED
        return SequenceSGR(key_code, IntCodes.EXTENDED_MODE_256, idx)

    @classmethod
    def init_color_rgb(cls, r: int, g: int, b: int, bg: bool = False) -> SequenceSGR:
        """
        Wrapper for creation of `SequenceSGR` operating in True Color mode (16M).
        Valid values for *r*, *g* and *b* are in range [0; 255]. This range
        linearly translates into [``0x00``; ``0xFF``] for each channel. The result
        value is composed as ``#RRGGBB``. For example, sequence with color of
        ``#FF3300`` can be created with::

            SequenceSGR.init_color_rgb(255, 51, 0)

        :param r:  Red channel value, 0 -- 255.
        :param g:  Blue channel value, 0 -- 255.
        :param b:  Green channel value, 0 -- 255.
        :param bg: Set to *True* to change the background color
                   (default is foreground).
        :return:   `SequenceSGR` with required params.
        """

        [cls._validate_extended_color(color) for color in [r, g, b]]
        key_code = IntCodes.BG_COLOR_EXTENDED if bg else IntCodes.COLOR_EXTENDED
        return SequenceSGR(key_code, IntCodes.EXTENDED_MODE_RGB, r, g, b)

    def assemble(self) -> str:
        if len(self._params) == 0:  # NOOP
            return ''

        params = self._params
        if params == [0]:  # \x1b[0m <=> \x1b[m, saving 1 byte
            params = []

        return (self._CONTROL_CHARACTER +
                self._INTRODUCER +
                self._SEPARATOR.join([str(param) for param in params]) +
                self._TERMINATOR)

    def __add__(self, other: SequenceSGR) -> SequenceSGR:
        self._ensure_sequence(other)
        return SequenceSGR(*self._params, *other._params)

    def __radd__(self, other: SequenceSGR) -> SequenceSGR:
        return other.__add__(self)

    def __iadd__(self, other: SequenceSGR) -> SequenceSGR:
        return self.__add__(other)

    def __eq__(self, other: SequenceSGR):
        if type(self) != type(other):
            return False
        return self._params == other._params

    @staticmethod
    def _ensure_sequence(subject: Any):
        if not isinstance(subject, SequenceSGR):
            raise TypeError(f'Expected SequenceSGR, got {type(subject)}')

    @staticmethod
    def _validate_extended_color(value: int):
        if value < 0 or value > 255:
            raise ValueError(
                f'Invalid color value: expected range [0-255], got: {value}')

    @classmethod
    def _terminator(cls) -> str:
        return cls._TERMINATOR

    @classmethod
    def _short_class_name(cls) -> str:
        return 'SGR'


# noinspection PyMethodMayBeStatic
class Span:
    """
    Class consisting of two `SequenceSGR` instances -- the first one, "opener",
    tells the terminal that's it should format subsequent characters as specified,
    and the second one, which reverses the effects of the  first one.
    """
    def __init__(self, *opening_params: str|int|SequenceSGR):
        """
        Create a `Span` with specified control sequence(s) as an opening sequence
        and **automatically compose** second (closing) sequence that will terminate
        attributes defined in the first one while keeping the others (*soft* reset).

        Resulting sequence param order is same as an argument order.

        Each argument can be specified as:
          - string key (name of any constant defined in `IntCodes`, case-insensitive)
          - integer param value (``IntCodes`` values)
          - existing `SequenceSGR` instance (params will be extracted).

        >>> Span('red', 'bold')
        Span[SGR[31;1], SGR[39;22]]
        >>> Span(IntCodes.GREEN)
        Span[SGR[32], SGR[39]]
        >>> Span(93, 4)
        Span[SGR[93;4], SGR[39;24]]
        >>> Span(Seqs.BG_BLACK + Seqs.RED)
        Span[SGR[40;31], SGR[49;39]]

        :param opening_params: string keys, integer codes or existing ``SequenceSGR``
                               instances to build ``Span`` from.
        """
        self._opening_seq = SequenceSGR(*opening_params)
        if len(opening_params) == 0:
            self._closing_seq = SequenceSGR()
            return

        from .registry.seqs import _SgrPairityRegistry
        self._closing_seq = _SgrPairityRegistry.get_closing_seq(self._opening_seq)

    @classmethod
    def init_explicit(cls, opening_seq: SequenceSGR = None,
                      closing_seq: SequenceSGR = None,
                      hard_reset_after: bool = False) -> Span:
        """
        Create new `Span` with explicitly specified opening and closing sequences.

        .. note ::
            `closing_seq` gets overwritten with `Seqs.RESET` if ``hard_reset_after`` is *True*.

        :param opening_seq:      Starter sequence, in general determening how `Span` will actually look like.
        :param closing_seq:      Finisher SGR sequence.
        :param hard_reset_after: Terminate *all* formatting after this span.
        """
        instance = Span()
        instance._opening_seq = cls._opt_arg(opening_seq)
        instance._closing_seq = cls._opt_arg(closing_seq)

        if hard_reset_after:
            from .registry import Seqs
            instance._closing_seq = Seqs.RESET

        return instance

    def wrap(self, text: Any = None) -> str:
        """
        Wrap given ``text`` string with ``SGRs`` defined on initialization -- `opening_seq`
        on the left, `closing_seq` on the right. ``str(text)`` will
        be invoked for all argument types with the exception of *None*,
        which will be replaced with an empty string.

        :param text:  String to wrap.
        :return:      ``text`` enclosed in instance's ``SGRs``, if any.
        """
        result = self._opening_seq.assemble()

        if text is not None:
            result += str(text)

        result += self._closing_seq.assemble()
        return result

    @property
    def opening_str(self) -> str:
        """ Return opening SGR sequence assembled. """
        return self._opening_seq.assemble()

    @property
    def opening_seq(self) -> 'SequenceSGR':
        """ Return opening SGR sequence instance. """
        return self._opening_seq

    @property
    def closing_str(self) -> str:
        """ Return closing SGR sequence assembled. """
        return self._closing_seq.assemble()

    @property
    def closing_seq(self) -> 'SequenceSGR':
        """ Return closing SGR sequence instance. """
        return self._closing_seq

    @classmethod
    def _opt_arg(self, arg: SequenceSGR | None) -> SequenceSGR:
        if not arg:
            return NOOP_SEQ
        return arg

    def __call__(self, text: Any = None) -> str:
        """
        Can be used instead of `wrap()` method.

        >>> Spans.RED('text') == Spans.RED.wrap('text')
        True
        """
        return self.wrap(text)

    def __eq__(self, other: Span) -> bool:
        if not isinstance(other, Span):
            return False
        return self._opening_seq == other._opening_seq and self._closing_seq == other._closing_seq

    def __repr__(self):
        return self.__class__.__name__ + '[{!r}, {!r}]'.format(self._opening_seq, self._closing_seq)


NOOP_SEQ = SequenceSGR()
"""
Special sequence in case you *have to* provide one or another SGR, but do 
not want any control sequences to be actually included in the output. 
``NOOP_SEQ.assemble()`` returns empty string, ``NOOP_SEQ.params`` 
returns empty list.

>>> NOOP_SEQ.assemble()
''
>>> NOOP_SEQ.params
[]
"""

NOOP_SPAN = Span()
"""
Special `Span` in cases where you *have to* select one or 
another `Span`, but do not want any control sequence to be actually included. 

- ``NOOP_SPAN(string)`` or ``NOOP_SPAN.wrap(string)`` returns ``string`` without any modifications;
- ``NOOP_SPAN.opening_str`` and ``NOOP_SPAN.closing_str`` are empty strings;
- ``NOOP_SPAN.opening_seq`` and ``NOOP_SPAN.closing_seq`` both returns `NOOP_SEQ`.

>>> NOOP_SPAN('text')
'text'
>>> NOOP_SPAN.opening_str
''
>>> NOOP_SPAN.opening_seq
SGR[^]
"""
