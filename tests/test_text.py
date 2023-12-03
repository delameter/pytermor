# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import io
import typing as t
from typing import Iterable as Ie

import pytest

import pytermor as pt
import pytermor.common
import pytermor.exception
import pytermor.text
from pytermor import *
from pytermor import (
    Text as Tx,
    FrozenText as Fzt,
    Fragment as Fg,
    IRenderable as IRen,
    Style as St,
    Composite as Co,
)
from pytermor.renderer import NoOpRenderer
from pytermor.text import is_rt
from tests import format_test_params, raises


def format_test_rt_params(val) -> str | None:
    if isinstance(val, str):
        max_sl = 9
        sample = val[:max_sl] + ("‥" * (len(val) > max_sl))
        return f'<str>[({len(val)}, "{sample}")]'
    if isinstance(val, Tx):
        return repr(val)[:16] + ".."
    if isinstance(val, IRen):
        try:
            return repr(val)
        except TypeError:
            pass
    return None


@pytest.mark.config(force_output_mode=OutputMode.TRUE_COLOR)
class TestText:
    def test_style_applying_works(self):
        assert Tx("123", St(fg="red")).render() == "\x1b[31m" "123" "\x1b[39m"

    def test_style_closing_works(self):
        text = Tx(Fg("123", St(fg="red")), Fg("456"))
        assert text.render() == "\x1b[31m" "123" "\x1b[39m" "456"

    def test_style_leaving_open_works(self):
        text = Tx(Fg("123", St(fg="red"), close_this=False), Fg("456"))
        assert text.render() == "\x1b[31m" "123" "\x1b[39m" "\x1b[31m" "456" "\x1b[39m"

    def test_style_resetting_works(self):
        style = St(fg="red")
        text = Tx(
            Fg("123", style, close_this=False),
            Fg("", style, close_prev=True),
            Fg("456"),
        )
        assert text.render() == "\x1b[31m" "123" "\x1b[39m" "456"

    def test_style_nesting_works(self):
        style1 = St(fg="red", bg="black", bold=True)
        style2 = St(fg="yellow", bg="green", underlined=True)
        text = Tx(
            Fg("1", style1, close_this=False),
            Fg("2", style2, close_this=False),
            Fg("3"),
            Fg("4", style2, close_prev=True),
            Fg("5", style1, close_prev=True),
            Fg("6"),
        )
        expected = (
            "\x1b[1;31;40m" + "1" + "\x1b[22;39;49m"
            "\x1b[1;4;33;42m" + "2" + "\x1b[22;24;39;49m"
            "\x1b[1;4;33;42m" + "3" + "\x1b[22;24;39;49m"
            "\x1b[1;4;33;42m" + "4" + "\x1b[22;24;39;49m"
            "\x1b[1;31;40m" + "5" + "\x1b[22;39;49m"
            "6"
        )
        assert text.render() == expected

    def test_raw_works(self):
        style1 = St(fg="red", bg="black", bold=True)
        style2 = St(fg="yellow", bg="green", underlined=True)
        text = Tx(
            Fg("1", style1, close_this=False),
            Fg("2", style2, close_this=False),
            Fg("3"),
            Fg("4", style2, close_prev=True),
            Fg("5", style1, close_prev=True),
            Fg("6"),
        )
        assert text.raw() == "123456"

    def test_as_fragments_works(self):
        style1 = St(fg="red", bg="black", bold=True)
        style2 = St(fg="yellow", bg="green", underlined=True)
        fragments = [
            Fg("1", style1, close_this=False),
            Fg("2", style2, close_this=False),
            Fg("3"),
            Fg("4", style2, close_prev=True),
            Fg("5", style1, close_prev=True),
            Fg("6"),
        ]
        text = Tx(*fragments)
        assert text.as_fragments() == fragments

    @pytest.mark.xfail(raises=LogicError)
    def test_inconsistent_fragments_rendering_fails(self):
        text = Tx(Fg("1", "red", close_prev=True))
        text.render()


