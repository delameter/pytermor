# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import logging
import unittest
from copy import copy
from typing import Dict

from pytermor import sequence, color, intcode
from pytermor.color import Color, ColorDefault, ColorIndexed, ColorRGB
from pytermor.sequence import SequenceSGR


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
        self.assertEquals(sequence.NOOP, color.NOOP.to_sgr_rgb(False))
        self.assertEquals(sequence.NOOP, color.NOOP.to_sgr_rgb(True))

        self.assertEquals(sequence.NOOP, color.NOOP.to_sgr_indexed(False))
        self.assertEquals(sequence.NOOP, color.NOOP.to_sgr_indexed(True))

        self.assertEquals(sequence.NOOP, color.NOOP.to_sgr_default(False))
        self.assertEquals(sequence.NOOP, color.NOOP.to_sgr_default(True))

    def test_format_value(self):
        self.assertEquals('0xff00ff', ColorRGB(0xff00ff).format_value())
        self.assertEquals('#ff00ff', ColorRGB(0xff00ff).format_value('#'))

    def test_format_noop_color_value(self):
        self.assertEqual('', color.NOOP.format_value())
        self.assertEqual('', color.NOOP.format_value('#'))


class TestColorMap(unittest.TestCase):
    _color_default_lookup_table: Dict[int, ColorDefault]
    _color_indexed_lookup_table: Dict[int, ColorIndexed]
    _color_rgb_lookup_table: Dict[int, ColorRGB]

    @classmethod
    def setUpClass(cls) -> None:
        ColorDefault.get_default()  # initialize color maps
        ColorIndexed.get_default()
        ColorRGB.get_default()

        # and copy lookup table origins:
        cls._color_default_lookup_table = copy(ColorDefault._color_map._lookup_table)
        cls._color_indexed_lookup_table = copy(ColorIndexed._color_map._lookup_table)
        cls._color_rgb_lookup_table = copy(ColorRGB._color_map._lookup_table)

    def tearDown(self) -> None:
        if hasattr(ColorIndexed, '_color_map'):
            ColorIndexed._color_map._lookup_table.clear()
            ColorIndexed._color_map._approximate_cache.clear()

        if hasattr(ColorRGB, '_color_map'):
            ColorRGB._color_map._lookup_table.clear()

    @classmethod
    def tearDownClass(cls) -> None:
        # recover original lookup tables from "backup".
        # it's necessary because the alternative is to use something
        # like ``importlib.reload(color)``, but this messes up ``isinstance()``
        # checks further in tests, as `color` classes are recreated and even
        # if they have the same name, they are not same objects anymore.

        ColorDefault._color_map._lookup_table = cls._color_default_lookup_table
        ColorIndexed._color_map._lookup_table = cls._color_indexed_lookup_table
        ColorRGB._color_map._lookup_table = cls._color_rgb_lookup_table

    def test_lookup_table_inits_on_real_color_creation(self):
        expected = ColorRGB(0x000000)

        self.assertEquals(1, len(ColorRGB._color_map._lookup_table))
        self.assertDictEqual({0x000000: expected},
                             ColorRGB._color_map._lookup_table)

    def test_lookup_table_stays_empty_on_noop_color_creation(self):
        ColorRGB()
        self.assertEquals(0, len(ColorRGB._color_map._lookup_table))

    def test_lookup_table_ignores_duplicates(self):
        expected = ColorIndexed(0x010203, 1)
        ColorIndexed(0x010203, 2)

        self.assertEquals(1, len(ColorIndexed._color_map._lookup_table))
        self.assertDictEqual({0x010203: expected},
                             ColorIndexed._color_map._lookup_table)

    def test_find_closest_works(self):
        expected = ColorIndexed(0x400000, 1)
        ColorIndexed(0x000000, 2)
        ColorIndexed(0x00d0d0, 3)

        self.assertEquals(expected, ColorIndexed.find_closest(0x500000))

    def test_find_closest_checks_lookup_table(self):
        expected = ColorIndexed(0x400000, 1)

        self.assertEquals(expected, ColorIndexed.find_closest(0x400000))
        self.assertEquals(0, len(ColorIndexed._color_map._approximate_cache))
        self.assertDictEqual({0x400000: expected},
                             ColorIndexed._color_map._lookup_table)

    def test_cache_works(self):
        expected = ColorIndexed(0x400000, 1)
        self.assertEquals(0, len(ColorIndexed._color_map._approximate_cache))

        ColorIndexed.find_closest(0x500000)
        self.assertDictEqual({0x400000: expected, 0x500000: expected},
                             ColorIndexed._color_map._approximate_cache)

        ColorIndexed.find_closest(0x300000)
        self.assertDictEqual(
            {0x400000: expected, 0x500000: expected, 0x300000: expected},
            ColorIndexed._color_map._approximate_cache
        )

        ColorIndexed.find_closest(0x500000)
        self.assertDictEqual(
            {0x400000: expected, 0x500000: expected, 0x300000: expected},
            ColorIndexed._color_map._approximate_cache
        )

    def test_cache_resets_on_new_color_creation(self):
        ColorIndexed(0x400000, 1)
        ColorIndexed.find_closest(0x500000)
        ColorIndexed(0x600000, 2)

        self.assertEquals(0, len(ColorIndexed._color_map._approximate_cache))

    def test_cache_doesnt_change_on_repeated_search(self):
        ColorIndexed(0x400000, 1)
        ColorIndexed.find_closest(0x500000)
        ColorIndexed(0x600000, 2)

        self.assertEquals(0, len(ColorIndexed._color_map._approximate_cache))

    def test_cache_is_not_invoked_for_rgb_color_search(self):
        ColorRGB(0x400000)
        ColorRGB.find_closest(0x141414)

        self.assertEquals(0, len(ColorRGB._color_map._approximate_cache))

    def test_search_returns_default_if_no_colors_registered(self):
        ColorRGB(0xffffff)
        ColorRGB._color_map._lookup_table.clear()
        ColorRGB._color_map._approximate_cache.clear()
        self.assertEqual(ColorIndexed.find_closest(0xffffff),
                         ColorIndexed.get_default())

        ColorIndexed(0xffffff, 1)
        ColorIndexed._color_map._lookup_table.clear()
        ColorIndexed._color_map._approximate_cache.clear()
        self.assertEqual(ColorIndexed.find_closest(0xffffff),
                         ColorIndexed.get_default())

        ColorDefault(0xffffff, intcode.WHITE, intcode.BG_WHITE)
        ColorDefault._color_map._lookup_table.clear()
        ColorDefault._color_map._approximate_cache.clear()
        self.assertEqual(ColorDefault.find_closest(0xffffff),
                         ColorDefault.get_default())


