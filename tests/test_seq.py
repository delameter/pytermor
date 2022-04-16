import unittest

from pytermor import seq, code, build, build_c256
from pytermor.seq import EmptySequenceSGR, SequenceSGR


class SequenceEqualityTestCase(unittest.TestCase):
    def test_regular_is_equal_to_regular(self):
        self.assertEqual(SequenceSGR(1, 31, 42),
                         SequenceSGR(1, 31, 42))

    def test_empty_is_equal_to_empty(self):
        self.assertEqual(EmptySequenceSGR(),
                         EmptySequenceSGR())

    def test_regular_is_not_equal_to_regular(self):
        self.assertNotEqual(SequenceSGR(2, 31, 42),
                            SequenceSGR(1, 31, 42))

    def test_empty_is_not_equal_to_regular(self):
        self.assertNotEqual(EmptySequenceSGR(),
                            SequenceSGR(1))


class SequenceAdditionTestCase(unittest.TestCase):
    def test_addition_of_regular_to_regular(self):
        self.assertEqual(SequenceSGR(1) + SequenceSGR(3), SequenceSGR(1, 3))

    def test_addition_of_regular_to_empty(self):
        self.assertEqual(SequenceSGR(41) + EmptySequenceSGR(), SequenceSGR(41))

    def test_addition_of_empty_to_regular(self):
        self.assertEqual(EmptySequenceSGR() + SequenceSGR(44), SequenceSGR(44))

    def test_addition_of_empty_to_empty(self):
        self.assertEqual(EmptySequenceSGR() + EmptySequenceSGR(), EmptySequenceSGR())


class SequenceBuildTestCase(unittest.TestCase):  # @todo negative
    def test_build_code_args(self):
        s = build(1, 31, 43)
        self.assertEqual(s, SequenceSGR(code.BOLD, code.RED, code.BG_YELLOW))

    def test_build_key_args(self):
        s = build('underlined', 'blue', 'bg_black')
        self.assertEqual(s, SequenceSGR(code.UNDERLINED, code.BLUE, code.BG_BLACK))

    def test_build_sgr_args(self):
        s = build(seq.HI_CYAN, seq.ITALIC)
        self.assertEqual(s, SequenceSGR(code.HI_CYAN, code.ITALIC))

    def test_build_mixed_args(self):
        s = build(102, 'bold', seq.INVERSED)
        self.assertEqual(s, SequenceSGR(code.BG_HI_GREEN, code.BOLD, code.INVERSED))

    def test_build_empty_arg(self):
        s = build(EmptySequenceSGR())
        self.assertEqual(s, EmptySequenceSGR())

    def test_build_mixed_with_empty_arg(self):
        s = build(3, EmptySequenceSGR())
        self.assertEqual(s, SequenceSGR(code.ITALIC))

    def test_build_c256_foreground(self):
        s = build_c256(141)
        self.assertEqual(s, SequenceSGR(code.COLOR_EXTENDED, code.EXTENDED_MODE_256, 141))

    def test_build_c256_background(self):
        s = build_c256(255, bg=True)
        self.assertEqual(s, SequenceSGR(code.BG_COLOR_EXTENDED, code.EXTENDED_MODE_256, 255))

    def test_build_c256_invalid(self):
        self.assertRaises(ValueError, build_c256, 266, bg=True)

    # @todo rgb

