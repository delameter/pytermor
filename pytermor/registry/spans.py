# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

from .int_codes import IntCodes
from ..common import Registry
from ..ansi import Span


class Spans(Registry[Span]):
    """
    Registry of span presets.

    .. attention::
       Registry constants are omitted from API doc pages to improve readability
       and avoid duplication. Summary list of all presets can be found in
       `guide.presets` section of the guide.
    """

    BOLD = Span(IntCodes.BOLD)
    DIM = Span(IntCodes.DIM)
    ITALIC = Span(IntCodes.ITALIC)
    UNDERLINED = Span(IntCodes.UNDERLINED)
    BLINK_SLOW = Span(IntCodes.BLINK_SLOW)
    BLINK_FAST = Span(IntCodes.BLINK_FAST)
    INVERSED = Span(IntCodes.INVERSED)
    HIDDEN = Span(IntCodes.HIDDEN)
    CROSSLINED = Span(IntCodes.CROSSLINED)
    DOUBLE_UNDERLINED = Span(IntCodes.DOUBLE_UNDERLINED)
    OVERLINED = Span(IntCodes.OVERLINED)

    BLACK = Span(IntCodes.BLACK)
    RED = Span(IntCodes.RED)
    GREEN = Span(IntCodes.GREEN)
    YELLOW = Span(IntCodes.YELLOW)
    BLUE = Span(IntCodes.BLUE)
    MAGENTA = Span(IntCodes.MAGENTA)
    CYAN = Span(IntCodes.CYAN)
    WHITE = Span(IntCodes.WHITE)

    GRAY = Span(IntCodes.GRAY)
    HI_RED = Span(IntCodes.HI_RED)
    HI_GREEN = Span(IntCodes.HI_GREEN)
    HI_YELLOW = Span(IntCodes.HI_YELLOW)
    HI_BLUE = Span(IntCodes.HI_BLUE)
    HI_MAGENTA = Span(IntCodes.HI_MAGENTA)
    HI_CYAN = Span(IntCodes.HI_CYAN)
    HI_WHITE = Span(IntCodes.HI_WHITE)

    BG_BLACK = Span(IntCodes.BG_BLACK)
    BG_RED = Span(IntCodes.BG_RED)
    BG_GREEN = Span(IntCodes.BG_GREEN)
    BG_YELLOW = Span(IntCodes.BG_YELLOW)
    BG_BLUE = Span(IntCodes.BG_BLUE)
    BG_MAGENTA = Span(IntCodes.BG_MAGENTA)
    BG_CYAN = Span(IntCodes.BG_CYAN)
    BG_WHITE = Span(IntCodes.BG_WHITE)

    BG_GRAY = Span(IntCodes.BG_GRAY)
    BG_HI_RED = Span(IntCodes.BG_HI_RED)
    BG_HI_GREEN = Span(IntCodes.BG_HI_GREEN)
    BG_HI_YELLOW = Span(IntCodes.BG_HI_YELLOW)
    BG_HI_BLUE = Span(IntCodes.BG_HI_BLUE)
    BG_HI_MAGENTA = Span(IntCodes.BG_HI_MAGENTA)
    BG_HI_CYAN = Span(IntCodes.BG_HI_CYAN)
    BG_HI_WHITE = Span(IntCodes.BG_HI_WHITE)
