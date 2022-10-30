# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import unittest

from pytermor.ansi import SequenceSGR, NOOP_SEQ, Seqs, IntCode, sgr_pairity_registry


class TestEquality(unittest.TestCase):
    def test_regular_is_equal_to_regular(self):
        self.assertEqual(SequenceSGR(1, 31, 42), SequenceSGR(1, 31, 42))

    def test_empty_is_equal_to_empty(self):
        self.assertEqual(NOOP_SEQ, SequenceSGR())

    def test_regular_is_not_equal_to_regular(self):
        self.assertNotEqual(SequenceSGR(2, 31, 42), SequenceSGR(1, 31, 42))

    def test_empty_is_not_equal_to_regular(self):
        self.assertNotEqual(SequenceSGR(), SequenceSGR(1))

    def test_empty_is_not_equal_to_reset(self):
        self.assertNotEqual(SequenceSGR(), SequenceSGR(0))

    def test_reset_is_not_equal_to_empty(self):
        self.assertNotEqual(NOOP_SEQ, SequenceSGR(0))


class TestAddition(unittest.TestCase):
    def test_addition_of_regular_to_regular(self):
        self.assertEqual(SequenceSGR(1) + SequenceSGR(3), SequenceSGR(1, 3))

    def test_addition_of_regular_to_empty(self):
        self.assertEqual(SequenceSGR(41) + NOOP_SEQ, SequenceSGR(41))

    def test_addition_of_empty_to_regular(self):
        self.assertEqual(SequenceSGR() + SequenceSGR(44), SequenceSGR(44))

    def test_addition_of_empty_to_empty(self):
        self.assertEqual(SequenceSGR() + NOOP_SEQ, SequenceSGR())

    def test_addition_of_empty_to_reset(self):
        self.assertEqual(SequenceSGR() + SequenceSGR(0), SequenceSGR(0))

    def test_addition_of_reset_to_empty(self):
        self.assertEqual(SequenceSGR(0) + SequenceSGR(), SequenceSGR(0))

    def test_invalid_type_addition(self):
        # noinspection PyTypeChecker
        self.assertRaises(TypeError, lambda: SequenceSGR(1) + 2)


class TestBuild(unittest.TestCase):
    def test_build_code_args(self):
        s = SequenceSGR(1, 31, 43)
        self.assertEqual(s, SequenceSGR(IntCode.BOLD, IntCode.RED, IntCode.BG_YELLOW))

    def test_build_key_args_invalid(self):
        self.assertRaises(KeyError, SequenceSGR, "invalid")

    def test_build_sgr_args(self):
        s = SequenceSGR(Seqs.HI_CYAN, Seqs.ITALIC)
        self.assertEqual(s, SequenceSGR(IntCode.HI_CYAN, IntCode.ITALIC))

    def test_build_mixed_args(self):
        s = SequenceSGR(102, SequenceSGR(Seqs.BOLD), Seqs.INVERSED)
        self.assertEqual(
            s, SequenceSGR(IntCode.BG_HI_GREEN, IntCode.BOLD, IntCode.INVERSED)
        )

    def test_build_mixed_args_invalid(self):
        self.assertRaises(KeyError, SequenceSGR, 1, "red", "")

    def test_build_empty_arg(self):
        s = SequenceSGR(SequenceSGR())
        self.assertEqual(s, NOOP_SEQ)

    def test_build_mixed_with_empty_arg(self):
        s = SequenceSGR(3, SequenceSGR())
        self.assertEqual(s, SequenceSGR(IntCode.ITALIC))

    def test_color_indexed_foreground(self):
        s = SequenceSGR.init_color_index256(141)
        self.assertEqual(
            s, SequenceSGR(IntCode.COLOR_EXTENDED, IntCode.EXTENDED_MODE_256, 141)
        )

    def test_color_indexed_background(self):
        s = SequenceSGR.init_color_index256(255, bg=True)
        self.assertEqual(
            s, SequenceSGR(IntCode.BG_COLOR_EXTENDED, IntCode.EXTENDED_MODE_256, 255)
        )

    def test_color_indexed_invalid(self):
        self.assertRaises(ValueError, SequenceSGR.init_color_index256, 266, bg=True)

    def test_color_rgb_foreground(self):
        s = SequenceSGR.init_color_rgb(10, 20, 30)
        self.assertEqual(
            s,
            SequenceSGR(IntCode.COLOR_EXTENDED, IntCode.EXTENDED_MODE_RGB, 10, 20, 30),
        )

    def test_color_rgb_background(self):
        s = SequenceSGR.init_color_rgb(50, 70, 90, bg=True)
        self.assertEqual(
            s,
            SequenceSGR(
                IntCode.BG_COLOR_EXTENDED, IntCode.EXTENDED_MODE_RGB, 50, 70, 90
            ),
        )

    def test_color_rgb_invalid(self):
        self.assertRaises(ValueError, SequenceSGR.init_color_rgb, 10, 310, 30)
        self.assertRaises(ValueError, SequenceSGR.init_color_rgb, 310, 10, 130)
        self.assertRaises(ValueError, SequenceSGR.init_color_rgb, 0, 0, 256, bg=True)


class TestRegistry(unittest.TestCase):  # @TODO more
    def test_closing_seq(self):
        self.assertEqual(
            sgr_pairity_registry.get_closing_seq(Seqs.BOLD + Seqs.RED),
            Seqs.BOLD_DIM_OFF + Seqs.COLOR_OFF,
        )
