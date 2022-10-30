# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import io
import sys
import unittest

from pytermor import Style, SequenceSGR, Text, RendererManager, NOOP_STYLE, SgrRenderer
from pytermor.common import LogicError
from pytermor.text import TmuxRenderer
from pytermor.util import ReplaceSGR


class TestText(unittest.TestCase):
    def setUp(self) -> None:
        RendererManager.set_forced_sgr_as_default()

    def test_style_applying_works(self):
        text = Text('123', Style(fg='red'))
        result = text.render()

        self.assertEqual('\x1b[31m' '123' '\x1b[39m', result)

    def test_style_closing_works(self):
        text = Text('123', Style(fg='red')).append('456', Style())
        result = text.render()

        self.assertEqual('\x1b[31m' '123' 
                         '\x1b[39m' '456',
                         result)

    def test_style_leaving_open_works(self):
        text = Text('123', Style(fg='red'), close_this=False).append('456', Style())
        result = text.render()

        self.assertEqual('\x1b[31m' '123' '\x1b[39m'
                         '\x1b[31m' '456' '\x1b[39m',
                         result)

    def test_style_resetting_works(self):
        style = Style(fg='red')
        text = (Text('123', style, close_this=False) +
                Text('', style, close_prev=True) +
                Text('456'))
        result = text.render()

        self.assertEqual('\x1b[31m' '123' '\x1b[39m'
                         '456',
                         result)

    def test_style_nesting_works(self):
        style1 = Style(fg='red', bg='black', bold=True)
        style2 = Style(fg='yellow', bg='green', underlined=True)
        text = (Text('1', style1, close_this=False) +
                Text('2', style2, close_this=False) +
                Text('3') +
                Text('4', style2, close_prev=True) +
                Text('5', style1, close_prev=True) +
                Text('6'))
        result = text.render()

        self.assertEqual('\x1b[1;31;40m'   '1' '\x1b[22;39;49m'
                         '\x1b[1;4;33;42m' '2' '\x1b[22;24;39;49m'
                         '\x1b[1;4;33;42m' '3' '\x1b[22;24;39;49m'
                         '\x1b[1;4;33;42m' '4' '\x1b[22;24;39;49m'
                         '\x1b[1;31;40m'   '5' '\x1b[22;39;49m'
                         '6',
                         result)


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
        self._test_format('123' '\x1b[31m' '456' '\x1b[39m' '789', "{:}")

    def test_string_format_works(self):
        self._test_format('123' '\x1b[31m' '456' '\x1b[39m' '789', "{:s}")

    def test_string_width_format_works(self):
        self._test_format('123' '\x1b[31m' '456' '\x1b[39m' '789',    "{:2s}")
        self._test_format('123' '\x1b[31m' '456' '\x1b[39m' '789   ', "{:12s}")

    def test_string_max_len_format_works(self):
        self._test_format('12', "{:.2s}")
        self._test_format('123' '\x1b[31m' '45' '\x1b[39m',        "{:.5s}")
        self._test_format('123' '\x1b[31m' '456' '\x1b[39m' '78',  "{:.8s}")
        self._test_format('123' '\x1b[31m' '456' '\x1b[39m' '789', "{:.12s}")

    def test_string_align_format_works(self):
        self._test_format('123'    '\x1b[31m' '456' '\x1b[39m' '789   ', "{:<12s}")
        self._test_format('   123' '\x1b[31m' '456' '\x1b[39m' '789',    "{:>12s}")
        self._test_format(' 123'   '\x1b[31m' '456' '\x1b[39m' '789  ',  "{:^12s}")

    def test_string_align_and_width_format_works(self):
        self._test_format('123' '\x1b[31m' '456' '\x1b[39m' '789', "{:<5s}")
        self._test_format('123' '\x1b[31m' '456' '\x1b[39m' '789', "{:>5s}")
        self._test_format('123' '\x1b[31m' '456' '\x1b[39m' '789', "{:^5s}")

    def test_string_align_and_max_len_format_works(self):
        self._test_format('123' '\x1b[31m' '45' '\x1b[39m', "{:<.5s}")
        self._test_format('123' '\x1b[31m' '45' '\x1b[39m', "{:>.5s}")
        self._test_format('123' '\x1b[31m' '45' '\x1b[39m', "{:^.5s}")

    def test_string_fill_format_works(self):
        self._test_format('123'    '\x1b[31m' '456' '\x1b[39m' '789...', "{:.<12s}")
        self._test_format('...123' '\x1b[31m' '456' '\x1b[39m' '789',    "{:.>12s}")
        self._test_format('!123'   '\x1b[31m' '456' '\x1b[39m' '789!!',  "{:!^12s}")

    def test_string_full_format_works(self):
        self._test_format('AAA123' '\x1b[31m' '45' '\x1b[39m' 'AAAA', "{:A^12.5}")

    def test_invalid_type_format_fails(self):
        for fmt in 'bcdoxXneEfFgGn%':
            self.assertRaises(ValueError, lambda text=self.text: f"{text:{fmt}}")


