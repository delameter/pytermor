# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import unittest

from pytermor import seq, sgr, build, build_c256, build_rgb, SequenceSGR


class TestEquality(unittest.TestCase):
    def test_regular_is_equal_to_regular(self):
        self.assertEqual(SequenceSGR(1, 31, 42), SequenceSGR(1, 31, 42))

    def test_empty_is_equal_to_empty(self):
        self.assertEqual(SequenceSGR(), SequenceSGR())

    def test_regular_is_not_equal_to_regular(self):
        self.assertNotEqual(SequenceSGR(2, 31, 42), SequenceSGR(1, 31, 42))

    def test_empty_is_not_equal_to_regular(self):
        self.assertNotEqual(SequenceSGR(), SequenceSGR(1))

    def test_empty_is_not_equal_to_reset(self):
        self.assertNotEqual(SequenceSGR(), SequenceSGR(0))

    def test_reset_is_not_equal_to_empty(self):
        self.assertNotEqual(SequenceSGR(), SequenceSGR(0))


class TestAddition(unittest.TestCase):
    def test_addition_of_regular_to_regular(self):
        self.assertEqual(SequenceSGR(1) + SequenceSGR(3), SequenceSGR(1, 3))

    def test_addition_of_regular_to_empty(self):
        self.assertEqual(SequenceSGR(41) + SequenceSGR(), SequenceSGR(41))

    def test_addition_of_empty_to_regular(self):
        self.assertEqual(SequenceSGR() + SequenceSGR(44), SequenceSGR(44))

    def test_addition_of_empty_to_empty(self):
        self.assertEqual(SequenceSGR() + SequenceSGR(), SequenceSGR())

    def test_addition_of_empty_to_reset(self):
        self.assertEqual(SequenceSGR() + SequenceSGR(0), SequenceSGR(0))

    def test_addition_of_reset_to_empty(self):
        self.assertEqual(SequenceSGR(0) + SequenceSGR(), SequenceSGR(0))

    def test_invalid_type_addition(self):
        self.assertRaises(TypeError, lambda: SequenceSGR(1) + 2)


class TestBuild(unittest.TestCase):
    def test_build_code_args(self):
        s = build(1, 31, 43)
        self.assertEqual(s, SequenceSGR(sgr.BOLD, sgr.RED, sgr.BG_YELLOW))

    def test_build_key_args(self):
        s = build('underlined', 'blue', 'bg_black')
        self.assertEqual(s, SequenceSGR(sgr.UNDERLINED, sgr.BLUE, sgr.BG_BLACK))

    def test_build_key_args_invalid(self):
        self.assertRaises(KeyError, build, 'invalid')

    def test_build_sgr_args(self):
        s = build(seq.HI_CYAN, seq.ITALIC)
        self.assertEqual(s, SequenceSGR(sgr.HI_CYAN, sgr.ITALIC))

    def test_build_mixed_args(self):
        s = build(102, 'bold', seq.INVERSED)
        self.assertEqual(s, SequenceSGR(sgr.BG_HI_GREEN, sgr.BOLD, sgr.INVERSED))

    def test_build_mixed_args_invalid(self):
        self.assertRaises(KeyError, build, 1, 'red', '')

    def test_build_empty_arg(self):
        s = build(SequenceSGR())
        self.assertEqual(s, SequenceSGR())

    def test_build_mixed_with_empty_arg(self):
        s = build(3, SequenceSGR())
        self.assertEqual(s, SequenceSGR(sgr.ITALIC))

    def test_build_c256_foreground(self):
        s = build_c256(141)
        self.assertEqual(s, SequenceSGR(sgr.COLOR_EXTENDED, sgr.EXTENDED_MODE_256, 141))

    def test_build_c256_background(self):
        s = build_c256(255, bg=True)
        self.assertEqual(s, SequenceSGR(sgr.BG_COLOR_EXTENDED, sgr.EXTENDED_MODE_256, 255))

    def test_build_c256_invalid(self):
        self.assertRaises(ValueError, build_c256, 266, bg=True)

    def test_build_rgb_foreground(self):
        s = build_rgb(10, 20, 30)
        self.assertEqual(s, SequenceSGR(sgr.COLOR_EXTENDED, sgr.EXTENDED_MODE_RGB, 10, 20, 30))

    def test_build_rgb_background(self):
        s = build_rgb(50, 70, 90, bg=True)
        self.assertEqual(s, SequenceSGR(sgr.BG_COLOR_EXTENDED, sgr.EXTENDED_MODE_RGB, 50, 70, 90))

    def test_build_rgb_invalid(self):
        self.assertRaises(ValueError, build_rgb, 10, 310, 30)
        self.assertRaises(ValueError, build_rgb, 310, 10, 130)
        self.assertRaises(ValueError, build_rgb, 0, 0, 256, bg=True)
