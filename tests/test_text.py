# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import typing as t

import pytest

import pytermor
import pytermor as pt
import pytermor.exception
import pytermor.text
from pytermor import OutputMode, Text, FrozenText, Fragment, IRenderable, Style, RT
from pytermor.renderer import NoOpRenderer

from tests import format_test_params

def format_test_rt_params(val) -> str | None:
    if isinstance(val, str):
        max_sl = 9
        sample = val[:max_sl] + ("‥" * (len(val) > max_sl))
        return f'<str>[({len(val)}, "{sample}")]'
    if isinstance(val, Text):
        return repr(val)[:16]+".."
    if isinstance(val, IRenderable):
        return repr(val)
    return None


@pytest.mark.setup(force_output_mode=OutputMode.TRUE_COLOR)
class TestText:
    def test_style_applying_works(self):
        assert Text("123", Style(fg="red")).render() == "\x1b[31m" "123" "\x1b[39m"

    def test_style_closing_works(self):
        text = Text(Fragment("123", Style(fg="red")), Fragment("456"))
        assert text.render() == "\x1b[31m" "123" "\x1b[39m" "456"

    def test_style_leaving_open_works(self):
        text = Text(Fragment("123", Style(fg="red"), close_this=False), Fragment("456"))
        assert text.render() == "\x1b[31m" "123" "\x1b[39m" "\x1b[31m" "456" "\x1b[39m"

    def test_style_resetting_works(self):
        style = Style(fg="red")
        text = Text(
            Fragment("123", style, close_this=False),
            Fragment("", style, close_prev=True),
            Fragment("456"),
        )
        assert text.render() == "\x1b[31m" "123" "\x1b[39m" "456"

    def test_style_nesting_works(self):
        style1 = Style(fg="red", bg="black", bold=True)
        style2 = Style(fg="yellow", bg="green", underlined=True)
        text = Text(
            Fragment("1", style1, close_this=False),
            Fragment("2", style2, close_this=False),
            Fragment("3"),
            Fragment("4", style2, close_prev=True),
            Fragment("5", style1, close_prev=True),
            Fragment("6"),
        )
        expected = (
            "\x1b[1;31;40m"   + "1" + "\x1b[22;39;49m"
            "\x1b[1;4;33;42m" + "2" + "\x1b[22;24;39;49m"
            "\x1b[1;4;33;42m" + "3" + "\x1b[22;24;39;49m"
            "\x1b[1;4;33;42m" + "4" + "\x1b[22;24;39;49m"
            "\x1b[1;31;40m"   + "5" + "\x1b[22;39;49m" + "6"
        )
        assert text.render() == expected

    def test_raw_works(self):
        style1 = Style(fg="red", bg="black", bold=True)
        style2 = Style(fg="yellow", bg="green", underlined=True)
        text = Text(
            Fragment("1", style1, close_this=False),
            Fragment("2", style2, close_this=False),
            Fragment("3"),
            Fragment("4", style2, close_prev=True),
            Fragment("5", style1, close_prev=True),
            Fragment("6"),
        )
        assert text.raw() == '123456'

    def test_as_fragments_works(self):
        style1 = Style(fg="red", bg="black", bold=True)
        style2 = Style(fg="yellow", bg="green", underlined=True)
        fragments = [
            Fragment("1", style1, close_this=False),
            Fragment("2", style2, close_this=False),
            Fragment("3"),
            Fragment("4", style2, close_prev=True),
            Fragment("5", style1, close_prev=True),
            Fragment("6"),
        ]
        text = Text(*fragments)
        assert pt.text.as_fragments(text) == fragments


