# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import logging
import unittest
from copy import copy
from typing import Dict

from pytermor.ansi import SequenceSGR, IntCodes, NOOP_SEQ
from pytermor.color import Color, ColorIndexed16, ColorIndexed256, ColorRGB, NOOP_COLOR


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
                actual_output = Color.hex_value_to_rgb_channels(input_num)
                logging.debug(subtest_msg + f' => "{actual_output}"')
                self.assertEquals(expected_output, actual_output)

    def test_noop(self):
        self.assertEquals(NOOP_SEQ, NOOP_COLOR.to_sgr(False))
        self.assertEquals(NOOP_SEQ, NOOP_COLOR.to_sgr(True))

    def test_format_value(self):
        self.assertEquals('0xff00ff', ColorRGB(0xff00ff).format_value())
        self.assertEquals('#ff00ff', ColorRGB(0xff00ff).format_value('#'))

    def test_format_noop_color_value(self):
        self.assertEqual('~', NOOP_COLOR.format_value())
        self.assertEqual('~', NOOP_COLOR.format_value('#'))


class TestColorMap(unittest.TestCase):
    _color_default_lookup_table: Dict[int, ColorIndexed16]
    _color_indexed_lookup_table: Dict[int, ColorIndexed256]
    _color_rgb_lookup_table: Dict[int, ColorRGB]

    @classmethod
    def setUpClass(cls) -> None:
        #ColorIndexed16.get_default()  # initialize color maps
        #ColorIndexed.get_default()
        #ColorRGB.get_default()

        # and copy lookup table origins:
        cls._color_default_lookup_table = copy(ColorIndexed16._approx._lookup_table)
        cls._color_indexed_lookup_table = copy(ColorIndexed256._approx._lookup_table)
        cls._color_rgb_lookup_table = copy(ColorRGB._approx._lookup_table)

    def tearDown(self) -> None:
        if ColorIndexed256._approx_initialized:
            ColorIndexed256._approx._lookup_table.clear()
            ColorIndexed256._approx._approximation_cache.clear()

        if ColorRGB._approx_initialized:
            ColorRGB._approx._lookup_table.clear()

    @classmethod
    def tearDownClass(cls) -> None:
        # recover original lookup tables from "backup".
        # it's necessary because the alternative is to use something
        # like ``importlib.reload(color)``, but this messes up ``isinstance()``
        # checks further in tests, as `color` classes are recreated and even
        # if they have the same name, they are not same objects anymore.

        ColorIndexed16._approx._lookup_table = cls._color_default_lookup_table
        ColorIndexed256._approx._lookup_table = cls._color_indexed_lookup_table
        ColorRGB._approx._lookup_table = cls._color_rgb_lookup_table

    def test_lookup_table_inits_on_real_color_creation(self):
        expected = ColorIndexed256(0x000000, 0, use_for_approximations=True)

        self.assertEquals(1, len(ColorIndexed256._approx._lookup_table))
        self.assertDictEqual({0x000000: expected}, ColorIndexed256._approx._lookup_table)

    def test_lookup_table_ignores_duplicates(self):
        expected = ColorIndexed256(0x010203, 1, use_for_approximations=True)
        ColorIndexed256(0x010203, 2, use_for_approximations=True)

        self.assertEquals(1, len(ColorIndexed256._approx._lookup_table))
        self.assertDictEqual({0x010203: expected},
                             ColorIndexed256._approx._lookup_table)

    def test_find_closest_works(self):
        expected = ColorIndexed256(0x400000, 1, use_for_approximations=True)
        ColorIndexed256(0x000000, 2, use_for_approximations=True)
        ColorIndexed256(0x00d0d0, 3, use_for_approximations=True)

        self.assertEquals(expected, ColorIndexed256.find_closest(0x500000))

    def test_cache_works(self):
        expected = ColorIndexed256(0x400000, 1, use_for_approximations=True)
        self.assertEquals(0, len(ColorIndexed256._approx._approximation_cache))

        ColorIndexed256.find_closest(0x500000)
        self.assertDictEqual({0x400000: expected, 0x500000: expected},
                             ColorIndexed256._approx._approximation_cache)

        ColorIndexed256.find_closest(0x300000)
        self.assertDictEqual(
            {0x400000: expected, 0x500000: expected, 0x300000: expected},
            ColorIndexed256._approx._approximation_cache)

        ColorIndexed256.find_closest(0x500000)
        self.assertDictEqual(
            {0x400000: expected, 0x500000: expected, 0x300000: expected},
            ColorIndexed256._approx._approximation_cache)

    def test_cache_resets_on_new_color_creation(self):
        ColorIndexed256(0x400000, 1, use_for_approximations=True)
        ColorIndexed256.find_closest(0x500000)
        ColorIndexed256(0x600000, 2, use_for_approximations=True)

        self.assertEquals(0, len(ColorIndexed256._approx._approximation_cache))

    def test_cache_doesnt_change_on_repeated_search(self):
        ColorIndexed256(0x400000, 1, use_for_approximations=True)
        ColorIndexed256.find_closest(0x500000)
        ColorIndexed256(0x600000, 2, use_for_approximations=True)

        self.assertEquals(0, len(ColorIndexed256._approx._approximation_cache))

    def test_cache_is_not_invoked_for_rgb_color_search(self):
        ColorRGB(0x400000)
        ColorRGB.find_closest(0x141414)

        self.assertEquals(0, len(ColorRGB._approx._approximation_cache))

    def test_search_returns_default_if_no_colors_registered(self):
        ColorRGB(0xffffff)
        ColorRGB._approx._lookup_table.clear()
        ColorRGB._approx._approximation_cache.clear()
        self.assertEqual(ColorIndexed256.find_closest(0xffffff),
                         ColorIndexed256.get_default())

        ColorIndexed256(0xffffff, 1)
        ColorIndexed256._approx._lookup_table.clear()
        ColorIndexed256._approx._approximation_cache.clear()
        self.assertEqual(ColorIndexed256.find_closest(0xffffff),
                         ColorIndexed256.get_default())

        ColorIndexed16(0xffffff, IntCodes.WHITE, IntCodes.BG_WHITE)
        ColorIndexed16._approx._lookup_table.clear()
        ColorIndexed16._approx._approximation_cache.clear()
        self.assertEqual(ColorIndexed16.find_closest(0xffffff),
                         ColorIndexed16.get_default())


