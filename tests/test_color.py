# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import logging
import unittest

import pytermor
from pytermor.common import LogicError

from pytermor import NOOP_SEQ, Style, SequenceSGR, IntCode, color
from pytermor.color import (
    NOOP_COLOR,
    Color16,
    Color256,
    ColorRGB,
    ColorNameConflictError,
    ColorCodeConflictError,
)


class TestStatic(unittest.TestCase):
    def test_hex_to_hsv_works(self):
        for input_idx, ((expected_output), input_num) in enumerate(
            [
                [(0, 0, 0.0), 0x000000],
                [(0, 0, 1.0), 0xFFFFFF],
                [(0, 1, 1.0), 0xFF0000],
                [(120, 1, 1.0), 0x00FF00],
                [(240, 1, 1.0), 0x0000FF],
                [(60, 1, 0.0), 0x010100],
                [(240, 1, 0.5), 0x000080],
                [(0, 0, 0), 0x1000000],
            ]
        ):
            subtest_msg = f'"#{input_num:06x}" -> "{expected_output}"'
            with self.subTest(msg=subtest_msg):
                actual_output = color.hex_to_hsv(input_num)
                logging.debug(subtest_msg + f' => "{actual_output}"')
                for idx in range(0, len(expected_output)):
                    self.assertAlmostEqual(
                        expected_output[idx], actual_output[idx], delta=0.01
                    )

    def test_hex_to_rgb_works(self):
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
                actual_output = color.hex_to_rgb(input_num)
                logging.debug(subtest_msg + f' => "{actual_output}"')
                self.assertEqual(expected_output, actual_output)

    def test_rgb_to_hex_works(self):
        for input_idx, ((expected_num), input_channels) in enumerate(
            [
                [0x000000, (0, 0, 0)],
                [0xFFFFFF, (255, 255, 255)],
                [0xFF0000, (255, 0, 0)],
                [0x00FF00, (0, 255, 0)],
                [0x0000FF, (0, 0, 255)],
                [0x010100, (1, 1, 0)],
                [0x000080, (0, 0, 128)],
            ]
        ):
            subtest_msg = f'"{input_channels}" -> "#{expected_num:06x}"'
            with self.subTest(msg=subtest_msg):
                actual_output = color.rgb_to_hex(*input_channels)
                logging.debug(subtest_msg + f' => "{actual_output}"')
                self.assertEqual(expected_num, actual_output)

    def test_hex_to_hsv_with_invalid_arg_fails(self):
        self.assertRaises(TypeError, color.hex_to_hsv, "1")

    def test_hex_to_rgb_with_invalid_arg_fails(self):
        self.assertRaises(TypeError, color.hex_to_rgb, "1")


