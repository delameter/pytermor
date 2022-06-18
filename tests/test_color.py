# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import logging
import unittest

from pytermor.color import Color, ColorDefault, ColorIndexed, ColorRGB


class TestColor(unittest.TestCase):
    def test_hex_value_to_channels(self):
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
                actual_output = Color.hex_value_to_channels(input_num)
                logging.debug(subtest_msg + f' => "{actual_output}"')
                self.assertEquals(expected_output, actual_output)


class TestColorRGB(unittest.TestCase):
    def tearDown(self) -> None:
        ColorRGB._color_map._exact_color_map.clear()
        ColorRGB._color_map._approximate_cache.clear()

    def test_hex_color_map_init_on_filled_color_creation(self):
        expected = ColorRGB(0x000000)

        self.assertEquals(1, len(ColorRGB._color_map._exact_color_map))
        self.assertListEqual([expected], list(ColorRGB._color_map._exact_color_map.values()))

    def test_hex_color_map_init_on_empty_color_creation(self):
        ColorRGB()
        self.assertEquals(0, len(ColorRGB._color_map._exact_color_map))

    def test_hex_color_map_ignores_duplicates(self):
        expected = ColorRGB(0x010203)
        ColorRGB(0x010203)

        self.assertEquals(1, len(ColorRGB._color_map._exact_color_map))
        self.assertListEqual([expected], list(ColorRGB._color_map._exact_color_map.values()))

    def test_find_closest_rgb_works(self):
        expected = ColorRGB(0x400000)
        ColorRGB(0x000000)
        ColorRGB(0x00d0d0)

        self.assertEquals(expected, ColorRGB.find_closest(0x500000))

    def test_find_closest_rgb_cache_works(self):
        ColorRGB(0x400000)
        ColorRGB.find_closest(0x500000)
