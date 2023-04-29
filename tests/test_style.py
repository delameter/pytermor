# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import pytest

from pytermor import Style, get_qname, IntCode, NOOP_STYLE, Color16, DEFAULT_COLOR, \
    LogicError, cv, NOOP_COLOR


def style_str(val) -> str | None:
    if isinstance(val, Style):
        return "%s(%s)" % (get_qname(val), val.repr_attrs(False))
    return None


class TestStyle:
    def test_default_colors_are_noop(self):
        assert Style().fg == NOOP_COLOR
        assert Style().bg == NOOP_COLOR

    def test_style_color_resolver(self):
        style1 = Style(fg=Color16(0x800000, IntCode.RED, IntCode.BG_RED))
        # @TODO

    @pytest.mark.parametrize(
        "style1,style2",
        [
            (Style(), NOOP_STYLE),
            (Style(), Style()),
            (Style(fg="red"), Style(fg="red")),
            (Style(bg="red"), Style(bg="red")),
            (Style(fg="red", bg="black"), Style(fg="red", bg="black")),
            (Style(fg="red", bold=True), Style(fg="red", bold=True)),
            (Style(underlined=True, italic=True), Style(underlined=True, italic=True)),
        ],
        ids=style_str,
    )
    def test_styles_with_equal_attrs_are_equal(self, style1, style2):
        assert style1 == style2

    @pytest.mark.parametrize(
        "style1,style2",
        [
            (Style(fg="red"), NOOP_STYLE),
            (Style(fg="blue"), Style()),
            (Style(fg="red"), Style(bg="red")),
            (Style(bg="red"), Style(fg="red")),
            (Style(fg="red", bg="black"), Style(fg="red", bg="yellow")),
            (Style(fg="red", bold=True), Style(fg="red", bold=False)),
            (Style(underlined=True, italic=True), Style(underlined=False, italic=True)),
        ],
        ids=style_str,
    )
    def test_styles_with_different_attrs_are_not_equal(self, style1, style2):
        assert style1 != style2

    @pytest.mark.xfail(raises=LogicError)
    def test_noop_style_immutability(self):
        NOOP_STYLE.bg = 'red'

    @pytest.mark.xfail(raises=LogicError)
    def test_noop_style_immutability_2(self):
        NOOP_STYLE.bold = True

    @pytest.mark.parametrize(
        "expected, style",
        [
            ("<Style[NOP]>", Style()),
            ("<_NoOpStyle[NOP]>", NOOP_STYLE),
            ("<Style[red]>", Style(fg='red')),
            ("<Style[|red]>", Style(bg='red')),
            ("<Style[x88]>", Style(fg=cv.DARK_RED)),
            ("<Style[|x88]>", Style(bg=cv.DARK_RED)),
            ("<Style[#400000]>", Style(fg=0x400000)),
            ("<Style[|#ffffff]>", Style(bg=0xffffff)),
            ("<Style[#ff00ff|#008000]>", Style(fg=0xff00ff, bg=0x008000)),
            ("<Style[#0052cc]>", Style(fg="jira blue")),
            ("<Style[|#ff9966]>", Style(bg="atomic tangerine")),
            ("<Style[#b3f5ff|#824b35]>", Style(fg="arctic chill", bg="green tea")),
            ("<Style[DEF]>", Style(fg=DEFAULT_COLOR)),
            ("<Style[|DEF]>", Style(bg=DEFAULT_COLOR)),
            ("<Style[+BOLD +DIM +ITAL +UNDE]>", Style(bold=True, dim=True, italic=True, underlined=True)),
            ("<Style[+CROS +DOUB +OVER]>", Style(overlined=True, crosslined=True, double_underlined=True)),
            ("<Style[+BLIN +INVE]>", Style(inversed=True, blink=True)),
            ("<Style[+DIM -BOLD]>", Style(bold=False, dim=True)),
            ("<Style[red +BOLD]>", Style(fg="red", bold=True)),
            ("<Style[|red -BOLD]>", Style(bg="red", bold=False)),
        ]
    )
    def test_style_repr(self, expected: str, style: Style):
        assert repr(style) == expected

    @pytest.mark.parametrize(
        "expected, style",
        [
            ("c31(#800000? red)", Style(fg='red')),
            ("|c31(#800000? red)", Style(bg='red')),
            ("c30(#000000? black)|c31(#800000? red)", Style(fg=cv.BLACK, bg=cv.RED)),
            ("x88(#870000 dark-red)", Style(fg=cv.DARK_RED)),
            ("|x88(#870000 dark-red)", Style(bg=cv.DARK_RED)),
            ("x237(#3a3a3a gray-23)|x88(#870000 dark-red)", Style(fg=cv.GRAY_23, bg=cv.DARK_RED)),
            ("#400000", Style(fg=0x400000)),
            ("|#ffffff", Style(bg=0xffffff)),
            ("#ff00ff|#008000", Style(fg=0xff00ff, bg=0x008000)),
            ("#0052cc(pacific-bridge)", Style(fg="jira blue")),
            ("|#ff9966(atomic-tangerine)", Style(bg="atomic tangerine")),
            ("#b3f5ff(arctic-chill)|#824b35(green-tea)", Style(fg="arctic chill", bg="green tea")),
        ]
    )
    def test_style_verbose_repr(self, expected: str, style: Style):
        assert style.repr_attrs(True) == expected


class TestStyleMerging:
    @pytest.mark.parametrize(
        "expected, base, fallback",
        [
            (NOOP_STYLE, Style(), NOOP_STYLE),
            (Style(fg="red"), Style(fg="red"), NOOP_STYLE),
            (Style(fg="red"), Style(), Style(fg="red")),
            (Style(fg="yellow"), Style(fg="yellow"), Style(fg="red")),
            (Style(bg="green"), Style(bg="green"), Style(bg=None)),
            (Style(bg=DEFAULT_COLOR), Style(bg=DEFAULT_COLOR), Style(bg=None)),
            (Style(bg='red', fg='blue'), Style(fg='blue'), Style(bg='red')),
            (Style(bg='blue', fg='red'), Style(fg='red'), Style(bg='blue')),
            (Style(bold=True), Style(bold=True), Style()),
            (Style(bold=False), Style(bold=False), Style()),
            (Style(bold=True), Style(bold=True), Style(bold=False)),
            (Style(bold=False), Style(bold=False), Style(bold=True)),
            (Style(bold=False), Style(), Style(bold=False)),
            (Style(bold=True), Style(), Style(bold=True)),
        ],
        ids=style_str,
    )
    def test_style_merging_fallback(self, expected: Style, base: Style, fallback: Style):
        assert base.merge_fallback(fallback) == expected

    @pytest.mark.xfail(raises=LogicError)
    def test_noop_style_immutability(self):
        NOOP_STYLE.merge_fallback(Style(bold=False))
