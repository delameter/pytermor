# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""
Module introducing `Span` abstractions. The key difference beetween them and
`Sequences` is that sequence can *open* text style and also *close*, or terminate
it. As for `Spans` -- they always do both; typical use-case of `Span` is to wrap
some text in opening SGR and closing one.

Name of any format preset in this module can be used as a string argument in
``build()`` and ``autocomplete()`` methods:

  ``autocomplete('red', 'bold')``

"""

from __future__ import annotations

from typing import Any

from . import sequence
from .sequence import build, intcode, SequenceSGR
from .registry import sgr_parity_registry


# noinspection PyMethodMayBeStatic
class Span:
    """
    Wrapper class that contains starter, or *opening*
    sequence and (optionally) *closing* sequence.

    Note that ``closing_seq`` is mutually exclusive with setting ``hard_reset_after``
    to *True*; in the latter case ``closing_seq`` .
    is ignored and gets overwritten with ``sequence.RESET``.

    :param opening_seq:      Starter sequence, in general determening how
                              Span will actually look like.
    :param closing_seq:      Finisher SGR sequence.
    :param hard_reset_after: Uses ``SequenceSGR(0)`` (breaker) as ``closing_seq``.
    """
    def __init__(self, opening_seq: SequenceSGR = None, closing_seq: SequenceSGR = None, hard_reset_after: bool = False):
        self._opening_seq: SequenceSGR = self._opt_arg(opening_seq)
        self._closing_seq: SequenceSGR = self._opt_arg(closing_seq)
        if hard_reset_after:
            self._closing_seq = SequenceSGR(intcode.RESET)

    def wrap(self, text: Any = None) -> str:
        """
        Wrap given ``text`` with Span's SGRs -- `opening_seq` to the left,
        `closing_seq` for another.

        :param text:  ``str(text)`` will be invoked for all argument types with the
                      exception of None, which will be replaced with empty string.
        :return:      Resulting string; input argument enclosed in span SGRs, if any.
        """
        result = self._opening_seq.print()

        if text is not None:
            result += str(text)

        result += self._closing_seq.print()
        return result

    @property
    def opening_str(self) -> str:
        """ Return opening SGR sequence encoded """
        return self._opening_seq.print()

    @property
    def opening_seq(self) -> 'SequenceSGR':
        """ Return opening SGR sequence instance """
        return self._opening_seq

    @property
    def closing_str(self) -> str:
        """ Return closing SGR sequence encoded """
        return self._closing_seq.print()

    @property
    def closing_seq(self) -> 'SequenceSGR':
        """ Return closing SGR sequence instance """
        return self._closing_seq

    def _opt_arg(self, arg: SequenceSGR | None) -> SequenceSGR:
        if not arg:
            return sequence.NOOP
        return arg

    def __call__(self, text: Any = None) -> str:
        """
        ``span_red("string")`` is the same as span_red.wrap("string").
        """
        return self.wrap(text)

    def __eq__(self, other: Span) -> bool:
        if not isinstance(other, Span):
            return False
        return self._opening_seq == other._opening_seq and self._closing_seq == other._closing_seq

    def __repr__(self):
        return self.__class__.__name__ + '[{!r}, {!r}]'.format(self._opening_seq, self._closing_seq)


def autocomplete(*args: str | int | SequenceSGR) -> Span:
    """
    Create new `Span` with specified control sequence(s) as an opening sequence
    and **automatically compose** closing sequence that will terminate attributes
    defined in the first one while keeping the others (soft reset).

    Resulting sequence param order is same as an argument order.

    Each sequence param can be specified as:
      - string key
      - integer param value (see `pytermor.intcode`)
      - existing `SequenceSGR` instance (params will be extracted).
    """

    opening_seq = build(*args)
    closing_seq = sgr_parity_registry.get_closing_seq(opening_seq)
    return Span(opening_seq, closing_seq)


# ---------------------------------------------------------------------------
# Span presets
# ---------------------------------------------------------------------------

noop = autocomplete()
"""
Special `Span` in cases where you *have to* select one or 
another `Span`, but do not want anything to be actually printed. 

- ``noop(string)`` or ``noop.wrap(string)`` returns ``string`` without any modifications;
- ``noop.opening_str`` and ``noop.closing_str`` are empty strings;
- ``noop.opening_seq`` and ``noop.closing_seq`` both returns ``sequence.NOOP``.
"""

bold = autocomplete(intcode.BOLD)              #:
dim = autocomplete(intcode.DIM)                #:
italic = autocomplete(intcode.ITALIC)          #:
underlined = autocomplete(intcode.UNDERLINED)  #:
inversed = autocomplete(intcode.INVERSED)      #:
overlined = autocomplete(intcode.OVERLINED)    #:

red = autocomplete(intcode.RED)                #:
green = autocomplete(intcode.GREEN)            #:
yellow = autocomplete(intcode.YELLOW)          #:
blue = autocomplete(intcode.BLUE)              #:
magenta = autocomplete(intcode.MAGENTA)        #:
cyan = autocomplete(intcode.CYAN)              #:
gray = autocomplete(intcode.GRAY)              #:

bg_black = autocomplete(intcode.BG_BLACK)      #:
bg_red = autocomplete(intcode.BG_RED)          #:
bg_green = autocomplete(intcode.BG_GREEN)      #:
bg_yellow = autocomplete(intcode.BG_YELLOW)    #:
bg_blue = autocomplete(intcode.BG_BLUE)        #:
bg_magenta = autocomplete(intcode.BG_MAGENTA)  #:
bg_cyan = autocomplete(intcode.BG_CYAN)        #:
bg_gray = autocomplete(intcode.BG_GRAY)        #:
