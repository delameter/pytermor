# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import pytest

from pytermor import Style, get_qname, IntCode, NOOP_STYLE, Color16, DEFAULT_COLOR, \
    LogicError


def style_str(val) -> str | None:
    if isinstance(val, Style):
        return "%s(%s)" % (get_qname(val), val.repr_attrs(False))
    return None


class TestStyle:
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