@pytest.mark.config(force_output_mode=OutputMode.TRUE_COLOR)
class TestComposite:
    def test_style_applying_works(self):
        assert (
            Co(Fg("12"), Fg("3", St(fg="red"))).render() == "12"
            "\x1b[31m" + "3" + "\x1b[39m"
        )

    def test_style_closing_works(self):
        comp = Co(Fg("123", St(fg="red")), Fg("456"))
        assert comp.render() == "\x1b[31m" "123" "\x1b[39m" "456"

    def test_style_leaving_open_works_as_expected(self):
        comp = Co(Fg("123", St(fg="red"), close_this=False), Fg("456"))
        assert comp.render() == "\x1b[31m" "123" "\x1b[39m" "456"

    def test_style_resetting_works(self):
        style = St(fg="red")
        comp = Co(
            Fg("123", style, close_this=False),
            Fg("", style, close_prev=True),
            Fg("456"),
        )
        assert comp.render() == "\x1b[31m" "123" "\x1b[39m" "456"

    def test_style_nesting_works(self):
        style1 = St(fg="red", bg="black", bold=True)
        style2 = St(fg="yellow", bg="green", underlined=True)
        comp = Co(
            Fg("1", style1, close_this=False),
            Fg("2", style2, close_this=False),
            Fg("3"),
            Fg("4", style2, close_prev=True),
            Fg("5", style1, close_prev=True),
            Fg("6"),
        )
        expected = (
            "\x1b[1;31;40m" + "1" + "\x1b[22;39;49m"
            "\x1b[4;33;42m" + "2" + "\x1b[24;39;49m"
            "3"
            "\x1b[4;33;42m" + "4" + "\x1b[24;39;49m"
            "\x1b[1;31;40m" + "5" + "\x1b[22;39;49m"
            "6"
        )
        assert comp.render() == expected

    def test_raw_works(self):
        style1 = St(fg="red", bg="black", bold=True)
        style2 = St(fg="yellow", bg="green", underlined=True)
        comp = Co(
            Fg("1", style1, close_this=False),
            Fg("2", style2, close_this=False),
            Fg("3"),
            Fg("4", style2, close_prev=True),
            Fg("5", style1, close_prev=True),
            Fg("6"),
        )
        assert comp.raw() == "123456"

    def test_as_fragments_works(self):
        style1 = St(fg="red", bg="black", bold=True)
        style2 = St(fg="yellow", bg="green", underlined=True)
        fragments = [
            Fg("1", style1, close_this=False),
            Fg("2", style2, close_this=False),
            Fg("3"),
            Fg("4", style2, close_prev=True),
            Fg("5", style1, close_prev=True),
            Fg("6"),
        ]
        comp = Co(*fragments)
        assert comp.as_fragments() == fragments

    def test_equal4(self):
        assert Co(Tx(Fg("1"), Fg("2"))) == Co(Tx("1", NOOP_STYLE, "2"))


class TestFargsFlow:
    @pytest.mark.parametrize(
        "input_fargs, expected_frags",
        [
            ([], []),
            ([""], [Fg()]),
            (
                ["1", "red"],
                [Fg("1", pt.cv.RED)],
            ),
            (
                ["1", "red", "2"],
                [Fg("1", pt.cv.RED), Fg("2", pt.NOOP_STYLE)],
            ),
            (
                ["1", "red", "2", "blue"],
                [Fg("1", pt.cv.RED), Fg("2", pt.cv.BLUE)],
            ),
            (
                ["1", "red", "2", "3", "blue"],
                [Fg("1", pt.cv.RED), Fg("2"), Fg("3", pt.cv.BLUE)],
            ),
            (
                ["1", pt.cv.DARK_RED_2],
                [Fg("1", pt.cv.DARK_RED_2)],
            ),
            (
                ["1", 0x5D8AA8],
                [Fg("1", pt.cvr.AIR_FORCE_BLUE)],
            ),
            (
                ["a", ("b",), "c"],
                [Fg("a"), Fg("b"), Fg("c")],
            ),
            (
                ["a", ("b", "green"), "c"],
                [Fg("a"), Fg("b", pt.cv.GREEN), Fg("c")],
            ),
            (
                [("a",), ("b", "green"), "c"],
                [Fg("a"), Fg("b", pt.cv.GREEN), Fg("c")],
            ),
            (
                [("a", "red"), "b", "blue"],
                [Fg("a", pt.cv.RED), Fg("b", pt.cv.BLUE)],
            ),
            (
                [("a", "red"), ("b", "blue")],
                [Fg("a", pt.cv.RED), Fg("b", pt.cv.BLUE)],
            ),
            (
                ["a", Fg("b", "green"), "c"],
                [Fg("a"), Fg("b", pt.cv.GREEN), Fg("c")],
            ),
            (
                ["a", "b", "blue"],
                [Fg("a"), Fg("b", pt.cv.BLUE)],
            ),
            (
                ["a", "b", tuple(), "blue"],
                [Fg("a"), Fg("b"), Fg("blue")],
            ),
            (
                [("a", "red", "b", "blue")],
                [Fg("a", pt.cv.RED), Fg("b", pt.cv.BLUE)],
            ),
        ],
        ids=format_test_rt_params,
    )
    def test_general(self, input_fargs: Ie[RT | FT], expected_frags: Ie[Fg] | None):
        assert Tx(*input_fargs).as_fragments() == expected_frags


