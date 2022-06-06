# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from .intcode import *


class Color16:
    def __init__(self, intcode_fg_color: int, intcode_bg_color: int):
        self._intcode_fg_color: int = intcode_fg_color
        self._intcode_bg_color: int = intcode_bg_color
        #self._: int =


# ---------------------------------------------------------------------------
# Color <-> SGR code mappings
# ---------------------------------------------------------------------------

black = Color16(BLACK, BG_BLACK)
gray = Color16(GRAY, BG_GRAY)

red = Color16(RED, BG_RED)
hi_red = Color16(HI_RED, BG_HI_RED)

green = Color16(GREEN, BG_GREEN)
hi_green = Color16(HI_GREEN, BG_HI_GREEN)

yellow = Color16(YELLOW, BG_YELLOW)
hi_yellow = Color16(HI_YELLOW, BG_HI_YELLOW)

blue = Color16(BLUE, BG_BLUE)
hi_blue = Color16(HI_BLUE, BG_HI_BLUE)

magenta = Color16(MAGENTA, BG_MAGENTA)
hi_magenta = Color16(HI_MAGENTA, BG_HI_MAGENTA)

cyan = Color16(CYAN, BG_CYAN)
hi_cyan = Color16(HI_CYAN, BG_HI_CYAN)

white = Color16(WHITE, BG_WHITE)
hi_white = Color16(HI_WHITE, BG_HI_WHITE)
