# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------

import io
import sys

import pytest

import pytermor as pt
from pytermor import SgrRenderer, OutputMode, Style


class TestRendererConfiguration:
    def test_force_color_enabling(self):
        renderer = SgrRenderer(OutputMode.TRUE_COLOR)
        sys.stdout = io.StringIO()

        result = pt.render("12345", Style(fg="red"), renderer)
        assert result == "\x1b[31m12345\x1b[39m"

    def test_force_color_disabling(self):
        result = pt.render("12345", Style(fg="red"), SgrRenderer(OutputMode.NO_ANSI))
        assert result == "12345"

    def test_force_color_default(self):
        result = pt.render("12345", Style(fg="red"), SgrRenderer(OutputMode.AUTO))
        if sys.stdout.isatty():
            assert result == "\x1b[31m12345\x1b[39m"
        else:
            assert result == "12345"


@pytest.mark.setup(renderer_class="TmuxRenderer")
class TestTmuxRenderer:
    def test_basic_render_works(self):
        result = pt.render("12345", Style(fg="red", bg="black", bold=True))
        assert result == (
            "#[fg=red bg=black bold]" "12345" "#[fg=default bg=default nobold]"
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
        assert result == (
            "#[blink bold strikethrough dim double-underscore "
            "reverse italics overline underscore]"
            "12345"
            "#[noblink nobold nostrikethrough nodim nodouble-underscore "
            "noreverse noitalics nooverline nounderscore]"
        )

    def test_color256_render_works(self):
        result = pt.render("12345", Style(fg="NavyBlue", bg="DarkRed"))
        expected = "#[fg=colour17 bg=colour88]" "12345" "#[fg=default bg=default]"
        assert result == expected

    def test_color_rgb_render_works(self):
        result = pt.render("12345", Style(fg=0x3AEBA1, bg=0x3AC5A6))
        expected = "#[fg=#3aeba1 bg=#3ac5a6]" "12345" "#[fg=default bg=default]"
        assert result == expected

    def test_nested_render_works(self):
        result = pt.Text(
            pt.Fragment("123", Style(fg="red"), close_this=False),
            pt.Fragment("456", Style(fg="blue"), close_this=False),
            pt.Fragment("789"),
            pt.Fragment("0qw", Style(fg="blue"), close_prev=True),
            pt.Fragment("ert", Style(fg="red"), close_prev=True),
            pt.Fragment("yui"),
        ).render(pt.renderer.TmuxRenderer)

        assert result == (
            "#[fg=red]" + "123" + "#[fg=default]"
            "#[fg=blue]" + "456" + "#[fg=default]"
            "#[fg=blue]" + "789" + "#[fg=default]"
            "#[fg=blue]" + "0qw" + "#[fg=default]"
            "#[fg=red]" + "ert" + "#[fg=default]"
            "yui"
        )

    def test_renderers_has_equal_hashes(self):
        renderer1 = pt.renderer.TmuxRenderer()
        renderer2 = pt.renderer.TmuxRenderer()
        assert renderer1 is not renderer2
        assert hash(renderer1) == hash(renderer2)


class TestHtmlRenderer:
    def test_renderers_has_equal_hashes(self):
        renderer1 = pt.HtmlRenderer()
        renderer2 = pt.HtmlRenderer()
        assert renderer1 is not renderer2
        assert hash(renderer1) == hash(renderer2)


class TestSgrRenderer:
    def test_renderers_with_different_setup_has_differing_hashes(self):
        renderer1 = pt.SgrRenderer(pt.OutputMode.NO_ANSI)
        renderer2 = pt.SgrRenderer(pt.OutputMode.TRUE_COLOR)
        assert hash(renderer1) != hash(renderer2)

    def test_renderers_with_same_setup_has_equal_hashes(self):
        renderer1 = pt.SgrRenderer(pt.OutputMode.XTERM_256)
        renderer2 = pt.SgrRenderer(pt.OutputMode.XTERM_256)
        assert renderer1 is not renderer2
        assert hash(renderer1) == hash(renderer2)


class TestSgrRendererDebugger:
    def test_renderers_with_different_setup_has_differing_hashes(self):
        renderer1 = pt.renderer.SgrDebugger(pt.OutputMode.NO_ANSI)
        renderer2 = pt.renderer.SgrDebugger(pt.OutputMode.TRUE_COLOR)
        assert hash(renderer1) != hash(renderer2)

    def test_renderer_after_update_has_differing_hash(self):
        renderer = pt.renderer.SgrDebugger(pt.OutputMode.TRUE_COLOR)
        hash_before = hash(renderer)
        renderer.set_format_never()
        assert hash_before != hash(renderer)

    def test_renderers_with_same_setup_has_equal_hashes(self):
        renderer1 = pt.renderer.SgrDebugger(pt.OutputMode.XTERM_256)
        renderer2 = pt.renderer.SgrDebugger(pt.OutputMode.XTERM_256)
        assert renderer1 is not renderer2
        assert hash(renderer1) == hash(renderer2)
