# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""
Module with SGR param integer codes, contains a complete or almost complete
list of reliably working ones.

Suitable for :class:`.Span` and :class:`.SequenceSGR` default constructors.
"""

RESET = 0  # hard reset code
BOLD = 1
DIM = 2
ITALIC = 3
UNDERLINED = 4
BLINK_SLOW = 5
BLINK_FAST = 6
INVERSED = 7
HIDDEN = 8
CROSSLINED = 9
DOUBLE_UNDERLINED = 21
OVERLINED = 53
NO_BOLD_DIM = 22  # there is no separate sequence for disabling either of BOLD or DIM while keeping the other
ITALIC_OFF = 23
UNDERLINED_OFF = 24
BLINK_OFF = 25
INVERSED_OFF = 27
HIDDEN_OFF = 28
CROSSLINED_OFF = 29
COLOR_OFF = 39
BG_COLOR_OFF = 49
OVERLINED_OFF = 55

BLACK = 30
RED = 31
GREEN = 32
YELLOW = 33
BLUE = 34
MAGENTA = 35
CYAN = 36
WHITE = 37
COLOR_EXTENDED = 38  # use color_indexed() and color_rgb() instead

BG_BLACK = 40
BG_RED = 41
BG_GREEN = 42
BG_YELLOW = 43
BG_BLUE = 44
BG_MAGENTA = 45
BG_CYAN = 46
BG_WHITE = 47
BG_COLOR_EXTENDED = 48  # use color_indexed() and color_rgb() instead

GRAY = 90
HI_RED = 91
HI_GREEN = 92
HI_YELLOW = 93
HI_BLUE = 94
HI_MAGENTA = 95
HI_CYAN = 96
HI_WHITE = 97
BG_GRAY = 100
BG_HI_RED = 101
BG_HI_GREEN = 102
BG_HI_YELLOW = 103
BG_HI_BLUE = 104
BG_HI_MAGENTA = 105
BG_HI_CYAN = 106
BG_HI_WHITE = 107

# RARELY SUPPORTED (thus excluded)
# 10-20: font selection
#    50: disable proportional spacing
#    51: framed
#    52: encircled
#    54: neither framed nor encircled
# 58-59: underline color
# 60-65: ideogram attributes
# 73-75: superscript and subscript

# ---------------------------------------------------------------------------

_EXTENDED_MODE_256 = 5
_EXTENDED_MODE_RGB = 2

# ---------------------------------------------------------------------------

LIST_COLORS = list(range(30, 39))
LIST_BG_COLORS = list(range(40, 49))
LIST_HI_COLORS = list(range(90, 98))
LIST_BG_HI_COLORS = list(range(100, 108))

LIST_ALL_COLORS = LIST_COLORS + LIST_BG_COLORS + LIST_HI_COLORS + LIST_BG_HI_COLORS