class TestAdding:
    frag1 = Fragment("123", "red")
    frag2 = Fragment("456", "blue")

    @pytest.mark.parametrize(
        "items, expected",
        [
            (["123", frag2], Fragment("123456", "blue")),
            ([frag1, "456"], Fragment("123456", "red")),
            ([frag1, frag2], Text(frag1, frag2)),
            ([FrozenText(frag1), "456"], FrozenText(frag1, Fragment("456"))),
            ([FrozenText(frag1), frag2], FrozenText(frag1, frag2)),
            ([Text(frag1), frag2], Text(frag1, frag2)),
            (["123", frag2, "789"], Fragment("123456789", "blue")),
            (
                ["123", FrozenText(frag2), "789"],
                FrozenText(Fragment("123"), frag2, Fragment("789")),
            ),
            (["123", Text(frag2), "789"], Text(Fragment("123"), frag2, Fragment("789"))),
        ],
    )
    def test_left_adding_works(
        self, items: t.Sequence[IRenderable], expected: IRenderable
    ):
        result = items[0]
        for element in items[1:]:
            result = result + element
        assert result == expected

    @pytest.mark.parametrize("renderable", [frag1, Text("123", "red")])
    def test_incremental_adding_works(self, renderable: IRenderable):
        renderable += "qwe"
        assert len(renderable) == 6
        assert renderable.render(NoOpRenderer).endswith("qwe")

    @pytest.mark.xfail(raises=pytermor.exception.LogicError)
    def test_incremental_adding_fails_for_immutables(self):
        ftext = FrozenText("123", "red")
        ftext += "qwe"
        assert ftext

    @pytest.mark.parametrize(
        "renderable", [frag1, FrozenText("123", "red"), Text("123", "red")]
    )
    def test_right_adding_works(self, renderable: IRenderable):
        result = "poi" + renderable
        assert len(result) == 6
        assert result.render(NoOpRenderer).startswith("poi")

    @pytest.mark.parametrize(
        "expected, item1, item2",
        [
            (FrozenText(frag1, frag2), FrozenText(frag1), FrozenText(frag2)),
            (Text(frag1, frag2), Text(frag1), Text(frag2)),
        ],
    )
    def test_adding_works(self, expected: RT, item1: RT, item2: RT):
        assert item1 + item2 == expected

    @pytest.mark.parametrize(
        "item1, item2", [(Text(frag1), 123), (Text(frag1), [frag2])]
    )
    @pytest.mark.xfail(raises=(TypeError, pytermor.exception.ArgTypeError))
    def test_adding_fails(self, item1: IRenderable, item2: IRenderable):
        assert item1 + item2


@pytest.mark.setup(force_output_mode=OutputMode.TRUE_COLOR)
class TestFragmentFormatting:
    def setup_method(self) -> None:
        self.fragment = Fragment("123456789")

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


@pytest.mark.setup(force_output_mode=OutputMode.XTERM_16)
class TestTextFormatting:
    @classmethod
    def setup_class(cls) -> None:
        cls.renderer_no_sgr = pt.renderer.NoOpRenderer()
        cls.fragments = [Fragment("123"), Fragment("456", "red"), Fragment("789")]

    # fmt: off
    @pytest.mark.parametrize(
        "kwargs, expected",
        [
            (dict(),               "123" "\x1b[31m" "456" "\x1b[39m"  "789"),
            (dict(align="left"),   "123" "\x1b[31m" "456" "\x1b[39m"  "789"),
            (dict(align="center"), "123" "\x1b[31m" "456" "\x1b[39m"  "789"),
            (dict(align="right"),  "123" "\x1b[31m" "456" "\x1b[39m"  "789"),
            (dict(align="left",   pad=2), "123" "\x1b[31m" "456" "\x1b[39m"  "789  "),
            (dict(align="center", pad=2), " 123" "\x1b[31m" "456" "\x1b[39m"  "789 "),
            (dict(align="right",  pad=2), "  123" "\x1b[31m" "456" "\x1b[39m"  "789"),
            (dict(width=0),    ""),
            (dict(width=1),    "1"),
            (dict(width=2),    "12"),
            (dict(width=3),    "123"),
            (dict(width=4),    "123" "\x1b[31m" "4"   "\x1b[39m"),
            (dict(width=5),    "123" "\x1b[31m" "45"  "\x1b[39m"),
            (dict(width=6),    "123" "\x1b[31m" "456" "\x1b[39m"),
            (dict(width=7),    "123" "\x1b[31m" "456" "\x1b[39m"  "7"),
            (dict(width=8),    "123" "\x1b[31m" "456" "\x1b[39m"  "78"),
            (dict(width=9),    "123" "\x1b[31m" "456" "\x1b[39m"  "789"),
            (dict(width=10),   "123" "\x1b[31m" "456" "\x1b[39m"  "789 "),
            (dict(width=11),   "123" "\x1b[31m" "456" "\x1b[39m"  "789  "),
            (dict(width=12),   "123" "\x1b[31m" "456" "\x1b[39m"  "789   "),
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
            (dict(width=5,  align="left"),    "123" "\x1b[31m" "45"  "\x1b[39m"),
            (dict(width=5,  align="right"),   "123" "\x1b[31m" "45"  "\x1b[39m"),
            (dict(width=5,  align="center"),  "123" "\x1b[31m" "45"  "\x1b[39m"),
            (dict(width=12, align="left"),    "123" "\x1b[31m" "456" "\x1b[39m"  "789   "),
            (dict(width=12, align="right"),            "   123" "\x1b[31m" "456" "\x1b[39m" "789"),
            (dict(width=12, align="center"),             " 123" "\x1b[31m" "456" "\x1b[39m" "789  "),
            (dict(width=12, align="left", fill="-"),      "123" "\x1b[31m" "456" "\x1b[39m" "789---"),
            (dict(width=12, align="right", fill="-"),  "---123" "\x1b[31m" "456" "\x1b[39m" "789"),
            (dict(width=12, align="center", fill="-"),   "-123" "\x1b[31m" "456" "\x1b[39m" "789--"),
            (dict(width=12, align="left", fill="-", pad=2),        "123" "\x1b[31m" "456" "\x1b[39m" "789---"),
            (dict(width=12, align="left", fill="-", pad=4),        "123" "\x1b[31m" "456" "\x1b[39m" "78----"),
            (dict(width=12, align="right", fill="-", pad=2),    "---123" "\x1b[31m" "456" "\x1b[39m" "789"),
            (dict(width=12, align="right", fill="-", pad=4),   "----123" "\x1b[31m" "456" "\x1b[39m" "78"),
            (dict(width=12, align="center", fill="-", pad=2),     "-123" "\x1b[31m" "456" "\x1b[39m" "789--"),
            (dict(width=12, align="center", fill="-", pad=4),    "--123" "\x1b[31m" "456" "\x1b[39m" "78--"),
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
            (dict(width=5, overflow="", fill="-"),  "123" "\x1b[31m" "45"   "\x1b[39m"),
            (dict(width=10, align="right", overflow="...", fill="-"),    "123" "\x1b[31m" "456"   "\x1b[39m" "7..."),
            (dict(width=0, overflow="...", fill="-", pad=2),  ""),
            (dict(width=1, overflow="...", fill="-", pad=2),  "-"),
            (dict(width=2, overflow="...", fill="-", pad=2),  "--"),
            (dict(width=3, overflow="...", fill="-", pad=2),  ".--"),
            (dict(width=4, overflow="...", fill="-", pad=2),  "..--"),
            (dict(width=5, overflow="...", fill="-", pad=2),  "...--"),
            (dict(width=6, overflow="...", fill="-", pad=2),  "1...--"),
        ],
        ids=format_test_params
    )
    # fmt: on
    def test_format(self, kwargs: dict, expected: str):
        text = Text(*self.fragments, **kwargs)
        expected_no_sgr = pt.SgrStringReplacer().apply(expected)
        assert pt.render(text) == expected
        assert pt.render(text, renderer=self.renderer_no_sgr) == expected_no_sgr