class TestAdding:
    frag1 = Fg("123", "red")
    frag2 = Fg("456", "blue")

    @pytest.mark.parametrize(
        "items, expected",
        [
            (
                ["123", frag2],
                Tx(Fg("123"), frag2),
            ),
            (
                [frag1, "456"],
                Tx(frag1, "456"),
            ),
            (
                [frag1, frag2],
                Tx(frag1, frag2),
            ),
            (
                [Fzt(frag1), "456"],
                Fzt(frag1, Fg("456")),
            ),
            (
                [Fzt(frag1), frag2],
                Fzt(frag1, frag2),
            ),
            (
                [Tx(frag1), frag2],
                Tx(frag1, frag2),
            ),
            (
                ["123", frag2, "789"],
                Tx(Fg("123"), frag2, Fg("789")),
            ),
            (
                ["123", Fzt(frag2), "789"],
                Fzt(Fg("123"), frag2, Fg("789")),
            ),
            (
                ["123", Tx(frag2), "789"],
                Tx(Fg("123"), frag2, Fg("789")),
            ),
            (
                ["123", Co(frag2), "789"],
                Co("123", frag2, "789"),
            ),
            (
                [Co(frag1), frag2, Co("789")],
                Co(frag1, frag2, Co("789")),
            ),
            (
                ["123", Co(frag2)],
                Co("123", frag2),
            ),
        ],
        ids=format_test_rt_params,
    )
    def test_left_adding_works(self, items: t.Sequence[IRen], expected: IRen):
        result = items[0]
        for element in items[1:]:
            result = result + element
        assert result == expected

    @pytest.mark.parametrize(
        "renderable", [frag1, Tx("123", "red"), Co(pt.Fragment("123", "red"))]
    )
    def test_incremental_adding_works(self, renderable: IRen):
        renderable += "qwe"
        assert len(renderable) == 6
        assert renderable.render(NoOpRenderer).endswith("qwe")

    @pytest.mark.xfail(raises=pytermor.exception.LogicError)
    def test_incremental_adding_fails_for_immutables(self):
        ftext = Fzt("123", "red")
        ftext += "qwe"
        assert ftext

    @pytest.mark.parametrize(
        "other, renderable",
        [
            (lambda: "poi", lambda: Fg("123", "red")),
            (lambda: Fg("poi", "blue"), lambda: Fg("123", "red")),
            (lambda: "poi", lambda: Fzt("123", "red")),
            (lambda: "poi", lambda: Tx("123", "red")),
            (lambda: "poi", lambda: Co(Fg("123", "red"))),
        ],
        ids=format_test_params,
    )
    @pytest.mark.parametrize(
        "fn",
        [
            lambda x, y: x + y,
            lambda x, y: y.__radd__(x),
        ],
        ids=format_test_params,
    )
    def test_right_adding_works(
        self,
        other: t.Callable[[], RT],
        renderable: t.Callable[[], RT],
        fn: t.Callable[[str, RT], RT],
    ):
        result = fn(other(), renderable())
        assert len(result) == 6
        assert result.render(SgrRenderer("no_ansi")).startswith("poi")

    @pytest.mark.parametrize(
        "expected, item1, item2",
        [
            (Fzt(frag1, frag2), Fzt(frag1), Fzt(frag2)),
            (Tx(frag1, frag2), Tx(frag1), Tx(frag2)),
        ],
    )
    def test_adding_works(self, expected: RT, item1: RT, item2: RT):
        assert item1 + item2 == expected

    @pytest.mark.parametrize("item1, item2", [(Tx(frag1), set()), (Tx(frag1), 2.33)])
    @pytest.mark.xfail(raises=TypeError)
    def test_adding_fails(self, item1: IRen, item2: IRen):
        assert item1 + item2


@pytest.mark.config(force_output_mode=OutputMode.TRUE_COLOR)
class TestFragmentFormatting:
    def setup_method(self) -> None:
        self.fragment = Fg("123456789")

    @pytest.mark.parametrize(
        "expected, template",
        [
            ("123456789", "{:}"),
            ("123456789", "{:s}"),
            ("123456789", "{:2s}"),
            ("123456789   ", "{:12s}"),
            ("12345", "{:.5s}"),
            ("12345678", "{:.8s}"),
            ("123456789", "{:.12s}"),
            ("123456789   ", "{:<12s}"),
            ("   123456789", "{:>12s}"),
            (" 123456789  ", "{:^12s}"),
            ("123456789", "{:<5s}"),
            ("123456789", "{:>5s}"),
            ("123456789", "{:^5s}"),
            ("12345", "{:<.5s}"),
            ("12345", "{:>.5s}"),
            ("12345", "{:^.5s}"),
            ("123456789...", "{:.<12s}"),
            ("...123456789", "{:.>12s}"),
            ("^123456789^^", "{:^^12s}"),
            ("AAA12345AAAA", "{:A^12.5s}"),
        ],
    )
    def test_format_works(self, expected: str, template: str):
        expected_no_sgr = pt.SgrStringReplacer().apply(expected)
        assert template.format(self.fragment) == expected
        assert template.format(self.fragment.raw()) == expected_no_sgr

    @pytest.mark.parametrize("format_type", "bcdoxXneEfFgGn%")
    @pytest.mark.xfail(raises=ValueError)
    def test_invalid_type_format_fails(self, format_type: str):
        assert f"{self.fragment:{format_type}}"

    @pytest.mark.parametrize(
        "expected, input, width",
        [
            ("12345     ", "12345", 10),
            ("12345", "1234567890", 5),
            ("12345", "12345", 5),
        ],
        ids=format_test_params,
    )
    def test_set_width(self, expected: str, input: str, width: int):
        frag = pt.Fragment(input)
        frag.set_width(width)
        assert frag.raw() == expected