class TestColorDefault(unittest.TestCase):
    def test_to_sgr_default(self):
        self.assertEquals(SequenceSGR(31),
                          ColorDefault(0x800000, intcode.RED, intcode.BG_RED)
                          .to_sgr_default(False))
        self.assertEquals(SequenceSGR(41),
                          ColorDefault(0x800000, intcode.RED, intcode.BG_RED)
                          .to_sgr_default(True))

    def test_to_sgr_indexed(self):
        self.assertEquals(SequenceSGR(38, 5, intcode.IDX_MAROON),
                          ColorDefault(0x800000, intcode.RED, intcode.BG_RED)
                          .to_sgr_indexed(False))
        self.assertEquals(SequenceSGR(48, 5, intcode.IDX_LIME),
                          ColorDefault(0x00ee00, intcode.HI_GREEN, intcode.BG_HI_GREEN)
                          .to_sgr_indexed(True))

    def test_to_sgr_rgb(self):
        self.assertEquals(SequenceSGR(38, 2, 128, 0, 0),
                          ColorDefault(0x800000, intcode.RED, intcode.BG_RED)
                          .to_sgr_rgb(False))
        self.assertEquals(SequenceSGR(48, 2, 128, 0, 0),
                          ColorDefault(0x800000, intcode.RED, intcode.BG_RED)
                          .to_sgr_rgb(True))

    def test_equality(self):
        self.assertTrue(ColorDefault(0x010203, 11, 12) == ColorDefault(0x010203, 11, 12))

    def test_not_equality(self):
        self.assertFalse(ColorDefault(0x010203, 11, 12) == ColorDefault(0xffeedd, 11, 12))
        self.assertFalse(ColorDefault(0x010203, 11, 12) == ColorDefault(0x010203, 12, 11))
        self.assertFalse(ColorDefault(0x010203, 11, 12) == ColorIndexed(0x010203, 12))
        self.assertFalse(ColorDefault(0x010203, 11, 12) == ColorRGB(0x010203))