@pytest.mark.setup(force_output_mode=OutputMode.TRUE_COLOR)
class TestSimpleTable:
    def setup_method(self) -> None:
        self.style = Style(fg="yellow")
        self.table = pt.SimpleTable(width=30, sep="|")

    @pytest.mark.parametrize(
        "cell",
        ["1", pt.Fragment("1"), pt.FrozenText("1"), pt.Text("1"), pt.SimpleTable("1")],
        ids=format_test_rt_params,
    )
    def test_cell_types_accepted(self, cell: pytermor.text.RT):
        self.table.add_row(cell)
        assert self.table.row_count == 1


class TestSplitting:
    @pytest.mark.parametrize(
        "expected, input",
        [(
            Text(
                Fragment("Testing", pt.Style(underlined=True)),
                Fragment(" "),
                Fragment("started", pt.Style(underlined=True)),
                Fragment(" "),
                Fragment("at", pt.Style(underlined=True)),
                Fragment(" "),
                Fragment("23:24", pt.Style(underlined=True)),
            ),
            Text(Fragment("Testing started at 23:24", pt.Style(underlined=True))),
        )],
        ids=format_test_rt_params
    )
    def test_splitting_works(self, expected: Text, input: Text):
        input.split_by_spaces()
        assert input == expected


class TestMisc:
    @pytest.mark.parametrize(
        "expected,max_len,args,kwargs",
        [
            ("  1  2   3", 10, ("1", "2", "3"), {"pad_left": True}),
            (
                " 1 2 3 4  ",
                10,
                ("1", "2", "3", Text("4", "red")),
                {"pad_left": True, "pad_right": True},
            ),
            (
                "555  666  ",
                10,
                (Fragment("555", "red"), Fragment("666", "blue")),
                {"pad_right": True},
            ),
            ("1234  56  ", 10, (Fragment("1234", "red"), "56"), {"pad_right": True}),
        ],
    )
    @pytest.mark.setup(renderer_class=NoOpRenderer.__name__)
    def test_distribute_padded(self, expected: str, max_len: int, args, kwargs):
        result = pt.distribute_padded(max_len, *args, **kwargs)
        result_rendered = pt.render(result)
        assert len(result) == max_len
        assert len(result_rendered) == max_len
        assert result_rendered == expected