@pytest.mark.config(force_output_mode=OutputMode.XTERM_16)
class TestTextFormatting:
    @classmethod
    def setup_class(cls) -> None:
        cls.renderer_no_sgr = pt.renderer.NoOpRenderer()
        cls.fragments = [Fg("123"), Fg("456", "red"), Fg("789")]

    # fmt: off
    @pytest.mark.parametrize(
        "kwargs, expected",
        [
            (dict(),                  "123" "\x1b[31m" "456" "\x1b[39m"  "789"),
            (dict(align="<"),         "123" "\x1b[31m" "456" "\x1b[39m"  "789"),
            (dict(align="^"),         "123" "\x1b[31m" "456" "\x1b[39m"  "789"),
            (dict(align=">"),         "123" "\x1b[31m" "456" "\x1b[39m"  "789"),
            (dict(align="<", pad=2),  "123" "\x1b[31m" "456" "\x1b[39m"  "789  "),
            (dict(align="^", pad=2),  " 123" "\x1b[31m" "456" "\x1b[39m"  "789 "),
            (dict(align=">", pad=2),  "  123" "\x1b[31m" "456" "\x1b[39m"  "789"),
            (dict(width=0),           ""),
            (dict(width=1),           "1"),
            (dict(width=2),           "12"),
            (dict(width=3),           "123"),
            (dict(width=4),           "123" "\x1b[31m" "4"   "\x1b[39m"),
            (dict(width=5),           "123" "\x1b[31m" "45"  "\x1b[39m"),
            (dict(width=6),           "123" "\x1b[31m" "456" "\x1b[39m"),
            (dict(width=7),           "123" "\x1b[31m" "456" "\x1b[39m"  "7"),
            (dict(width=8),           "123" "\x1b[31m" "456" "\x1b[39m"  "78"),
            (dict(width=9),           "123" "\x1b[31m" "456" "\x1b[39m"  "789"),
            (dict(width=10),          "123" "\x1b[31m" "456" "\x1b[39m"  "789 "),
            (dict(width=11),          "123" "\x1b[31m" "456" "\x1b[39m"  "789  "),
            (dict(width=12),          "123" "\x1b[31m" "456" "\x1b[39m"  "789   "),
            (dict(width=0, pad=2),    ""),
            (dict(width=1, pad=2),    " "),
            (dict(width=2, pad=2),    "  "),
            (dict(width=3, pad=2),    "1  "),
            (dict(width=4, pad=2),    "12  "),
            (dict(width=5, pad=2),    "123  "),
            (dict(width=6, pad=2),    "123" "\x1b[31m" "4"   "  \x1b[39m"),
            (dict(width=7, pad=2),    "123" "\x1b[31m" "45"  "  \x1b[39m"),
            (dict(width=8, pad=2),    "123" "\x1b[31m" "456" "  \x1b[39m"),
            (dict(width=9, pad=2),    "123" "\x1b[31m" "456" "\x1b[39m"  "7  "),
            (dict(width=10, pad=2),   "123" "\x1b[31m" "456" "\x1b[39m"  "78  "),
            (dict(width=11, pad=2),   "123" "\x1b[31m" "456" "\x1b[39m"  "789  "),
            (dict(width=12, pad=2),   "123" "\x1b[31m" "456" "\x1b[39m"  "789   "),
            (dict(width=5,  align="<"),    "123" "\x1b[31m" "45"  "\x1b[39m"),
            (dict(width=5,  align="^"),    "123" "\x1b[31m" "45"  "\x1b[39m"),
            (dict(width=5,  align=">"),    "123" "\x1b[31m" "45"  "\x1b[39m"),
            (dict(width=12, align="<"),    "123" "\x1b[31m" "456" "\x1b[39m"  "789   "),
            (dict(width=12, align="^"),    " 123" "\x1b[31m" "456" "\x1b[39m" "789  "),
            (dict(width=12, align=">"),    "   123" "\x1b[31m" "456" "\x1b[39m" "789"),
            (dict(width=12, align="<", fill="-"),     "123" "\x1b[31m" "456" "\x1b[39m" "789---"),
            (dict(width=12, align=">", fill="-"),  "---123" "\x1b[31m" "456" "\x1b[39m" "789"),
            (dict(width=12, align="^", fill="-"),    "-123" "\x1b[31m" "456" "\x1b[39m" "789--"),
            (dict(width=12, align="<", fill="-", pad=4),      "123" "\x1b[31m" "456" "\x1b[39m" "78----"),
            (dict(width=12, align="<", fill="-", pad=2),      "123" "\x1b[31m" "456" "\x1b[39m" "789---"),
            (dict(width=12, align="^", fill="-", pad=2),     "-123" "\x1b[31m" "456" "\x1b[39m" "789--"),
            (dict(width=12, align="^", fill="-", pad=4),    "--123" "\x1b[31m" "456" "\x1b[39m" "78--"),
            (dict(width=12, align=">", fill="-", pad=2),   "---123" "\x1b[31m" "456" "\x1b[39m" "789"),
            (dict(width=12, align=">", fill="-", pad=4),  "----123" "\x1b[31m" "456" "\x1b[39m" "78"),
            (dict(width=0, overflow="."),  ""),
            (dict(width=1, overflow="."),  "."),
            (dict(width=2, overflow="."),  "1."),
            (dict(width=3, overflow="."),  "12."),
            (dict(width=4, overflow="."),  "123" "\x1b[31m" "."   "\x1b[39m"),
            (dict(width=5, overflow="."),  "123" "\x1b[31m" "4."  "\x1b[39m"),
            (dict(width=6, overflow="."),  "123" "\x1b[31m" "45." "\x1b[39m"),
            (dict(width=7, overflow="."),  "123" "\x1b[31m" "456" "\x1b[39m" "."),
            (dict(width=8, overflow="."),  "123" "\x1b[31m" "456" "\x1b[39m" "7."),
            (dict(width=9, overflow="."),  "123" "\x1b[31m" "456" "\x1b[39m" "78."),
            (dict(width=10, overflow="."), "123" "\x1b[31m" "456" "\x1b[39m" "789 "),
            (dict(width=11, overflow="."), "123" "\x1b[31m" "456" "\x1b[39m" "789  "),
            (dict(width=12, overflow="."), "123" "\x1b[31m" "456" "\x1b[39m" "789   "),
            (dict(width=0, overflow="..."),  ""),
            (dict(width=1, overflow="..."),  "."),
            (dict(width=2, overflow="..."),  ".."),
            (dict(width=3, overflow="..."),  "..."),
            (dict(width=4, overflow="..."),  "1..."),
            (dict(width=5, overflow="..."),  "12..."),
            (dict(width=6, overflow="..."),  "123" "\x1b[31m" "..."   "\x1b[39m"),
            (dict(width=7, overflow="..."),  "123" "\x1b[31m" "4..."  "\x1b[39m"),
            (dict(width=8, overflow="..."),  "123" "\x1b[31m" "45..." "\x1b[39m"),
            (dict(width=9, overflow="..."),  "123" "\x1b[31m" "456"   "\x1b[39m" "..."),
            (dict(width=10, overflow="..."), "123" "\x1b[31m" "456"   "\x1b[39m" "7..."),
            (dict(width=11, overflow="..."), "123" "\x1b[31m" "456"   "\x1b[39m" "78..."),
            (dict(width=12, overflow="..."), "123" "\x1b[31m" "456"   "\x1b[39m" "789   "),
            (dict(width=0, overflow="...", fill="-"),  ""),
            (dict(width=1, overflow="...", fill="-"),  "."),
            (dict(width=2, overflow="...", fill="-"),  ".."),
            (dict(width=3, overflow="...", fill="-"),  "..."),
            (dict(width=4, overflow="...", fill="-"),  "1..."),
            (dict(width=5, overflow="...", fill="-"),  "12..."),
            (dict(width=0, overflow="...", fill="-", pad=2),  ""),
            (dict(width=1, overflow="...", fill="-", pad=2),  "-"),
            (dict(width=2, overflow="...", fill="-", pad=2),  "--"),
            (dict(width=3, overflow="...", fill="-", pad=2),  ".--"),
            (dict(width=4, overflow="...", fill="-", pad=2),  "..--"),
            (dict(width=5, overflow="...", fill="-", pad=2),  "...--"),
            (dict(width=6, overflow="...", fill="-", pad=2),  "1...--"),
            (dict(width=5, overflow="", fill="-"),               "123" "\x1b[31m" "45" "\x1b[39m"),
            (dict(width=9, align=">", overflow="...", fill="-"), "123" "\x1b[31m" "456" "\x1b[39m" "..."),
        ],
        ids=format_test_params
    )
    # fmt: on
    def test_format(self, kwargs: dict, expected: str):
        text = Tx(*self.fragments, **kwargs)
        expected_no_sgr = pt.SgrStringReplacer().apply(expected)
        assert pt.render(text) == expected
        assert pt.render(text, renderer=self.renderer_no_sgr) == expected_no_sgr


