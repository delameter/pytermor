# ------------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
from .format import Format
from .sequence import SGRSequence

# -----------------------------------------------------------------------------
# Select Graphic Rendition control sequences

RESET = SGRSequence(0)

# attributes
BOLD = SGRSequence(1)
DIM = SGRSequence(2)
ITALIC = SGRSequence(3)
UNDERLINED = SGRSequence(4)
BLINK_SLOW = SGRSequence(5)
BLINK_FAST = SGRSequence(6)
INVERSED = SGRSequence(7)
HIDDEN = SGRSequence(8)
CROSSLINED = SGRSequence(9)
DOUBLE_UNDERLINED = SGRSequence(21)
OVERLINED = SGRSequence(53)

DIM_BOLD_OFF = SGRSequence(22)
ITALIC_OFF = SGRSequence(23)
UNDERLINED_OFF = SGRSequence(24)
BLINK_OFF = SGRSequence(25)
INVERSED_OFF = SGRSequence(27)
HIDDEN_OFF = SGRSequence(28)
CROSSLINED_OFF = SGRSequence(29)
OVERLINED_OFF = SGRSequence(55)

# text colors
BLACK = SGRSequence(30)
RED = SGRSequence(31)
GREEN = SGRSequence(32)
YELLOW = SGRSequence(33)
BLUE = SGRSequence(34)
MAGENTA = SGRSequence(35)
CYAN = SGRSequence(36)
WHITE = SGRSequence(37)
MODE8_START = SGRSequence(38, 5)  # 3rd param required
COLOR_OFF = SGRSequence(39)

# background colors
BG_BLACK = SGRSequence(40)
BG_RED = SGRSequence(41)
BG_GREEN = SGRSequence(42)
BG_YELLOW = SGRSequence(43)
BG_BLUE = SGRSequence(44)
BG_MAGENTA = SGRSequence(45)
BG_CYAN = SGRSequence(46)
BG_WHITE = SGRSequence(47)
BG_MODE8_START = SGRSequence(48, 5)  # 3rd param required
BG_COLOR_OFF = SGRSequence(49)

# high intensity text colors
GRAY = SGRSequence(90)
HI_RED = SGRSequence(91)
HI_GREEN = SGRSequence(92)
HI_YELLOW = SGRSequence(93)
HI_BLUE = SGRSequence(94)
HI_MAGENTA = SGRSequence(95)
HI_CYAN = SGRSequence(96)
HI_WHITE = SGRSequence(97)

# high intensity background colors
BG_GRAY = SGRSequence(100)
BG_HI_RED = SGRSequence(101)
BG_HI_GREEN = SGRSequence(102)
BG_HI_YELLOW = SGRSequence(103)
BG_HI_BLUE = SGRSequence(104)
BG_HI_MAGENTA = SGRSequence(105)
BG_HI_CYAN = SGRSequence(106)
BG_HI_WHITE = SGRSequence(107)

# rarely supported
# 10-20: font selection
#    50: disable proportional spacing
#    51: framed
#    52: encircled
#    54: neither framed nor encircled
# 58-59: underline color
# 60-65: ideogram attributes
# 73-75: superscript and subscript

# -----------------------------------------------------------------------------
# SGR sequences combined into togglable text formats

fmt_bold = Format(BOLD, DIM_BOLD_OFF)
fmt_dim = Format(DIM, DIM_BOLD_OFF)
fmt_italic = Format(ITALIC, ITALIC_OFF)
fmt_underline = Format(UNDERLINED, UNDERLINED_OFF)
fmt_inverse = Format(INVERSED, INVERSED_OFF)
fmt_overline = Format(OVERLINED, OVERLINED_OFF)

fmt_red = Format(RED, COLOR_OFF)
fmt_green = Format(GREEN, COLOR_OFF)
fmt_yellow = Format(YELLOW, COLOR_OFF)
fmt_blue = Format(BLUE, COLOR_OFF)
fmt_magenta = Format(MAGENTA, COLOR_OFF)
fmt_cyan = Format(CYAN, COLOR_OFF)

fmt_bg_red = Format(BG_RED, BG_COLOR_OFF)
fmt_bg_green = Format(BG_GREEN, BG_COLOR_OFF)
fmt_bg_yellow = Format(BG_YELLOW, BG_COLOR_OFF)
fmt_bg_blue = Format(BG_BLUE, BG_COLOR_OFF)
fmt_bg_magenta = Format(BG_MAGENTA, BG_COLOR_OFF)
fmt_bg_cyan = Format(BG_CYAN, BG_COLOR_OFF)
