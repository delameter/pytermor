# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import logging
import unittest

from pytermor.ansi import (
    SequenceSGR,
    NOOP_SEQ,
    SeqIndex,
    IntCode,
    _sgr_pairity_registry,
    make_color_rgb,
    make_color_256, make_erase_in_line, make_hyperlink_part, assemble_hyperlink,
)


class TestSequenceSGR(unittest.TestCase):
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

    def test_build_code_args(self):
        s = SequenceSGR(1, 31, 43)
        self.assertEqual(s, SequenceSGR(IntCode.BOLD, IntCode.RED, IntCode.BG_YELLOW))

    def test_build_key_args_invalid(self):
        self.assertRaises(KeyError, SequenceSGR, "invalid")

    def test_build_sgr_args(self):
        s = SequenceSGR(SeqIndex.HI_CYAN, SeqIndex.ITALIC)
        self.assertEqual(s, SequenceSGR(IntCode.HI_CYAN, IntCode.ITALIC))

    def test_build_mixed_args(self):
        s = SequenceSGR(102, SequenceSGR(SeqIndex.BOLD), SeqIndex.INVERSED)
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

    def test_make_color_256_foreground(self):
        s1 = make_color_256(141)
        s2 = SequenceSGR(IntCode.COLOR_EXTENDED, IntCode.EXTENDED_MODE_256, 141)
        self.assertEqual(s1, s2)

    def test_make_color_256_background(self):
        s1 = make_color_256(255, bg=True)
        s2 = SequenceSGR(IntCode.BG_COLOR_EXTENDED, IntCode.EXTENDED_MODE_256, 255)
        self.assertEqual(s1, s2)

    def test_make_color_256_invalid(self):
        self.assertRaises(ValueError, make_color_256, 266, bg=True)

    def test_make_color_rgb_foreground(self):
        s1 = make_color_rgb(10, 20, 30)
        s2 = SequenceSGR(IntCode.COLOR_EXTENDED, IntCode.EXTENDED_MODE_RGB, 10, 20, 30)
        self.assertEqual(s1, s2)

    def test_make_color_rgb_background(self):
        s1 = make_color_rgb(50, 70, 90, bg=True)
        s2 = SequenceSGR(
            IntCode.BG_COLOR_EXTENDED, IntCode.EXTENDED_MODE_RGB, 50, 70, 90
        )
        self.assertEqual(s1, s2)

    def test_make_color_rgb_invalid(self):
        self.assertRaises(ValueError, make_color_rgb, 10, 310, 30)
        self.assertRaises(ValueError, make_color_rgb, 310, 10, 130)
        self.assertRaises(ValueError, make_color_rgb, 0, 0, 256, bg=True)


class TestSequenceCSI(unittest.TestCase):
    def test_make_erase_in_line(self):
        s = make_erase_in_line()


class TestSequenceOSC(unittest.TestCase):
    def test_make_hyperlink_part(self):
        s = make_hyperlink_part('http://example.test')
        self.assertIn('http://example.test', s.assemble())

    def test_assemble_hyperlink(self):
        s = assemble_hyperlink('http://example.test', 'label')
        self.assertIn('http://example.test', s)
        self.assertIn('label', s)


class TestSgrRegistry(unittest.TestCase):
    def test_closing_seq(self):
        for opening_seq, expected_closing_seq in [
            (NOOP_SEQ, NOOP_SEQ),
            (SeqIndex.WHITE, SeqIndex.COLOR_OFF),
            (SeqIndex.BG_HI_GREEN, SeqIndex.BG_COLOR_OFF),
            (SeqIndex.UNDERLINED, SeqIndex.UNDERLINED_OFF),
            (SeqIndex.BOLD + SeqIndex.RED, SeqIndex.BOLD_DIM_OFF + SeqIndex.COLOR_OFF),
            (SeqIndex.DIM, SeqIndex.BOLD_DIM_OFF),
            (make_color_256(128, False), SeqIndex.COLOR_OFF),
            (make_color_256(128, True), SeqIndex.BG_COLOR_OFF),
            (make_color_rgb(128, 0, 128, False), SeqIndex.COLOR_OFF),
            (make_color_rgb(128, 0, 128, True), SeqIndex.BG_COLOR_OFF),
            (make_erase_in_line(), NOOP_SEQ),
        ]:
            subtest_msg = f'"{opening_seq}" -> "{expected_closing_seq}"'
            with self.subTest(msg=subtest_msg, opening_seq=opening_seq):
                actual_output = _sgr_pairity_registry.get_closing_seq(opening_seq)
                logging.debug(subtest_msg + f' => "{actual_output}"')
                self.assertEqual(
                    expected_closing_seq,
                    _sgr_pairity_registry.get_closing_seq(opening_seq),
                )
