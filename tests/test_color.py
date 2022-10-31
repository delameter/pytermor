# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import logging
import unittest

from pytermor import NOOP_SEQ, Style, SequenceSGR, IntCode
from pytermor.color import NOOP_COLOR, Color, Color16, Color256, ColorRGB


class TestStatic(unittest.TestCase):
    def test_hex_value_to_rgb_channels(self):
        for input_idx, ((expected_output), input_num) in enumerate(
            [
                [(0, 0, 0), 0x000000],
                [(255, 255, 255), 0xFFFFFF],
                [(255, 0, 0), 0xFF0000],
                [(0, 255, 0), 0x00FF00],
                [(0, 0, 255), 0x0000FF],
                [(1, 1, 0), 0x010100],
                [(0, 0, 128), 0x000080],
                [(0, 0, 0), 0x1000000],
            ]
        ):
            subtest_msg = f'"#{input_num:06x}" -> "{expected_output}"'
            with self.subTest(msg=subtest_msg):
                actual_output = Color.hex_to_rgb(input_num)
            logging.debug(subtest_msg + f' => "{actual_output}"')
            self.assertEqual(expected_output, actual_output)

    def test_noop(self):
        self.assertEqual(NOOP_SEQ, NOOP_COLOR.to_sgr(True, Color16))
        self.assertEqual(NOOP_SEQ, NOOP_COLOR.to_sgr(False, ColorRGB))
        self.assertEqual(NOOP_COLOR, Style().fg)
        self.assertEqual(NOOP_COLOR, Style().bg)

    def test_format_value(self):
        self.assertEqual("0xff00ff", ColorRGB(0xFF00FF).format_value())
        self.assertEqual("#ff00ff", ColorRGB(0xFF00FF).format_value("#"))

    def test_format_noop_color_value(self):
        self.assertEqual("~", NOOP_COLOR.format_value())
        self.assertEqual("~", NOOP_COLOR.format_value("#"))


class TestColorMap(unittest.TestCase):
    def test_lookup_table_inits_on_real_color_creation(self):
        pass

    def test_lookup_table_ignores_duplicates(self):
        pass

    def test_find_closest_works(self):
        pass

    def test_cache_works(self):
        pass

    def test_search_returns_default_if_no_colors_registered(self):
        pass


class TestColorIndexed16(unittest.TestCase):
    def test_to_sgr(self):
        self.assertEqual(
            SequenceSGR(31), Color16(0x800000, IntCode.RED, IntCode.BG_RED).to_sgr(False)
        )
        self.assertEqual(
            SequenceSGR(41), Color16(0x800000, IntCode.RED, IntCode.BG_RED).to_sgr(True)
        )

    def test_equality(self):
        self.assertTrue(Color16(0x010203, 11, 12) == Color16(0x010203, 11, 12))

    def test_not_equality(self):
        self.assertFalse(Color16(0x010203, 11, 12) == Color16(0xFFEEDD, 11, 12))
        self.assertFalse(Color16(0x010203, 11, 12) == Color16(0x010203, 12, 11))
        self.assertFalse(Color16(0x010203, 11, 12) == Color256(0x010203, 12))
        self.assertFalse(Color16(0x010203, 11, 12) == ColorRGB(0x010203))


class TestColorIndexed256(unittest.TestCase):
    def test_to_sgr(self):
        self.assertEqual(SequenceSGR(38, 5, 1), Color256(0xFFCC01, 1).to_sgr(False))
        self.assertEqual(SequenceSGR(48, 5, 1), Color256(0xFFCC01, 1).to_sgr(True))

    def test_equality(self):
        self.assertTrue(Color256(0x010203, 11) == Color256(0x010203, 11))

    def test_not_equality(self):
        self.assertFalse(Color256(0x010203, 11) == Color256(0x010203, 12))
        self.assertFalse(Color256(0x010203, 11) == Color256(0x030201, 11))
        self.assertFalse(Color256(0x010203, 11) == Color256(0xFFEE14, 88))
        self.assertFalse(Color256(0x010203, 11) == Color16(0x010203, 11, 11))
        self.assertFalse(Color256(0x010203, 11) == ColorRGB(0x010203))


class TestColorRGB(unittest.TestCase):
    def test_to_sgr(self):
        self.assertEqual(
            SequenceSGR(38, 2, 255, 51, 255), ColorRGB(0xFF33FF).to_sgr(False)
        )
        self.assertEqual(
            SequenceSGR(48, 2, 255, 51, 153), ColorRGB(0xFF3399).to_sgr(True)
        )

    def test_equality(self):
        self.assertTrue(ColorRGB(0x010203) == ColorRGB(0x010203))

    def test_not_equality(self):
        self.assertFalse(ColorRGB(0x010203) == ColorRGB(0x030201))
        self.assertFalse(ColorRGB(0x010203) == Color256(0x010203, 1))
        self.assertFalse(
            ColorRGB(0x010203) == Color16(0x556677, IntCode.WHITE, IntCode.BG_WHITE)
        )
