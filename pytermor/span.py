# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""
Module introducing `Span` low-level abstractions. The key difference beetween them and
``Sequences`` is that sequence can *open* text style and also *close*, or terminate
it. As for ``Spans`` -- they always do both; typical use-case of `Span` is to wrap
some text in opening SGR and closing one.

.. testsetup:: *

    from pytermor import sequence, intcode
    from pytermor.span import Span, NOOP, RED

"""

from __future__ import annotations

from typing import Any

from . import sequence
from .sequence import build, intcode, SequenceSGR, sgr_parity_registry


# noinspection PyMethodMayBeStatic
class Span:
    def __init__(self, *opening_params: str|int|SequenceSGR):
        """
        Create a `Span` with specified control sequence(s) as an opening sequence
        and **automatically compose** second (closing) sequence that will terminate
        attributes defined in the first one while keeping the others (*soft* reset).

        Resulting sequence param order is same as an argument order.

        Each argument can be specified as:
          - string key (name of any constant defined in :mod:`.intcode`, case-insensitive)
          - integer param value (defined in :mod:`.intcode`)
          - existing `SequenceSGR` instance (params will be extracted).

        >>> Span('red', 'bold')
        Span[SGR[31;1], SGR[39;22]]
        >>> Span(intcode.GREEN)
        Span[SGR[32], SGR[39]]
        >>> Span(93, 4)
        Span[SGR[93;4], SGR[39;24]]
        >>> Span(sequence.BG_BLACK + sequence.RED)
        Span[SGR[40;31], SGR[49;39]]

        :param opening_params: string keys, integer codes or existing ``SequenceSGR``
                               instances to build ``Span`` from.
        """
        self._opening_seq = build(*opening_params)
        self._closing_seq = sgr_parity_registry.get_closing_seq(self._opening_seq)

    @classmethod
    def from_seq(cls, opening_seq: SequenceSGR = None, closing_seq: SequenceSGR = None,
                 hard_reset_after: bool = False) -> Span:
        """
        Create new `Span` with explicitly specified opening and closing sequences.

        .. note ::
            `closing_seq` gets overwritten with :data:`.sequence.RESET` if
            ``hard_reset_after`` is *True*.

        :param opening_seq:      Starter sequence, in general determening how `Span` will actually look like.
        :param closing_seq:      Finisher SGR sequence.
        :param hard_reset_after: Terminate *all* formatting after this span.
        """
        instance = Span()
        instance._opening_seq = cls._opt_arg(opening_seq)
        instance._closing_seq = cls._opt_arg(closing_seq)

        if hard_reset_after:
            instance._closing_seq = sequence.RESET

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
        result = self._opening_seq.encode()

        if text is not None:
            result += str(text)

        result += self._closing_seq.encode()
        return result

    @property
    def opening_str(self) -> str:
        """ Return opening SGR sequence encoded. """
        return self._opening_seq.encode()

    @property
    def opening_seq(self) -> 'SequenceSGR':
        """ Return opening SGR sequence instance. """
        return self._opening_seq

    @property
    def closing_str(self) -> str:
        """ Return closing SGR sequence encoded. """
        return self._closing_seq.encode()

    @property
    def closing_seq(self) -> 'SequenceSGR':
        """ Return closing SGR sequence instance. """
        return self._closing_seq

    @classmethod
    def _opt_arg(self, arg: SequenceSGR | None) -> SequenceSGR:
        if not arg:
            return sequence.NOOP
        return arg

    def __call__(self, text: Any = None) -> str:
        """
        Can be used instead of `wrap()` method.

        >>> RED('text') == RED.wrap('text')
        True
        """
        return self.wrap(text)

    def __eq__(self, other: Span) -> bool:
        if not isinstance(other, Span):
            return False
        return self._opening_seq == other._opening_seq and self._closing_seq == other._closing_seq

    def __repr__(self):
        return self.__class__.__name__ + '[{!r}, {!r}]'.format(self._opening_seq, self._closing_seq)


# -- Span presets -------------------------------------------------------------

NOOP = Span()
"""
Special `Span` in cases where you *have to* select one or 
another `Span`, but do not want any control sequence to be actually included. 

- ``NOOP(string)`` or ``NOOP.wrap(string)`` returns ``string`` without any modifications;
- ``NOOP.opening_str`` and ``NOOP.closing_str`` are empty strings;
- ``NOOP.opening_seq`` and ``NOOP.closing_seq`` both returns `sequence.NOOP`.

>>> NOOP('text')
'text'
>>> NOOP.opening_str
''
>>> NOOP.opening_seq
SGR[^]

"""

BOLD = Span(intcode.BOLD)
DIM = Span(intcode.DIM)
ITALIC = Span(intcode.ITALIC)
UNDERLINED = Span(intcode.UNDERLINED)
INVERSED = Span(intcode.INVERSED)
OVERLINED = Span(intcode.OVERLINED)

BLACK = Span(intcode.BLACK)
RED = Span(intcode.RED)
GREEN = Span(intcode.GREEN)
YELLOW = Span(intcode.YELLOW)
BLUE = Span(intcode.BLUE)
MAGENTA = Span(intcode.MAGENTA)
CYAN = Span(intcode.CYAN)

GRAY = Span(intcode.GRAY)
HI_RED = Span(intcode.HI_RED)
HI_GREEN = Span(intcode.HI_GREEN)
HI_YELLOW = Span(intcode.HI_YELLOW)
HI_BLUE = Span(intcode.HI_BLUE)
HI_MAGENTA = Span(intcode.HI_MAGENTA)
HI_CYAN = Span(intcode.HI_CYAN)

BG_BLACK = Span(intcode.BG_BLACK)
BG_RED = Span(intcode.BG_RED)
BG_GREEN = Span(intcode.BG_GREEN)
BG_YELLOW = Span(intcode.BG_YELLOW)
BG_BLUE = Span(intcode.BG_BLUE)
BG_MAGENTA = Span(intcode.BG_MAGENTA)
BG_CYAN = Span(intcode.BG_CYAN)
BG_GRAY = Span(intcode.BG_GRAY)
