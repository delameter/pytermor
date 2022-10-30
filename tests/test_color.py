# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import logging
import unittest

import pytermor as pt
import pytermor.color as col


class TestStatic(unittest.TestCase):
    def test_hex_value_to_rgb_channels(self):
        for input_idx, ((expected_output), input_num) in enumerate([
            [(0, 0, 0), 0x000000],
            [(255, 255, 255), 0xffffff],
            [(255, 0, 0), 0xff0000],
            [(0, 255, 0), 0x00ff00],
            [(0, 0, 255), 0x0000ff],
            [(1, 1, 0), 0x010100],
            [(0, 0, 128), 0x000080],
            [(0, 0, 0), 0x1000000],
        ]):
            subtest_msg = f'"#{input_num:06x}" -> "{expected_output}"'
            with self.subTest(msg=subtest_msg):
                actual_output = col.hex_value_to_rgb_channels(input_num)
                logging.debug(subtest_msg + f' => "{actual_output}"')
                self.assertEqual(expected_output, actual_output)

    def test_noop(self):
        self.assertEqual(pt.NOOP_SEQ, col.NOOP_COLOR.to_sgr(False, True, False))
        self.assertEqual(pt.NOOP_SEQ, col.NOOP_COLOR.to_sgr(True, True, False))

    def test_format_value(self):
        self.assertEqual('0xff00ff', col.ColorRGB(0xff00ff).format_value())
        self.assertEqual('#ff00ff', col.ColorRGB(0xff00ff).format_value('#'))

    def test_format_noop_color_value(self):
        self.assertEqual('~', col.NOOP_COLOR.format_value())
        self.assertEqual('~', col.NOOP_COLOR.format_value('#'))


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
        self.assertEqual(pt.SequenceSGR(31),
                         col.ColorIndexed16(0x800000, pt.IntCode.RED, pt.IntCode.BG_RED).to_sgr(False))
        self.assertEqual(pt.SequenceSGR(41),
                         col.ColorIndexed16(0x800000, pt.IntCode.RED, pt.IntCode.BG_RED).to_sgr(True))

    def test_equality(self):
        self.assertTrue(
            col.ColorIndexed16(0x010203, 11, 12) == col.ColorIndexed16(0x010203, 11, 12))

    def test_not_equality(self):
        self.assertFalse(
            col.ColorIndexed16(0x010203, 11, 12) == col.ColorIndexed16(0xffeedd, 11, 12))
        self.assertFalse(
            col.ColorIndexed16(0x010203, 11, 12) == col.ColorIndexed16(0x010203, 12, 11))
        self.assertFalse(col.ColorIndexed16(0x010203, 11, 12) == col.ColorIndexed256(0x010203, 12))
        self.assertFalse(col.ColorIndexed16(0x010203, 11, 12) == col.ColorRGB(0x010203))


class TestColorIndexed(unittest.TestCase):
    def test_to_sgr(self):
        self.assertEqual(pt.SequenceSGR(38, 5, 1), col.ColorIndexed256(0xffcc01, 1).to_sgr(False))
        self.assertEqual(pt.SequenceSGR(48, 5, 1), col.ColorIndexed256(0xffcc01, 1).to_sgr(True))

    def test_equality(self):
        self.assertTrue(col.ColorIndexed256(0x010203, 11) == col.ColorIndexed256(0x010203, 11))

    def test_not_equality(self):
        self.assertFalse(col.ColorIndexed256(0x010203, 11) == col.ColorIndexed256(0x010203, 12))
        self.assertFalse(col.ColorIndexed256(0x010203, 11) == col.ColorIndexed256(0x030201, 11))
        self.assertFalse(col.ColorIndexed256(0x010203, 11) == col.ColorIndexed256(0xffee14, 88))
        self.assertFalse(col.ColorIndexed256(0x010203, 11) == col.ColorIndexed16(0x010203, 11, 11))
        self.assertFalse(col.ColorIndexed256(0x010203, 11) == col.ColorRGB(0x010203))


class TestColorRGB(unittest.TestCase):
    def test_to_sgr(self):
        self.assertEqual(pt.SequenceSGR(38, 2, 255, 51, 255),
                         col.ColorRGB(0xff33ff).to_sgr(False, allow_rgb=True))
        self.assertEqual(pt.SequenceSGR(48, 2, 255, 51, 153),
                         col.ColorRGB(0xff3399).to_sgr(True, allow_rgb=True))

    def test_equality(self):
        self.assertTrue(col.ColorRGB(0x010203) == col.ColorRGB(0x010203))

    def test_not_equality(self):
        self.assertFalse(col.ColorRGB(0x010203) == col.ColorRGB(0x030201))
        self.assertFalse(col.ColorRGB(0x010203) == col.ColorIndexed256(0x010203, 1))
        self.assertFalse(col.ColorRGB(0x010203) ==
                         col.ColorIndexed16(0x556677, pt.IntCode.WHITE, pt.IntCode.BG_WHITE))
