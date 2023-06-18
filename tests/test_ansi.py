# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import typing

import pytest
from pytest import mark

from pytermor import compose_clear_line_fill_bg, compose_hyperlink
from pytermor.ansi import *
from pytermor.ansi import _PAIRITY_REGISTRY
from tests import format_test_params


class TestSequenceNf:
    def test_assembling(self):
        assert SequenceNf("#", "3", "?").assemble() == "\x1b#?3"


class TestSequenceOSC:
    def test_compose_hyperlink(self):
        s = compose_hyperlink("http://example.test", "label")
        assert s.count("\x1b]8;;") == 2
        assert s.count("\x1b\\") == 2
        assert "http://example.test" in s
        assert "label" in s


class TestSequenceCSI:
    def test_intcode_param_cast(self):
        assert SequenceCSI(None, IntCode.WHITE) == SequenceCSI(None, 37)

    @mark.parametrize(
        "line, exp_seq",
        [(None, f"\x1b[1G"), (1, f"\x1b[1;1H"), (10, f"\x1b[10;1H")],
        ids=format_test_params,
    )
    def test_compose_clear_line_fill_bg(self, line: int | None, exp_seq: str):
        s = compose_clear_line_fill_bg(SeqIndex.BG_BLACK, line)

        assert exp_seq in s
        assert f"\x1b[2K" in s
        assert SeqIndex.BG_BLACK.assemble() in s


class TestSequenceSGR:
    def test_regular_is_equal_to_regular(self):
        assert SequenceSGR(1, 31, 42) == SequenceSGR(1, 31, 42)

    def test_regular_is_not_equal_to_regular(self):
        assert SequenceSGR(2, 31, 42) != SequenceSGR(1, 31, 42)

    def test_empty_is_not_equal_to_reset(self):
        assert SequenceSGR() != SequenceSGR(0)

    def test_addition_of_regular_to_regular(self):
        assert SequenceSGR(1) + SequenceSGR(3) == SequenceSGR(1, 3)

    def test_addition_of_regular_to_noop(self):
        assert SequenceSGR(41) + NOOP_SEQ == SequenceSGR(41)

    def test_addition_of_noop_to_regular(self):
        assert NOOP_SEQ + SequenceSGR(31) == SequenceSGR(31)

    def test_addition_of_noop_to_noop(self):
        assert NOOP_SEQ + NOOP_SEQ == NOOP_SEQ

    def test_addition_of_empty_to_regular(self):
        assert SequenceSGR() + SequenceSGR(44) == SequenceSGR(44)

    def test_addition_of_empty_to_noop(self):
        assert SequenceSGR() + NOOP_SEQ == SequenceSGR()

    def test_addition_of_empty_to_reset(self):
        assert SequenceSGR() + SequenceSGR(0) == SequenceSGR(0)

    def test_addition_of_reset_to_empty(self):
        assert SequenceSGR(0) + SequenceSGR() == SequenceSGR(0)

    def test_iaddition(self):
        s = SequenceSGR(4)
        s += SequenceSGR(1)
        assert s == SequenceSGR(4, 1)

    def test_iaddition_noop(self):
        s = NOOP_SEQ
        s += SequenceSGR(1)
        assert s == SequenceSGR(1)

    @pytest.mark.xfail(raises=TypeError)
    def test_invalid_addition_fails(self):
        # noinspection PyTypeChecker
        NOOP_SEQ + SequenceST()

    @pytest.mark.xfail(raises=TypeError)
    def test_invalid_type_addition(self):
        # noinspection PyTypeChecker
        SequenceSGR(1) + 2

    def test_build_code_args(self):
        assert SequenceSGR(1, 31, 43) == SequenceSGR(
            IntCode.BOLD, IntCode.RED, IntCode.BG_YELLOW
        )

    @pytest.mark.xfail(raises=KeyError)
    def test_build_key_args_invalid(self):
        SequenceSGR("invalid")

    def test_build_sgr_args(self):
        s = SequenceSGR(SeqIndex.HI_CYAN, SeqIndex.ITALIC)
        assert s == SequenceSGR(IntCode.HI_CYAN, IntCode.ITALIC)

    def test_build_mixed_args(self):
        s = SequenceSGR(102, SequenceSGR(SeqIndex.BOLD), SeqIndex.INVERSED)
        assert s == SequenceSGR(IntCode.BG_HI_GREEN, IntCode.BOLD, IntCode.INVERSED)

    @pytest.mark.xfail(raises=KeyError)
    def test_build_mixed_args_invalid(self):
        SequenceSGR(1, "red", "")

    def test_build_mixed_with_empty_arg(self):
        assert SequenceSGR(3, SequenceSGR()) == SequenceSGR(IntCode.ITALIC)

    def test_make_color_256_foreground(self):
        s1 = make_color_256(141)
        s2 = SequenceSGR(IntCode.COLOR_EXTENDED, IntCode.EXTENDED_MODE_256, 141)
        assert s1 == s2

    def test_make_color_256_background(self):
        s1 = make_color_256(255, target=ColorTarget.BG)
        s2 = SequenceSGR(IntCode.BG_COLOR_EXTENDED, IntCode.EXTENDED_MODE_256, 255)
        assert s1 == s2

    @pytest.mark.xfail(raises=ValueError)
    def test_make_color_256_invalid(self):
        make_color_256(266, target=ColorTarget.BG)

    def test_make_color_rgb_foreground(self):
        s1 = make_color_rgb(10, 20, 30)
        s2 = SequenceSGR(IntCode.COLOR_EXTENDED, IntCode.EXTENDED_MODE_RGB, 10, 20, 30)
        assert s1 == s2

    def test_make_color_rgb_background(self):
        s1 = make_color_rgb(50, 70, 90, target=ColorTarget.BG)
        s2 = SequenceSGR(
            IntCode.BG_COLOR_EXTENDED, IntCode.EXTENDED_MODE_RGB, 50, 70, 90
        )
        assert s1 == s2

    @pytest.mark.parametrize(
        "args",
        [
            (10, 310, 30),
            (310, 10, 130),
            (0, 0, 256, ColorTarget.BG),
        ],
    )
    @pytest.mark.xfail(raises=ValueError)
    def test_make_color_rgb_invalid(self, args: tuple):
        make_color_rgb(*args)

    @pytest.mark.xfail(raises=TypeError)
    def test_sgr_fails_on_invalid_param(self):
        # noinspection PyTypeChecker
        SequenceSGR([])

    def test_sgr_hash(self):
        assert hash(SequenceSGR(0)) == hash(SequenceSGR(0))

    def test_noop_seq_is_false(self):
        assert not bool(NOOP_SEQ)


