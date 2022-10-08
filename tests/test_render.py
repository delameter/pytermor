# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import unittest

from pytermor import Style, SequenceSGR
from pytermor.common import LogicError
from pytermor.render import TmuxRenderer


class TestTmux(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        TmuxRenderer.set_up(True)

    def test_basic_render_works(self):
        result = TmuxRenderer.render('12345', Style(fg='red', bg='black', bold=True))
        self.assertEqual('#[bold]#[fg=red]#[bg=black]'
                         '12345'
                         '#[nobold nodim]#[fg=default]#[bg=default]',
                         result)

    def test_attribute_render_works(self):
        result = TmuxRenderer.render('12345',
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
        result = TmuxRenderer.render('12345', Style(fg='navy_blue', bg='dark_red'))

        self.assertEqual('#[fg=color17]#[bg=color88]'
                         '12345'
                         '#[fg=default]#[bg=default]',
                         result)

    def test_color_rgb_render_works(self):
        result = TmuxRenderer.render('12345', Style(fg=0x3aeba1, bg=0x3ac5a6))

        self.assertEqual('#[fg=#3aeba1]#[bg=#3ac5a6]'
                         '12345'
                         '#[fg=default]#[bg=default]',
                         result)

    def test_rendering_of_broken_extended_sgr_fails(self):
        self.assertRaises(
            ValueError,
            lambda: TmuxRenderer._sgr_to_tmux_style(SequenceSGR(38, 100, 3))
        )

    def test_rendering_of_unmapped_sgr_fails(self):
        self.assertRaises(
            LogicError,
            lambda: TmuxRenderer._sgr_to_tmux_style(SequenceSGR(255))
        )
