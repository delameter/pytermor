import unittest

from pytermor import autof, seq, sgr
from pytermor.seq import SequenceSGR


class FormatEqualityTestCase(unittest.TestCase):
    pass  # @todo


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

    def test_autof_empty_sgr(self):
        f = autof(SequenceSGR())

        self.assertEqual(f.opening_seq, SequenceSGR())
        self.assertEqual(f.closing_seq, SequenceSGR())

    def test_autof_multiple_with_empty_sgr(self):
        f = autof(seq.BOLD, SequenceSGR(), seq.RED)

        self.assertEqual(f.opening_seq, SequenceSGR(sgr.BOLD, sgr.RED))
        self.assertEqual(f.closing_seq, SequenceSGR(sgr.BOLD_DIM_OFF, sgr.COLOR_OFF))