class TestColorRegistry(unittest.TestCase):
    # @TODO the state of the registry better be reset before each one of those,
    #       but at the moment I don't see a fast and reliable way to achieve this

    def test_registering_works(self):
        map_length_start = len(ColorRGB._registry)
        col = ColorRGB(0x2, "test 2", register=True)

        self.assertEqual(map_length_start + 1, len(ColorRGB._registry))
        self.assertIs(col, color.resolve("test 2", ColorRGB))

    def test_registering_of_duplicate_doesnt_change_map_length(self):
        ColorRGB(0x3, "test 3", register=True)
        map_length_start = len(ColorRGB._registry)
        ColorRGB(0x3, "test 3", register=True)

        self.assertEqual(map_length_start, len(ColorRGB._registry))

    def test_registering_of_name_duplicate_fails(self):
        ColorRGB(0x4, "test 4", register=True)
        self.assertRaises(ColorNameConflictError, ColorRGB, 0x3, "test 4", register=True)

    def test_resolving_of_non_existing_color_fails(self):
        self.assertRaises(LookupError, color.resolve, "non-existing-color", Color256)

    def test_resolving_of_ambiguous_color_works_upon_abstract_color(self):
        col = color.resolve("green")
        self.assertEqual(col.hex_value, 0x008000)
        self.assertEqual(type(col), Color16)

    def test_resolving_of_ambiguous_color_works_upon_color_16(self):
        col = color.resolve("green", Color16)
        self.assertEqual(col.hex_value, 0x008000)
        self.assertEqual(type(col), Color16)

    def test_resolving_of_ambiguous_color_works_upon_color_256(self):
        col = color.resolve("green", Color256)
        self.assertEqual(col.hex_value, 0x008000)
        self.assertEqual(type(col), Color256)

    def test_resolving_of_ambiguous_color_works_upon_color_rgb(self):
        col = color.resolve("green", ColorRGB)
        self.assertEqual(col.hex_value, 0x1CAC78)
        self.assertEqual(type(col), ColorRGB)

    def test_registering_of_variation_works(self):
        col = ColorRGB(0x5, "test 5", variation_map={0x2: "2"}, register=True)

        self.assertEqual(len(col.variations), 1)
        vari = col.variations.get("2")

        self.assertIs(vari.base, col)
        self.assertEqual(vari.name, "2")
        self.assertIs(color.resolve("test 5 2", ColorRGB), vari)

    def test_creating_color_without_name_works(self):
        col = Color256(0x6, code=256, register=True)
        self.assertIsNone(col.name)


class TestColorIndex(unittest.TestCase):
    def test_adding_to_index_works(self):
        index_length_start = len(ColorRGB._index)
        col = ColorRGB(0x1, "test 1", index=True)

        self.assertEqual(index_length_start + 1, len(ColorRGB._index))
        self.assertIs(col, ColorRGB.find_closest(0x1))

    def test_adding_duplicate_to_index_doesnt_change_index_length(self):
        Color16(0x1, 131, 141, "test 1", index=True)
        index_length_start = len(Color16._index)
        Color16(0x1, 131, 141, "test 1", index=True)

        self.assertEqual(index_length_start, len(Color16._index))

    def test_adding_code_duplicate_to_index_fails(self):
        Color16(0x1, 131, 141, "test 1", index=True)
        self.assertRaises(
            ColorCodeConflictError, Color16, 0x2, 131, 141, "test 1", index=True
        )

    def test_getting_of_non_existing_color_fails(self):
        self.assertRaises(KeyError, Color256.get_by_code, 256)


class TestColor(unittest.TestCase):
    def test_module_method_resolve_works(self):
        col = ColorRGB(0x1, "test 1", register=True)
        self.assertIs(col, color.resolve("test-1"))

    def test_module_method_resolve_of_non_existing_color_fails(self):
        self.assertRaises(LookupError, color.resolve, "non-existing-color")

    def test_module_method_find_closest_works_as_256_by_default(self):
        self.assertIs(pytermor.cv.AQUAMARINE_1, color.find_closest(0x87FFD7))

    def test_module_method_find_closest_works_for_16(self):
        self.assertIs(pytermor.cv.WHITE, color.find_closest(0x87FFD7, Color16))

    def test_module_method_find_closest_works_for_rgb(self):
        self.assertIs(
            color.resolve("aquamarine", ColorRGB), color.find_closest(0x87FFD7, ColorRGB)
        )

    def test_module_method_approximate_works_as_256_by_default(self):
        self.assertIs(pytermor.cv.AQUAMARINE_1, color.approximate(0x87FFD7)[0].color)

    def test_module_method_approximate_works_for_16(self):
        self.assertIs(pytermor.cv.WHITE, color.approximate(0x87FFD7, Color16)[0].color)

    def test_module_method_approximate_works_for_rgb(self):
        self.assertIs(
            color.resolve("aquamarine", ColorRGB),
            color.approximate(0x87FFD7, ColorRGB)[0].color,
        )


