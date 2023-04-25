# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import unittest

import pytest

from pytermor.ansi import (
    SequenceSGR,
    NOOP_SEQ,
    SeqIndex,
    IntCode,
    _SGR_PAIRITY_REGISTRY,
    make_color_rgb,
    make_color_256,
    make_erase_in_line,
    make_hyperlink_part,
    assemble_hyperlink,
    contains_sgr,
)

def format_test_params(val) -> str | None:
    if isinstance(val, (list, tuple)):
        return "("+",".join(map(str, val))+")"
    return None


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


class TestContainsSgr:
    example = (
        "[38;5;237m"
        "-"
        "[0m"
        " delameter "
        "[1;34m"
        "4"
        "[22;39m"
        "[1;2;34m"
        ".1"
        "[22;22;39m"
        "[34m"
        "k"
        "[m"
    )

    @pytest.mark.parametrize(
        "expected_span_idx, expected_span_value, codes",
        [
            [1, (7, 10), [237]],
            [1, None, [37]],
            [1, (5, 10), [5, 237]],
            [1, (2, 10), [38, 5, 237]],
            [1, (2, 4), [38]],
            [1, (14, 15), [0]],
            [1, None, [4]],
            [1, None, [34, 4]],
            [1, (73, 73), []],
            [1, None, [0, 0]],
            [1, None, [34, 22]],
            [1, (56, 61), [22, 22]],
            [1, None, [22, 2]],
            [1, (45, 48), [1, 2]],
            [0, (0, 11), [237]],
            [0, (12, 16), [0]],
            [0, (43, 52), [1, 2]],
            [0, None, [222]],
        ],
        ids=format_test_params,
    )
    def test_contains_seq(
        self,
        expected_span_idx: int,
        expected_span_value: tuple[int, int] | None,
        codes: list[int],
    ):
        if (match := contains_sgr(TestContainsSgr.example, *codes)) is None:
            assert expected_span_value is None
        else:
            assert match.span(expected_span_idx) == expected_span_value


class TestSequenceCSI(unittest.TestCase):
    def test_make_erase_in_line(self):
        s = make_erase_in_line()


class TestSequenceOSC(unittest.TestCase):
    def test_make_hyperlink_part(self):
        s = make_hyperlink_part("http://example.test")
        self.assertIn("http://example.test", s.assemble())

    def test_assemble_hyperlink(self):
        s = assemble_hyperlink("http://example.test", "label")
        self.assertIn("http://example.test", s)
        self.assertIn("label", s)


class TestSgrRegistry:
    @pytest.mark.parametrize(
        "opening,expected_closing",
        [
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
        ],
    )
    def test_closing_seq(self, opening: SequenceSGR, expected_closing: SequenceSGR):
        assert _SGR_PAIRITY_REGISTRY.get_closing_seq(opening) == expected_closing
