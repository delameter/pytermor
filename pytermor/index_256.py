# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

from .color import Color256
from .ansi import IntCode

# fmt: off
Color256(0x000000, 0,   'black',             add_to_map=True, color16_equiv=IntCode.BLACK)
Color256(0x800000, 1,   'red',               add_to_map=True, color16_equiv=IntCode.RED)
Color256(0x008000, 2,   'green',             add_to_map=True, color16_equiv=IntCode.GREEN)
Color256(0x808000, 3,   'yellow',            add_to_map=True, color16_equiv=IntCode.YELLOW)
Color256(0x000080, 4,   'blue',              add_to_map=True, color16_equiv=IntCode.BLUE)
Color256(0x800080, 5,   'magenta',           add_to_map=True, color16_equiv=IntCode.MAGENTA)
Color256(0x008080, 6,   'cyan',              add_to_map=True, color16_equiv=IntCode.CYAN)
Color256(0xc0c0c0, 7,   'white',             add_to_map=True, color16_equiv=IntCode.WHITE)
Color256(0x808080, 8,   'gray',              add_to_map=True, color16_equiv=IntCode.GRAY)
Color256(0x800000, 9,   'hired',             add_to_map=True, color16_equiv=IntCode.HI_RED)
Color256(0x008000, 10,  'higreen',           add_to_map=True, color16_equiv=IntCode.HI_GREEN)
Color256(0x808000, 11,  'hiyellow',          add_to_map=True, color16_equiv=IntCode.HI_YELLOW)
Color256(0x000080, 12,  'hiblue',            add_to_map=True, color16_equiv=IntCode.HI_BLUE)
Color256(0x800080, 13,  'himagenta',         add_to_map=True, color16_equiv=IntCode.HI_MAGENTA)
Color256(0x008080, 14,  'hicyan',            add_to_map=True, color16_equiv=IntCode.HI_CYAN)
Color256(0xc0c0c0, 15,  'hiwhite',           add_to_map=True, color16_equiv=IntCode.HI_WHITE)
Color256(0x000000, 16,  'gray0',             add_to_map=True)
Color256(0x00005f, 17,  'navyblue',          add_to_map=True)
Color256(0x000087, 18,  'darkblue',          add_to_map=True)
Color256(0x0000af, 19,  'blue3',             add_to_map=True)
Color256(0x0000d7, 20,  'blue2',             add_to_map=True) #                                Blue3
Color256(0x0000ff, 21,  'blue1',             add_to_map=True)
Color256(0x005f00, 22,  'darkgreen',         add_to_map=True)
Color256(0x005f5f, 23,  'deepskyblue7',      add_to_map=True) #                                DeepSkyBlue4
Color256(0x005f87, 24,  'deepskyblue6',      add_to_map=True) #                                DeepSkyBlue4
Color256(0x005faf, 25,  'deepskyblue5',      add_to_map=True) #                                DeepSkyBlue4
Color256(0x005fd7, 26,  'dodgerblue3',       add_to_map=True)
Color256(0x005fff, 27,  'dodgerblue2',       add_to_map=True)
Color256(0x008700, 28,  'green5',            add_to_map=True) #                                Green4
Color256(0x00875f, 29,  'springgreen4',      add_to_map=True)
Color256(0x008787, 30,  'turquoise4',        add_to_map=True)
Color256(0x0087af, 31,  'deepskyblue4',      add_to_map=True) #                                DeepSkyBlue3
Color256(0x0087d7, 32,  'deepskyblue3',      add_to_map=True)
Color256(0x0087ff, 33,  'dodgerblue1',       add_to_map=True)
Color256(0x00af00, 34,  'green4',            add_to_map=True) #                                Green3
Color256(0x00af5f, 35,  'springgreen5',      add_to_map=True) #                                SpringGreen3
Color256(0x00af87, 36,  'darkcyan',          add_to_map=True)
Color256(0x00afaf, 37,  'lightseagreen',     add_to_map=True)
Color256(0x00afd7, 38,  'deepskyblue2',      add_to_map=True)
Color256(0x00afff, 39,  'deepskyblue1',      add_to_map=True)
Color256(0x00d700, 40,  'green3',            add_to_map=True)
Color256(0x00d75f, 41,  'springgreen3',      add_to_map=True)
Color256(0x00d787, 42,  'springgreen6',      add_to_map=True) #                                SpringGreen2
Color256(0x00d7af, 43,  'cyan3',             add_to_map=True)
Color256(0x00d7d7, 44,  'darkturquoise',     add_to_map=True)
Color256(0x00d7ff, 45,  'turquoise2',        add_to_map=True)
Color256(0x00ff00, 46,  'green2',            add_to_map=True) #                                Green1
Color256(0x00ff5f, 47,  'springgreen2',      add_to_map=True)
Color256(0x00ff87, 48,  'springgreen1',      add_to_map=True)
Color256(0x00ffaf, 49,  'mediumspringgreen', add_to_map=True)
Color256(0x00ffd7, 50,  'cyan2',             add_to_map=True)
Color256(0x00ffff, 51,  'cyan1',             add_to_map=True)
Color256(0x5f0000, 52,  'darkred2',          add_to_map=True) #                                DarkRed
Color256(0x5f005f, 53,  'deeppink8',         add_to_map=True) #                                DeepPink4
Color256(0x5f0087, 54,  'purple5',           add_to_map=True) #                                Purple4
Color256(0x5f00af, 55,  'purple4',           add_to_map=True)
Color256(0x5f00d7, 56,  'purple3',           add_to_map=True)
Color256(0x5f00ff, 57,  'blueviolet',        add_to_map=True)
Color256(0x5f5f00, 58,  'orange4',           add_to_map=True)
Color256(0x5f5f5f, 59,  'gray37',            add_to_map=True)
Color256(0x5f5f87, 60,  'mediumpurple7',     add_to_map=True) #                                MediumPurple4
Color256(0x5f5faf, 61,  'slateblue3',        add_to_map=True)
Color256(0x5f5fd7, 62,  'slateblue2',        add_to_map=True) #                                SlateBlue3
Color256(0x5f5fff, 63,  'royalblue1',        add_to_map=True)
Color256(0x5f8700, 64,  'chartreuse6',       add_to_map=True) #                                Chartreuse4
Color256(0x5f875f, 65,  'darkseagreen9',     add_to_map=True) #                                DarkSeaGreen4
Color256(0x5f8787, 66,  'paleturquoise4',    add_to_map=True)
Color256(0x5f87af, 67,  'steelblue',         add_to_map=True)
Color256(0x5f87d7, 68,  'steelblue3',        add_to_map=True)
Color256(0x5f87ff, 69,  'cornflowerblue',    add_to_map=True)
Color256(0x5faf00, 70,  'chartreuse5',       add_to_map=True) #                                Chartreuse3
Color256(0x5faf5f, 71,  'darkseagreen8',     add_to_map=True) #                                DarkSeaGreen4
Color256(0x5faf87, 72,  'cadetblue2',        add_to_map=True) #                                CadetBlue
Color256(0x5fafaf, 73,  'cadetblue',         add_to_map=True)
Color256(0x5fafd7, 74,  'skyblue3',          add_to_map=True)
Color256(0x5fafff, 75,  'steelblue2',        add_to_map=True) #                                SteelBlue1
Color256(0x5fd700, 76,  'chartreuse4',       add_to_map=True) #                                Chartreuse3
Color256(0x5fd75f, 77,  'palegreen4',        add_to_map=True) #                                PaleGreen3
Color256(0x5fd787, 78,  'seagreen3',         add_to_map=True)
Color256(0x5fd7af, 79,  'aquamarine3',       add_to_map=True)
Color256(0x5fd7d7, 80,  'mediumturquoise',   add_to_map=True)
Color256(0x5fd7ff, 81,  'steelblue1',        add_to_map=True)
Color256(0x5fff00, 82,  'chartreuse2',       add_to_map=True)
Color256(0x5fff5f, 83,  'seagreen4',         add_to_map=True) #                                SeaGreen2
Color256(0x5fff87, 84,  'seagreen2',         add_to_map=True) #                                SeaGreen1
Color256(0x5fffaf, 85,  'seagreen1',         add_to_map=True)
Color256(0x5fffd7, 86,  'aquamarine2',       add_to_map=True) #                                Aquamarine1
Color256(0x5fffff, 87,  'darkslategray2',    add_to_map=True)
Color256(0x870000, 88,  'darkred',           add_to_map=True)
Color256(0x87005f, 89,  'deeppink7',         add_to_map=True) #                                DeepPink4
Color256(0x870087, 90,  'darkmagenta2',      add_to_map=True) #                                DarkMagenta
Color256(0x8700af, 91,  'darkmagenta',       add_to_map=True)
Color256(0x8700d7, 92,  'darkviolet2',       add_to_map=True) #                                DarkViolet
Color256(0x8700ff, 93,  'purple2',           add_to_map=True) #                                Purple
Color256(0x875f00, 94,  'orange3',           add_to_map=True) #                                Orange4
Color256(0x875f5f, 95,  'lightpink3',        add_to_map=True) #                                LightPink4
Color256(0x875f87, 96,  'plum4',             add_to_map=True)
Color256(0x875faf, 97,  'mediumpurple6',     add_to_map=True) #                                MediumPurple3
Color256(0x875fd7, 98,  'mediumpurple5',     add_to_map=True) #                                MediumPurple3
Color256(0x875fff, 99,  'slateblue1',        add_to_map=True)
Color256(0x878700, 100, 'yellow6',           add_to_map=True) #                                Yellow4
Color256(0x87875f, 101, 'wheat4',            add_to_map=True)
Color256(0x878787, 102, 'gray53',            add_to_map=True)
Color256(0x8787af, 103, 'lightslategray',    add_to_map=True)
Color256(0x8787d7, 104, 'mediumpurple4',     add_to_map=True) #                                MediumPurple
Color256(0x8787ff, 105, 'lightslateblue',    add_to_map=True)
Color256(0x87af00, 106, 'yellow4',           add_to_map=True)
Color256(0x87af5f, 107, 'darkolivegreen6',   add_to_map=True) #                                DarkOliveGreen3
Color256(0x87af87, 108, 'darkseagreen7',     add_to_map=True) #                                DarkSeaGreen
Color256(0x87afaf, 109, 'lightskyblue3',     add_to_map=True)
Color256(0x87afd7, 110, 'lightskyblue2',     add_to_map=True) #                                LightSkyBlue3
Color256(0x87afff, 111, 'skyblue2',          add_to_map=True)
Color256(0x87d700, 112, 'chartreuse3',       add_to_map=True) #                                Chartreuse2
Color256(0x87d75f, 113, 'darkolivegreen4',   add_to_map=True) #                                DarkOliveGreen3
Color256(0x87d787, 114, 'palegreen3',        add_to_map=True)
Color256(0x87d7af, 115, 'darkseagreen5',     add_to_map=True) #                                DarkSeaGreen3
Color256(0x87d7d7, 116, 'darkslategray3',    add_to_map=True)
Color256(0x87d7ff, 117, 'skyblue1',          add_to_map=True)
Color256(0x87ff00, 118, 'chartreuse1',       add_to_map=True)
Color256(0x87ff5f, 119, 'lightgreen2',       add_to_map=True) #                                LightGreen
Color256(0x87ff87, 120, 'lightgreen',        add_to_map=True)
Color256(0x87ffaf, 121, 'palegreen1',        add_to_map=True)
Color256(0x87ffd7, 122, 'aquamarine1',       add_to_map=True)
Color256(0x87ffff, 123, 'darkslategray1',    add_to_map=True)
Color256(0xaf0000, 124, 'red4',              add_to_map=True) #                                Red3
Color256(0xaf005f, 125, 'deeppink6',         add_to_map=True) #                                DeepPink4
Color256(0xaf0087, 126, 'mediumvioletred',   add_to_map=True)
Color256(0xaf00af, 127, 'magenta6',          add_to_map=True) #                                Magenta3
Color256(0xaf00d7, 128, 'darkviolet',        add_to_map=True)
Color256(0xaf00ff, 129, 'purple',            add_to_map=True)
Color256(0xaf5f00, 130, 'darkorange3',       add_to_map=True)
Color256(0xaf5f5f, 131, 'indianred4',        add_to_map=True) #                                IndianRed
Color256(0xaf5f87, 132, 'hotpink5',          add_to_map=True) #                                HotPink3
Color256(0xaf5faf, 133, 'mediumorchid4',     add_to_map=True) #                                MediumOrchid3
Color256(0xaf5fd7, 134, 'mediumorchid3',     add_to_map=True) #                                MediumOrchid
Color256(0xaf5fff, 135, 'mediumpurple2',     add_to_map=True)
Color256(0xaf8700, 136, 'darkgoldenrod',     add_to_map=True)
Color256(0xaf875f, 137, 'lightsalmon3',      add_to_map=True)
Color256(0xaf8787, 138, 'rosybrown',         add_to_map=True)
Color256(0xaf87af, 139, 'gray63',            add_to_map=True)
Color256(0xaf87d7, 140, 'mediumpurple3',     add_to_map=True) #                                MediumPurple2
Color256(0xaf87ff, 141, 'mediumpurple1',     add_to_map=True)
Color256(0xafaf00, 142, 'gold3',             add_to_map=True)
Color256(0xafaf5f, 143, 'darkkhaki',         add_to_map=True)
Color256(0xafaf87, 144, 'navajowhite3',      add_to_map=True)
Color256(0xafafaf, 145, 'gray69',            add_to_map=True)
Color256(0xafafd7, 146, 'lightsteelblue3',   add_to_map=True)
Color256(0xafafff, 147, 'lightsteelblue2',   add_to_map=True) #                                LightSteelBlue
Color256(0xafd700, 148, 'yellow5',           add_to_map=True) #                                Yellow3
Color256(0xafd75f, 149, 'darkolivegreen5',   add_to_map=True) #                                DarkOliveGreen3
Color256(0xafd787, 150, 'darkseagreen6',     add_to_map=True) #                                DarkSeaGreen3
Color256(0xafd7af, 151, 'darkseagreen4',     add_to_map=True) #                                DarkSeaGreen2
Color256(0xafd7d7, 152, 'lightcyan3',        add_to_map=True)
Color256(0xafd7ff, 153, 'lightskyblue1',     add_to_map=True)
Color256(0xafff00, 154, 'greenyellow',       add_to_map=True)
Color256(0xafff5f, 155, 'darkolivegreen3',   add_to_map=True) #                                DarkOliveGreen2
Color256(0xafff87, 156, 'palegreen2',        add_to_map=True) #                                PaleGreen1
Color256(0xafffaf, 157, 'darkseagreen3',     add_to_map=True) #                                DarkSeaGreen2
Color256(0xafffd7, 158, 'darkseagreen1',     add_to_map=True)
Color256(0xafffff, 159, 'paleturquoise1',    add_to_map=True)
Color256(0xd70000, 160, 'red3',              add_to_map=True)
Color256(0xd7005f, 161, 'deeppink5',         add_to_map=True) #                                DeepPink3
Color256(0xd70087, 162, 'deeppink3',         add_to_map=True)
Color256(0xd700af, 163, 'magenta3',          add_to_map=True)
Color256(0xd700d7, 164, 'magenta5',          add_to_map=True) #                                Magenta3
Color256(0xd700ff, 165, 'magenta4',          add_to_map=True) #                                Magenta2
Color256(0xd75f00, 166, 'darkorange2',       add_to_map=True) #                                DarkOrange3
Color256(0xd75f5f, 167, 'indianred3',        add_to_map=True) #                                IndianRed
Color256(0xd75f87, 168, 'hotpink4',          add_to_map=True) #                                HotPink3
Color256(0xd75faf, 169, 'hotpink3',          add_to_map=True) #                                HotPink2
Color256(0xd75fd7, 170, 'orchid3',           add_to_map=True) #                                Orchid
Color256(0xd75fff, 171, 'mediumorchid2',     add_to_map=True) #                                MediumOrchid1
Color256(0xd78700, 172, 'orange2',           add_to_map=True) #                                Orange3
Color256(0xd7875f, 173, 'lightsalmon2',      add_to_map=True) #                                LightSalmon3
Color256(0xd78787, 174, 'lightpink2',        add_to_map=True) #                                LightPink3
Color256(0xd787af, 175, 'pink3',             add_to_map=True)
Color256(0xd787d7, 176, 'plum3',             add_to_map=True)
Color256(0xd787ff, 177, 'violet',            add_to_map=True)
Color256(0xd7af00, 178, 'gold2',             add_to_map=True) #                                Gold3
Color256(0xd7af5f, 179, 'lightgoldenrod5',   add_to_map=True) #                                LightGoldenrod3
Color256(0xd7af87, 180, 'tan',               add_to_map=True)
Color256(0xd7afaf, 181, 'mistyrose3',        add_to_map=True)
Color256(0xd7afd7, 182, 'thistle3',          add_to_map=True)
Color256(0xd7afff, 183, 'plum2',             add_to_map=True)
Color256(0xd7d700, 184, 'yellow3',           add_to_map=True)
Color256(0xd7d75f, 185, 'khaki3',            add_to_map=True)
Color256(0xd7d787, 186, 'lightgoldenrod3',   add_to_map=True) #                                LightGoldenrod2
Color256(0xd7d7af, 187, 'lightyellow3',      add_to_map=True)
Color256(0xd7d7d7, 188, 'gray84',            add_to_map=True)
Color256(0xd7d7ff, 189, 'lightsteelblue1',   add_to_map=True)
Color256(0xd7ff00, 190, 'yellow2',           add_to_map=True)
Color256(0xd7ff5f, 191, 'darkolivegreen2',   add_to_map=True) #                                DarkOliveGreen1
Color256(0xd7ff87, 192, 'darkolivegreen1',   add_to_map=True)
Color256(0xd7ffaf, 193, 'darkseagreen2',     add_to_map=True) #                                DarkSeaGreen1
Color256(0xd7ffd7, 194, 'honeydew2',         add_to_map=True)
Color256(0xd7ffff, 195, 'lightcyan1',        add_to_map=True)
Color256(0xff0000, 196, 'red1',              add_to_map=True)
Color256(0xff005f, 197, 'deeppink4',         add_to_map=True) #                                DeepPink2
Color256(0xff0087, 198, 'deeppink2',         add_to_map=True) #                                DeepPink1
Color256(0xff00af, 199, 'deeppink1',         add_to_map=True)
Color256(0xff00d7, 200, 'magenta2',          add_to_map=True)
Color256(0xff00ff, 201, 'magenta1',          add_to_map=True)
Color256(0xff5f00, 202, 'orangered1',        add_to_map=True)
Color256(0xff5f5f, 203, 'indianred1',        add_to_map=True)
Color256(0xff5f87, 204, 'indianred2',        add_to_map=True) #                                IndianRed1
Color256(0xff5faf, 205, 'hotpink2',          add_to_map=True) #                                HotPink
Color256(0xff5fd7, 206, 'hotpink',           add_to_map=True)
Color256(0xff5fff, 207, 'mediumorchid1',     add_to_map=True)
Color256(0xff8700, 208, 'darkorange',        add_to_map=True)
Color256(0xff875f, 209, 'salmon1',           add_to_map=True)
Color256(0xff8787, 210, 'lightcoral',        add_to_map=True)
Color256(0xff87af, 211, 'palevioletred1',    add_to_map=True)
Color256(0xff87d7, 212, 'orchid2',           add_to_map=True)
Color256(0xff87ff, 213, 'orchid1',           add_to_map=True)
Color256(0xffaf00, 214, 'orange1',           add_to_map=True)
Color256(0xffaf5f, 215, 'sandybrown',        add_to_map=True)
Color256(0xffaf87, 216, 'lightsalmon1',      add_to_map=True)
Color256(0xffafaf, 217, 'lightpink1',        add_to_map=True)
Color256(0xffafd7, 218, 'pink1',             add_to_map=True)
Color256(0xffafff, 219, 'plum1',             add_to_map=True)
Color256(0xffd700, 220, 'gold1',             add_to_map=True)
Color256(0xffd75f, 221, 'lightgoldenrod4',   add_to_map=True) #                                LightGoldenrod2
Color256(0xffd787, 222, 'lightgoldenrod2',   add_to_map=True)
Color256(0xffd7af, 223, 'navajowhite1',      add_to_map=True)
Color256(0xffd7d7, 224, 'mistyrose1',        add_to_map=True)
Color256(0xffd7ff, 225, 'thistle1',          add_to_map=True)
Color256(0xffff00, 226, 'yellow1',           add_to_map=True)
Color256(0xffff5f, 227, 'lightgoldenrod1',   add_to_map=True)
Color256(0xffff87, 228, 'khaki1',            add_to_map=True)
Color256(0xffffaf, 229, 'wheat1',            add_to_map=True)
Color256(0xffffd7, 230, 'cornsilk1',         add_to_map=True)
Color256(0xffffff, 231, 'gray100',           add_to_map=True)
GRAY_3 = Color256(0x080808, 232, 'gray3',             add_to_map=True)
Color256(0x121212, 233, 'gray7',             add_to_map=True)
Color256(0x1c1c1c, 234, 'gray11',            add_to_map=True)
Color256(0x262626, 235, 'gray15',            add_to_map=True)
Color256(0x303030, 236, 'gray19',            add_to_map=True)
Color256(0x3a3a3a, 237, 'gray23',            add_to_map=True)
Color256(0x444444, 238, 'gray27',            add_to_map=True)
GRAY_30 = Color256(0x4e4e4e, 239, 'gray30',            add_to_map=True)
Color256(0x585858, 240, 'gray35',            add_to_map=True)
Color256(0x626262, 241, 'gray39',            add_to_map=True)
GRAY_42 = Color256(0x6c6c6c, 242, 'gray42',            add_to_map=True)
Color256(0x767676, 243, 'gray46',            add_to_map=True)
Color256(0x808080, 244, 'gray50',            add_to_map=True)
Color256(0x8a8a8a, 245, 'gray54',            add_to_map=True)
Color256(0x949494, 246, 'gray58',            add_to_map=True)
Color256(0x9e9e9e, 247, 'gray62',            add_to_map=True)
Color256(0xa8a8a8, 248, 'gray66',            add_to_map=True)
Color256(0xb2b2b2, 249, 'gray70',            add_to_map=True)
Color256(0xbcbcbc, 250, 'gray74',            add_to_map=True)
Color256(0xc6c6c6, 251, 'gray78',            add_to_map=True)
GRAY_82 = Color256(0xd0d0d0, 252, 'gray82',            add_to_map=True)
Color256(0xdadada, 253, 'gray85',            add_to_map=True)
Color256(0xe4e4e4, 254, 'gray89',            add_to_map=True)
Color256(0xeeeeee, 255, 'gray93',            add_to_map=True)
# fmt: on
