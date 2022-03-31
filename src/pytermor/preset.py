# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
# SGR = "Select Graphic Rendition", most common escape sequence variety
from .sequence import SequenceSGR

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

BOLD_DIM_OFF = SequenceSGR(22)
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
# modifier groups for format auto-breaking
from .sequence import ModifierGroup

_mgroup_super = ModifierGroup(RESET, [])
_mgroup_bold = ModifierGroup(BOLD_DIM_OFF, [BOLD])
_mgroup_dim = ModifierGroup(BOLD_DIM_OFF, [DIM])
_mgroup_italic = ModifierGroup(ITALIC_OFF, [ITALIC])
_mgroup_underlined = ModifierGroup(UNDERLINED_OFF, [UNDERLINED, DOUBLE_UNDERLINED])
_mgroup_blink = ModifierGroup(BLINK_OFF, [BLINK_SLOW, BLINK_FAST])
_mgroup_inversed = ModifierGroup(INVERSED_OFF, [INVERSED])
_mgroup_hidden = ModifierGroup(HIDDEN_OFF, [HIDDEN])
_mgroup_crosslined = ModifierGroup(CROSSLINED_OFF, [CROSSLINED])
_mgroup_overlined = ModifierGroup(OVERLINED_OFF, [OVERLINED])
_mgroup_color = ModifierGroup(COLOR_OFF, [
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE,
    GRAY, HI_RED, HI_GREEN, HI_YELLOW, HI_BLUE, HI_MAGENTA, HI_CYAN, HI_WHITE, 
    MODE24_START, MODE8_START,
])
_mgroup_bg_color = ModifierGroup(BG_COLOR_OFF, [
    BG_BLACK, BG_RED, BG_GREEN, BG_YELLOW, BG_BLUE, BG_MAGENTA, BG_CYAN, BG_WHITE, 
    BG_GRAY, BG_HI_RED, BG_HI_GREEN, BG_HI_YELLOW, BG_HI_BLUE, BG_HI_MAGENTA, BG_HI_CYAN, BG_HI_WHITE,
    BG_MODE24_START, BG_MODE8_START,
])

# -----------------------------------------------------------------------------
# ready to use combined SGRs with "soft" format reset
from .format import Format


fmt_bold = Format(BOLD, _mgroup_bold.breaker)
fmt_dim = Format(DIM, _mgroup_dim.breaker)
fmt_italic = Format(ITALIC, _mgroup_italic.breaker)
fmt_underline = Format(UNDERLINED, _mgroup_underlined.breaker)
fmt_inverse = Format(INVERSED, _mgroup_inversed.breaker)
fmt_overline = Format(OVERLINED, _mgroup_overlined.breaker)

fmt_red = Format(RED, _mgroup_color.breaker)
fmt_green = Format(GREEN, _mgroup_color.breaker)
fmt_yellow = Format(YELLOW, _mgroup_color.breaker)
fmt_blue = Format(BLUE, _mgroup_color.breaker)
fmt_magenta = Format(MAGENTA, _mgroup_color.breaker)
fmt_cyan = Format(CYAN, _mgroup_color.breaker)

fmt_bg_red = Format(BG_RED, _mgroup_bg_color.breaker)
fmt_bg_green = Format(BG_GREEN, _mgroup_bg_color.breaker)
fmt_bg_yellow = Format(BG_YELLOW, _mgroup_bg_color.breaker)
fmt_bg_blue = Format(BG_BLUE, _mgroup_bg_color.breaker)
fmt_bg_magenta = Format(BG_MAGENTA, _mgroup_bg_color.breaker)
fmt_bg_cyan = Format(BG_CYAN, _mgroup_bg_color.breaker)
