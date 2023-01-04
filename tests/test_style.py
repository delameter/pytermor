# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

import pytest

import pytermor as pt
from pytermor import Style, get_qname


def style_str(val) -> str|None:
    if isinstance(val, Style):
        return "%s(%s)" % (get_qname(val), val.repr_attrs(False))
    return None


class TestStyle:
    def test_style_color_resolver(self):
        style1 = Style(fg=pt.Color16(0x800000, pt.IntCode.RED, pt.IntCode.BG_RED))
        # @TODO

    @pytest.mark.parametrize('style1,style2', [
            (Style(), pt.NOOP_STYLE),
            (Style(), Style()),
            (Style(fg="red"), Style(fg="red")),
            (Style(bg="red"), Style(bg="red")),
            (Style(fg="red", bg="black"), Style(fg="red", bg="black")),
            (Style(fg="red", bold=True), Style(fg="red", bold=True)),
            (Style(underlined=True, italic=True), Style(underlined=True, italic=True)),
    ], ids=style_str)
    def test_styles_with_equal_attrs_are_equal(self, style1, style2):
        assert style1 == style2

    @pytest.mark.parametrize('style1,style2', [
            (Style(fg="red"), pt.NOOP_STYLE),
            (Style(fg="blue"), Style()),
            (Style(fg="red"), Style(bg="red")),
            (Style(bg="red"), Style(fg="red")),
            (Style(fg="red", bg="black"), Style(fg="red", bg="yellow")),
            (Style(fg="red", bold=True), Style(fg="red", bold=False)),
            (Style(underlined=True, italic=True), Style(underlined=False, italic=True)),
        ], ids=style_str)
    def test_styles_with_different_attrs_are_not_equal(self, style1, style2):
        assert style1 != style2

