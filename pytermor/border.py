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

from .common import fit, Align, pad, isiterable


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

    def __str__(self):
        return "".join(self.parts)

    def make(
        self,
        width: int,
        content: Iterable[str] | str = None,
        align: Align | str = Align.LEFT,
        pad_x: int = 1,
        pad_y: int = 0,
    ) -> Iterable[str]:
        if not isiterable(content):
            content = [content]
        if pad_y:
            pad_y_lines = pad_y * [""]
            content = pad_y_lines + content + pad_y_lines

        yield self.make_top(width, None, None, 0)
        yield from [self.make_middle(width, line, align, pad_x) for line in content]
        yield self.make_bottom(width, None, None, 0)

    def make_top(self, *args) -> str:
        return self._make_line(self.tl, self.t, self.tr, *args)

    def make_middle(self, *args) -> str:
        return self._make_line(self.l, " ", self.r, *args)

    def make_bottom(self, *args) -> str:
        return self._make_line(self.bl, self.b, self.br, *args)

    def _make_line(
        self,
        left: str,
        fill: str,
        right: str,
        width: int,
        content: str,
        align: Align,
        pad_x: int,
    ) -> str:
        content_width = max(0, width - (len(left) + len(right) + 2 * pad_x))
        pad_left = pad_right = pad(pad_x)
        fill = fit(content or "", content_width, align or Align.LEFT, fill=fill)
        return left + pad_left + fill + pad_right + right