class TestApproximation(unittest.TestCase):
    def test_find_closest_works_for_16(self):
        self.assertIs(pytermor.cv.WHITE, Color16.find_closest(0x87FFD7))

    def test_find_closest_works_for_256(self):
        self.assertIs(pytermor.cv.AQUAMARINE_1, Color256.find_closest(0x87FFD7))

    def test_find_closest_works_for_rgb(self):
        self.assertEqual(0x7FFFD4, ColorRGB.find_closest(0x87FFD7).hex_value)

    def test_approximate_works_for_16(self):
        self.assertIs(pytermor.cv.WHITE, Color16.approximate(0x87FFD7)[0].color)

    def test_approximate_works_for_256(self):
        self.assertIs(
            pytermor.cv.AQUAMARINE_1, Color256.approximate(0x87FFD7)[0].color
        )

    def test_approximate_works_for_rgb(self):
        self.assertEqual(0x7FFFD4, ColorRGB.approximate(0x87FFD7)[0].color.hex_value)


class TestColor16(unittest.TestCase):
    def test_get_code(self):
        col = Color16(0xF00000, IntCode.RED, IntCode.BG_RED)
        self.assertEqual(IntCode.RED, col.code_fg)
        self.assertEqual(IntCode.BG_RED, col.code_bg)

    def test_to_sgr_without_upper_bound_results_in_sgr_16(self):
        col = Color16(0x800000, IntCode.RED, IntCode.BG_RED)
        self.assertEqual(SequenceSGR(31), col.to_sgr(False))
        self.assertEqual(SequenceSGR(41), col.to_sgr(True))

    def test_to_sgr_with_rgb_upper_bound_results_in_sgr_16(self):
        col = Color16(0x800000, IntCode.RED, IntCode.BG_RED)
        self.assertEqual(SequenceSGR(31), col.to_sgr(False, upper_bound=ColorRGB))
        self.assertEqual(SequenceSGR(41), col.to_sgr(True, upper_bound=ColorRGB))

    def test_to_sgr_with_256_upper_bound_results_in_sgr_16(self):
        col = Color16(0x800000, IntCode.RED, IntCode.BG_RED)
        self.assertEqual(SequenceSGR(31), col.to_sgr(False, upper_bound=Color256))
        self.assertEqual(SequenceSGR(41), col.to_sgr(True, upper_bound=Color256))

    def test_to_sgr_with_16_upper_bound_results_in_sgr_16(self):
        col = Color16(0x800000, IntCode.RED, IntCode.BG_RED)
        self.assertEqual(SequenceSGR(31), col.to_sgr(False, upper_bound=Color16))
        self.assertEqual(SequenceSGR(41), col.to_sgr(True, upper_bound=Color16))

    def test_to_tmux(self):
        col = Color16(0xF00000, IntCode.RED, IntCode.BG_RED, "ultrared")
        self.assertEqual("ultrared", col.to_tmux(False))
        self.assertEqual("ultrared", col.to_tmux(True))

    def test_to_tmux_without_name_fails(self):
        col = Color16(0x800000, IntCode.RED, IntCode.BG_RED)
        self.assertRaises(LogicError, col.to_tmux, False)

    def test_format_value(self):
        self.assertEqual("0x800000", Color16(0x800000, 133, 143).format_value())
        self.assertEqual("#800000", Color16(0x800000, 134, 144).format_value("#"))

    def test_equality(self):
        self.assertTrue(Color16(0x010203, 11, 12) == Color16(0x010203, 11, 12))

    def test_not_equality(self):
        self.assertFalse(Color16(0x010203, 11, 12) == Color16(0xFFEEDD, 11, 12))
        self.assertFalse(Color16(0x010203, 11, 12) == Color16(0x010203, 12, 11))
        self.assertFalse(Color16(0x010203, 11, 12) == Color256(0x010203, 12))
        self.assertFalse(Color16(0x010203, 11, 12) == ColorRGB(0x010203))

    def test_to_hsv(self):
        col = Color16(0x800000, IntCode.RED, IntCode.BG_RED)
        h, s, v = col.to_hsv()
        self.assertAlmostEqual(0, h)
        self.assertAlmostEqual(1, s)
        self.assertAlmostEqual(0.50, v, delta=0.01)

    def test_to_rgb(self):
        col = Color16(0x800000, IntCode.RED, IntCode.BG_RED)
        r, g, b = col.to_rgb()
        self.assertEqual(128, r)
        self.assertEqual(0, g)
        self.assertEqual(0, b)


