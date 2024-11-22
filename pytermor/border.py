# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
"""
Module for drawing various borders around text using
ASCII and Unicode characters.
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from functools import cached_property

from .color import DEFAULT_COLOR
from .common import fit, Align, pad, isiterable, flatten
from .cval import cv
from .style import Styles, FrozenStyle
from .text import Fragment, FrozenText, RT, Text, echo


@dataclass(frozen=True)
class Border:
    """
    Attribute diagram and argument order::

        TL  T  TR    1 → 2 → 3
          ┌ ─ ┐      ↑ ┌ ─ ┐ ↓     L, TL,  T, TR,  R, BL,  B, BR
        L │   │ R    0 │   │ 4
          └ ─ ┘        └ ─ ┘       0 → 1 → 2 → 3 → 4 → 5 → 6 → 7
        BL  B  BR    5 → 6 → 7

    >>> data = ["example", "loooooooooooooong", "string"]
    >>> for line in LINE_SINGLE.make(12, data):
    ...     print(line)
    ┌──────────┐
    │ example  │
    │ loooooo‥ │
    │ string   │
    └──────────┘

    """

    _DEFAULT = "\u2800"  # U+2800 ▕ ⠀ ▏So BRAILLE PATTERN BLANK

    l: str = _DEFAULT
    tl: str = _DEFAULT
    t: str = _DEFAULT
    tr: str = _DEFAULT
    r: str = _DEFAULT
    bl: str = _DEFAULT
    b: str = _DEFAULT
    br: str = _DEFAULT

    @cached_property
    def parts(self) -> list[str]:
        return [self.l, self.tl, self.t, self.tr, self.r, self.bl, self.b, self.br]

    @cached_property
    def part_chars(self) -> set[str]:
        return {*self.parts}

    @cached_property
    def part_dict(self) -> dict[str, str]:
        return {
            "l": self.l,
            "tl": self.tl,
            "t": self.t,
            "tr": self.tr,
            "r": self.r,
            "bl": self.bl,
            "b": self.b,
            "br": self.br,
        }

    def __str__(self):
        return "".join(self.parts)

    def make(
        self,
        width: int,
        content: Iterable[RT] | RT = None,
        align: Align | str = Align.LEFT,
        pad_x: int = 1,
        pad_y: int = 0,
    ) -> Iterable[RT]:
        if not isiterable(content):
            content = [content]
        if pad_y:
            pad_y_lines = pad_y * [""]
            content = pad_y_lines + content + pad_y_lines

        yield self.make_top(width, None, None, 0)
        yield from [self.make_middle(width, line, align, pad_x) for line in content]
        yield self.make_bottom(width, None, None, 0)

    def make_top(self, *args) -> RT:
        return self._make_line(self.tl, self.t, self.tr, *args)

    def make_middle(self, *args) -> RT:
        return self._make_line(self.l, " ", self.r, *args)

    def make_bottom(self, *args) -> RT:
        return self._make_line(self.bl, self.b, self.br, *args)

    # noinspection PyMethodMayBeStatic
    def _make_line(
        self,
        left: RT,
        fill: RT,
        right: RT,
        width: int,
        content: RT,
        align: Align,
        pad_x: int,
    ) -> RT:
        content_width = max(0, width - (len(left) + len(right) + 2 * pad_x))
        pad_left = pad_right = pad(pad_x)
        content = content or ""
        align = align or Align.LEFT
        if isinstance(content, str):
            fill = fit(content, content_width, align, fill=fill)
            return left + pad_left + fill + pad_right + right
        return FrozenText(
            left,
            pad_left,
            content,
            pad_right,
            right,
            width=content_width + len(left) + len(pad_left) + len(pad_right) + len(right),
            align=align,
            fill=fill,
        )


class _BorderDebuggerStyles(Styles):
    BORDER_DEBUG = {
        "tr": cv.HI_RED,
        "t": cv.RED,
        "tl": cv.HI_YELLOW,
        "l": cv.YELLOW,
        "bl": cv.HI_GREEN,
        "r": cv.MAGENTA,
        "br": cv.HI_MAGENTA,
        "b": cv.GREEN,
    }

    @classmethod
    def get_color(cls, part: str) -> FrozenStyle:
        # corner = len(part) > 1
        return FrozenStyle(fg=cls.BORDER_DEBUG.get(part, DEFAULT_COLOR), bg=cv.GRAY_0)


@dataclass(frozen=True)
class _BorderDebugger(Border):
    idx: int = None
    name: str = None

    @cached_property
    def mod_tl(self):
        return Fragment(self.tl, _BorderDebuggerStyles.get_color("tl"))

    @cached_property
    def mod_t(self):
        return Fragment(self.t, _BorderDebuggerStyles.get_color("t"))

    @cached_property
    def mod_tr(self):
        return Fragment(self.tr, _BorderDebuggerStyles.get_color("tr"))

    @cached_property
    def mod_l(self):
        return Fragment(self.l, _BorderDebuggerStyles.get_color("l"))

    @cached_property
    def mod_r(self):
        return Fragment(self.r, _BorderDebuggerStyles.get_color("r"))

    @cached_property
    def mod_bl(self):
        return Fragment(self.bl, _BorderDebuggerStyles.get_color("bl"))

    @cached_property
    def mod_b(self):
        return Fragment(self.b, _BorderDebuggerStyles.get_color("b"))

    @cached_property
    def mod_br(self):
        return Fragment(self.br, _BorderDebuggerStyles.get_color("br"))

    def make_top(self, *args) -> RT:
        return self._make_line(self.mod_tl, self.mod_t, self.mod_tr, *args)

    def make_middle(self, *args) -> RT:
        return self._make_line(self.mod_l, " ", self.mod_r, *args)

    def make_bottom(self, *args) -> RT:
        return self._make_line(self.mod_bl, self.mod_b, self.mod_br, *args)

    def print_sample(self):
        out_w = 40
        inn_left_w = 0
        align_inn_right = "^"
        inn_left = None
        if self.name:
            inn_left_w = 33
            out_w += inn_left_w
            align_inn_right = ">"

            def __raw(*line: RT) -> list[str]:
                return [s.raw() for s in line]

            inn_left_1 = __raw(*self.make(6, f"{self.idx:02}"))
            inn_left_2 = __raw(
                *self.make(inn_left_w - 6, fit(self.name or "", inn_left_w - 10, "^"))
            )
            inn_left = [i1 + i2 for (i1, i2) in zip(inn_left_1, inn_left_2)]
        inn_right_w = out_w - inn_left_w - 4

        sample_values = [
            ("  ", Fragment(v, _BorderDebuggerStyles.get_color("")), " ")
            for v in self.part_dict.values()
        ]
        sample_labels = [
            (" ", Fragment(f"{k.upper():^3s}", _BorderDebuggerStyles.get_color(k)), "")
            for k in self.part_dict.keys()
        ]
        inn_right = [
            FrozenText(*sample_values, cv.GRAY_100, width=inn_right_w, align=align_inn_right),
            FrozenText(pad(inn_right_w)),
            FrozenText(*flatten(sample_labels), width=inn_right_w, align=align_inn_right),
        ]
        if self.name:
            inner = [i1 + i2 for (i1, i2) in zip(inn_left, inn_right)]
        else:
            inner = inn_right
        outer = [*self.make(out_w, [Text(line) for line in inner], "<", pad_x=1, pad_y=0)]

        for line in outer:
            echo(line)

    @classmethod
    def print_all_samples(cls):
        for (idx, (name, border)) in enumerate(sorted(ALL.items())):
            dbg = cls(*border.parts, idx + 1, name)
            dbg.print_sample()
            echo()


ASCII_DOTTED = Border(*":...::.:")
"""
.. highlight:: rst