class TestColorIndexed(unittest.TestCase):
    def test_to_sgr_default(self):
        self.assertEquals(SequenceSGR(93), ColorIndexed(0xffcc01, 1).to_sgr_default(False))
        self.assertEquals(SequenceSGR(103), ColorIndexed(0xffcc01, 1).to_sgr_default(True))

    def test_to_sgr_indexed(self):
        self.assertEquals(SequenceSGR(38, 5, 1),
                          ColorIndexed(0xffcc01, 1).to_sgr_indexed(False))
        self.assertEquals(SequenceSGR(48, 5, 2),
                          ColorIndexed(0x010101, 2).to_sgr_indexed(True))

    def test_to_sgr_rgb(self):
        self.assertEquals(SequenceSGR(38, 2, 255, 254, 253),
                          ColorIndexed(0xfffefd, 10).to_sgr_rgb(False))
        self.assertEquals(SequenceSGR(48, 2, 1, 2, 3),
                          ColorIndexed(0x010203, 20).to_sgr_rgb(True))

    def test_equality(self):
        self.assertTrue(ColorIndexed(0x010203, 11) == ColorIndexed(0x010203, 11))

    def test_not_equality(self):
        self.assertFalse(ColorIndexed(0x010203, 11) == ColorIndexed(0x010203, 12))
        self.assertFalse(ColorIndexed(0x010203, 11) == ColorIndexed(0x030201, 11))
        self.assertFalse(ColorIndexed(0x010203, 11) == ColorIndexed(0xffee14, 88))
        self.assertFalse(ColorIndexed(0x010203, 11) == ColorDefault(0x010203, 11, 11))
        self.assertFalse(ColorIndexed(0x010203, 11) == ColorRGB(0x010203))


class TestColorRGB(unittest.TestCase):
    def test_to_sgr_default(self):
        self.assertEquals(SequenceSGR(95), ColorRGB(0xff33ff).to_sgr_default(False))
        self.assertEquals(SequenceSGR(105), ColorRGB(0xff3399).to_sgr_default(True))

    def test_to_sgr_indexed(self):
        self.assertEquals(SequenceSGR(38, 5, intcode.IDX_VIOLET),
                          ColorRGB(0xd888fe).to_sgr_indexed(False))
        self.assertEquals(SequenceSGR(48, 5, intcode.IDX_FUCHSIA),
                          ColorRGB(0xfd03fd).to_sgr_indexed(True))

    def test_to_sgr_rgb(self):
        self.assertEquals(SequenceSGR(38, 2, 255, 51, 153),
                          ColorRGB(0xff3399).to_sgr_rgb(False))
        self.assertEquals(SequenceSGR(48, 2, 255, 51, 153),
                          ColorRGB(0xff3399).to_sgr_rgb(True))

    def test_equality(self):
        self.assertTrue(ColorRGB(0x010203) == ColorRGB(0x010203))

    def test_not_equality(self):
        self.assertFalse(ColorRGB(0x010203) == ColorRGB(0x030201))
        self.assertFalse(ColorRGB(0x010203) == ColorIndexed(0x010203, 1))
        self.assertFalse(ColorRGB(0x010203) ==
                         ColorDefault(0x556677, intcode.WHITE, intcode.BG_WHITE))