class TestRendererConfiguration(unittest.TestCase):
    def test_force_color_enabling(self):
        self.renderer = SgrRenderer().setup(force_styles=True)
        sys.stdout = io.StringIO()

        result = self.renderer.render('12345', Style(fg='red'))
        self.assertEqual('\x1b[31m12345\x1b[39m', result)

    def test_force_color_disabling(self):
        self.renderer = SgrRenderer().setup(force_styles=False)

        result = self.renderer.render('12345', Style(fg='red'))
        self.assertEqual('12345', result)

    def test_force_color_default(self):
        self.renderer = SgrRenderer().setup(force_styles=False)

        result = self.renderer.render('12345', Style(fg='red'))
        if sys.stdout.isatty():
            self.assertEqual('\x1b[31m12345\x1b[39m', result)
        else:
            self.assertEqual('12345', result)


class TestTmuxRenderer(unittest.TestCase):
    def setUp(self) -> None:
        self.renderer = TmuxRenderer().setup(force_styles=True)

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
            '#[noblink]#[nobold nodim]#[nostrikethrough]#[nobold nodim]#[nounderscore]'
            '#[noreverse]#[noitalics]#[nooverline]#[nounderscore]',
            result
        )

    def test_color256_render_works(self):
        result = self.renderer.render('12345', Style(fg='NavyBlue', bg='DarkRed'))

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

    def test_nested_render_works(self):
        result = (Text('123', Style(fg='red'), close_this=False) +
                  Text('456', Style(fg='blue'), close_this=False) +
                  Text('789') +
                  Text('0qw', Style(fg='blue'), close_prev=True) +
                  Text('ert', Style(fg='red'), close_prev=True) +
                  'yui'
                  ).render(self.renderer)

        self.assertEqual('#[fg=red]'  '123' '#[fg=default]'
                         '#[fg=blue]' '456' '#[fg=default]'
                         '#[fg=blue]' '789' '#[fg=default]'
                         '#[fg=blue]' '0qw' '#[fg=default]'
                         '#[fg=red]'  'ert' '#[fg=default]'
                         'yui',
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


class TestStyle(unittest.TestCase):
    def test_styles_with_equal_attrs_are_equal(self):
        for style1, style2 in [
            (Style(), NOOP_STYLE),
            (Style(), Style()),
            (Style(fg='red'), Style(fg='red')),
            (Style(bg='red'), Style(bg='red')),
            (Style(fg='red', bg='black'), Style(fg='red', bg='black')),
            (Style(fg='red', bold=True), Style(fg='red', bold=True)),
            (Style(underlined=True, italic=True), Style(underlined=True, italic=True)),
        ]:
            with self.subTest():
                self.assertEqual(style1, style2)

    def test_styles_with_different_attrs_are_not_equal(self):
        for style1, style2 in [
            (Style(fg='red'), NOOP_STYLE),
            (Style(fg='blue'), Style()),
            (Style(fg='red'), Style(bg='red')),
            (Style(bg='red'), Style(fg='red')),
            (Style(fg='red', bg='black'), Style(fg='red', bg='yellow')),
            (Style(fg='red', bold=True), Style(fg='red', bold=False)),
            (Style(underlined=True, italic=True), Style(underlined=False, italic=True)),
        ]:
            with self.subTest(style1=style1, style2=style2):
                self.assertNotEqual(style1, style2)
