# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

import typing as t
import unittest

import pytest

import pytermor as pt
import pytermor.utilstr
from pytermor import RendererManager, TmuxRenderer, IRenderable
from pytermor.common import Align as A
from pytermor.renderer import NoOpRenderer, SgrRendererDebugger
from pytermor.style import Style


def rt_str(val) -> str | None:
    if isinstance(val, str):
        max_sl = 9
        sample = val[:max_sl] + ("‥" * (len(val) > max_sl))
        return f'<str>[({len(val)}, "{sample}")]'
    if isinstance(val, IRenderable):
        return repr(val)
    return None


class TestString(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pt.RendererManager.set_default_format_always()

    def setUp(self) -> None:
        self.style = Style(fg="red")
        self.string = pt.String("123", self.style)

    def test_style_applying_works(self):
        self.assertEqual("\x1b[31m" "123" "\x1b[39m", self.string.render())

    def test_fragment_is_accessible(self):
        self.assertEqual(len(self.string.fragments), 1)
        self.assertIsInstance(self.string.fragments[0], pt.text._Fragment)

    def test_style_is_accessible(self):
        self.assertIs(self.string.style, self.style)

    def test_length_is_correct(self):
        self.assertEqual(len(self.string), 3)


class TestFixedString:
    @classmethod
    def setup_class(cls) -> None:
        pt.RendererManager.set_default_format_always()

    def setup_method(self) -> None:
        self.style = Style(fg="blue")
        self.string = pt.FixedString("123", self.style)

    def test_style_applying_works(self):
        assert "\x1b[34m" "123" "\x1b[39m" == self.string.render()

    def test_fragment_is_accessible(self):
        assert len(self.string.fragments) == 1
        assert isinstance(self.string.fragments[0], pt.text._Fragment)

    def test_style_is_accessible(self):
        assert self.string.style is self.style

    def test_origin_is_accessible(self):
        assert len(self.string.origin) == 3

    def test_length_is_correct(self):
        assert len(self.string) == 3

    @pytest.mark.parametrize("pad_left, pad_right", [(2, 0), (0, 2), (2, 2)])
    @pytest.mark.xfail(raises=ValueError)
    def test_init_with_invalid_width_fails(self, pad_left: int, pad_right: int):
        pt.FixedString("1234567", width=1, pad_left=pad_left, pad_right=pad_right)

    @pytest.mark.xfail(raises=ValueError)
    def test_init_with_invalid_align_fails(self):
        pt.FixedString("1234567", align="FUFLO")  # noqa

    @pytest.mark.parametrize(
        "initial, expected, width, args",
        [
            ("1234567", "123", 3, {"align": A.LEFT}),
            ("1234567", "345", 3, {"align": A.CENTER}),
            ("1234567", "567", 3, {"align": A.RIGHT}),
            ("123", "123  ", 5, {"align": A.LEFT}),
            ("123", " 123 ", 5, {"align": A.LEFT, "pad_left": 1}),
            ("123", "123  ", 5, {"align": A.LEFT, "pad_right": 1}),
            ("123", " 123 ", 5, {"align": A.CENTER}),
            ("123", "  123", 5, {"align": A.CENTER, "pad_left": 2}),
            ("123", "123  ", 5, {"align": A.CENTER, "pad_right": 2}),
            ("123", "  123", 5, {"align": A.RIGHT}),
            ("123", "  123", 5, {"align": A.RIGHT, "pad_left": 1}),
            ("123", " 123 ", 5, {"align": A.RIGHT, "pad_right": 1}),
            ("123", "  1  ", 5, {"align": A.LEFT, "pad_left": 2, "pad_right": 2}),
            ("123", "  2  ", 5, {"align": A.CENTER, "pad_left": 2, "pad_right": 2}),
            ("123", " 12  ", 5, {"align": A.CENTER, "pad_left": 1, "pad_right": 2}),
            ("123", "  3  ", 5, {"align": A.RIGHT, "pad_left": 2, "pad_right": 2}),
        ],
    )
    def test_padding_alignment_cropping(
        self, initial: str, expected: str, width: int, args: dict
    ):
        assert expected == pt.FixedString(initial, width=width, **args).raw


class TestText(unittest.TestCase):
    def setUp(self) -> None:
        pt.RendererManager.set_default_format_always()

    def test_style_applying_works(self):
        text = pt.Text("123", Style(fg="red"))
        result = text.render()

        self.assertEqual("\x1b[31m" "123" "\x1b[39m", result)

    def test_style_closing_works(self):
        text = pt.Text("123", Style(fg="red")).append("456", Style())
        result = text.render()

        self.assertEqual("\x1b[31m" "123" "\x1b[39m" "456", result)

    def test_style_leaving_open_works(self):
        text = pt.Text("123", Style(fg="red"), close_this=False).append("456", Style())
        result = text.render()

        self.assertEqual("\x1b[31m" "123" "\x1b[39m" "\x1b[31m" "456" "\x1b[39m", result)

    def test_style_resetting_works(self):
        style = Style(fg="red")
        text = (
            pt.Text("123", style, close_this=False)
            + pt.Text("", style, close_prev=True)
            + pt.Text("456")
        )
        result = text.render()

        self.assertEqual("\x1b[31m" "123" "\x1b[39m" "456", result)

    def test_style_nesting_works(self):
        style1 = Style(fg="red", bg="black", bold=True)
        style2 = Style(fg="yellow", bg="green", underlined=True)
        text = (
            pt.Text("1", style1, close_this=False)
            + pt.Text("2", style2, close_this=False)
            + pt.Text("3")
            + pt.Text("4", style2, close_prev=True)
            + pt.Text("5", style1, close_prev=True)
            + pt.Text("6")
        )
        result = text.render()

        self.assertEqual(
            "\x1b[1;31;40m"
            "1"
            "\x1b[22;39;49m"
            "\x1b[1;4;33;42m"
            "2"
            "\x1b[22;24;39;49m"
            "\x1b[1;4;33;42m"
            "3"
            "\x1b[22;24;39;49m"
            "\x1b[1;4;33;42m"
            "4"
            "\x1b[22;24;39;49m"
            "\x1b[1;31;40m"
            "5"
            "\x1b[22;39;49m"
            "6",
            result,
        )


class TestTextFormatting(unittest.TestCase):
    def setUp(self) -> None:
        pt.RendererManager.set_default_format_always()

        self.text = pt.Text()
        self.text.append("123")
        self.text.append("456", Style(fg="red"))
        self.text.append("789")

    def _test_format(self, expected: str, template: str):
        expected_no_sgr = pytermor.utilstr.SgrStringReplacer().apply(expected)
        self.assertEqual(expected, template.format(self.text))
        self.assertEqual(expected_no_sgr, template.format(self.text.raw))

    def test_default_format_works(self):
        self._test_format("123" "\x1b[31m" "456" "\x1b[39m" "789", "{:}")

    def test_string_format_works(self):
        self._test_format("123" "\x1b[31m" "456" "\x1b[39m" "789", "{:s}")

    def test_string_width_format_works(self):
        self._test_format("123" "\x1b[31m" "456" "\x1b[39m" "789", "{:2s}")
        self._test_format("123" "\x1b[31m" "456" "\x1b[39m" "789   ", "{:12s}")

    def test_string_max_len_format_works(self):
        self._test_format("12", "{:.2s}")
        self._test_format("123" "\x1b[31m" "45" "\x1b[39m", "{:.5s}")
        self._test_format("123" "\x1b[31m" "456" "\x1b[39m" "78", "{:.8s}")
        self._test_format("123" "\x1b[31m" "456" "\x1b[39m" "789", "{:.12s}")

    def test_string_align_format_works(self):
        self._test_format("123" "\x1b[31m" "456" "\x1b[39m" "789   ", "{:<12s}")
        self._test_format("   123" "\x1b[31m" "456" "\x1b[39m" "789", "{:>12s}")
        self._test_format(" 123" "\x1b[31m" "456" "\x1b[39m" "789  ", "{:^12s}")

    def test_string_align_and_width_format_works(self):
        self._test_format("123" "\x1b[31m" "456" "\x1b[39m" "789", "{:<5s}")
        self._test_format("123" "\x1b[31m" "456" "\x1b[39m" "789", "{:>5s}")
        self._test_format("123" "\x1b[31m" "456" "\x1b[39m" "789", "{:^5s}")

    def test_string_align_and_max_len_format_works(self):
        self._test_format("123" "\x1b[31m" "45" "\x1b[39m", "{:<.5s}")
        self._test_format("123" "\x1b[31m" "45" "\x1b[39m", "{:>.5s}")
        self._test_format("123" "\x1b[31m" "45" "\x1b[39m", "{:^.5s}")

    def test_string_fill_format_works(self):
        self._test_format("123" "\x1b[31m" "456" "\x1b[39m" "789...", "{:.<12s}")
        self._test_format("...123" "\x1b[31m" "456" "\x1b[39m" "789", "{:.>12s}")
        self._test_format("!123" "\x1b[31m" "456" "\x1b[39m" "789!!", "{:!^12s}")

    def test_string_full_format_works(self):
        self._test_format("AAA123" "\x1b[31m" "45" "\x1b[39m" "AAAA", "{:A^12.5}")

    def test_invalid_type_format_fails(self):
        for fmt in "bcdoxXneEfFgGn%":
            self.assertRaises(ValueError, lambda text=self.text: f"{text:{fmt}}")


class TestSimpleTable:
    @classmethod
    def setup_class(cls) -> None:
        pt.RendererManager.set_default_format_always()

    def setup_method(self) -> None:
        self.style = Style(fg="yellow")
        self.table = pt.SimpleTable(width=30, sep="|")

    @pytest.mark.parametrize(
        "cell",
        [
            "1",
            pt.String("1"),
            pt.FixedString("1"),
            pt.FrozenText("1"),
            pt.Text("1"),
            pt.SimpleTable("1"),
        ],
        ids=rt_str,
    )
    def test_cell_types_accepted(self, cell: pt.RT):
        self.table.add_row(cell)
        assert self.table.row_count == 1


class TestCache:
    immutable_renderables = [pt.String, pt.FixedString, pt.FrozenText]

    @pytest.mark.parametrize("renderable_class", immutable_renderables)
    def test_cache_works(self, renderable_class: t.Type):
        string = renderable_class("12345", pt.Style(bg="yellow"))
        renderer = RendererManager.get_default()
        rendered = string.render(renderer)
        assert renderer in string._renders_cache.keys()
        assert rendered is string._renders_cache.get(renderer)

    @pytest.mark.parametrize("renderable_class", immutable_renderables)
    def test_cache_with_another_renderer_is_different(self, renderable_class: t.Type):
        string = renderable_class("12345", pt.Style(bg="yellow"))
        renderer_sgr = RendererManager.get_default()
        renderer_html = pt.HtmlRenderer()
        rendered_sgr = string.render(renderer_sgr)
        rendered_html = string.render(renderer_html)
        assert rendered_sgr != rendered_html
        assert len(string._renders_cache) == 2
        assert renderer_sgr in string._renders_cache.keys()
        assert renderer_html in string._renders_cache.keys()

    @pytest.mark.parametrize("renderable_class", [pt.Text])
    def test_cache_is_disabled_for_mutable_renderables(self, renderable_class: t.Type):
        string = renderable_class("12345", pt.Style(bg="yellow"))
        renderer = RendererManager.get_default()
        string.render(renderer)
        assert len(string._renders_cache) == 0


class TestMisc:
    @pytest.mark.parametrize(
        "expected,max_len,args,kwargs",
        [
            ("  1  2   3", 10, ("1", "2", "3"), {"pad_left": True}),
            (
                " 1 2 3 4  ",
                10,
                ("1", "2", "3", pt.FrozenText("4", "red")),
                {"pad_left": True, "pad_right": True},
            ),
            (
                "555  666  ",
                10,
                (pt.String("555", "red"), pt.Text("666", "blue")),
                {"pad_right": True},
            ),
            (
                "  1234 56 ",
                10,
                (pt.FixedString("1234", "red", 6, "right"), "56"),
                {"pad_right": True},
            ),
        ],
    )
    def test_distribute_padded(self, expected: str, max_len: int, args, kwargs):
        result = pt.distribute_padded(max_len, *args, **kwargs)
        result_rendered = pt.render(result, renderer=NoOpRenderer())
        assert len(result) == max_len
        assert len(result_rendered) == max_len
        assert result_rendered == expected
