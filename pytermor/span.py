# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""
Module introducing `Span` abstractions. The key difference beetween them and
``Sequences`` is that sequence can *open* text style and also *close*, or terminate
it. As for ``Spans`` -- they always do both; typical use-case of `Span` is to wrap
some text in opening SGR and closing one.

Name of any format preset in this module can be used as a string argument in
:func:`.build` and :func:`.autospan` methods::

    autospan('red', 'bold')

"""

from __future__ import annotations

from typing import Any

from . import sequence
from .sequence import build, intcode, SequenceSGR, sgr_parity_registry


def autospan(*args: str | int | SequenceSGR) -> Span:
    """
    Create new `Span` with specified control sequence(s) as an opening sequence
    and **automatically compose** closing sequence that will terminate attributes
    defined in the first one while keeping the others (soft reset).

    Resulting sequence param order is same as an argument order.

    Each sequence param can be specified as:
      - string key (see :mod:`.span`)
      - integer param value (see :mod:`~pytermor.intcode`)
      - existing `SequenceSGR` instance (params will be extracted).
    """

    opening_seq = build(*args)
    closing_seq = sgr_parity_registry.get_closing_seq(opening_seq)
    return Span(opening_seq, closing_seq)


# noinspection PyMethodMayBeStatic
class Span:
    """
    Wrapper class that contains starter, or *opening*
    sequence and (optionally) *closing* sequence.

    Note that `closing_seq` gets overwritten with
    :data:`.sequence.RESET` if ``hard_reset_after`` is *True*.

    :param opening_seq:      Starter sequence, in general determening how
                              `Span` will actually look like.
    :param closing_seq:      Finisher SGR sequence.
    :param hard_reset_after: Set `closing_seq` to a hard reset sequence.
    """
    def __init__(self, opening_seq: SequenceSGR = None, closing_seq: SequenceSGR = None, hard_reset_after: bool = False):
        self._opening_seq: SequenceSGR = self._opt_arg(opening_seq)
        self._closing_seq: SequenceSGR = self._opt_arg(closing_seq)
        if hard_reset_after:
            self._closing_seq = SequenceSGR(intcode.RESET)

    def wrap(self, text: Any = None) -> str:
        """
        Wrap given ``text`` with ``SGRs`` of the ``Span`` -- `opening_seq`
        on the left, `closing_seq` on the right. ``str(text)`` will
        be invoked for all argument types with the exception of *None*,
        which will be replaced with an empty string.

        :param text:  String to wrap.
        :return:      Resulting string; input argument enclosed to instance's ``SGRs``, if any.
        """
        result = self._opening_seq.print()

        if text is not None:
            result += str(text)

        result += self._closing_seq.print()
        return result

    @property
    def opening_str(self) -> str:
        """ Return opening SGR sequence encoded. """
        return self._opening_seq.print()

    @property
    def opening_seq(self) -> 'SequenceSGR':
        """ Return opening SGR sequence instance. """
        return self._opening_seq

    @property
    def closing_str(self) -> str:
        """ Return closing SGR sequence encoded. """
        return self._closing_seq.print()

    @property
    def closing_seq(self) -> 'SequenceSGR':
        """ Return closing SGR sequence instance. """
        return self._closing_seq

    def _opt_arg(self, arg: SequenceSGR | None) -> SequenceSGR:
        if not arg:
            return sequence.NOOP
        return arg

    def __call__(self, text: Any = None) -> str:
        """
        `red("string")` is the same as `red.wrap("string")`.
        """
        return self.wrap(text)

    def __eq__(self, other: Span) -> bool:
        if not isinstance(other, Span):
            return False
        return self._opening_seq == other._opening_seq and self._closing_seq == other._closing_seq

    def __repr__(self):
        return self.__class__.__name__ + '[{!r}, {!r}]'.format(self._opening_seq, self._closing_seq)


# ---------------------------------------------------------------------------
# Span presets
# ---------------------------------------------------------------------------

noop = autospan()
"""
Special `Span` in cases where you *have to* select one or 
another `Span`, but do not want anything to be actually printed. 

- ``noop(string)`` or ``noop.wrap(string)`` returns ``string`` without any modifications;
- ``noop.opening_str`` and ``noop.closing_str`` are empty strings;
- ``noop.opening_seq`` and ``noop.closing_seq`` both returns ``sequence.NOOP``.
"""

bold = autospan(intcode.BOLD)              #:
dim = autospan(intcode.DIM)                #:
italic = autospan(intcode.ITALIC)          #:
underlined = autospan(intcode.UNDERLINED)  #:
inversed = autospan(intcode.INVERSED)      #:
overlined = autospan(intcode.OVERLINED)    #:

black = autospan(intcode.BLACK)            #:
red = autospan(intcode.RED)                #:
green = autospan(intcode.GREEN)            #:
yellow = autospan(intcode.YELLOW)          #:
blue = autospan(intcode.BLUE)              #:
magenta = autospan(intcode.MAGENTA)        #:
cyan = autospan(intcode.CYAN)              #:
gray = autospan(intcode.GRAY)              #:
hi_red = autospan(intcode.HI_RED)          #:
hi_green = autospan(intcode.HI_GREEN)      #:
hi_yellow = autospan(intcode.HI_YELLOW)    #:
hi_blue = autospan(intcode.HI_BLUE)        #:
hi_magenta = autospan(intcode.HI_MAGENTA)  #:
hi_cyan = autospan(intcode.HI_CYAN)        #:

bg_black = autospan(intcode.BG_BLACK)      #:
bg_red = autospan(intcode.BG_RED)          #:
bg_green = autospan(intcode.BG_GREEN)      #:
bg_yellow = autospan(intcode.BG_YELLOW)    #:
bg_blue = autospan(intcode.BG_BLUE)        #:
bg_magenta = autospan(intcode.BG_MAGENTA)  #:
bg_cyan = autospan(intcode.BG_CYAN)        #:
bg_gray = autospan(intcode.BG_GRAY)        #:
