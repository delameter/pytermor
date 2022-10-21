# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import unittest

from pytermor import Style, SequenceSGR, Text, RendererManager
from pytermor.common import LogicError
from pytermor.text import TmuxRenderer
from pytermor.util import ReplaceSGR


class TestText(unittest.TestCase):
    def setUp(self) -> None:
        RendererManager.set_forced_sgr_as_default()

    def test_style_applying_works(self):
        text = Text('123', style=Style(fg='red'))
        result = text.render()

        self.assertEqual('\x1b[31m123\x1b[39m', result)


class TestTextFormatting(unittest.TestCase):
    def setUp(self) -> None:
        RendererManager.set_forced_sgr_as_default()

        self.text = Text()
        self.text.append('123')
        self.text.append('456', Style(fg='red'))
        self.text.append('789')

    def _test_format(self, expected: str, template: str):
        expected_no_sgr = ReplaceSGR().apply(expected)
        self.assertEqual(expected, template.format(self.text))
        self.assertEqual(expected_no_sgr, template.format(self.text.raw()))

    def test_default_format_works(self):
        self._test_format('123\x1b[31m456\x1b[39m789', "{:}")

    def test_string_format_works(self):
        self._test_format('123\x1b[31m456\x1b[39m789', "{:s}")

    def test_string_width_format_works(self):
        self._test_format('123\x1b[31m456\x1b[39m789', "{:2s}")
        self._test_format('123\x1b[31m456\x1b[39m789   ', "{:12s}")

    def test_string_max_len_format_works(self):
        self._test_format('12', "{:.2s}")
        self._test_format('123\x1b[31m45\x1b[39m', "{:.5s}")
        self._test_format('123\x1b[31m456\x1b[39m78', "{:.8s}")
        self._test_format('123\x1b[31m456\x1b[39m789', "{:.12s}")

    def test_string_align_format_works(self):
        self._test_format('123\x1b[31m456\x1b[39m789   ', "{:<12s}")
        self._test_format('   123\x1b[31m456\x1b[39m789', "{:>12s}")
        self._test_format(' 123\x1b[31m456\x1b[39m789  ', "{:^12s}")

    def test_string_align_and_width_format_works(self):
        self._test_format('123\x1b[31m456\x1b[39m789', "{:<5s}")
        self._test_format('123\x1b[31m456\x1b[39m789', "{:>5s}")
        self._test_format('123\x1b[31m456\x1b[39m789', "{:^5s}")

    def test_string_align_and_max_len_format_works(self):
        self._test_format('123\x1b[31m45\x1b[39m', "{:<.5s}")
        self._test_format('123\x1b[31m45\x1b[39m', "{:>.5s}")
        self._test_format('123\x1b[31m45\x1b[39m', "{:^.5s}")

    def test_string_fill_format_works(self):
        self._test_format('123\x1b[31m456\x1b[39m789...', "{:.<12s}")
        self._test_format('...123\x1b[31m456\x1b[39m789', "{:.>12s}")
        self._test_format('!123\x1b[31m456\x1b[39m789!!', "{:!^12s}")

    def test_string_full_format_works(self):
        self._test_format('AAA123\x1b[31m45\x1b[39mAAAA', "{:A^12.5}")

    def test_invalid_type_format_fails(self):
        for fmt in 'bcdoxXneEfFgGn%':
            self.assertRaises(ValueError, lambda text=self.text: f"{text:{fmt}}")


class TestTmux(unittest.TestCase):
    def setUp(self) -> None:
        self.renderer = TmuxRenderer().setup(True)

    def test_basic_render_works(self):
        result = self.renderer.render('12345', Style(fg='red', bg='black', bold=True))
        self.assertEqual('#[bold]#[fg=red]#[bg=black]'
                         '12345'
                         '#[nobold nodim]#[fg=default]#[bg=default]',
                         result)

    def test_attribute_render_works(self):
        result = self.renderer.render('12345',
                                      Style(blink=True, bold=True, crosslined=True,
                                            dim=True, double_underlined=True,
                                            inversed=True, italic=True, overlined=True,
                                            underlined=True))
        self.assertEqual(
            '#[blink]#[bold]#[strikethrough]#[dim]#[double-underscore]#[reverse]'
            '#[italics]#[overline]#[underscore]'
            '12345'
            '#[noblink]#[nobold nodim]#[nostrikethrough]#[nobold nodim]#[nounderscore]#[noreverse]'
            '#[noitalics]#[nooverline]#[nounderscore]',
            result
        )

    def test_color256_render_works(self):
        result = self.renderer.render('12345', Style(fg='navy_blue', bg='dark_red'))

        self.assertEqual('#[fg=color17]#[bg=color88]'
                         '12345'
                         '#[fg=default]#[bg=default]',
                         result)

    def test_color_rgb_render_works(self):
        result = self.renderer.render('12345', Style(fg=0x3aeba1, bg=0x3ac5a6))

        self.assertEqual('#[fg=#3aeba1]#[bg=#3ac5a6]'
                         '12345'
                         '#[fg=default]#[bg=default]',
                         result)

    def test_rendering_of_broken_extended_sgr_fails(self):
        self.assertRaises(
            ValueError,
            lambda: self.renderer._sgr_to_tmux_style(SequenceSGR(38, 100, 3))
        )

    def test_rendering_of_unmapped_sgr_fails(self):
        self.assertRaises(
            LogicError,
            lambda: self.renderer._sgr_to_tmux_style(SequenceSGR(255))
        )
