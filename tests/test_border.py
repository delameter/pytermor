# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import io
import pydoc

from pytest import mark

from pytermor.border import *
from tests import format_test_params, load_data_file


class TestBorder:
    @mark.parametrize(
        "border, expected",
        ids=format_test_params,
        argvalues=[
            (ASCII_SINGLE, ["+---+", "|<->|", "+---+"]),
        ],
    )
    def test_making_works(self, border: Border, expected: list[str]):
        assert [*border.make(5, "<->".splitlines(), pad_x=0)] == expected

    def test_format_matches(self):
        expected_fname = "test_border_exp.txt"
        list_buffer = io.StringIO()

        for idx, (origin_name, border) in enumerate(ALL.items()):
            cw = 27
            content = [origin_name]
            output_lines = []
            for line in border.make(6, f"{idx+1:02d}", "^"):
                output_lines.append(line)

            for n, line in enumerate(border.make(cw, content, "^")):
                output_lines[n] += line

            for ol in output_lines:
                print(ol, file=list_buffer)
            print(file=list_buffer)

        list_buffer.seek(0)
        print(list_buffer)
        list_buffer.seek(0)
        assert load_data_file(expected_fname).strip() == list_buffer.read().strip()

    def test_new_instance(self):
        border = Border(*"|⁺¯⁺|₊_₊")
        assert border.part_chars == {*"|_¯⁺₊"}
        assert [*border.make(3, ["1", "2", "3"], pad_x=0)] == ["⁺¯⁺", "|1|", "|2|", "|3|", "₊_₊"]
