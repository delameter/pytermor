# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from .format import Format
from .sequence import SequenceSGR
# -----------------------------------------------------------------------------
# SGR = "Select Graphic Rendition", most common escape sequence variety

RESET = SequenceSGR(0)

# attributes
BOLD = SequenceSGR(1)
DIM = SequenceSGR(2)
ITALIC = SequenceSGR(3)
UNDERLINED = SequenceSGR(4)
BLINK_SLOW = SequenceSGR(5)
BLINK_FAST = SequenceSGR(6)
INVERSED = SequenceSGR(7)
HIDDEN = SequenceSGR(8)
CROSSLINED = SequenceSGR(9)
DOUBLE_UNDERLINED = SequenceSGR(21)
OVERLINED = SequenceSGR(53)

DIM_BOLD_OFF = SequenceSGR(22)
ITALIC_OFF = SequenceSGR(23)
UNDERLINED_OFF = SequenceSGR(24)
BLINK_OFF = SequenceSGR(25)
INVERSED_OFF = SequenceSGR(27)
HIDDEN_OFF = SequenceSGR(28)
CROSSLINED_OFF = SequenceSGR(29)
OVERLINED_OFF = SequenceSGR(55)

# text colors
BLACK = SequenceSGR(30)
RED = SequenceSGR(31)
GREEN = SequenceSGR(32)
YELLOW = SequenceSGR(33)
BLUE = SequenceSGR(34)
MAGENTA = SequenceSGR(35)
CYAN = SequenceSGR(36)
WHITE = SequenceSGR(37)
MODE24_START = SequenceSGR(38, 2)  # 3 params required (r, g, b)
MODE8_START = SequenceSGR(38, 5)  # 1 param required (color code)
COLOR_OFF = SequenceSGR(39)

# background colors
BG_BLACK = SequenceSGR(40)
BG_RED = SequenceSGR(41)
BG_GREEN = SequenceSGR(42)
BG_YELLOW = SequenceSGR(43)
BG_BLUE = SequenceSGR(44)
BG_MAGENTA = SequenceSGR(45)
BG_CYAN = SequenceSGR(46)
BG_WHITE = SequenceSGR(47)
BG_MODE24_START = SequenceSGR(48, 2)  # 3 params required (r, g, b)
BG_MODE8_START = SequenceSGR(48, 5)  # 1 param required (color code)
BG_COLOR_OFF = SequenceSGR(49)

# high intensity text colors
GRAY = SequenceSGR(90)
HI_RED = SequenceSGR(91)
HI_GREEN = SequenceSGR(92)
HI_YELLOW = SequenceSGR(93)
HI_BLUE = SequenceSGR(94)
HI_MAGENTA = SequenceSGR(95)
HI_CYAN = SequenceSGR(96)
HI_WHITE = SequenceSGR(97)

# high intensity background colors
BG_GRAY = SequenceSGR(100)
BG_HI_RED = SequenceSGR(101)
BG_HI_GREEN = SequenceSGR(102)
BG_HI_YELLOW = SequenceSGR(103)
BG_HI_BLUE = SequenceSGR(104)
BG_HI_MAGENTA = SequenceSGR(105)
BG_HI_CYAN = SequenceSGR(106)
BG_HI_WHITE = SequenceSGR(107)

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
# ready to use combined SGRs with "soft" format reset

fmt_bold = Format(BOLD, DIM_BOLD_OFF) # noqa DuplicatedCode
fmt_dim = Format(DIM, DIM_BOLD_OFF)
fmt_italic = Format(ITALIC, ITALIC_OFF)
fmt_underline = Format(UNDERLINED, UNDERLINED_OFF)
fmt_inverse = Format(INVERSED, INVERSED_OFF)
fmt_overline = Format(OVERLINED, OVERLINED_OFF)

fmt_red = Format(RED, COLOR_OFF)
fmt_green = Format(GREEN, COLOR_OFF)
fmt_yellow = Format(YELLOW, COLOR_OFF)
fmt_blue = Format(BLUE, COLOR_OFF) # noqa DuplicatedCode
fmt_magenta = Format(MAGENTA, COLOR_OFF)  # it's duplicated purposely, geez
fmt_cyan = Format(CYAN, COLOR_OFF)

fmt_bg_red = Format(BG_RED, BG_COLOR_OFF)
fmt_bg_green = Format(BG_GREEN, BG_COLOR_OFF)
fmt_bg_yellow = Format(BG_YELLOW, BG_COLOR_OFF)
fmt_bg_blue = Format(BG_BLUE, BG_COLOR_OFF)
fmt_bg_magenta = Format(BG_MAGENTA, BG_COLOR_OFF)
fmt_bg_cyan = Format(BG_CYAN, BG_COLOR_OFF)
