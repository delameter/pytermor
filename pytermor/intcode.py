# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""
Module with SGR param integer codes, contains a complete or almost complete
list of reliably working ones.

Suitable for :class:`.Span` and :class:`.SequenceSGR` default constructors.
"""
# -- Default attributes and colors --------------------------------------------

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
NO_BOLD_DIM = 22  # there is no separate sequence for disabling either
ITALIC_OFF = 23               # of BOLD or DIM while keeping the other
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
#    26: proportional spacing
#    50: disable proportional spacing
#    51: framed
#    52: encircled
#    54: neither framed nor encircled
# 58-59: underline color
# 60-65: ideogram attributes
# 73-75: superscript and subscript


# -- Default colors lists -----------------------------------------------------

LIST_COLORS = list(range(30, 39))
LIST_BG_COLORS = list(range(40, 49))
LIST_HI_COLORS = list(range(90, 98))
LIST_BG_HI_COLORS = list(range(100, 108))

LIST_ALL_COLORS = LIST_COLORS + LIST_BG_COLORS + \
                  LIST_HI_COLORS + LIST_BG_HI_COLORS


# -- EXTENDED modifiers -------------------------------------------------------

_EXTENDED_MODE_256 = 5
_EXTENDED_MODE_RGB = 2


# -- Indexed mode / 256 colors ------------------------------------------------
# ---------------------------------- GENERATED ---------------------------------

XTERM_BLACK = 0
XTERM_MAROON = 1
XTERM_GREEN = 2
XTERM_OLIVE = 3
XTERM_NAVY = 4
XTERM_PURPLE_5 = 5
XTERM_TEAL = 6
XTERM_SILVER = 7
XTERM_GREY = 8
XTERM_RED = 9
XTERM_LIME = 10
XTERM_YELLOW = 11
XTERM_BLUE = 12
XTERM_FUCHSIA = 13
XTERM_AQUA = 14
XTERM_WHITE = 15
XTERM_GREY_0 = 16
XTERM_NAVY_BLUE = 17
XTERM_DARK_BLUE = 18
XTERM_BLUE_3 = 19
XTERM_BLUE_2 = 20
XTERM_BLUE_1 = 21
XTERM_DARK_GREEN = 22
XTERM_DEEP_SKY_BLUE_7 = 23
XTERM_DEEP_SKY_BLUE_6 = 24
XTERM_DEEP_SKY_BLUE_5 = 25
XTERM_DODGER_BLUE_3 = 26
XTERM_DODGER_BLUE_2 = 27
XTERM_GREEN_5 = 28
XTERM_SPRING_GREEN_4 = 29
XTERM_TURQUOISE_4 = 30
XTERM_DEEP_SKY_BLUE_4 = 31
XTERM_DEEP_SKY_BLUE_3 = 32
XTERM_DODGER_BLUE_1 = 33
XTERM_GREEN_4 = 34
XTERM_SPRING_GREEN_5 = 35
XTERM_DARK_CYAN = 36
XTERM_LIGHT_SEA_GREEN = 37
XTERM_DEEP_SKY_BLUE_2 = 38
XTERM_DEEP_SKY_BLUE_1 = 39
XTERM_GREEN_3 = 40
XTERM_SPRING_GREEN_3 = 41
XTERM_SPRING_GREEN_6 = 42
XTERM_CYAN_3 = 43
XTERM_DARK_TURQUOISE = 44
XTERM_TURQUOISE_2 = 45
XTERM_GREEN_2 = 46
XTERM_SPRING_GREEN_2 = 47
XTERM_SPRING_GREEN_1 = 48
XTERM_MEDIUM_SPRING_GREEN = 49
XTERM_CYAN_2 = 50
XTERM_CYAN_1 = 51
XTERM_DARK_RED_2 = 52
XTERM_DEEP_PINK_8 = 53
XTERM_PURPLE_6 = 54
XTERM_PURPLE_4 = 55
XTERM_PURPLE_3 = 56
XTERM_BLUE_VIOLET = 57
XTERM_ORANGE_4 = 58
XTERM_GREY_37 = 59
XTERM_MEDIUM_PURPLE_7 = 60
XTERM_SLATE_BLUE_3 = 61
XTERM_SLATE_BLUE_2 = 62
XTERM_ROYAL_BLUE_1 = 63
XTERM_CHARTREUSE_6 = 64
XTERM_DARK_SEA_GREEN_9 = 65
XTERM_PALE_TURQUOISE_4 = 66
XTERM_STEEL_BLUE = 67
XTERM_STEEL_BLUE_3 = 68
XTERM_CORNFLOWER_BLUE = 69
XTERM_CHARTREUSE_5 = 70
XTERM_DARK_SEA_GREEN_8 = 71
XTERM_CADET_BLUE_2 = 72
XTERM_CADET_BLUE = 73
XTERM_SKY_BLUE_3 = 74
XTERM_STEEL_BLUE_2 = 75
XTERM_CHARTREUSE_4 = 76
XTERM_PALE_GREEN_4 = 77
XTERM_SEA_GREEN_3 = 78
XTERM_AQUAMARINE_3 = 79
XTERM_MEDIUM_TURQUOISE = 80
XTERM_STEEL_BLUE_1 = 81
XTERM_CHARTREUSE_2 = 82
XTERM_SEA_GREEN_4 = 83
XTERM_SEA_GREEN_2 = 84
XTERM_SEA_GREEN_1 = 85
XTERM_AQUAMARINE_2 = 86
XTERM_DARK_SLATE_GRAY_2 = 87
XTERM_DARK_RED = 88
XTERM_DEEP_PINK_7 = 89
XTERM_DARK_MAGENTA_2 = 90
XTERM_DARK_MAGENTA = 91
XTERM_DARK_VIOLET_2 = 92
XTERM_PURPLE_2 = 93
XTERM_ORANGE_3 = 94
XTERM_LIGHT_PINK_3 = 95
XTERM_PLUM_4 = 96
XTERM_MEDIUM_PURPLE_6 = 97
XTERM_MEDIUM_PURPLE_5 = 98
XTERM_SLATE_BLUE_1 = 99
XTERM_YELLOW_6 = 100
XTERM_WHEAT_4 = 101
XTERM_GREY_53 = 102
XTERM_LIGHT_SLATE_GREY = 103
XTERM_MEDIUM_PURPLE_4 = 104
XTERM_LIGHT_SLATE_BLUE = 105
XTERM_YELLOW_4 = 106
XTERM_DARK_OLIVE_GREEN_6 = 107
XTERM_DARK_SEA_GREEN_7 = 108
XTERM_LIGHT_SKY_BLUE_3 = 109
XTERM_LIGHT_SKY_BLUE_2 = 110
XTERM_SKY_BLUE_2 = 111
XTERM_CHARTREUSE_3 = 112
XTERM_DARK_OLIVE_GREEN_4 = 113
XTERM_PALE_GREEN_3 = 114
XTERM_DARK_SEA_GREEN_5 = 115
XTERM_DARK_SLATE_GRAY_3 = 116
XTERM_SKY_BLUE_1 = 117
XTERM_CHARTREUSE_1 = 118
XTERM_LIGHT_GREEN_2 = 119
XTERM_LIGHT_GREEN = 120
XTERM_PALE_GREEN_1 = 121
XTERM_AQUAMARINE_1 = 122
XTERM_DARK_SLATE_GRAY_1 = 123
XTERM_RED_4 = 124
XTERM_DEEP_PINK_6 = 125
XTERM_MEDIUM_VIOLET_RED = 126
XTERM_MAGENTA_6 = 127
XTERM_DARK_VIOLET = 128
XTERM_PURPLE = 129
XTERM_DARK_ORANGE_3 = 130
XTERM_INDIAN_RED_4 = 131
XTERM_HOT_PINK_5 = 132
XTERM_MEDIUM_ORCHID_4 = 133
XTERM_MEDIUM_ORCHID_3 = 134
XTERM_MEDIUM_PURPLE_2 = 135
XTERM_DARK_GOLDENROD = 136
XTERM_LIGHT_SALMON_3 = 137
XTERM_ROSY_BROWN = 138
XTERM_GREY_63 = 139
XTERM_MEDIUM_PURPLE_3 = 140
XTERM_MEDIUM_PURPLE_1 = 141
XTERM_GOLD_3 = 142
XTERM_DARK_KHAKI = 143
XTERM_NAVAJO_WHITE_3 = 144
XTERM_GREY_69 = 145
XTERM_LIGHT_STEEL_BLUE_3 = 146
XTERM_LIGHT_STEEL_BLUE_2 = 147
XTERM_YELLOW_5 = 148
XTERM_DARK_OLIVE_GREEN_5 = 149
XTERM_DARK_SEA_GREEN_6 = 150
XTERM_DARK_SEA_GREEN_4 = 151
XTERM_LIGHT_CYAN_3 = 152
XTERM_LIGHT_SKY_BLUE_1 = 153
XTERM_GREEN_YELLOW = 154
XTERM_DARK_OLIVE_GREEN_3 = 155
XTERM_PALE_GREEN_2 = 156
XTERM_DARK_SEA_GREEN_3 = 157
XTERM_DARK_SEA_GREEN_1 = 158
XTERM_PALE_TURQUOISE_1 = 159
XTERM_RED_3 = 160
XTERM_DEEP_PINK_5 = 161
XTERM_DEEP_PINK_3 = 162
XTERM_MAGENTA_3 = 163
XTERM_MAGENTA_5 = 164
XTERM_MAGENTA_4 = 165
XTERM_DARK_ORANGE_2 = 166
XTERM_INDIAN_RED_3 = 167
XTERM_HOT_PINK_4 = 168
XTERM_HOT_PINK_3 = 169
XTERM_ORCHID_3 = 170
XTERM_MEDIUM_ORCHID_2 = 171
XTERM_ORANGE_2 = 172
XTERM_LIGHT_SALMON_2 = 173
XTERM_LIGHT_PINK_2 = 174
XTERM_PINK_3 = 175
XTERM_PLUM_3 = 176
XTERM_VIOLET = 177
XTERM_GOLD_2 = 178
XTERM_LIGHT_GOLDENROD_5 = 179
XTERM_TAN = 180
XTERM_MISTY_ROSE_3 = 181
XTERM_THISTLE_3 = 182
XTERM_PLUM_2 = 183
XTERM_YELLOW_3 = 184
XTERM_KHAKI_3 = 185
XTERM_LIGHT_GOLDENROD_3 = 186
XTERM_LIGHT_YELLOW_3 = 187
XTERM_GREY_84 = 188
XTERM_LIGHT_STEEL_BLUE_1 = 189
XTERM_YELLOW_2 = 190
XTERM_DARK_OLIVE_GREEN_2 = 191
XTERM_DARK_OLIVE_GREEN_1 = 192
XTERM_DARK_SEA_GREEN_2 = 193
XTERM_HONEYDEW_2 = 194
XTERM_LIGHT_CYAN_1 = 195
XTERM_RED_1 = 196
XTERM_DEEP_PINK_4 = 197
XTERM_DEEP_PINK_2 = 198
XTERM_DEEP_PINK_1 = 199
XTERM_MAGENTA_2 = 200
XTERM_MAGENTA_1 = 201
XTERM_ORANGE_RED_1 = 202
XTERM_INDIAN_RED_1 = 203
XTERM_INDIAN_RED_2 = 204
XTERM_HOT_PINK_2 = 205
XTERM_HOT_PINK = 206
XTERM_MEDIUM_ORCHID_1 = 207
XTERM_DARK_ORANGE = 208
XTERM_SALMON_1 = 209
XTERM_LIGHT_CORAL = 210
XTERM_PALE_VIOLET_RED_1 = 211
XTERM_ORCHID_2 = 212
XTERM_ORCHID_1 = 213
XTERM_ORANGE_1 = 214
XTERM_SANDY_BROWN = 215
XTERM_LIGHT_SALMON_1 = 216
XTERM_LIGHT_PINK_1 = 217
XTERM_PINK_1 = 218
XTERM_PLUM_1 = 219
XTERM_GOLD_1 = 220
XTERM_LIGHT_GOLDENROD_4 = 221
XTERM_LIGHT_GOLDENROD_2 = 222
XTERM_NAVAJO_WHITE_1 = 223
XTERM_MISTY_ROSE_1 = 224
XTERM_THISTLE_1 = 225
XTERM_YELLOW_1 = 226
XTERM_LIGHT_GOLDENROD_1 = 227
XTERM_KHAKI_1 = 228
XTERM_WHEAT_1 = 229
XTERM_CORNSILK_1 = 230
XTERM_GREY_100 = 231
XTERM_GREY_3 = 232
XTERM_GREY_7 = 233
XTERM_GREY_11 = 234
XTERM_GREY_15 = 235
XTERM_GREY_19 = 236
XTERM_GREY_23 = 237
XTERM_GREY_27 = 238
XTERM_GREY_30 = 239
XTERM_GREY_35 = 240
XTERM_GREY_39 = 241
XTERM_GREY_42 = 242
XTERM_GREY_46 = 243
XTERM_GREY_50 = 244
XTERM_GREY_54 = 245
XTERM_GREY_58 = 246
XTERM_GREY_62 = 247
XTERM_GREY_66 = 248
XTERM_GREY_70 = 249
XTERM_GREY_74 = 250
XTERM_GREY_78 = 251
XTERM_GREY_82 = 252
XTERM_GREY_85 = 253
XTERM_GREY_89 = 254
XTERM_GREY_93 = 255