ASCII_SINGLE = Border(*"|+-+|+-+")
"""
ASCII single line border::

    +----------------------+
    |     ASCII_SINGLE     |
    +----------------------+

:meta hide-value:
"""
ASCII_DOUBLE = Border(*"#*=*#*=*")
"""
ASCII double line border::

    *======================*
    #     ASCII_DOUBLE     #
    *======================*

:meta hide-value:
"""
ASCII_DOTTED = Border(*":...:.::")
"""
ASCII dotted border::

    ........................
    :     ASCII_DOTTED     :
    .:::::::::::::::::::::::

:meta hide-value:
"""
LINE_SINGLE = Border(*"│┌─┐│└─┘")
"""
Unicode single line border::

    ┌──────────────────────┐
    │     LINE_SINGLE      │
    └──────────────────────┘

:meta hide-value:
"""
LINE_ROUNDED = Border(*"│╭─╮│╰─╯")
"""
Unicode rounded single line border::

    ╭──────────────────────╮
    │     LINE_ROUNDED     │
    ╰──────────────────────╯

:meta hide-value:
"""
LINE_BOLD = Border(*"┃┏━┓┃┗━┛")
"""
Unicode bold single line border::

    ┏━━━━━━━━━━━━━━━━━━━━━━┓
    ┃      LINE_BOLD       ┃
    ┗━━━━━━━━━━━━━━━━━━━━━━┛

:meta hide-value:
"""
LINE_DOUBLE = Border(*"║╔═╗║╚═╝")
"""
Unicode double line border::

    ╔══════════════════════╗
    ║     LINE_DOUBLE      ║
    ╚══════════════════════╝

:meta hide-value:
"""
LINE_DASHED = Border(*"╎╶╌╴╎╶╌╴")
"""
Unicode dashed line border, var. 1::

    ╶╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╴
    ╎     LINE_DASHED      ╎
    ╶╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╴

:meta hide-value:
"""
LINE_DASHED_2 = Border(*"┆╶┄╴┆╶┄╴")
"""
Unicode dashed line border, var. 2::

    ╶┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄╴
    ┆    LINE_DASHED_2     ┆
    ╶┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄╴

:meta hide-value:
"""
LINE_DASHED_3 = Border(*"┊╶┈╴┊╶┈╴")
"""
Unicode dashed line border, var. 3::

    ╶┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈╴
    ┊    LINE_DASHED_3     ┊
    ╶┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈╴

:meta hide-value:
"""
LINE_DASHED_BOLD = Border(*"╏╺╍╸╏╺╍╸")
"""
Unicode bold dashed line border, var. 1::

    ╺╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╸
    ╏   LINE_DASHED_BOLD   ╏
    ╺╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╍╸

:meta hide-value:
"""
LINE_DASHED_BOLD_2 = Border(*"┇╺┅╸┇╺┅╸")
"""
Unicode bold dashed line border, var. 2::

    ╺┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅╸
    ┇  LINE_DASHED_BOLD_2  ┇
    ╺┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅╸

:meta hide-value:
"""
LINE_DASHED_BOLD_3 = Border(*"┋╺┉╸┋╺┉╸")
"""
Unicode bold dashed line border, var. 3::

    ╺┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉╸
    ┋  LINE_DASHED_BOLD_3  ┋
    ╺┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉┉╸

:meta hide-value:
"""
LINE_DASHED_HALF = Border(*"╷╷╴╴╶╶╵╵")  # @FIXME
"""
Unicode dashed half-freq. line border::

    ╷╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴
    ╷   LINE_DASHED_HALF   ╶
    ╶╵╵╵╵╵╵╵╵╵╵╵╵╵╵╵╵╵╵╵╵╵╵╵

:meta hide-value:
"""
LINE_DASHED_HALF_BOLD = Border(*"╻╻╸╸╺╺╹╹")   # @FIXME
"""
Unicode bold dashed half-freq. line border::

    ╻╸╸╸╸╸╸╸╸╸╸╸╸╸╸╸╸╸╸╸╸╸╸╸╸
    ╻ LINE_DASHED_HALF_BOLD ╺
    ╺╹╹╹╹╹╹╹╹╹╹╹╹╹╹╹╹╹╹╹╹╹╹╹╹

:meta hide-value:
"""
BLOCK_THIN = Border(*"▕▕▔▏▏▕▁▏")
"""
Unicode thin (1/8) block border::

    ▕▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▏
    ▕      BLOCK_THIN      ▏
    ▕▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▏

:meta hide-value:
"""
BLOCK_THIN_INNER = Border(l="▕", t="▁", b="▔", r="▏")
"""
Unicode thin (1/8) block inner border::

    ⠀▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁⠀
    ▕   BLOCK_THIN_INNER   ▏
    ⠀▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔⠀

:meta hide-value:
"""
BLOCK_THIN_ROUNDED = Border(*"▏▔▕▁")
"""
Unicode thin (1/8) block rounded border::

    ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
    ▏  BLOCK_THIN_ROUNDED  ▕
    ▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁

:meta hide-value:
"""
BLOCK_THICK = Border(*"▌▛▀▜▐▙▄▟")
"""
Unicode thick (1/2) block border::

    ▛▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▜
    ▌     BLOCK_THICK      ▐
    ▙▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▟

:meta hide-value:
"""
BLOCK_THICK_INNER = Border(*"▐▗▄▖▌▝▀▘")
"""
Unicode thick (1/2) block inner border::

    ▗▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▖
    ▐  BLOCK_THICK_INNER   ▌
    ▝▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▘

:meta hide-value:
"""
BLOCK_THICK_ROUNDED = Border(*"▌▞▀▚▐▚▄▞")
"""
Unicode thick (1/2) block rounded border::

    ▞▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▚
    ▌ BLOCK_THICK_ROUNDED  ▐
    ▚▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▞

:meta hide-value:
"""
BLOCK_DOTTED_REGULAR = Border(*"▖▌▘▀▄▗▐▝")
"""
Unicode dotted (1/4) block border::

    ▌▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▀
    ▖ BLOCK_DOTTED_REGULAR ▄
    ▗▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▝

:meta hide-value:
"""
BLOCK_DOTTED_COMPACT = Border(*"▗▗▖▖▝▝▘▘")
"""
Unicode dotted (1/4) block compact border::

    ▗▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖
    ▗ BLOCK_DOTTED_COMPACT ▝
    ▝▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘

:meta hide-value:
"""
BLOCK_DOTTED_UNIFORM_LT = Border(*"▘" * 8)
"""
Unicode uniform (1/4) block border, var. 1::

    ▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘
    ▘ BLOCK_DOTTED_UNIFORM_LT ▘
    ▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘▘

:meta hide-value:
"""
BLOCK_DOTTED_UNIFORM_RT = Border(*"▝" * 8)
"""
Unicode uniform (1/4) block border, var. 2::

    ▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝
    ▝ BLOCK_DOTTED_UNIFORM_RT ▝
    ▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝▝

:meta hide-value:
"""
BLOCK_DOTTED_UNIFORM_LB = Border(*"▖" * 8)
"""
Unicode uniform (1/4) block border, var. 3::

    ▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖
    ▖ BLOCK_DOTTED_UNIFORM_LB ▖
    ▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖▖

:meta hide-value:
"""
BLOCK_DOTTED_UNIFORM_RB = Border(*"▗" * 8)
"""
Unicode uniform (1/4) block border, var. 4::

    ▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗
    ▗ BLOCK_DOTTED_UNIFORM_RB ▗
    ▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗▗

:meta hide-value:
"""
BLOCK_FULL = Border(*"█" * 8)
"""
Unicode full (1/1) block border::

    ████████████████████████
    █      BLOCK_FULL      █
    ████████████████████████

:meta hide-value:
"""
DOTS = Border(*"⡇⡏⠉⢹⢸⣇⣀⣸")
"""
Braille dots border::

    ⡏⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⢹
    ⡇         DOTS         ⢸
    ⣇⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣸

:meta hide-value:
"""
DOTS_INNER = Border(*"⢸⢀⣀⡀⡇⠈⠉⠁")
"""
Braille dots inner border::

    ⢀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⡀
    ⢸      DOTS_INNER      ⡇
    ⠈⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠁

:meta hide-value:
"""
DOTS_ROUNDED = Border(*"⡇⡔⠉⢹⢸⣇⣀⣸")
"""
Braille dots rounded border::

    ⡔⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⢹
    ⡇     DOTS_ROUNDED     ⢸
    ⣇⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣸

:meta hide-value:
"""
DOTS_LIGHT = Border(*"⡪⡪⠊⡪⡪⡪⡠⡪")
"""
Braille expanded dots border::

    ⡪⠊⠊⠊⠊⠊⠊⠊⠊⠊⠊⠊⠊⠊⠊⠊⠊⠊⠊⠊⠊⠊⠊⡪
    ⡪      DOTS_LIGHT      ⡪
    ⡪⡠⡠⡠⡠⡠⡠⡠⡠⡠⡠⡠⡠⡠⡠⡠⡠⡠⡠⡠⡠⡠⡠⡪

:meta hide-value:
"""
DOTS_HEAVY = Border(*"⣿⣿⠛⣿⣿⣿⣤⣿")
"""
Braille condensed dots border::

    ⣿⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⣿
    ⣿      DOTS_HEAVY      ⣿
    ⣿⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣿

:meta hide-value:
"""
