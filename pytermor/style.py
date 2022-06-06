# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from dataclasses import dataclass
from typing import List

from .color import Color16 as Color
from .intcode import *


@dataclass(frozen=True)
class Style:
    color: Color = None
    bg_color: Color = None
    attributes: List = None


@dataclass(frozen=True)
class Stylesheet:
    default: Style = Style()


# ---------------------------------------------------------------------------
# Color <-> SGR code mappings
# ---------------------------------------------------------------------------

black = Color(BLACK, BG_BLACK)
gray = Color(GRAY, BG_GRAY)

red = Color(RED, BG_RED)
hi_red = Color(HI_RED, BG_HI_RED)

green = Color(GREEN, BG_GREEN)
hi_green = Color(HI_GREEN, BG_HI_GREEN)

yellow = Color(YELLOW, BG_YELLOW)
hi_yellow = Color(HI_YELLOW, BG_HI_YELLOW)

blue = Color(BLUE, BG_BLUE)
hi_blue = Color(HI_BLUE, BG_HI_BLUE)

magenta = Color(MAGENTA, BG_MAGENTA)
hi_magenta = Color(HI_MAGENTA, BG_HI_MAGENTA)

cyan = Color(CYAN, BG_CYAN)
hi_cyan = Color(HI_CYAN, BG_HI_CYAN)

white = Color(WHITE, BG_WHITE)
hi_white = Color(HI_WHITE, BG_HI_WHITE)