class TestColor256(unittest.TestCase):
    def test_get_code(self):
        col = Color256(0xF00000, 257)
        self.assertEqual(257, col.code)

    def test_to_sgr_without_upper_bound_results_in_sgr_256(self):
        col = Color256(0xFFCC01, 1)
        self.assertEqual(SequenceSGR(38, 5, 1), col.to_sgr(False))
        self.assertEqual(SequenceSGR(48, 5, 1), col.to_sgr(True))

    def test_to_sgr_with_rgb_upper_bound_results_in_sgr_256(self):
        col = Color256(0xFFCC01, 1)
        expected_sgr_fg = SequenceSGR(38, 2, 255, 204, 1)
        expected_sgr_bg = SequenceSGR(48, 2, 255, 204, 1)
        self.assertEqual(expected_sgr_fg, col.to_sgr(False, upper_bound=ColorRGB))
        self.assertEqual(expected_sgr_bg, col.to_sgr(True, upper_bound=ColorRGB))

    def test_to_sgr_with_256_upper_bound_results_in_sgr_256(self):
        col = Color256(0xFFCC01, 1)
        self.assertEqual(SequenceSGR(38, 5, 1), col.to_sgr(False, upper_bound=Color256))
        self.assertEqual(SequenceSGR(48, 5, 1), col.to_sgr(True, upper_bound=Color256))

    def test_to_sgr_with_16_upper_bound_results_in_sgr_16(self):
        col = Color256(0xFFCC01, 1)
        self.assertEqual(SequenceSGR(93), col.to_sgr(False, upper_bound=Color16))
        self.assertEqual(SequenceSGR(103), col.to_sgr(True, upper_bound=Color16))

    def test_to_sgr_with_16_upper_bound_results_in_sgr_16_equiv(self):
        col16 = Color16(0xFFCC00, 132, 142, index=True)
        col = Color256(0xFFCC01, 1, color16_equiv=col16)
        self.assertEqual(col16.to_sgr(False), col.to_sgr(False, upper_bound=Color16))
        self.assertEqual(col16.to_sgr(True), col.to_sgr(True, upper_bound=Color16))

    def test_to_tmux(self):
        col = Color256(0xFF00FF, 258)
        self.assertEqual("colour258", col.to_tmux(False))
        self.assertEqual("colour258", col.to_tmux(True))

    def test_format_value(self):
        self.assertEqual("0xFF00FF", Color256(0xFF00FF, 259).format_value())
        self.assertEqual("#FF00FF", Color256(0xFF00FF, 260).format_value("#"))

    def test_equality(self):
        self.assertTrue(Color256(0x010203, 11) == Color256(0x010203, 11))

    def test_not_equality(self):
        self.assertFalse(Color256(0x010203, 11) == Color256(0x010203, 12))
        self.assertFalse(Color256(0x010203, 11) == Color256(0x030201, 11))
        self.assertFalse(Color256(0x010203, 11) == Color256(0xFFEE14, 88))
        self.assertFalse(Color256(0x010203, 11) == Color16(0x010203, 11, 11))
        self.assertFalse(Color256(0x010203, 11) == ColorRGB(0x010203))

    def test_to_hsv(self):
        col = Color256(0x808000, code=256)
        h, s, v = col.to_hsv()
        self.assertAlmostEqual(60, h)
        self.assertAlmostEqual(1, s)
        self.assertAlmostEqual(0.50, v, delta=0.01)

    def test_to_rgb(self):
        col = Color256(0x808000, code=256)
        r, g, b = col.to_rgb()
        self.assertEqual(128, r)
        self.assertEqual(128, g)
        self.assertEqual(0, b)


