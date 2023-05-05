# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import typing
from math import isclose

import pytest

from pytermor import (
    Style,
    IntCode,
    NOOP_STYLE,
    Color16,
    DEFAULT_COLOR,
    LogicError,
    cv,
    NOOP_COLOR, Color256, ColorRGB, ArgTypeError, IColor, make_style, )

from . import format_test_params


class TestStyle:
    @pytest.mark.parametrize(
        "expected, arg",
        [
            (NOOP_STYLE,            None),
            (Style(fg='red'),       'red'),
            (Style(fg='green'),     cv.GREEN),
            (Style(fg='navy_blue'), cv.NAVY_BLUE),
            (Style(fg=0x0eb0b0),    0x0eb0b0),
            (Style(fg=0xaaaaaa),    "#aaa"),
            (Style(fg=0xa0aaca),    "#a0aaca"),
            (
                Style(bg='yellow', bold=True),
                Style(bg='yellow', bold=True),
             ),
            pytest.param(None, [], marks=pytest.mark.xfail(raises=ArgTypeError)),
        ],
        ids=format_test_params
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
            (0xaf8700, cv.DARK_GOLDENROD),
            (0x800000, Color16(0x800000, IntCode.RED, IntCode.BG_RED)),
            (0xffaacc, Color256(0xffaacc, 263)),
            (0xff00cc, ColorRGB(0xff00cc)),
            (0x00aacc, 0x00aacc),
            (0x9a9a9a, "#9a9a9a"),
            (0x666666, "#666"),
            (0x000000, "black"),
            (0x00005f, "navy_blue"),
            (0x0052cc, "jira_blue"),
            pytest.param(None, [], marks=pytest.mark.xfail(raises=ArgTypeError)),
            pytest.param(None, None, marks=pytest.mark.xfail(raises=LogicError)),
        ],
        ids=format_test_params,
    )
    def test_style_color_resolver(self, expected_result: int, color_arg: typing.Any):
        st = Style()
        st.fg = color_arg
        assert st.fg.hex_value == expected_result

    @pytest.mark.parametrize(
        "st",
        [
            Style(),
            Style(fg='red'),
            Style(bg='green'),
            Style(fg='blue', bg='black'),
        ]
    )
    def test_flip(self, st: Style):
        st_flipped = st.clone().flip()
        assert st_flipped.fg == st.bg
        assert st_flipped.bg == st.fg

    @pytest.mark.parametrize(
        "expected_fg_brightness, bg",
        [
            (.10, 0xff0000),
            (.10, 0xffff00),
            (.10, 0x00ffff),
            (.10, 0x0000ff),
            (.10, 0xffffff),
            (.10, 0x800000),
            (.10, 0x008000),
            (.10, 0x000080),  # @TODO fix this
            (.10, 0x808000),
            (.10, 0x008080),
            (.10, 0x808080),
            (.80, 0x400000),
            (.80, 0x004000),
            (.80, 0x000040),
            (.80, 0x404040),
            (.80, 0x000000),
        ]
    )
    def test_autopick_fg(self, expected_fg_brightness: float, bg: int|None):
        st = Style(bg=bg).autopick_fg()
        fg_brightness = st.fg.to_hsv().value
        assert isclose(fg_brightness, expected_fg_brightness, abs_tol=.10)  # 10% margin

    def test_autopick_fg_doesnt_change_without_bg(self):
        assert Style(fg=0x800080).autopick_fg().fg.hex_value == 0x800080

    @pytest.mark.parametrize(
        "style1,style2",
        [
            (Style(frozen=True), NOOP_STYLE),
            (Style(), Style()),
            (Style(fg="red"), Style(fg="red")),
            (Style(bg="red"), Style(bg="red")),
            (Style(fg="red", bg="black"), Style(fg="red", bg="black")),
            (Style(fg="red", bold=True), Style(fg="red", bold=True)),
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
            ("bold", lambda st: setattr(st, "bold", True)),
            ("flip", lambda st: st.flip()),
            ("autopick_fg", lambda st: st.autopick_fg()),
            ("merge_fallback", lambda st: st.merge_fallback(Style())),
            ("merge_overwrite", lambda st: st.merge_overwrite(Style())),
        ],
        ids=format_test_params,
    )
    @pytest.mark.parametrize("instantiate_fn", [
        lambda: Style(frozen=True),
        lambda: NOOP_STYLE.__class__(),
    ])
    @pytest.mark.xfail(raises=LogicError)
    def test_frozen_style_immutability(
        self,
        label: str,
        instantiate_fn: typing.Callable[[], Style],
        change_fn: typing.Callable[[Style], None],
    ):
        change_fn(instantiate_fn())

    @pytest.mark.parametrize(
        "expected, style",
        [
            ("<Style[]>", Style()),
            ("<*Style[]>", Style(frozen=True)),
            ("<*_NoOpStyle[]>", NOOP_STYLE),
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
        ],
    )
    def test_style_repr(self, expected: str, style: Style):
        assert repr(style) == expected

    @pytest.mark.parametrize(
        "expected, style, verbose",
        [
            ("c31(#800000? red)", Style(fg='red'), True),
            ("|c31(#800000? red)", Style(bg='red'), True),
            ("c30(#000000? black)|c31(#800000? red)", Style(fg=cv.BLACK, bg=cv.RED), True),
            ("x88(#870000 dark-red)", Style(fg=cv.DARK_RED), True),
            ("|x88(#870000 dark-red)", Style(bg=cv.DARK_RED), True),
            ("x237(#3a3a3a gray-23)|x88(#870000 dark-red)", Style(fg=cv.GRAY_23, bg=cv.DARK_RED), True),
            ("#400000", Style(fg=0x400000), True),
            ("|#ffffff", Style(bg=0xffffff), True),
            ("#ff00ff|#008000", Style(fg=0xff00ff, bg=0x008000), True),
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
        ]
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
            (Style(bg='red', fg='blue'), Style(fg='blue'), Style(bg='red')),
            (Style(bg='blue', fg='red'), Style(fg='red'), Style(bg='blue')),
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

    @pytest.mark.xfail(raises=LogicError)
    def test_noop_style_immutability(self):
        NOOP_STYLE.merge_fallback(Style(bold=False))