class TestSgrRegistry:
    @pytest.mark.parametrize(
        "opening, expected_closing",
        [
            (NOOP_SEQ, NOOP_SEQ),
            (SeqIndex.WHITE, SeqIndex.COLOR_OFF),
            (SeqIndex.BG_HI_GREEN, SeqIndex.BG_COLOR_OFF),
            (SeqIndex.UNDERLINED, SeqIndex.UNDERLINED_OFF),
            (SeqIndex.BOLD + SeqIndex.RED, SeqIndex.BOLD_DIM_OFF + SeqIndex.COLOR_OFF),
            (SeqIndex.DIM, SeqIndex.BOLD_DIM_OFF),
            (make_color_256(128), SeqIndex.COLOR_OFF),
            (make_color_256(128, target=ColorTarget.BG), SeqIndex.BG_COLOR_OFF),
            (make_color_rgb(128, 0, 128), SeqIndex.COLOR_OFF),
            (make_color_rgb(128, 0, 128, target=ColorTarget.BG), SeqIndex.BG_COLOR_OFF),
            pytest.param(
                make_erase_in_line(0),
                NOOP_SEQ,
                marks=pytest.mark.xfail(raises=TypeError),
            ),
        ],
        ids=format_test_params,
    )
    def test_closing_seq(self, opening: SequenceSGR, expected_closing: SequenceSGR):
        assert _PAIRITY_REGISTRY.get_closing_seq(opening) == expected_closing

    @pytest.mark.parametrize(
        "opening, expected_closing",
        [
            (SequenceSGR(1, 80, 3), SequenceSGR(22, 23)),
            (SequenceSGR(80), NOOP_SEQ),
        ],
        ids=format_test_params,
    )
    def test_unknown_opening_seq_gets_noop_pair(
        self, opening: SequenceSGR, expected_closing: SequenceSGR
    ):
        assert _PAIRITY_REGISTRY.get_closing_seq(opening) == expected_closing

    def test_enclose(self):
        opening_seq = SequenceSGR(31, 42)
        assert enclose(opening_seq, "text") == "\x1b[31;42mtext\x1b[39;49m"


