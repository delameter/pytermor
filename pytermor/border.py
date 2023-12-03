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

from .common import fit, Align

@dataclass(frozen=True)
class Border:
    """
    Attribute diagram::

        LT  T  RT      3×T
          ┌ ─ ┐       ┌───┐
        L │   │ R  →  │'''│
          └ ─ ┘       └───┘
        LB  B  RB      3×B
    """

    _DEFAULT = " "

    l: str = _DEFAULT
    lt: str = _DEFAULT
    t: str = _DEFAULT
    rt: str = _DEFAULT
    lb: str = _DEFAULT
    b: str = _DEFAULT
    rb: str = _DEFAULT
    r: str = _DEFAULT

    @cached_property
    def chars(self) -> set[str]:
        return {*(self.l + self.lt + self.t + self.rt + self.lb + self.b + self.rb + self.r)}

    def make(self, width: int, lines: list[str] = None, align=Align.LEFT) -> Iterable[str]:
        yield self.make_top(width, None, None)
        for line in lines:
            yield self.make_middle(width, line, align)
        yield self.make_bottom(width, None, None)

    def make_top(self, *args) -> str:
        return self._make_line(self.lt, self.t, self.rt, *args)

    def make_middle(self, *args) -> str:
        return self._make_line(self.l, " ", self.r, *args)

    def make_bottom(self, *args) -> str:
        return self._make_line(self.lb, self.b, self.rb, *args)

    def _make_line(self, l: str, f: str, r: str, width: int, content: str, align: Align) -> str:
        return l + fit(content or "", width - (len(l) + len(r)), align or Align.LEFT, fill=f) + r


BORDER_ASCII_SINGLE = Border(*"|+-++-+|")
""" . """
BORDER_ASCII_DOUBLE = Border(*"#*=**=*#")
""" . """

BORDER_LINE_SINGLE = Border(*"│┌─┐└─┘│")
""" . """
BORDER_LINE_SINGLE_ROUND = Border(*"│╭─╮╰─╯│")
""" . """
BORDER_LINE_BOLD = Border(*"┃┏━┓┗━┛┃")
""" . """
BORDER_LINE_DOUBLE = Border(*"║╔═╗╚═╝║")
""" . """
BORDER_LINE_DASHED = Border(*"╎╶╌╴╶╌╴╎")
""" . """
BORDER_LINE_DASHED_2 = Border(*"┆╶┄╴╶┄╴┆")
""" . """
BORDER_LINE_DASHED_3 = Border(*"┊╶┈╴╶┈╴┊")
""" . """
BORDER_LINE_DASHED_BOLD = Border(*"╏╺╍╸╺╍╸╏")
""" . """
BORDER_LINE_DASHED_BOLD_2 = Border(*"┇╺┅╸╺┅╸┇")
""" . """
BORDER_LINE_DASHED_BOLD_3 = Border(*"┋╺┉╸╺┉╸┋")
""" . """

BORDER_SOLID_18_COMPACT = Border(l="▕", t="▁", b="▔", r="▏")
""" . """
BORDER_SOLID_18_REGULAR = Border(*"▕▕▔▏▕▁▏▏")
""" . """
BORDER_SOLID_18_DIAGONAL = Border(*"▏▔▁▕")
""" . """
BORDER_SOLID_12_COMPACT = Border(*"▐▗▄▖▝▀▘▌")
""" . """
BORDER_SOLID_12_REGULAR = Border(*"▌▛▀▜▙▄▟▐")
""" . """
BORDER_SOLID_12_DIAGONAL = Border(*"▌▞▀▚▚▄▞▐")
""" . """
BORDER_SOLID_12_EXTENDED = Border(*"██▀██▄██")
""" . """
BORDER_SOLID_FULL = Border(*8 * "█")
""" . """

BORDER_DOTTED_COMPACT = Border(*"⢸⢀⣀⡀⠈⠉⠁⡇")
""" . """
BORDER_DOTTED_REGULAR = Border(*"⡇⡏⠉⢹⣇⣀⣸⢸")
""" . """
BORDER_DOTTED_DOUBLE = Border(*"⣿⣿⠛⣿⣿⣤⣿⣿")
""" . """
BORDER_DOTTED_DOUBLE_SEMI = Border(*"⡪⡪⠊⡪⡪⡠⡪⡪")
""" . """
