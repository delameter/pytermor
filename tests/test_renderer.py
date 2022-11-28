# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------

import io
import sys
import unittest

import pytermor as pt
from pytermor import SgrRenderer, OutputMode, Style


class TestRendererConfiguration(unittest.TestCase):
    def test_force_color_enabling(self):
        renderer = SgrRenderer(OutputMode.TRUE_COLOR)
        sys.stdout = io.StringIO()

        result = pt.render("12345", Style(fg="red"), renderer)
        self.assertEqual("\x1b[31m12345\x1b[39m", result)

    def test_force_color_disabling(self):
        result = pt.render("12345", Style(fg="red"), SgrRenderer(OutputMode.NO_ANSI))
        self.assertEqual("12345", result)

    def test_force_color_default(self):
        result = pt.render("12345", Style(fg="red"), SgrRenderer(OutputMode.AUTO))
        if sys.stdout.isatty():
            self.assertEqual("\x1b[31m12345\x1b[39m", result)
        else:
            self.assertEqual("12345", result)


class TestTmuxRenderer(unittest.TestCase):
    def setUp(self) -> None:
        self.maxDiff = 2000
        pt.RendererManager.set_default(pt.renderer.TmuxRenderer)

    def test_basic_render_works(self):
        result = pt.render("12345", Style(fg="red", bg="black", bold=True))
        self.assertEqual(
            "#[fg=red bg=black bold]"
            "12345"
            "#[fg=default bg=default nobold]",
            result,
        )

    def test_attribute_render_works(self):
        result = pt.render(
            "12345",
            Style(
                blink=True,
                bold=True,
                crosslined=True,
                dim=True,
                double_underlined=True,
                inversed=True,
                italic=True,
                overlined=True,
                underlined=True,
            ),
        )
        self.assertEqual(
            "#[blink bold strikethrough dim double-underscore reverse"
            " italics overline underscore]"
            "12345"
            "#[noblink nobold nostrikethrough nodim nodouble-underscore"
            " noreverse noitalics nooverline nounderscore]",
            result,
        )

    def test_color256_render_works(self):
        result = pt.render("12345", Style(fg="NavyBlue", bg="DarkRed"))

        self.assertEqual(
            "#[fg=colour17 bg=colour88]" "12345" "#[fg=default bg=default]", result
        )

    def test_color_rgb_render_works(self):
        result = pt.render("12345", Style(fg=0x3AEBA1, bg=0x3AC5A6))

        self.assertEqual(
            "#[fg=#3AEBA1 bg=#3AC5A6]" "12345" "#[fg=default bg=default]", result
        )

    def test_nested_render_works(self):
        result = (
            pt.Text("123", Style(fg="red"), close_this=False)
            + pt.Text("456", Style(fg="blue"), close_this=False)
            + pt.Text("789")
            + pt.Text("0qw", Style(fg="blue"), close_prev=True)
            + pt.Text("ert", Style(fg="red"), close_prev=True)
            + "yui"
        ).render(pt.renderer.TmuxRenderer)

        self.assertEqual(
            "#[fg=red]"
            "123"
            "#[fg=default]"
            "#[fg=blue]"
            "456"
            "#[fg=default]"
            "#[fg=blue]"
            "789"
            "#[fg=default]"
            "#[fg=blue]"
            "0qw"
            "#[fg=default]"
            "#[fg=red]"
            "ert"
            "#[fg=default]"
            "yui",
            result,
        )