@pytest.mark.config(force_output_mode=OutputMode.TRUE_COLOR)
class TestSimpleTable:
    def setup_method(self) -> None:
        self.style = St(fg="yellow")
        self.table = pt.SimpleTable(width=30, sep="|")

    @pytest.mark.parametrize(
        "cell",
        ["1", pt.Fragment("1"), pt.FrozenText("1"), pt.Text("1"), pt.SimpleTable("1")],
        ids=format_test_rt_params,
    )
    def test_cell_types_accepted(self, cell: pytermor.common.RT):
        self.table.add_row(cell)
        assert self.table.row_count == 1


class TestSplitting:
    @pytest.mark.parametrize(
        "expected, input",
        [
            (
                Tx(
                    Fg("Testing", pt.Style(underlined=True)),
                    Fg(" "),
                    Fg("started", pt.Style(underlined=True)),
                    Fg(" "),
                    Fg("at", pt.Style(underlined=True)),
                    Fg(" "),
                    Fg("23:24", pt.Style(underlined=True)),
                ),
                Tx(Fg("Testing started at 23:24", pt.Style(underlined=True))),
            )
        ],
        ids=format_test_rt_params,
    )
    def test_splitting_works(self, expected: Tx, input: Tx):
        input.split_by_spaces()
        assert input == expected