ASCII dotted border::

    .................................
    : 01 ::      ASCII_DOTTED       :
    :....::.........................:

:meta hide-value:
"""

ASCII_DOUBLE = Border(*"#*=*#*=*")
"""
ASCII double line border:: 

    *====**=========================*
    # 02 ##      ASCII_DOUBLE       #
    *====**=========================*

:meta hide-value:
"""

ASCII_SINGLE = Border(*"|+-+|+-+")
"""
ASCII single line border::

    +----++-------------------------+
    | 03 ||      ASCII_SINGLE       |
    +----++-------------------------+
 
:meta hide-value:
"""

BLOCK_DOTTED_COMPACT = Border(*"▗▗▗▖▘▝▘▘")
"""
Unicode dotted (1/4) block compact border::

    ▗▗▗▗▗▖▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▖
    ▗ 04 ▘▗  BLOCK_DOTTED_COMPACT   ▘
    ▝▘▘▘▘▘▝▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘

:meta hide-value:
"""

BLOCK_DOTTED_REGULAR = Border(*"▖▌▘▀▝▄▗▐")
"""
Unicode dotted (1/4) block border::

    ▌▘▘▘▘▀▌▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▀
    ▖ 05 ▝▖  BLOCK_DOTTED_REGULAR   ▝
    ▄▗▗▗▗▐▄▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▐

:meta hide-value:
"""

BLOCK_DOTTED_UNIFORM_LB = Border(*"▖" * 8)
"""
Unicode uniform (1/4) block border, var. 3::

    ▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖
    ▖ 06 ▖▖ BLOCK_DOTTED_UNIFORM_LB ▖
    ▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖

:meta hide-value:
"""

BLOCK_DOTTED_UNIFORM_LT = Border(*"▘" * 8)
"""
Unicode uniform (1/4) block border, var. 1::

    ▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘
    ▘ 07 ▘▘ BLOCK_DOTTED_UNIFORM_LT ▘
    ▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘

:meta hide-value:
"""

BLOCK_DOTTED_UNIFORM_RB = Border(*"▗" * 8)
"""
Unicode uniform (1/4) block border, var. 4::

    ▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗
    ▗ 08 ▗▗ BLOCK_DOTTED_UNIFORM_RB ▗
    ▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗

:meta hide-value:
"""

BLOCK_DOTTED_UNIFORM_RT = Border(*"▝" * 8)
"""
Unicode uniform (1/4) block border, var. 2::

    ▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝
    ▝ 09 ▝▝ BLOCK_DOTTED_UNIFORM_RT ▝
    ▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝

:meta hide-value:
"""

BLOCK_FULL = Border(*"█" * 8)
"""
Unicode full (1/1) block border::

    █████████████████████████████████
    █ 10 ██       BLOCK_FULL        █
    █████████████████████████████████

:meta hide-value:
"""

BLOCK_THICK = Border(*"▌▛▀▜▐▙▄▟")
"""
Unicode thick (1/2) block border::

    ▛▀▀▀▀▜▛▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▜
    ▌ 11 ▐▌       BLOCK_THICK       ▐
    ▙▄▄▄▄▟▙▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▟

:meta hide-value:
"""

BLOCK_THICK_INNER = Border(*"▐▗▄▖▌▝▀▘")
"""
Unicode thick (1/2) block inner border::

    ▗▄▄▄▄▖▗▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▖
    ▐ 12 ▌▐    BLOCK_THICK_INNER    ▌
    ▝▀▀▀▀▘▝▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▘

:meta hide-value:
"""

BLOCK_THICK_ROUNDED = Border(*"▌▞▀▚▐▚▄▞")
"""
Unicode thick (1/2) block rounded border::

    ▞▀▀▀▀▚▞▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▚
    ▌ 13 ▐▌   BLOCK_THICK_ROUNDED   ▐
    ▚▄▄▄▄▞▚▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▞

:meta hide-value:
"""

BLOCK_THIN = Border(*"▕▕▔▏▏▕▁▏")
"""
Unicode thin (1/8) block border::

    ▕▔▔▔▔▏▕▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▏
    ▕ 14 ▏▕       BLOCK_THIN        ▏
    ▕▁▁▁▁▏▕▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▏

:meta hide-value:
"""

BLOCK_THIN_INNER = Border(l="▕", t="▁", b="▔", r="▏")
"""
Unicode thin (1/8) block inner border::

    ⠀▁▁▁▁⠀⠀▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁⠀
    ▕ 15 ▏▕    BLOCK_THIN_INNER     ▏
    ⠀▔▔▔▔⠀⠀▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔⠀

:meta hide-value:
"""

BLOCK_THIN_ROUNDED = Border(*"▏▔▕▁")
"""
Unicode thin (1/8) block rounded border::

    ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
    ▏ 16 ▕▏   BLOCK_THIN_ROUNDED    ▕
    ▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁

:meta hide-value:
"""

DOTS = Border(*"⡇⡏⠉⢹⢸⣇⣀⣸")
"""
Braille dots border::

    ⡏⠉⠉⠉⠉⢹⡏⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⢹
    ⡇ 17 ⢸⡇          DOTS           ⢸
    ⣇⣀⣀⣀⣀⣸⣇⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣸

:meta hide-value:
"""

DOTS_DIAGONAL_LBRT = Border(*"⠞⠔⠔⠔⠞⠞⠔⠞")
"""
Braille diagonal dots border::

    ⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔
    ⠞ 18 ⠞⠞   DOTS_DIAGONAL_LBRT    ⠞
    ⠞⠔⠔⠔⠔⠞⠞⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠔⠞

:meta hide-value:
"""

DOTS_DIAGONAL_RBLT = Border(*"⢦⢄⢄⢄⢦⢦⢄⢦")
"""
Braille diagonal dots border::

    ⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄
    ⢦ 19 ⢦⢦   DOTS_DIAGONAL_RBLT    ⢦
    ⢦⢄⢄⢄⢄⢦⢦⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢄⢦

:meta hide-value:
"""

DOTS_HEAVY = Border(*"⣿⣿⠛⣿⣿⣿⣤⣿")
"""
Braille condensed dots border::

    ⣿⠛⠛⠛⠛⣿⣿⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⣿
    ⣿ 20 ⣿⣿       DOTS_HEAVY        ⣿
    ⣿⣤⣤⣤⣤⣿⣿⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣿

:meta hide-value:
"""

DOTS_INNER = Border(*"⢸⢀⣀⡀⡇⠈⠉⠁")
"""
Braille dots inner border::

    ⢀⣀⣀⣀⣀⡀⢀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⡀
    ⢸ 21 ⡇⢸       DOTS_INNER        ⡇
    ⠈⠉⠉⠉⠉⠁⠈⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠁

:meta hide-value:
"""

DOTS_LIGHT = Border(*"⡪⡪⠊⡪⡪⡪⡠⡪")
"""
Braille expanded dots border::

    ⡪⠊⠊⠊⠊⡪⡪⠊⠊⠊⠊⠊⠊⠊⠊⠊⠊⠊⠊⠊⠊⠊⠊⠊⠊⠊⠊⠊⠊⠊⠊⠊⡪
    ⡪ 22 ⡪⡪       DOTS_LIGHT        ⡪
    ⡪⡠⡠⡠⡠⡪⡪⡠⡠⡠⡠⡠⡠⡠⡠⡠⡠⡠⡠⡠⡠⡠⡠⡠⡠⡠⡠⡠⡠⡠⡠⡠⡪

:meta hide-value:
"""

DOTS_ROUNDED = Border(*"⡇⡔⠉⢢⢸⠣⣀⠜")
"""
Braille dots rounded border::

    ⡔⠉⠉⠉⠉⢢⡔⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⢢
    ⡇ 23 ⢸⡇      DOTS_ROUNDED       ⢸
    ⠣⣀⣀⣀⣀⠜⠣⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⠜

:meta hide-value:
"""

LINE_BOLD = Border(*"┃┏━┓┃┗━┛")
"""
Unicode bold single line border::

    ┏━━━━┓┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃ 24 ┃┃        LINE_BOLD        ┃
    ┗━━━━┛┗━━━━━━━━━━━━━━━━━━━━━━━━━┛

:meta hide-value:
"""

LINE_DASHED = Border(*"╎╶╌╴╎╶╌╴")
"""
Unicode dashed line border, var. 1::

    ╶╌╌╌╌╴╶╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╴
    ╎ 25 ╎╎       LINE_DASHED       ╎
    ╶╌╌╌╌╴╶╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╴

:meta hide-value:
"""

LINE_DASHED_2 = Border(*"┆╶┄╴┆╶┄╴")
"""
Unicode dashed line border, var. 2::

    ╶┄┄┄┄╴╶┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄╴
    ┆ 26 ┆┆      LINE_DASHED_2      ┆
    ╶┄┄┄┄╴╶┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄╴

:meta hide-value:
"""

LINE_DASHED_3 = Border(*"┊╶┈╴┊╶┈╴")
"""
Unicode dashed line border, var. 3::

    ╶┈┈┈┈╴╶┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈╴
    ┊ 27 ┊┊      LINE_DASHED_3      ┊
    ╶┈┈┈┈╴╶┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈╴

:meta hide-value:
"""

LINE_DASHED_BOLD = Border(*"╏╺╍╸╏╺╍╸")
"""
Unicode bold dashed line border, var. 1::

    ╺╍╍╍╍╸╺╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╸
    ╏ 28 ╏╏    LINE_DASHED_BOLD     ╏
    ╺╍╍╍╍╸╺╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╸

:meta hide-value:
"""

LINE_DASHED_BOLD_2 = Border(*"┇╺┅╸┇╺┅╸")
"""
Unicode bold dashed line border, var. 2::

    ╺┅┅┅┅╸╺┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅╸
    ┇ 29 ┇┇   LINE_DASHED_BOLD_2    ┇
    ╺┅┅┅┅╸╺┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅╸

:meta hide-value:
"""

LINE_DASHED_BOLD_3 = Border(*"┋╺┉╸┋╺┉╸")
"""
Unicode bold dashed line border, var. 3::

    ╺┉┉┉┉╸╺┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉╸
    ┋ 30 ┋┋   LINE_DASHED_BOLD_3    ┋
    ╺┉┉┉┉╸╺┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉╸

