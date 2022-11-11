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
        self.assertEqual("0xFF00FF", ColorRGB(0xFF00FF).format_value())
        self.assertEqual("#FF00FF", ColorRGB(0xFF00FF).format_value("#"))

    def test_format_noop_color_value(self):
        self.assertEqual("NOP", NOOP_COLOR.format_value())
        self.assertEqual("NOP", NOOP_COLOR.format_value("#"))


class TestNameMap(unittest.TestCase):
    def test_resolving_of_ambiguous_color_works_upon_abstract_color(self):
        col = Color.resolve("green")
        self.assertEqual(col.hex_value, 0x008000)
        self.assertEqual(type(col), Color16)

    def test_resolving_of_ambiguous_color_works_upon_color_16(self):
        col = Color16.resolve("green")
        self.assertEqual(col.hex_value, 0x008000)
        self.assertEqual(type(col), Color16)

    def test_resolving_of_ambiguous_color_works_upon_color_256(self):
        col = Color256.resolve("green")
        self.assertEqual(col.hex_value, 0x008000)
        self.assertEqual(type(col), Color256)

    def test_resolving_of_ambiguous_color_works_upon_color_rgb(self):
        col = ColorRGB.resolve("green")
        self.assertEqual(col.hex_value, 0x1CAC78)
        self.assertEqual(type(col), ColorRGB)

    def test_registering_of_variation_works(self):
        col = ColorRGB(
            0x000001,
            "test 000001",
            variation_map={0x000002: "ii"},
            register=True,
            index=True,
        )

        self.assertEqual(len(col.variations), 1)
        vari = col.variations.get("ii")

        self.assertIs(vari.base, col)
        self.assertEqual(vari.name, "ii")
        self.assertIs(ColorRGB.find_closest(0x000003), vari)
        self.assertIs(ColorRGB.resolve("test_000001-ii"), vari)


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