class TestColorRGB(unittest.TestCase):
    def test_to_sgr_without_upper_bound_results_in_sgr_rgb(self):
        col = ColorRGB(0xFF33FF)
        self.assertEqual(SequenceSGR(38, 2, 255, 51, 255), col.to_sgr(False))
        self.assertEqual(SequenceSGR(48, 2, 255, 51, 255), col.to_sgr(True))

    def test_to_sgr_with_rgb_upper_bound_results_in_sgr_rgb(self):
        col = ColorRGB(0xFF33FF)
        expected_sgr_fg = SequenceSGR(38, 2, 255, 51, 255)
        expected_sgr_bg = SequenceSGR(48, 2, 255, 51, 255)
        self.assertEqual(expected_sgr_fg, col.to_sgr(False, upper_bound=ColorRGB))
        self.assertEqual(expected_sgr_bg, col.to_sgr(True, upper_bound=ColorRGB))

    def test_to_sgr_with_256_upper_bound_results_in_sgr_256(self):
        col = ColorRGB(0xFF33FF)
        self.assertEqual(
            SequenceSGR(38, 5, 207), col.to_sgr(False, upper_bound=Color256)
        )
        self.assertEqual(SequenceSGR(48, 5, 207), col.to_sgr(True, upper_bound=Color256))

    def test_to_sgr_with_16_upper_bound_results_in_sgr_16(self):
        col = ColorRGB(0xFF33FF)
        self.assertEqual(SequenceSGR(95), col.to_sgr(False, upper_bound=Color16))
        self.assertEqual(SequenceSGR(105), col.to_sgr(True, upper_bound=Color16))

    def test_to_tmux(self):
        col = ColorRGB(0xFF00FF)
        self.assertEqual("#FF00FF", col.to_tmux(False))
        self.assertEqual("#FF00FF", col.to_tmux(True))

    def test_format_value(self):
        self.assertEqual("0xFF00FF", ColorRGB(0xFF00FF).format_value())
        self.assertEqual("#FF00FF", ColorRGB(0xFF00FF).format_value("#"))

    def test_equality(self):
        self.assertTrue(ColorRGB(0x010203) == ColorRGB(0x010203))

    def test_not_equality(self):
        self.assertFalse(ColorRGB(0x010203) == ColorRGB(0x030201))
        self.assertFalse(ColorRGB(0x010203) == Color256(0x010203, 1))
        self.assertFalse(
            ColorRGB(0x010203) == Color16(0x556677, IntCode.WHITE, IntCode.BG_WHITE)
        )

    def test_to_hsv(self):
        col = ColorRGB(0x008000)
        h, s, v = col.to_hsv()
        self.assertAlmostEqual(120, h)
        self.assertAlmostEqual(1, s)
        self.assertAlmostEqual(0.50, v, delta=0.01)

    def test_to_rgb(self):
        col = ColorRGB(0x008000)
        r, g, b = col.to_rgb()
        self.assertEqual(0, r)
        self.assertEqual(128, g)
        self.assertEqual(0, b)


class TestNoopColor(unittest.TestCase):
    def test_noop(self):
        self.assertEqual(NOOP_SEQ, NOOP_COLOR.to_sgr(True, Color16))
        self.assertEqual(NOOP_SEQ, NOOP_COLOR.to_sgr(False, ColorRGB))
        self.assertEqual(NOOP_COLOR, Style().fg)
        self.assertEqual(NOOP_COLOR, Style().bg)

    def test_format_noop_color_value(self):
        self.assertEqual("NOP", NOOP_COLOR.format_value())
        self.assertEqual("NOP", NOOP_COLOR.format_value("#"))

    def test_to_tmux(self):
        self.assertEqual("", NOOP_COLOR.to_tmux(False))
        self.assertEqual("", NOOP_COLOR.to_tmux(True))

    def test_getting_hex_value_fails(self):
        self.assertRaises(LogicError, lambda: NOOP_COLOR.hex_value)