:meta hide-value:
"""

LINE_DASHED_HALF = Border(*"╷╷╴╴╵╶╶╵")
"""
Unicode dashed half-freq. line border::

    ╷╴╴╴╴╴╷╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴
    ╷ 31 ╵╷    LINE_DASHED_HALF     ╵
    ╶╶╶╶╶╵╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╶╵

:meta hide-value:
"""

LINE_DASHED_HALF_BOLD = Border(*"╻╻╸╸╹╺╺╹")
"""
Unicode bold dashed half-freq. line border::

    ╻╸╸╸╸╸╻╸╸╸╸╸╸╸╸╸╸╸╸╸╸╸╸╸╸╸╸╸╸╸╸╸╸
    ╻ 32 ╹╻  LINE_DASHED_HALF_BOLD  ╹
    ╺╺╺╺╺╹╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╺╹

:meta hide-value:
"""

LINE_DOUBLE = Border(*"║╔═╗║╚═╝")
"""
Unicode double line border::

    ╔════╗╔═════════════════════════╗
    ║ 33 ║║       LINE_DOUBLE       ║
    ╚════╝╚═════════════════════════╝

:meta hide-value:
"""

LINE_ROUNDED = Border(*"│╭─╮│╰─╯")
"""
Unicode rounded single line border::

    ╭────╮╭─────────────────────────╮
    │ 34 ││      LINE_ROUNDED       │
    ╰────╯╰─────────────────────────╯

:meta hide-value:
"""

LINE_SINGLE = Border(*"│┌─┐│└─┘")
"""
Unicode single line border::

    ┌────┐┌─────────────────────────┐
    │ 35 ││       LINE_SINGLE       │
    └────┘└─────────────────────────┘

:meta hide-value:
"""


ALL = {
    "ASCII_DOTTED": ASCII_DOTTED,
    "ASCII_DOUBLE": ASCII_DOUBLE,
    "ASCII_SINGLE": ASCII_SINGLE,
    "BLOCK_DOTTED_COMPACT": BLOCK_DOTTED_COMPACT,
    "BLOCK_DOTTED_REGULAR": BLOCK_DOTTED_REGULAR,
    "BLOCK_DOTTED_UNIFORM_LB": BLOCK_DOTTED_UNIFORM_LB,
    "BLOCK_DOTTED_UNIFORM_LT": BLOCK_DOTTED_UNIFORM_LT,
    "BLOCK_DOTTED_UNIFORM_RB": BLOCK_DOTTED_UNIFORM_RB,
    "BLOCK_DOTTED_UNIFORM_RT": BLOCK_DOTTED_UNIFORM_RT,
    "BLOCK_FULL": BLOCK_FULL,
    "BLOCK_THICK": BLOCK_THICK,
    "BLOCK_THICK_INNER": BLOCK_THICK_INNER,
    "BLOCK_THICK_ROUNDED": BLOCK_THICK_ROUNDED,
    "BLOCK_THIN": BLOCK_THIN,
    "BLOCK_THIN_INNER": BLOCK_THIN_INNER,
    "BLOCK_THIN_ROUNDED": BLOCK_THIN_ROUNDED,
    "DOTS": DOTS,
    "DOTS_DIAGONAL_LBRT": DOTS_DIAGONAL_LBRT,
    "DOTS_DIAGONAL_RBLT": DOTS_DIAGONAL_RBLT,
    "DOTS_HEAVY": DOTS_HEAVY,
    "DOTS_INNER": DOTS_INNER,
    "DOTS_LIGHT": DOTS_LIGHT,
    "DOTS_ROUNDED": DOTS_ROUNDED,
    "LINE_BOLD": LINE_BOLD,
    "LINE_DASHED": LINE_DASHED,
    "LINE_DASHED_2": LINE_DASHED_2,
    "LINE_DASHED_3": LINE_DASHED_3,
    "LINE_DASHED_BOLD": LINE_DASHED_BOLD,
    "LINE_DASHED_BOLD_2": LINE_DASHED_BOLD_2,
    "LINE_DASHED_BOLD_3": LINE_DASHED_BOLD_3,
    "LINE_DASHED_HALF": LINE_DASHED_HALF,
    "LINE_DASHED_HALF_BOLD": LINE_DASHED_HALF_BOLD,
    "LINE_DOUBLE": LINE_DOUBLE,
    "LINE_ROUNDED": LINE_ROUNDED,
    "LINE_SINGLE": LINE_SINGLE,
}