class TestEchoRender:
    PARAMSET = [
        ("", "", NOOP_STYLE),
        ("\x1b[33m12345\x1b[39m", "12345", pt.Styles.WARNING),
        ("\x1b[33m12345\x1b[39m", pt.Text("12345", pt.Styles.WARNING), NOOP_STYLE),
    ]

    @pytest.mark.config(force_output_mode="xterm_16")
    @pytest.mark.parametrize(
        "expected, input, st",
        [
            *PARAMSET,
            (
                ["\x1b[31m1\x1b[39m", "\x1b[31m2\x1b[39m", "\x1b[31m3\x1b[39m"],
                ["1", "2", "3"],
                pt.Styles.ERROR,
            ),
        ],
        ids=format_test_params,
    )
    def test_render(self, expected: str | t.List[str], input: RT | t.List[RT], st: FT):
        assert pt.render(input, st) == expected

    @pytest.mark.config(force_output_mode="xterm_16")
    @pytest.mark.parametrize(
        "expected, input, st",
        [
            *PARAMSET,
            (
                "\x1b[31m1\x1b[39m" "\x1b[31m2\x1b[39m" "\x1b[31m3\x1b[39m",
                ["1", "2", "3"],
                pt.Styles.ERROR,
            ),
        ],
        ids=format_test_params,
    )
    @pytest.mark.parametrize("fn", [pt.echo, pt.echoi])
    def test_echo(
        self, fn: t.Callable, expected: str | t.List[str], input: RT | t.List[RT], st: FT
    ):
        fn(input, st, file=(file := io.StringIO()))
        file.seek(0)
        data = file.read().rstrip("\n")
        assert "".join(data) == expected


