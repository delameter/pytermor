# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import unittest

from pytermor.ansi import SequenceSGR, Span, Seqs, IntCodes, NOOP_SEQ


class TestEquality(unittest.TestCase):
    def test_same_are_equal(self):
        f1 = Span(SequenceSGR(IntCodes.BOLD), SequenceSGR(IntCodes.RESET))
        f2 = Span(SequenceSGR(IntCodes.BOLD), SequenceSGR(IntCodes.RESET))

        self.assertEqual(f1, f2)

    def test_diff_are_not_equal(self):
        f1 = Span(SequenceSGR(IntCodes.BG_HI_YELLOW), SequenceSGR(IntCodes.BG_COLOR_OFF))
        f2 = Span(SequenceSGR(IntCodes.BOLD), SequenceSGR(IntCodes.RESET))

        self.assertNotEqual(f1, f2)

    def test_diff_opening_are_not_equal(self):
        f1 = Span(SequenceSGR(IntCodes.BOLD), SequenceSGR(IntCodes.RESET))
        f2 = Span(SequenceSGR(IntCodes.ITALIC), SequenceSGR(IntCodes.RESET))

        self.assertNotEqual(f1, f2)

    def test_diff_closing_are_not_equal(self):
        f1 = Span(SequenceSGR(IntCodes.BOLD), SequenceSGR(IntCodes.RESET))
        f2 = Span(SequenceSGR(IntCodes.BOLD), SequenceSGR(IntCodes.BOLD_DIM_OFF))

        self.assertNotEqual(f1, f2)

    def test_diff_opening_only_are_not_equal(self):
        f1 = Span(SequenceSGR(IntCodes.GREEN))
        f2 = Span(SequenceSGR(IntCodes.BLUE))

        self.assertNotEqual(f1, f2)

    def test_format_is_not_equal_to_sgr(self):
        f1 = Span(SequenceSGR(IntCodes.BOLD))

        self.assertNotEqual(f1, SequenceSGR(IntCodes.BOLD))

    def test_empty_are_equal(self):
        f1 = Span(SequenceSGR())
        f2 = Span(NOOP_SEQ)

        self.assertEqual(f1, f2)

    def test_empty_is_not_equal_to_reset(self):
        f1 = Span(SequenceSGR())
        f2 = Span(SequenceSGR(0))

        self.assertNotEqual(f1, f2)


class TestWrap(unittest.TestCase):
    pass  # @todo


class TestAutoCompletion(unittest.TestCase):
    def test_autocomplete_single_sgr(self):
        f = Span(Seqs.BOLD)

        self.assertEqual(f.opening_seq, SequenceSGR(IntCodes.BOLD))
        self.assertEqual(f.closing_seq, SequenceSGR(IntCodes.BOLD_DIM_OFF))

    def test_autocomplete_multiple_sgr(self):
        f = Span(Seqs.UNDERLINED + Seqs.YELLOW + Seqs.BG_RED)

        self.assertEqual(f.opening_seq, SequenceSGR(IntCodes.UNDERLINED, IntCodes.YELLOW, IntCodes.BG_RED))
        self.assertEqual(f.closing_seq, SequenceSGR(IntCodes.UNDERLINED_OFF, IntCodes.COLOR_OFF, IntCodes.BG_COLOR_OFF))

    def test_autocomplete_no_args(self):
        f = Span()

        self.assertEqual(f.opening_seq, SequenceSGR())
        self.assertEqual(f.closing_seq, SequenceSGR())

    def test_autocomplete_empty_sgr(self):
        f = Span(SequenceSGR())

        self.assertEqual(f.opening_seq, SequenceSGR())
        self.assertEqual(f.closing_seq, NOOP_SEQ)

    def test_autocomplete_multiple_with_empty_sgr(self):
        f = Span(Seqs.BOLD, SequenceSGR(), Seqs.RED)

        self.assertEqual(f.opening_seq, SequenceSGR(IntCodes.BOLD, IntCodes.RED))
        self.assertEqual(f.closing_seq, SequenceSGR(IntCodes.BOLD_DIM_OFF, IntCodes.COLOR_OFF))
