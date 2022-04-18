import unittest

from pytermor import autof, seq, sgr, SequenceSGR, Format


class FormatEqualityTestCase(unittest.TestCase):
    def test_same_are_equal(self):
        f1 = Format(SequenceSGR(sgr.BOLD), SequenceSGR(sgr.RESET))
        f2 = Format(SequenceSGR(sgr.BOLD), SequenceSGR(sgr.RESET))

        self.assertEqual(f1, f2)

    def test_diff_are_not_equal(self):
        f1 = Format(SequenceSGR(sgr.BG_HI_YELLOW), SequenceSGR(sgr.BG_COLOR_OFF))
        f2 = Format(SequenceSGR(sgr.BOLD), SequenceSGR(sgr.RESET))

        self.assertNotEqual(f1, f2)

    def test_diff_opening_are_not_equal(self):
        f1 = Format(SequenceSGR(sgr.BOLD), SequenceSGR(sgr.RESET))
        f2 = Format(SequenceSGR(sgr.ITALIC), SequenceSGR(sgr.RESET))

        self.assertNotEqual(f1, f2)

    def test_diff_closing_are_not_equal(self):
        f1 = Format(SequenceSGR(sgr.BOLD), SequenceSGR(sgr.RESET))
        f2 = Format(SequenceSGR(sgr.BOLD), SequenceSGR(sgr.BOLD_DIM_OFF))

        self.assertNotEqual(f1, f2)

    def test_diff_opening_only_are_not_equal(self):
        f1 = Format(SequenceSGR(sgr.GREEN))
        f2 = Format(SequenceSGR(sgr.BLUE))

        self.assertNotEqual(f1, f2)

    def test_format_is_not_equal_to_sgr(self):
        f1 = Format(SequenceSGR(sgr.BOLD))

        self.assertNotEqual(f1, SequenceSGR(sgr.BOLD))

    def test_empty_are_equal(self):
        f1 = Format(SequenceSGR())
        f2 = Format(SequenceSGR())

        self.assertEqual(f1, f2)

    def test_empty_is_not_equal_to_reset(self):
        f1 = Format(SequenceSGR())
        f2 = Format(SequenceSGR(0))

        self.assertNotEqual(f1, f2)


class FormatWrapTestCase(unittest.TestCase):
    pass  # @todo


class AutoFormatTestCase(unittest.TestCase):
    def test_autof_single_sgr(self):
        f = autof(seq.BOLD)

        self.assertEqual(f.opening_seq, SequenceSGR(sgr.BOLD))
        self.assertEqual(f.closing_seq, SequenceSGR(sgr.BOLD_DIM_OFF))

    def test_autof_multiple_sgr(self):
        f = autof(seq.UNDERLINED + seq.YELLOW + seq.BG_RED)

        self.assertEqual(f.opening_seq, SequenceSGR(sgr.UNDERLINED, sgr.YELLOW, sgr.BG_RED))
        self.assertEqual(f.closing_seq, SequenceSGR(sgr.UNDERLINED_OFF, sgr.COLOR_OFF, sgr.BG_COLOR_OFF))

    def test_autof_no_args(self):
        f = autof()

        self.assertEqual(f.opening_seq, SequenceSGR())
        self.assertEqual(f.closing_seq, SequenceSGR())

    def test_autof_empty_sgr(self):
        f = autof(SequenceSGR())

        self.assertEqual(f.opening_seq, SequenceSGR())
        self.assertEqual(f.closing_seq, SequenceSGR())

    def test_autof_multiple_with_empty_sgr(self):
        f = autof(seq.BOLD, SequenceSGR(), seq.RED)

        self.assertEqual(f.opening_seq, SequenceSGR(sgr.BOLD, sgr.RED))
        self.assertEqual(f.closing_seq, SequenceSGR(sgr.BOLD_DIM_OFF, sgr.COLOR_OFF))
