# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import unittest

import pytermor as pt
import pytermor.utilstr
from pytermor.style import Style


class TestText(unittest.TestCase):
    def setUp(self) -> None:
        pt.RendererManager.set_default_to_force_formatting()

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
        pt.RendererManager.set_default_to_force_formatting()

        self.text = pt.Text()
        self.text.append("123")
        self.text.append("456", Style(fg="red"))
        self.text.append("789")

    def _test_format(self, expected: str, template: str):
        expected_no_sgr = pytermor.utilstr.SgrStringReplacer().apply(expected)
        self.assertEqual(expected, template.format(self.text))
        self.assertEqual(expected_no_sgr, template.format(self.text.raw()))

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


