# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import unittest

from pytermor import sequence, intcode, build, color_indexed, color_rgb, SequenceSGR


class TestEquality(unittest.TestCase):
    def test_regular_is_equal_to_regular(self):
        self.assertEqual(SequenceSGR(1, 31, 42), SequenceSGR(1, 31, 42))

    def test_empty_is_equal_to_empty(self):
        self.assertEqual(sequence.NOOP, SequenceSGR())

    def test_regular_is_not_equal_to_regular(self):
        self.assertNotEqual(SequenceSGR(2, 31, 42), SequenceSGR(1, 31, 42))

    def test_empty_is_not_equal_to_regular(self):
        self.assertNotEqual(SequenceSGR(), SequenceSGR(1))

    def test_empty_is_not_equal_to_reset(self):
        self.assertNotEqual(SequenceSGR(), SequenceSGR(0))

    def test_reset_is_not_equal_to_empty(self):
        self.assertNotEqual(sequence.NOOP, SequenceSGR(0))


class TestAddition(unittest.TestCase):
    def test_addition_of_regular_to_regular(self):
        self.assertEqual(SequenceSGR(1) + SequenceSGR(3), SequenceSGR(1, 3))

    def test_addition_of_regular_to_empty(self):
        self.assertEqual(SequenceSGR(41) + sequence.NOOP, SequenceSGR(41))

    def test_addition_of_empty_to_regular(self):
        self.assertEqual(SequenceSGR() + SequenceSGR(44), SequenceSGR(44))

    def test_addition_of_empty_to_empty(self):
        self.assertEqual(SequenceSGR() + sequence.NOOP, SequenceSGR())

    def test_addition_of_empty_to_reset(self):
        self.assertEqual(SequenceSGR() + SequenceSGR(0), SequenceSGR(0))

    def test_addition_of_reset_to_empty(self):
        self.assertEqual(SequenceSGR(0) + SequenceSGR(), SequenceSGR(0))

    def test_invalid_type_addition(self):
        # noinspection PyTypeChecker
        self.assertRaises(TypeError, lambda: SequenceSGR(1) + 2)


class TestBuild(unittest.TestCase):
    def test_build_code_args(self):
        s = build(1, 31, 43)
        self.assertEqual(s, SequenceSGR(intcode.BOLD, intcode.RED, intcode.BG_YELLOW))

    def test_build_key_args(self):
        s = build('underlined', 'blue', 'bg_black')
        self.assertEqual(s, SequenceSGR(intcode.UNDERLINED, intcode.BLUE, intcode.BG_BLACK))

    def test_build_key_args_invalid(self):
        self.assertRaises(KeyError, build, 'invalid')

    def test_build_sgr_args(self):
        s = build(sequence.HI_CYAN, sequence.ITALIC)
        self.assertEqual(s, SequenceSGR(intcode.HI_CYAN, intcode.ITALIC))

    def test_build_mixed_args(self):
        s = build(102, 'bold', sequence.INVERSED)
        self.assertEqual(s, SequenceSGR(intcode.BG_HI_GREEN, intcode.BOLD, intcode.INVERSED))

    def test_build_mixed_args_invalid(self):
        self.assertRaises(KeyError, build, 1, 'red', '')

    def test_build_empty_arg(self):
        s = build(SequenceSGR())
        self.assertEqual(s, sequence.NOOP)

    def test_build_mixed_with_empty_arg(self):
        s = build(3, SequenceSGR())
        self.assertEqual(s, SequenceSGR(intcode.ITALIC))

    def test_color_indexed_foreground(self):
        s = color_indexed(141)
        self.assertEqual(s, SequenceSGR(intcode.COLOR_EXTENDED, intcode.EXTENDED_MODE_256, 141))

    def test_color_indexed_background(self):
        s = color_indexed(255, bg=True)
        self.assertEqual(s, SequenceSGR(intcode.BG_COLOR_EXTENDED, intcode.EXTENDED_MODE_256, 255))

    def test_color_indexed_invalid(self):
        self.assertRaises(ValueError, color_indexed, 266, bg=True)

    def test_color_rgb_foreground(self):
        s = color_rgb(10, 20, 30)
        self.assertEqual(s, SequenceSGR(intcode.COLOR_EXTENDED, intcode.EXTENDED_MODE_RGB, 10, 20, 30))

    def test_color_rgb_background(self):
        s = color_rgb(50, 70, 90, bg=True)
        self.assertEqual(s, SequenceSGR(intcode.BG_COLOR_EXTENDED, intcode.EXTENDED_MODE_RGB, 50, 70, 90))

    def test_color_rgb_invalid(self):
        self.assertRaises(ValueError, color_rgb, 10, 310, 30)
        self.assertRaises(ValueError, color_rgb, 310, 10, 130)
        self.assertRaises(ValueError, color_rgb, 0, 0, 256, bg=True)
