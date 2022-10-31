# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------

import unittest

import pytermor as pt
from pytermor import Style


class TestStyle(unittest.TestCase):
    def test_style_color_resolver(self):
        style1 = Style(fg=pt.Color16(0x800000, pt.IntCode.RED, pt.IntCode.BG_RED))
        # @TODO

    def test_styles_with_equal_attrs_are_equal(self):
        for style1, style2 in [
            (Style(), pt.NOOP_STYLE),
            (Style(), Style()),
            (Style(fg="red"), Style(fg="red")),
            (Style(bg="red"), Style(bg="red")),
            (Style(fg="red", bg="black"), Style(fg="red", bg="black")),
            (Style(fg="red", bold=True), Style(fg="red", bold=True)),
            (Style(underlined=True, italic=True), Style(underlined=True, italic=True)),
        ]:
            with self.subTest():
                self.assertEqual(style1, style2)

    def test_styles_with_different_attrs_are_not_equal(self):
        for style1, style2 in [
            (Style(fg="red"), pt.NOOP_STYLE),
            (Style(fg="blue"), Style()),
            (Style(fg="red"), Style(bg="red")),
            (Style(bg="red"), Style(fg="red")),
            (Style(fg="red", bg="black"), Style(fg="red", bg="yellow")),
            (Style(fg="red", bold=True), Style(fg="red", bold=False)),
            (Style(underlined=True, italic=True), Style(underlined=False, italic=True)),
        ]:
            with self.subTest(style1=style1, style2=style2):
                self.assertNotEqual(style1, style2)