class TestMaking:
    @pytest.mark.parametrize(
        "expected, fn, args",
        [
            ("\x1b[38;5;12m", make_color_256, [12]),
            ("\x1b[48;5;122m", make_color_256, [122, ColorTarget.BG]),
            ("\x1b[58;5;222m", make_color_256, [222, ColorTarget.UNDERLINE]),
            ("\x1b[38;2;255;128;32m", make_color_rgb, [255, 128, 32]),
            ("\x1b[48;2;32;128;255m", make_color_rgb, [32, 128, 255, ColorTarget.BG]),
            ("\x1b[58;2;1;2;3m", make_color_rgb, [1, 2, 3, ColorTarget.UNDERLINE]),
            ("\x1b[1;1H", make_reset_cursor, []),
            ("\x1b[2;3H", make_set_cursor, [2, 3]),
            ("\x1b[4A", make_move_cursor_up, [4]),
            ("\x1b[5B", make_move_cursor_down, [5]),
            ("\x1b[6D", make_move_cursor_left, [6]),
            ("\x1b[7C", make_move_cursor_right, [7]),
            ("\x1b[8F", make_move_cursor_up_to_start, [8]),
            ("\x1b[9E", make_move_cursor_down_to_start, [9]),
            ("\x1b[10d", make_set_cursor_line, [10]),
            ("\x1b[11G", make_set_cursor_column, [11]),
            ("\x1b[6n", make_query_cursor_position, []),
            ("\x1b[0J", make_erase_in_display, [0]),
            ("\x1b[1J", make_erase_in_display, [1]),
            ("\x1b[2J", make_erase_in_display, [2]),
            ("\x1b[3J", make_erase_in_display, [3]),
            ("\x1b[0J", make_clear_display_after_cursor, []),
            ("\x1b[1J", make_clear_display_before_cursor, []),
            ("\x1b[2J", make_clear_display, []),
            ("\x1b[3J", make_clear_history, []),
            ("\x1b[0K", make_erase_in_line, [0]),
            ("\x1b[1K", make_erase_in_line, [1]),
            ("\x1b[2K", make_erase_in_line, [2]),
            ("\x1b[0K", make_clear_line_after_cursor, []),
            ("\x1b[1K", make_clear_line_before_cursor, []),
            ("\x1b[2K", make_clear_line, []),
            ("\x1b[?25h", make_show_cursor, []),
            ("\x1b[?25l", make_hide_cursor, []),
            ("\x1b[?47h", make_save_screen, []),
            ("\x1b[?47l", make_restore_screen, []),
            ("\x1b[?1049h", make_enable_alt_screen_buffer, []),
            ("\x1b[?1049l", make_disable_alt_screen_buffer, []),
            ("\x1b7", make_save_cursor_position, []),
            ("\x1b8", make_restore_cursor_position, []),
        ],
        ids=format_test_params,
    )
    def test_making_works(
        self, fn: typing.Callable[[...], ISequence], args: t.Iterable[int], expected: str
    ):
        actual = fn(*args)
        assert len(actual) == 0
        assert actual.assemble() == expected

    @pytest.mark.parametrize("argval", [-1, 256])
    @pytest.mark.parametrize(
        "fn, argnum",
        [
            (make_color_256, 1),
            (make_color_rgb, 3),
        ],
        ids=format_test_params,
    )
    @pytest.mark.xfail(raises=ValueError)
    def test_making_with_illegal_color_fails(
        self, argval: int, fn: typing.Callable[[...], ISequence], argnum: int
    ):
        fn(*([argval] * argnum))

    @pytest.mark.parametrize("argval", [-1, 0])
    @pytest.mark.parametrize(
        "fn, argnum",
        [
            (make_set_cursor, 2),
            (make_move_cursor_up, 1),
            (make_move_cursor_down, 1),
            (make_move_cursor_left, 1),
            (make_move_cursor_right, 1),
            (make_move_cursor_up_to_start, 1),
            (make_move_cursor_down_to_start, 1),
            (make_set_cursor_line, 1),
            (make_set_cursor_column, 1),
        ],
        ids=format_test_params,
    )
    @pytest.mark.xfail(raises=ValueError)
    def test_making_with_illegal_coords_fails(
        self, argval: int, fn: typing.Callable[[...], ISequence], argnum: int
    ):
        fn(*([argval] * argnum))

    @pytest.mark.parametrize("argval", [-1, 10])
    @pytest.mark.parametrize(
        "fn, argnum",
        [
            (make_erase_in_display, 1),
            (make_erase_in_line, 1),
        ],
        ids=format_test_params,
    )
    @pytest.mark.xfail(raises=ValueError)
    def test_making_with_illegal_mode_fails(
        self, argval: int, fn: typing.Callable[[...], ISequence], argnum: int
    ):
        fn(*([argval] * argnum))


class TestSubtypeParam:
    sp = SeqIndex.CURLY_UNDERLINED.params[0]

    def test_properties(self):
        assert self.sp.value == 4
        assert self.sp.subtype == 3

    def test_to_str(self):
        assert str(self.sp) == "4:3"

    def test_sorting(self):
        arr = [
            sp1 := SubtypedParam(4, 3),
            sp2 := SubtypedParam(14, 1),
            sp3 := SubtypedParam(4, 2),
        ]
        assert sorted(arr) == [sp3, sp1, sp2]
