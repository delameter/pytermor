# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import os.path
import typing as t

import pytest

from pytermor import (
    SeqIndex,
    SequenceCSI,
    SequenceFe,
    SequenceFs,
    SequenceNf,
    SequenceSGR,
    SequenceST,
    contains_sgr,
    decompose_report_cursor_position,
    parse,
)
from pytermor.ansi import ISequence, SequenceFp, SequenceOSC
from pytermor.exception import ParseError
from tests import format_test_params, load_data_file


def read_file(filename: str) -> str:
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if not os.path.isfile(filepath):
        raise FileNotFoundError(
            f"Required data file '{filename}' not found in test directory"
        )
    with open(filepath, "rt") as f:
        return f.read()


class TestParser:
    @pytest.mark.parametrize(
        "input, expected_output",
        [
            (
                "\x1b[1;91mr\x1b[22;39m\x1b[1;33mw\x1b[22;39m\x1b[1;93mx\x1b[22;39m"
                "\x1b[2;91mr\x1b[22;39m\x1b[2;33mw\x1b[22;39m\x1b[2;93mx\x1b[22;39m"
                "\x1b[37mr\x1b[39m\x1b[90mw\x1b[39m\x1b[90mx\x1b[39m",
                [
                    SequenceSGR(1, 91),
                    "r",
                    SequenceSGR(22, 39),
                    SequenceSGR(1, 33),
                    "w",
                    SequenceSGR(22, 39),
                    SequenceSGR(1, 93),
                    "x",
                    SequenceSGR(22, 39),
                    SequenceSGR(2, 91),
                    "r",
                    SequenceSGR(22, 39),
                    SequenceSGR(2, 33),
                    "w",
                    SequenceSGR(22, 39),
                    SequenceSGR(2, 93),
                    "x",
                    SequenceSGR(22, 39),
                    SequenceSGR(37),
                    "r",
                    SequenceSGR(39),
                    SequenceSGR(90),
                    "w",
                    SequenceSGR(39),
                    SequenceSGR(90),
                    "x",
                    SequenceSGR(39),
                ],
            ),
            (
                f"=\x1b[4:3m.\x1b[48;2;128;64;32m.\x1b[0m=",
                [
                    "=",
                    SeqIndex.CURLY_UNDERLINED,
                    ".",
                    SequenceSGR(48, 2, 128, 64, 32),
                    ".",
                    SeqIndex.RESET,
                    "=",
                ],
            ),
            (
                "\x1b[48;5;235m\x1b[0KQUICK␣START\n",
                [SequenceSGR(48, 5, 235), SequenceCSI("K", 0), "QUICK␣START\n"],
            ),
            (
                "\x1bP3;4\x1b\\\x1bP",
                [
                    SequenceFe("P", 3, 4),
                    SequenceST(),
                    SequenceFe("P"),
                ],
            ),
            (
                "\x1b]8;;http://localhost\x1b\\local\x1b]8;;\x1b\\",
                [
                    SequenceOSC(8, "", ""),
                    "http://localhost",
                    SequenceST(),
                    "local",
                    SequenceOSC(8, "", ""),
                    SequenceST(),
                ],
            ),
            (
                "z\x1b %abc\x1b#3def\x1b&%ghi",
                [
                    "z",
                    SequenceNf("%", " ", "a"),
                    "bc",
                    SequenceNf("#", "3"),
                    "def",
                    SequenceNf("&", "g", "%"),
                    "hi",
                ],
            ),
            (
                "abc\x1b7def\x1b81\x1b=<\x1b>0op",
                [
                    "abc",
                    SequenceFp("7"),
                    "def",
                    SequenceFp("8"),
                    "1",
                    SequenceFp("="),
                    "<",
                    SequenceFp(">"),
                    "0op",
                ],
            ),
            (
                "qwe\x1b[2@abc\x1b[3;4H;;\x1b[LL.\x1b[?2Jab",
                [
                    "qwe",
                    SequenceCSI("@", 2),
                    "abc",
                    SequenceCSI("H", 3, 4),
                    ";;",
                    SequenceCSI("L"),
                    "L.",
                    SequenceCSI("J", 2, interm="?"),
                    "ab",
                ],
            ),
            (
                "123\x1b|abc\x1b~def\x1b}x",
                [
                    "123",
                    SequenceFs("|"),
                    "abc",
                    SequenceFs("~"),
                    "def",
                    SequenceFs("}"),
                    "x",
                ],
            ),
        ],
    )
    def test_parsing(
        self, input: str | t.Callable[[], str], expected_output: list[ISequence | str]
    ):
        if isinstance(input, t.Callable):
            input = input()
        assert [*parse(input)] == expected_output

    def test_all_escapes_recognized(self):
        input = load_data_file("test_all_escapes_inp.txt")
        for part in parse(input):
            if isinstance(part, str):
                assert "\x1b" not in part

    @pytest.mark.xfail(raises=ParseError)
    def test_csi_fails_on_invalid_param(self):
        [*parse("\x1b[=D")]  # noqa

    @pytest.mark.xfail(raises=ParseError)
    def test_sgr_fails_on_invalid_param(self):
        [*parse("\x1b[=m")]  # noqa


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

    def test_contains_seq_returns_none_on_empty_str(self):
        assert contains_sgr("", 1) == None


class TestMisc:
    def test_decompose_report_cursor_position_returns_none_on_no_match(self):
        assert decompose_report_cursor_position("") is None
