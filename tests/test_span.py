# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import unittest

from pytermor import autocomplete, sequence, intcode, Span
from pytermor.sequence import SequenceSGR


class TestEquality(unittest.TestCase):
    def test_same_are_equal(self):
        f1 = Span(SequenceSGR(intcode.BOLD), SequenceSGR(intcode.RESET))
        f2 = Span(SequenceSGR(intcode.BOLD), SequenceSGR(intcode.RESET))

        self.assertEqual(f1, f2)

    def test_diff_are_not_equal(self):
        f1 = Span(SequenceSGR(intcode.BG_HI_YELLOW), SequenceSGR(intcode.BG_COLOR_OFF))
        f2 = Span(SequenceSGR(intcode.BOLD), SequenceSGR(intcode.RESET))

        self.assertNotEqual(f1, f2)

    def test_diff_opening_are_not_equal(self):
        f1 = Span(SequenceSGR(intcode.BOLD), SequenceSGR(intcode.RESET))
        f2 = Span(SequenceSGR(intcode.ITALIC), SequenceSGR(intcode.RESET))

        self.assertNotEqual(f1, f2)

    def test_diff_closing_are_not_equal(self):
        f1 = Span(SequenceSGR(intcode.BOLD), SequenceSGR(intcode.RESET))
        f2 = Span(SequenceSGR(intcode.BOLD), SequenceSGR(intcode.NO_BOLD_DIM))

        self.assertNotEqual(f1, f2)

    def test_diff_opening_only_are_not_equal(self):
        f1 = Span(SequenceSGR(intcode.GREEN))
        f2 = Span(SequenceSGR(intcode.BLUE))

        self.assertNotEqual(f1, f2)

    def test_format_is_not_equal_to_sgr(self):
        f1 = Span(SequenceSGR(intcode.BOLD))

        self.assertNotEqual(f1, SequenceSGR(intcode.BOLD))

    def test_empty_are_equal(self):
        f1 = Span(SequenceSGR())
        f2 = Span(sequence.NOOP)

        self.assertEqual(f1, f2)

    def test_empty_is_not_equal_to_reset(self):
        f1 = Span(SequenceSGR())
        f2 = Span(SequenceSGR(0))

        self.assertNotEqual(f1, f2)


class TestWrap(unittest.TestCase):
    pass  # @todo


class TestAutoCompletion(unittest.TestCase):
    def test_autocomplete_single_sgr(self):
        f = autocomplete(sequence.BOLD)

        self.assertEqual(f.opening_seq, SequenceSGR(intcode.BOLD))
        self.assertEqual(f.closing_seq, SequenceSGR(intcode.NO_BOLD_DIM))

    def test_autocomplete_multiple_sgr(self):
        f = autocomplete(sequence.UNDERLINED + sequence.YELLOW + sequence.BG_RED)

        self.assertEqual(f.opening_seq, SequenceSGR(intcode.UNDERLINED, intcode.YELLOW, intcode.BG_RED))
        self.assertEqual(f.closing_seq, SequenceSGR(intcode.UNDERLINED_OFF, intcode.COLOR_OFF, intcode.BG_COLOR_OFF))

    def test_autocomplete_no_args(self):
        f = autocomplete()

        self.assertEqual(f.opening_seq, SequenceSGR())
        self.assertEqual(f.closing_seq, SequenceSGR())

    def test_autocomplete_empty_sgr(self):
        f = autocomplete(SequenceSGR())

        self.assertEqual(f.opening_seq, SequenceSGR())
        self.assertEqual(f.closing_seq, sequence.NOOP)

    def test_autocomplete_multiple_with_empty_sgr(self):
        f = autocomplete(sequence.BOLD, SequenceSGR(), sequence.RED)

        self.assertEqual(f.opening_seq, SequenceSGR(intcode.BOLD, intcode.RED))
        self.assertEqual(f.closing_seq, SequenceSGR(intcode.NO_BOLD_DIM, intcode.COLOR_OFF))