class TestColorIndexed16(unittest.TestCase):
    def test_to_sgr(self):
        self.assertEquals(SequenceSGR(31),
                          ColorIndexed16(0x800000, IntCodes.RED, IntCodes.BG_RED).to_sgr(
                              False))
        self.assertEquals(SequenceSGR(41),
                          ColorIndexed16(0x800000, IntCodes.RED, IntCodes.BG_RED).to_sgr(
                              True))

    def test_equality(self):
        self.assertTrue(
            ColorIndexed16(0x010203, 11, 12) == ColorIndexed16(0x010203, 11, 12))

    def test_not_equality(self):
        self.assertFalse(
            ColorIndexed16(0x010203, 11, 12) == ColorIndexed16(0xffeedd, 11, 12))
        self.assertFalse(
            ColorIndexed16(0x010203, 11, 12) == ColorIndexed16(0x010203, 12, 11))
        self.assertFalse(ColorIndexed16(0x010203, 11, 12) == ColorIndexed256(0x010203, 12))
        self.assertFalse(ColorIndexed16(0x010203, 11, 12) == ColorRGB(0x010203))


class TestColorIndexed(unittest.TestCase):
    def test_to_sgr(self):
        self.assertEquals(SequenceSGR(38, 5, 1), ColorIndexed256(0xffcc01, 1).to_sgr(False))
        self.assertEquals(SequenceSGR(48, 5, 1), ColorIndexed256(0xffcc01, 1).to_sgr(True))

    def test_equality(self):
        self.assertTrue(ColorIndexed256(0x010203, 11) == ColorIndexed256(0x010203, 11))

    def test_not_equality(self):
        self.assertFalse(ColorIndexed256(0x010203, 11) == ColorIndexed256(0x010203, 12))
        self.assertFalse(ColorIndexed256(0x010203, 11) == ColorIndexed256(0x030201, 11))
        self.assertFalse(ColorIndexed256(0x010203, 11) == ColorIndexed256(0xffee14, 88))
        self.assertFalse(ColorIndexed256(0x010203, 11) == ColorIndexed16(0x010203, 11, 11))
        self.assertFalse(ColorIndexed256(0x010203, 11) == ColorRGB(0x010203))


class TestColorRGB(unittest.TestCase):
    def test_to_sgr(self):
        self.assertEquals(SequenceSGR(38, 2, 255, 51, 255),
                          ColorRGB(0xff33ff).to_sgr(False))
        self.assertEquals(SequenceSGR(48, 2, 255, 51, 153),
                          ColorRGB(0xff3399).to_sgr(True))

    def test_equality(self):
        self.assertTrue(ColorRGB(0x010203) == ColorRGB(0x010203))

    def test_not_equality(self):
        self.assertFalse(ColorRGB(0x010203) == ColorRGB(0x030201))
        self.assertFalse(ColorRGB(0x010203) == ColorIndexed256(0x010203, 1))
        self.assertFalse(ColorRGB(0x010203) == ColorIndexed16(0x556677, IntCodes.WHITE,
                                                            IntCodes.BG_WHITE))