class TestWrap:
    @pytest.mark.config(force_output_mode="xterm_16")
    @pytest.mark.parametrize(
        "expected, input",
        [
            ("  :Note:", ":Note:"),
            (
                (
                    "  :Note: In this example the library assumes that\n"
                    "your terminal supports all color modes including\n"
                    "256-color and True Color, and forces the renderer\n"
                    "to act accordingly."
                ),
                [
                    ":Note: In this example the library assumes that your terminal supports "
                    "all color modes including 256-color and True Color, and forces "
                    "the renderer to act accordingly."
                ],
            ),
            (
                (
                    "  :Note:   In this example the library assumes\n"
                    "that your terminal supports all color modes\n"
                    "including 256-color and True Color, and forces the\n"
                    "renderer to act accordingly."
                ),
                [
                    ":Note: \n In this example the library assumes that your terminal supports "
                    "all color modes including 256-color and True Color, and forces "
                    "the renderer to act accordingly."
                ],
            ),
            (
                (
                    "  :Note:\n"
                    "    In this example the library assumes that your\n"
                    "terminal supports all color modes including\n"
                    "256-color and True Color, and forces the renderer\n"
                    "to act accordingly."
                ),
                [
                    ":Note: \n\n  In this example the library assumes that your terminal supports "
                    "all color modes including 256-color and True Color, and forces "
                    "the renderer to act accordingly."
                ],
            ),
            (
                (
                    "  :Note:\n"
                    "  In this example the library assumes that your\n"
                    "terminal supports all color modes including\n"
                    "256-color and True Color, and forces the renderer\n"
                    "to act accordingly."
                ),
                [
                    ":Note:",
                    "In this example the library assumes that your terminal supports "
                    "all color modes including 256-color and True Color, and forces "
                    "the renderer to act accordingly.",
                ],
            ),
            (
                (
                    "  :Note:\n"
                    "   In this example the library assumes that your\n"
                    "terminal supports all color modes including\n"
                    "256-color and True Color, and forces the renderer\n"
                    "to act accordingly."
                ),
                [
                    ":Note:\n",
                    "In this example the library assumes that your terminal supports "
                    "all color modes including 256-color and True Color, and forces "
                    "the renderer to act accordingly.",
                ],
            ),
            (
                (
                    "  :Note:\n"
                    "\n"
                    "  In this example the library assumes that your\n"
                    "terminal supports all color modes including\n"
                    "256-color and True Color, and forces the renderer\n"
                    "to act accordingly."
                ),
                [
                    ":Note:\n\n",
                    "In this example the library assumes that your terminal supports "
                    "all color modes including 256-color and True Color, and forces "
                    "the renderer to act accordingly.",
                ],
            ),
            (
                (
                    "  \x1b[33m:Note:\x1b[39m\n"
                    "  \n"
                    "\x1b[90mIn this example the library assumes that your\n"
                    "terminal supports all color modes including\n"
                    "256-color and True Color, and forces the renderer\n"
                    "to act accordingly.\x1b[39m"
                ),
                [
                    pt.Fragment(":Note:", pt.Styles.WARNING) + "\n",
                    pt.Fragment(
                        "In this example the library assumes that your terminal supports "
                        "all color modes including 256-color and True Color, and forces "
                        "the renderer to act accordingly.",
                        pt.Style(fg="gray"),
                    ),
                ],
            ),
            (
                (
                    "  \x1b[33m:Note:\x1b[39m\n"
                    "  \x1b[93;101mIn this example the library assumes that your\n"
                    "terminal supports all color modes including\n"
                    "256-color and True Color, and forces renderer to\n"
                    "act accordingly.\x1b[39;49m"
                ),
                [
                    pt.Fragment(":Note:", pt.Styles.WARNING),
                    pt.Fragment(
                        "In this example the library assumes that your terminal "
                        "supports all color modes including 256-color and True Color,"
                        " and forces renderer to act accordingly.",
                        pt.Styles.INCONSISTENCY,
                    ),
                ],
            ),
        ],
        ids=format_test_params,
    )
    def test_wrap_sgr(self, expected: str, input: t.List[str]):
        pt.echo(
            input, wrap=50, indent_first=2, indent_subseq=0, file=(file := io.StringIO())
        )
        file.seek(0)
        data = file.read().rstrip("\n")
        assert "".join(data) == expected


class TestMisc:
    @pytest.mark.parametrize(
        "expected,max_len,args,kwargs",
        [
            ("  1  2   3", 10, ("1", "2", "3"), {"pad_left": True}),
            (
                " 1 2 3 4  ",
                10,
                ("1", "2", "3", Tx("4", "red")),
                {"pad_left": True, "pad_right": True},
            ),
            (
                "555  666  ",
                10,
                (Fg("555", "red"), Fg("666", "blue")),
                {"pad_right": True},
            ),
            (
                "1234  56  ",
                10,
                (Fg("1234", "red"), "56"),
                {"pad_right": True},
            ),
            raises(ValueError, "1 2 3", 5, ("1", "2", "3"), {"pad_left": True}),
        ],
    )
    @pytest.mark.config(renderer_class=NoOpRenderer.__name__)
    def test_distribute_padded(self, expected: str, max_len: int, args, kwargs):
        result = pt.distribute_padded(max_len, *args, **kwargs)
        result_rendered = pt.render(result)
        assert len(result) == max_len
        assert len(result_rendered) == max_len
        assert result_rendered == expected

    @pytest.mark.parametrize(
        "expected, class_",
        [
            (True, str),
            (True, Fragment),
            (True, FrozenText),
            (True, Text),
            (True, Composite),
            (False, int),
            (False, float),
            (False, bool),
            (False, bytes),
            (False, list),
            (False, dict),
        ],
        ids=format_test_rt_params,
    )
    def test_is_rt(self, expected: bool, class_: type):
        assert is_rt(class_()) == expected
