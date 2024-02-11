# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import typing
from math import isclose

import pytest
from pytermor.cval import cv
from pytermor import (
    Style,
    IntCode,
    NOOP_STYLE,
    Color16,
    DEFAULT_COLOR,
    NOOP_COLOR,
    Color256,
    ColorRGB,
    make_style,
    RGB,
    HSV,
    XYZ,
    LAB,
)
from pytermor.exception import LogicError, ArgTypeError

from tests import format_test_params


class TestStyle:
    @pytest.mark.parametrize(
        "expected, arg",
        [
            (NOOP_STYLE, None),
            (Style(fg="red"), "red"),
            (Style(fg="green"), cv.GREEN),
            (Style(fg="navy_blue"), cv.NAVY_BLUE),
            (Style(fg=0x0EB0B0), 0x0EB0B0),
            (Style(fg=0xAAAAAA), "#aaa"),
            (Style(fg=0xA0AACA), "#a0aaca"),
            (Style(bg="red", bold=True), Style(bg="red", bold=True)),
            (Style(bold=True, frozen=True), 'bold'),
            (Style(dim=True, frozen=True), 'dim'),
            (Style(italic=True, frozen=True), 'italic'),
            (Style(underlined=True, frozen=True), 'underlined'),
            pytest.param(None, [], marks=pytest.mark.xfail(raises=ArgTypeError)),
        ],
        ids=format_test_params,
    )
    def test_make_style(self, expected: Style, arg: typing.Any):
        assert make_style(arg) == expected

    def test_default_colors_are_noop(self):
        assert Style().fg == NOOP_COLOR
        assert Style().bg == NOOP_COLOR

    @pytest.mark.parametrize(
        "expected_result, color_arg",
        [
            (0x800000, cv.RED),
            (0xAF8700, cv.DARK_GOLDENROD),
            (0x800000, Color16(0x800000, IntCode.RED, IntCode.BG_RED)),
            (0xFFAACC, Color256(0xFFAACC, 263)),
            (0xFF00CC, ColorRGB(0xFF00CC)),
            (0x00AACC, 0x00AACC),
            (0x9A9A9A, "#9a9a9a"),
            (0x666666, "#666"),
            (0x000000, "black"),
            (0x00005F, "navy_blue"),
            (0x0052CC, "jira_blue"),
            (0x111488, RGB(0x111488)),
            (0x808000, HSV(60, 1.0, 0.5)),
            (0xCCB7B4, XYZ(50, 50, 50)),
            (0xCF4B22, LAB(50, 50, 50)),
            pytest.param(None, [], marks=pytest.mark.xfail(raises=ArgTypeError)),
            pytest.param(None, None, marks=pytest.mark.xfail(raises=AttributeError)),
        ],
        ids=format_test_params,
    )
    def test_style_color_resolver(self, expected_result: int, color_arg: typing.Any):
        st = Style()
        st.fg = color_arg
        assert st.fg.int == expected_result

    @pytest.mark.parametrize(
        "st",
        [
            Style(),
            Style(fg="red"),
            Style(bg="green"),
            Style(fg="blue", bg="black"),
        ],
    )
    def test_flip(self, st: Style):
        st_flipped = st.clone().flip()
        assert st_flipped.fg == st.bg
        assert st_flipped.bg == st.fg

    @pytest.mark.parametrize(
        "expected_fg_brightness, bg",
        [
            (0.00, 0xFF0000),
            (0.00, 0xFFFF00),
            (0.00, 0x00FFFF),
            (1.00, 0x0000FF),
            (0.00, 0xFFFFFF),
            (1.00, 0x800000),
            (1.00, 0x008000),
            (1.00, 0x000080),
            (0.00, 0x808000),
            (1.00, 0x008080),
            (0.00, 0x808080),
            (1.00, 0x400000),
            (1.00, 0x004000),
            (1.00, 0x000040),
            (1.00, 0x404040),
            (1.00, 0x000000),
        ],
        ids=format_test_params,
    )
    def test_autopick_fg(self, expected_fg_brightness: float, bg: int | None):
        st = Style(bg=bg).autopick_fg()
        fg_brightness = st.fg.hsv.value
        assert isclose(fg_brightness, expected_fg_brightness, abs_tol=0.10)  # 10% margin

    def test_autopick_fg_doesnt_change_without_bg(self):
        assert Style(fg=0x800080).autopick_fg().fg.int == 0x800080

    @pytest.mark.parametrize(
        "style1,style2",
        [
            (Style(frozen=True), NOOP_STYLE),
            (Style(), Style()),
            (Style(fg="red"), Style(fg="red")),
            (Style(bg="red"), Style(bg="red")),
            (Style(fg="red", bg="black"), Style(fg="red", bg="black")),
            (Style(fg="red", bold=True), Style(fg="red", bold=True)),
            (
                Style(underline_color="red", bold=True),
                Style(underline_color="red", bold=True),
            ),
            (Style(underlined=True, italic=True), Style(underlined=True, italic=True)),
        ],
        ids=format_test_params,
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
            (Style(underline_color="red"), Style(underline_color="dark-red")),
            (Style(underlined=True, italic=True), Style(underlined=False, italic=True)),
        ],
        ids=format_test_params,
    )
    def test_styles_with_different_attrs_are_not_equal(self, style1, style2):
        assert style1 != style2

    def test_style_clone_equals_to_origin(self):
        st = Style(fg="yellow", bold=True)
        assert st.clone() == st

    def test_style_clone_is_not_origin(self):
        st = Style(fg="yellow", bold=True)
        assert st.clone() is not st

    def test_frozen_style_clone_equals_to_origin(self):
        st = Style(fg="yellow", bold=True, frozen=True)
        assert st.clone(frozen=True) == st

    def test_frozen_style_clone_is_mutable(self):
        st = Style(fg="yellow", bold=True, frozen=True)
        st.clone().fg = "red"

    @pytest.mark.parametrize(
        "label, change_fn",
        [
            ("fg", lambda st: setattr(st, "fg", "blue")),
            ("bg", lambda st: setattr(st, "bg", "red")),
            ("underline_color", lambda st: setattr(st, "underline_color", "yellow")),
            ("bold", lambda st: setattr(st, "bold", True)),
            ("flip", lambda st: st.flip()),
            ("autopick_fg", lambda st: st.autopick_fg()),
            ("merge_fallback", lambda st: st.merge_fallback(Style())),
            ("merge_overwrite", lambda st: st.merge_overwrite(Style())),
        ],
        ids=format_test_params,
    )
    @pytest.mark.parametrize(
        "instantiate_fn",
        [
            lambda: Style(frozen=True),
            lambda: NOOP_STYLE.__class__(),
        ],
    )
    def test_frozen_style_immutability(
        self,
        label: str,
        instantiate_fn: typing.Callable[[], Style],
        change_fn: typing.Callable[[Style], None],
    ):
        with pytest.raises(LogicError, match="is immutable"):
            change_fn(instantiate_fn())

    @pytest.mark.parametrize(
        "expected, style",
        [
            ("<Style[]>", Style()),
            ("<@Style[]>", Style(frozen=True)),
            ("<@NoOpStyle[]>", NOOP_STYLE),
            ("<Style[red]>", Style(fg="red")),
            ("<Style[|red]>", Style(bg="red")),
            ("<Style[x88]>", Style(fg=cv.DARK_RED)),
            ("<Style[|x88]>", Style(bg=cv.DARK_RED)),
            ("<Style[#400000]>", Style(fg=0x400000)),
            ("<Style[|#ffffff]>", Style(bg=0xFFFFFF)),
            ("<Style[#ff00ff|#008000]>", Style(fg=0xFF00FF, bg=0x008000)),
            ("<Style[#0052cc]>", Style(fg="jira blue")),
            ("<Style[|#ff9966]>", Style(bg="atomic tangerine")),
            ("<Style[#b3f5ff|#824b35]>", Style(fg="arctic chill", bg="green tea")),
            ("<Style[U:#e7c899]>", Style(underline_color="icathian yellow")),
            (
                "<Style[red|blue U:yellow]>",
                Style(fg="red", bg="blue", underline_color="yellow"),
            ),
            ("<Style[red U:yellow]>", Style(fg="red", underline_color="yellow")),
            ("<Style[|blue U:yellow]>", Style(bg="blue", underline_color="yellow")),
            ("<Style[DEF]>", Style(fg=DEFAULT_COLOR)),
            ("<Style[|DEF]>", Style(bg=DEFAULT_COLOR)),
            ("<Style[U:DEF]>", Style(underline_color=DEFAULT_COLOR)),
            (
                "<Style[+BOLD +DIM +ITAL +UNDE]>",
                Style(bold=True, dim=True, italic=True, underlined=True),
            ),
            (
                "<Style[+CROS +DOUB +OVER]>",
                Style(overlined=True, crosslined=True, double_underlined=True),
            ),
            ("<Style[+BLIN +INVE]>", Style(inversed=True, blink=True)),
            ("<Style[+DIM -BOLD]>", Style(bold=False, dim=True)),
            ("<Style[red +BOLD]>", Style(fg="red", bold=True)),
            ("<Style[|red -BOLD]>", Style(bg="red", bold=False)),
            ("<Style[U:yellow -BOLD]>", Style(underline_color="yellow", bold=False)),
        ],
    )
    def test_style_repr(self, expected: str, style: Style):
        assert repr(style) == expected

    @pytest.mark.parametrize(
        "expected, style, verbose",
        [
            ("c31(#800000? red)", Style(fg="red"), True),
            ("|c31(#800000? red)", Style(bg="red"), True),
            (
                "c30(#000000? black)|c31(#800000? red)",
                Style(fg=cv.BLACK, bg=cv.RED),
                True,
            ),
            ("U:c93(#ffff00? hi-yellow)", Style(underline_color=cv.HI_YELLOW), True),
            ("x88(#870000 dark-red)", Style(fg=cv.DARK_RED), True),
            ("|x88(#870000 dark-red)", Style(bg=cv.DARK_RED), True),
            (
                "x237(#3a3a3a gray-23)|x88(#870000 dark-red)",
                Style(fg=cv.GRAY_23, bg=cv.DARK_RED),
                True,
            ),
            ("#400000", Style(fg=0x400000), True),
            ("|#ffffff", Style(bg=0xFFFFFF), True),
            ("#ff00ff|#008000", Style(fg=0xFF00FF, bg=0x008000), True),
            ("#0052cc(pacific-bridge)", Style(fg="jira blue"), True),
            ("|#ff9966(atomic-tangerine)", Style(bg="atomic tangerine"), True),
            (
                "#b3f5ff(arctic-chill)|#824b35(green-tea) +DOUBLE_UNDERLINED",
                Style(fg="arctic chill", bg="green tea", double_underlined=True),
                True,
            ),
            (
                "#b3f5ff|#824b35 +DOUB",
                Style(fg="arctic chill", bg="green tea", double_underlined=True),
                False,
            ),
            (
                "#400000|#ffffff U:#808000",
                Style(fg=0x400000, bg=0xFFFFFF, underline_color=0x808000),
                True,
            ),
        ],
    )
    def test_style_verbose_repr(self, expected: str, style: Style, verbose: bool):
        assert style.repr_attrs(verbose) == expected


