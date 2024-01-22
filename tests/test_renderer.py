# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import io
import os
import sys

import pytest

import pytermor as pt
from . import format_test_params
from pytermor import (
    SgrRenderer,
    OutputMode,
    Style,
    TmuxRenderer,
    RendererManager,
    IRenderer,
    HtmlRenderer,
    force_ansi_rendering,
    force_no_ansi_rendering, NOOP_STYLE,
)


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


@pytest.mark.config(renderer_classname=TmuxRenderer.__name__)
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

    def test_has_equal_hashes(self):
        renderer1 = pt.renderer.TmuxRenderer()
        renderer2 = pt.renderer.TmuxRenderer()
        assert renderer1 is not renderer2
        assert hash(renderer1) == hash(renderer2)

    def test_clone(self):
        renderer1 = pt.TmuxRenderer()
        renderer2 = renderer1.clone()
        assert renderer1 is not renderer2
        assert hash(renderer1) == hash(renderer2)


@pytest.mark.config(renderer_classname=HtmlRenderer.__name__)
class TestHtmlRenderer:
    def test_noop_render_works(self):
        result = HtmlRenderer().render("12345", NOOP_STYLE)
        assert result == '12345'

    def test_basic_render_works(self):
        result = pt.render("12345", Style(fg="red", bg="black", bold=True))
        assert result == (
            '<span style="background-color: #000000; color: #800000; font-weight: '
            '700">12345</span>'
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
            '<span style="border: 1px dotted; filter: brightness(0.75) saturate(0.5); '
            "font-style: italic; font-weight: 700; text-decoration: double line-through "
            'overline underline">12345</span>'
        )

    def test_color256_render_works(self):
        result = pt.render("12345", Style(fg="NavyBlue", bg="DarkRed"))
        expected = '<span style="background-color: #870000; color: #00005f">12345</span>'
        assert result == expected

    def test_color_rgb_render_works(self):
        result = pt.render("12345", Style(fg=0x3AEBA1, bg=0x3AC5A6))
        expected = '<span style="background-color: #3ac5a6; color: #3aeba1">12345</span>'
        assert result == expected

    def test_nested_render_works(self):
        result = pt.Text(
            pt.Fragment("123", Style(fg="red"), close_this=False),
            pt.Fragment("456", Style(fg="blue"), close_this=False),
            pt.Fragment("789"),
            pt.Fragment("0qw", Style(fg="blue"), close_prev=True),
            pt.Fragment("ert", Style(fg="red"), close_prev=True),
            pt.Fragment("yui"),
        ).render(pt.renderer.HtmlRenderer)

        assert result == (
            '<span style="color: #800000">123</span>'
            '<span style="color: #000080">456</span>'
            '<span style="color: #000080">789</span>'
            '<span style="color: #000080">0qw</span>'
            '<span style="color: #800000">ert</span>'
            '<span style="">yui</span>'
        )

    def test_has_equal_hashes(self):
        renderer1 = pt.renderer.HtmlRenderer()
        renderer2 = pt.renderer.HtmlRenderer()
        assert renderer1 is not renderer2
        assert hash(renderer1) == hash(renderer2)

    def test_clone(self):
        renderer1 = pt.HtmlRenderer()
        renderer2 = renderer1.clone()
        assert renderer1 is not renderer2
        assert hash(renderer1) == hash(renderer2)


class TestSgrRenderer:
    @classmethod
    def _make_fake_tty_renderer(cls, *, close: bool = False) -> SgrRenderer:
        fake_io = io.StringIO()
        fake_io.isatty = lambda: True
        if close:
            fake_io.close()
        return SgrRenderer(io=fake_io)

    @classmethod
    def _del_environ(cls, key: str):
        try:
            del os.environ[key]
        except KeyError:
            pass

    def test_mode_detect(self):
        assert SgrRenderer()._output_mode == OutputMode.NO_ANSI

    @pytest.mark.parametrize(
        "expected, term, colorterm",
        [
            (OutputMode.XTERM_256, "", ""),
            (OutputMode.NO_ANSI, "xterm", ""),
            (OutputMode.XTERM_16, "xterm-color", ""),
            (OutputMode.TRUE_COLOR, "xterm-256color", "truecolor"),
            (OutputMode.TRUE_COLOR, "xterm-256color", "24bit"),
        ],
        ids=format_test_params,
    )
    def test_mode_detect_by_env(self, expected: OutputMode, term: str, colorterm: str):
        os.environ["TERM"] = term
        os.environ["COLORTERM"] = colorterm
        assert self._make_fake_tty_renderer()._output_mode == expected

    def test_mode_detect_on_closed_io(self):
        assert (
            self._make_fake_tty_renderer(close=True)._output_mode == OutputMode.NO_ANSI
        )

    @pytest.mark.config(default_output_mode="xterm_16")
    def test_mode_default_value_utilized(self):
        self._del_environ("TERM")
        self._del_environ("COLORTERM")
        assert self._make_fake_tty_renderer()._output_mode == OutputMode.XTERM_16

    @pytest.mark.config(force_output_mode="xterm_16")
    def test_mode_forced_value_utilized(self):
        assert SgrRenderer()._output_mode == OutputMode.XTERM_16

    def test_mode_as_string_supported(self):
        assert SgrRenderer("xterm_16")._output_mode == OutputMode.XTERM_16

    def test_different_setup_has_differing_hashes(self):
        renderer1 = pt.SgrRenderer(pt.OutputMode.NO_ANSI)
        renderer2 = pt.SgrRenderer(pt.OutputMode.TRUE_COLOR)
        assert hash(renderer1) != hash(renderer2)

    def test_same_setup_has_equal_hashes(self):
        renderer1 = pt.SgrRenderer(pt.OutputMode.XTERM_256)
        renderer2 = pt.SgrRenderer(pt.OutputMode.XTERM_256)
        assert renderer1 is not renderer2
        assert hash(renderer1) == hash(renderer2)

    def test_clone(self):
        renderer1 = pt.SgrRenderer(pt.OutputMode.XTERM_256)
        renderer2 = renderer1.clone()
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


class TestRendererManager:
    def teardown_method(self):
        RendererManager.override(None)

    def test_override_class_works(self):
        RendererManager.override(SgrRenderer)
        assert isinstance(RendererManager.get(), SgrRenderer)

    def test_override_none_works(self):
        RendererManager.override(None)
        assert isinstance(RendererManager.get(), IRenderer)

    @pytest.mark.config(renderer_classname=TmuxRenderer.__name__)
    def test_override_config_value_works(self):
        RendererManager.override()
        assert isinstance(RendererManager.get(), TmuxRenderer)

    def test_override_instance_works(self):
        RendererManager.override(renderer := SgrRenderer())
        assert RendererManager.get() is renderer

    # def test_set_as_string_works(self):
    #     RendererManager.set_default("HtmlRenderer")
    #     assert isinstance(RendererManager.get_default(), HtmlRenderer)


class TestMisc:
    def test_force_ansi_rendering(self):
        force_ansi_rendering()
        assert (
            RendererManager.get().render("123", "red") == "\x1b[31m"
            "123"
            "\x1b[39m"
        )

    def test_force_no_ansi_rendering(self):
        force_no_ansi_rendering()
        assert RendererManager.get().render("123", "red") == "123"