class TestStyleMerging:
    @pytest.mark.parametrize(
        "expected, base, fallback",
        [
            (Style(), Style(), NOOP_STYLE),
            (Style(fg="red"), Style(fg="red"), NOOP_STYLE),
            (Style(fg="red"), Style(), Style(fg="red")),
            (Style(fg="yellow"), Style(fg="yellow"), Style(fg="red")),
            (Style(bg="green"), Style(bg="green"), Style(bg=None)),
            (Style(bg=DEFAULT_COLOR), Style(bg=DEFAULT_COLOR), Style(bg=None)),
            (Style(bg="red", fg="blue"), Style(fg="blue"), Style(bg="red")),
            (
                Style(underlined=False, underline_color="yellow"),
                Style(underlined=None, underline_color="yellow"),
                Style(underlined=False, underline_color="green"),
            ),
            (Style(bold=True), Style(bold=True), Style()),
            (Style(bold=False), Style(bold=False), Style()),
            (Style(bold=True), Style(bold=True), Style(bold=False)),
            (Style(bold=False), Style(bold=False), Style(bold=True)),
            (Style(bold=False), Style(), Style(bold=False)),
            (Style(bold=True), Style(), Style(bold=True)),
        ],
        ids=format_test_params,
    )
    def test_style_merging_fallback(self, expected: Style, base: Style, fallback: Style):
        assert base.merge_fallback(fallback) == expected

    @pytest.mark.parametrize(
        "expected, base, overwrite",
        [
            (Style(), Style(), NOOP_STYLE),
            (Style(fg="red"), Style(fg="red"), NOOP_STYLE),
            (Style(fg="red"), Style(), Style(fg="red")),
            (Style(fg="red"), Style(fg="yellow"), Style(fg="red")),
            (Style(bg="green"), Style(bg="green"), Style(bg=None)),
            (Style(bg=DEFAULT_COLOR), Style(bg=DEFAULT_COLOR), Style(bg=None)),
            (Style(bg="red", fg="blue"), Style(fg="blue"), Style(bg="red")),
            (
                Style(underlined=False, underline_color="green"),
                Style(underlined=None, underline_color="yellow"),
                Style(underlined=False, underline_color="green"),
            ),
            (Style(bold=True), Style(bold=True), Style()),
            (Style(bold=False), Style(bold=False), Style()),
            (Style(bold=False), Style(bold=True), Style(bold=False)),
            (Style(bold=True), Style(bold=False), Style(bold=True)),
            (Style(bold=False), Style(), Style(bold=False)),
            (Style(bold=True), Style(), Style(bold=True)),
        ],
        ids=format_test_params,
    )
    def test_style_merging_overwrite(
        self, expected: Style, base: Style, overwrite: Style
    ):
        assert base.merge_overwrite(overwrite) == expected

    @pytest.mark.parametrize(
        "expected, base, replace",
        [
            (Style(), Style(), NOOP_STYLE),
            (Style(), Style(fg="red"), NOOP_STYLE),
            (Style(fg="red"), Style(), Style(fg="red")),
            (Style(fg="red"), Style(fg="yellow"), Style(fg="red")),
            (Style(), Style(bg="green"), Style(bg=None)),
            (Style(), Style(bg=DEFAULT_COLOR), Style(bg=None)),
            (Style(bg="red"), Style(fg="blue"), Style(bg="red")),
            (
                Style(underlined=False, underline_color="green"),
                Style(underlined=None, underline_color="yellow"),
                Style(underlined=False, underline_color="green"),
            ),
            (Style(), Style(bold=True), Style()),
            (Style(), Style(bold=False), Style()),
            (Style(bold=False), Style(bold=True), Style(bold=False)),
            (Style(bold=True), Style(bold=False), Style(bold=True)),
            (Style(bold=False), Style(), Style(bold=False)),
            (Style(bold=True), Style(), Style(bold=True)),
        ],
        ids=format_test_params,
    )
    def test_style_merging_replace(self, expected: Style, base: Style, replace: Style):
        assert base.merge_replace(replace) == expected

    def test_noop_style_immutability(self):
        with pytest.raises(LogicError, match="is immutable"):
            NOOP_STYLE.merge_fallback(Style(bold=False))
