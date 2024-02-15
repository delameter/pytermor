# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import logging
import math
import os
import re
import sys
from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from collections.abc import Iterable

import pytest
import typing as t
from pytermor import Color256, IFilter, StringReplacer
from pytermor.common import (
    ExtendedEnum,
    Align,
    fit,
    cut,
    pad,
    padv,
    only,
    but,
    ours,
    others,
    chunk,
    ismutable,
    flatten,
    char_range,
    get_qname,
    instantiate,
    joinn,
    filtern,
    filterf,
    filtere,
    filternv,
    filterfv,
    filterev,
)
from pytermor.renderer import SgrRenderer, TmuxRenderer, NoopRenderer, IRenderer
from pytermor.filter import IT, OT
from pytermor.style import FT
from pytermor.text import RT
from tests import format_test_params, skip_pre_310_typing


class IExampleEnum(ExtendedEnum):
    @property
    @abstractmethod
    def VALUE1(self):
        ...

    @property
    @abstractmethod
    def VALUE2(self):
        ...

    @property
    @abstractmethod
    def VALUE3(self):
        ...


class ExampleStrEnum(IExampleEnum, str, ExtendedEnum):
    VALUE1 = "v1"
    VALUE2 = "v2"
    VALUE3 = "v3"


class ExampleIntEnum(IExampleEnum, int, ExtendedEnum):
    VALUE1 = 1
    VALUE2 = 2
    VALUE3 = 3


class ExampleTupleEnum(IExampleEnum, tuple, ExtendedEnum):
    VALUE1 = (1,)
    VALUE2 = (2, 1)
    VALUE3 = (3, 2, 1)


@pytest.mark.parametrize("cls", [ExampleStrEnum, ExampleIntEnum, ExampleTupleEnum])
class TestExtendedEnum:
    def test_list(self, cls: IExampleEnum):
        assert cls.list() == [cls.VALUE1.value, cls.VALUE2.value, cls.VALUE3.value]

    def test_dict(self, cls: IExampleEnum):
        assert cls.dict() == {
            cls.VALUE1: cls.VALUE1.value,
            cls.VALUE2: cls.VALUE2.value,
            cls.VALUE3: cls.VALUE3.value,
        }

    def test_rdict(self, cls: IExampleEnum):
        assert cls.rdict() == {
            cls.VALUE1.value: cls.VALUE1,
            cls.VALUE2.value: cls.VALUE2,
            cls.VALUE3.value: cls.VALUE3,
        }

    def test_resolve_by_value(self, cls: IExampleEnum):
        assert cls.resolve_by_value(cls.VALUE1.value) == cls.VALUE1

    def test_resolve_by_invalid_value(self, cls: IExampleEnum):
        pytest.raises(LookupError, cls.resolve_by_value, "12345")


class TestAlign:
    @pytest.mark.parametrize(
        "inp",
        [
            Align.LEFT,
            Align.CENTER,
            Align.RIGHT,
            "<",
            None,
            "LEFT",
            pytest.param(2, marks=pytest.mark.xfail(raises=KeyError)),
        ],
    )
    def test_align(self, inp: str | Align):
        assert isinstance(Align.resolve(inp), (Align, str))


class TestCutAndFit:
    @pytest.mark.parametrize(
        "inp, max_len, align, keep, overflow, fillchar, expected_fit",
        [
            ("1234567890", 12, None, None, "‥", " ", "1234567890  "),
            ("1234567890", 10, None, None, "‥", " ", "1234567890"),
            ("1234567890", 9, None, None, "‥", " ", "12345678‥"),
            ("1234567890", 5, None, None, "‥", " ", "1234‥"),
            ("1234567890", 2, None, None, "‥", " ", "1‥"),
            ("1234567890", 1, None, None, "‥", " ", "‥"),
            ("1234567890", 0, None, None, "‥", " ", ""),
            ("", 0, None, None,  "", " ", ""),
            # align and keep:
            ("1", 1, "<", None, "‥", " ", "1"),
            ("12", 2, "<", None, "‥", " ", "12"),
            ("123", 3, "<", None, "‥", " ", "123"),
            ("1234", 3, "<", None, "‥", " ", "12‥"),
            ("123", 4, "<", None, "‥", " ", "123 "),
            ("1234567890", 12, "^", None,  "‥", " ", " 1234567890 "),
            ("1234567890", 10, "^", None,  "‥", " ", "1234567890"),
            ("1234567890", 9, "^", None,  "‥", " ", "12345678‥"),
            ("1234567890", 5, "^", None,  "‥", " ", "1234‥"),
            ("1234567890", 2, "^", None,  "‥", " ", "1‥"),
            ("1234567890", 1, "^", None,  "‥", " ", "‥"),
            ("1234567890", 0, "^", None,  "‥", " ", ""),
            ("1234567890", 12, ">", None,  "‥", " ", "  1234567890"),
            ("1234567890", 10, ">", None,  "‥", " ", "1234567890"),
            ("1234567890", 9, ">", None,  "‥", " ", "12345678‥"),
            ("1234567890", 5, ">", None,  "‥", " ", "1234‥"),
            ("1234567890", 2, ">", None,  "‥", " ", "1‥"),
            ("1234567890", 1, ">", None,  "‥", " ", "‥"),
            ("1234567890", 0, ">", None,  "‥", " ", ""),
            ("1234567890", 12, "<", "^",  "‥", " ", "1234567890  "),
            ("1234567890", 10, "<", "^",  "‥", " ", "1234567890"),
            ("1234567890", 9, "<", "^",  "‥", " ", "1234‥7890"),
            ("1234567890", 5, "<", "^",  "‥", " ", "12‥90"),
            ("1234567890", 12, "<", ">",  "‥", " ", "1234567890  "),
            ("1234567890", 10, "<", ">",  "‥", " ", "1234567890"),
            ("1234567890", 9, "<", ">",  "‥", " ", "‥34567890"),
            ("1234567890", 5, "<", ">",  "‥", " ", "‥7890"),
            ("1234567890", 12, "^", "^",  "‥", " ", " 1234567890 "),
            ("1234567890", 10, "^", "^",  "‥", " ", "1234567890"),
            ("1234567890", 9, "^", "^",  "‥", " ", "1234‥7890"),
            ("1234567890", 5, "^", "^",  "‥", " ", "12‥90"),
            ("1234567890", 12, "^", ">",  "‥", " ", " 1234567890 "),
            ("1234567890", 10, "^", ">",  "‥", " ", "1234567890"),
            ("1234567890", 9, "^", ">",  "‥", " ", "‥34567890"),
            ("1234567890", 5, "^", ">",  "‥", " ", "‥7890"),
            ("1234567890", 12, ">", "^",  "‥", " ", "  1234567890"),
            ("1234567890", 10, ">", "^",  "‥", " ", "1234567890"),
            ("1234567890", 9, ">", "^",  "‥", " ", "1234‥7890"),
            ("1234567890", 5, ">", "^",  "‥", " ", "12‥90"),
            ("1234567890", 12, ">", ">",  "‥", " ", "  1234567890"),
            ("1234567890", 10, ">", ">",  "‥", " ", "1234567890"),
            ("1234567890", 9, ">", ">",  "‥", " ", "‥34567890"),
            ("1234567890", 5, ">", ">",  "‥", " ", "‥7890"),
            ("1234567890", 0, "<", None,  "...", " ", ""),
            ("1234567890", 1, "<", None,  "..?", " ", "."),
            ("1234567890", 2, "<", None,  "..?", " ", ".."),
        ],
        ids=format_test_params,
    )
    def test_fit(
        self,
        inp: str,
        max_len: int,
        align: Align | str,
        keep: Align | str,
        overflow: str,
        fillchar: str,
        expected_fit: str,
    ):
        actual_fit = fit(inp, max_len, align,keep=keep, overflow=overflow, fill=fillchar)
        assert len(actual_fit) <= max_len
        assert actual_fit == expected_fit

    @pytest.mark.parametrize(
        "inp, max_len, align, keep, overflow, fillchar, expected_fit",
        [
            # overflow can also be a multi-character string:
            ("1234567890", 3, "<", None,  "..?", " ", "..?"),
            ("1234567890", 4, "<", None,  "..?", " ", "1..?"),
            ("1234567890", 5, "<", None,  "..?", " ", "12..?"),
            ("1234567890", 9, "<", None,  "..?", " ", "123456..?"),
            ("1234567890", 10, "<", None,  "..?", " ", "1234567890"),
            ("1234567890", 12, "<", None,  "..?", " ", "1234567890  "),
            ("1234567890", 12, "<", None,  "..?", "*", "1234567890**"),
            ("1234567890", 12, "<", None,  "..?", "][", "1234567890]["),
            # as well as an empty string:
            ("1234567890", 12, "<", None, "", "-", "1234567890--"),
            ("1234567890", 8, "<", None, "", "-", "12345678"),
            ("1234567890", 0, "^", None, "...", " ", ""),
            ("1234567890", 1, "^", ">", "..?", " ", "?"),
            ("1234567890", 2, "^", None, "..?", " ", ".."),
            ("1234567890", 3, "^", None, "..?", " ", "..?"),
            ("1234567890", 4, "^", None, "..?", " ", "1..?"),
            ("1234567890", 5, "^", "^", "..?", " ", "1..?0"),
            ("1234567890", 9, "^", "^", "..?", " ", "123..?890"),
            ("1234567890", 10, "^", None, "", " ", "1234567890"),
            # multichar fill is supported; note that exact char sequence depends
            # on length of fill part, and on which side it is, i.e. fill is asymmetric:
            ("1234567890", 16, "^", None, "", "- ", "- -1234567890 - "),
            ("1234567890", 16, "^", None, "", r"\/", r"\/\1234567890/\/"),
            ("THATS NICE", 12, "^", None, "", "[]", "[THATS NICE]"),
            ("‥SOMETIMES", 13, "^", None, "", "[]", "[‥SOMETIMES]["),
            ("1234567890", 0, "^", None, "...", " ", ""),
            ("1234567890", 1, ">", None, "..?", " ", "."),
            ("1234567890", 2, ">", None, "..?", " ", ".."),
            ("1234567890", 3, ">", None, "..?", " ", "..?"),
            ("1234567890", 4, ">", ">", "..?", " ", "..?0"),
            ("1234567890", 5, ">", ">", "..?", " ", "..?90"),
            ("1234567890", 9, ">", None, "..?", " ", "123456..?"),
            ("1234567890", 10, ">", None, "..?", " ", "1234567890"),
            ("1234567890", 12, ">", None, "..?", " ", "  1234567890"),
            ("1234567890", 12, ">", None, "..?", "<>", "<>1234567890"),
            ("1234567890", 12, ">", None, "..", "ы", "ыы1234567890"),
            ("1234567890", 8, ">", "^", "х?й", " ", "12х?й890"),
            ("@", 6, "<", "<", "", "|¯|_", "@|¯|_|"),
            ("@", 6, ">", "<", "", "|¯|_", "|¯|_|@"),
            ("@", 6, "^", "<", "", "|¯|_", "|¯@|_|"),
            ("@", 2, "<", "<", "<|>", " ", "@ "),
            ("@@", 1, "<", "<", "<|>", " ", "<"),
            ("@@", 2, "<", "<", "<|>", " ", "@@"),
            ("@@@", 2, "<", "<", "<|>", " ", "<|"),
            ("@@@", 2, "<", "<", "<|>", " ", "<|"),
            ("@@@", 2, "<", "^", "<|>", " ", "<>"),
            ("@@@", 2, "<", ">", "<|>", " ", "|>"),
            ("@@@", 2, ">", "<", "<|>", " ", "<|"),
            ("@@@", 2, ">", "^", "<|>", " ", "<>"),
            ("@@@", 2, ">", ">", "<|>", " ", "|>"),
            ("@@@", 2, "^", "<", "<|>", " ", "<|"),
            ("@@@", 2, "^", "^", "<|>", " ", "<>"),
            ("@@@", 2, "^", ">", "<|>", " ", "|>"),
            ("@@@@", 3, "^", "^", "<|>", " ", "<|>"),
            ("|", 7, "^", "^", "", "<>", "<><|><>"),
        ],
        ids=format_test_params,
    )
    def test_fit_multichar(
        self,
        inp: str,
        max_len: int,
        align: Align | str,
        keep: Align | str,
        overflow: str,
        fillchar: str,
        expected_fit: str,
    ):
        actual_fit = fit(inp, max_len, align,keep=keep, overflow=overflow, fill=fillchar)
        assert len(actual_fit) <= max_len
        assert actual_fit == expected_fit

    @pytest.mark.parametrize(
        "inp, max_len, align, keep, overflow, expected_cut",
        [
            ("1234567890", 12, None, None, "‥", "1234567890"),
            ("1234567890", 10, None, None, "‥", "1234567890"),
            ("1234567890", 9, None, None, "‥", "12345678‥"),
            ("1234567890", 5, None, None, "‥", "1234‥"),
            ("1234567890", 2, None, None, "‥", "1‥"),
            ("1234567890", 1, None, None, "‥", "‥"),
            ("1234567890", 0, None, None, "‥", ""),
            ("1234567890", 12, "^", "^", "‥", "1234567890"),
            ("1234567890", 10, "^", "^", "‥", "1234567890"),
            ("1234567890", 9, "^", "^", "‥", "1234‥7890"),
            ("1234567890", 5, "^", "^", "‥", "12‥90"),
            ("1234567890", 2, "^", "^", "‥", "‥0"),
            ("1234567890", 1, "^", "^", "‥", "‥"),
            ("1234567890", 0, "^", "^", "‥", ""),
            ("1234567890", 12, ">", ">", "‥", "1234567890"),
            ("1234567890", 10, ">", ">", "‥", "1234567890"),
            ("1234567890", 9, ">", ">", "‥", "‥34567890"),
            ("1234567890", 5, ">", ">", "‥", "‥7890"),
            ("1234567890", 2, ">", ">", "‥", "‥0"),
            ("1234567890", 1, ">", ">", "‥", "‥"),
            ("1234567890", 0, ">", ">", "‥", ""),
            ("1234567890", 0, "<", "<", "...", ""),
            ("1234567890", 1, "<", "<", "..?", "."),
            ("1234567890", 2, "<", "<", "..?", ".."),
            ("1234567890", 3, "<", "<", "..?", "..?"),
            ("1234567890", 4, "<", "<", "..?", "1..?"),
            ("1234567890", 5, "<", "<", "..?", "12..?"),
            ("1234567890", 9, "<", "<", "..?", "123456..?"),
            ("1234567890", 10, "<", "<", "..?", "1234567890"),
            ("1234567890", 12, "<", "<", "..?", "1234567890"),
            ("1234567890", 0, "^", "^", "...", ""),
            ("1234567890", 1, "^", "^", "..?", "?"),
            ("1234567890", 2, "^", "^", "..?", ".?"),
            ("1234567890", 3, "^", "^", "..?", "..?"),
            ("1234567890", 4, "^", "^", "..?", "..?0"),
            ("1234567890", 5, "^", "^", "..?", "1..?0"),
            ("1234567890", 9, "^", "^", "..?", "123..?890"),
            ("1234567890", 10, "^", "^", "..?", "1234567890"),
            ("1234567890", 12, "^", "^", "..?", "1234567890"),
            ("1234567890", 0, "^", "^", "...", ""),
            ("1234567890", 1, ">", ">", "..?", "?"),
            ("1234567890", 2, ">", ">", "..?", ".?"),
            ("1234567890", 3, ">", ">", "..?", "..?"),
            ("1234567890", 4, ">", ">", "..?", "..?0"),
            ("1234567890", 5, ">", ">", "..?", "..?90"),
            ("1234567890", 9, ">", ">", "..?", "..?567890"),
            ("1234567890", 10, ">", ">", "..?", "1234567890"),
            ("1234567890", 12, ">", ">", "..?", "1234567890"),
        ],
        ids=format_test_params,
    )
    def test_cut(
        self,
        inp: str,
        max_len: int,
        align: Align | str,
        keep: Align | str,
        overflow: str,
        expected_cut: str,
    ):
        actual_cut = cut(inp, max_len, align, keep=keep, overflow=overflow)
        assert len(actual_cut) <= max_len
        assert actual_cut == expected_cut


class TestPadding:
    def test_pad(self, n=10):
        assert pad(n) == n * " "

    def test_padv(self, n=10):
        assert padv(n) == n * "\n"


class TestRelations:
    def test_only(self):
        assert only(int, [1, 2, 3, "4", 5, 6, 7]) == [1, 2, 3, 5, 6, 7]

    def test_but(self):
        assert but(int, [1, 2, 3, "4", 5, 6, 7]) == ["4"]

    def test_ours(self):
        assert ours(t.Iterable, [[1], {2}, {3: 4}, 5]) == [[1], {2}, {3: 4}]

    def test_others(self):
        assert others(t.Iterable, [[1], {2}, {3: 4}, 5]) == [5]


class TestChunk:
    @pytest.mark.parametrize(
        "size, inp, expected",
        [
            (0, range(3), []),
            (1, range(3), [(0,), (1,), (2,)]),
            (2, range(5), [(0, 1), (2, 3), (4,)]),
            (3, range(11), [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9, 10)]),
            (5, range(5), [(0, 1, 2, 3, 4)]),
        ],
        ids=format_test_params,
    )
    def test_chunk(self, size: int, inp: t.Iterable, expected: list):
        assert [*chunk(inp, size)] == expected


class TestMutability:
    @pytest.mark.parametrize(
        "inp, exp_mutable",
        [
            (bool(), False),
            (int(), False),
            (float(), False),
            (complex(), False),
            (str(), False),
            (bytes(), False),
            (tuple(), False),
            (frozenset(), False),
            (object(), False),
            (set(), True),
            (list(), True),
            (dict(), True),
            (bytearray(), True),
            pytest.param(Align.LEFT, True, marks=pytest.mark.xfail(raises=TypeError)),
        ],
        ids=format_test_params,
    )
    def test_mutability(self, inp, exp_mutable: bool):
        assert ismutable(inp) == exp_mutable


class TestFlatten:
    ARRAY_2D = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ]
    ARRAY_3D = [
        [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        [[11, 12, 13], [14, 15, 16], [17, 18, 19]],
        [[21, 22, 23], [24, 25, 26], [27, 28, 29]],
    ]
    ARRAY_5D = [
        [[[[[1, 2]]]]],
        [[[[[3, 4]]]]],
    ]
    ARRAY_IRREGULAR = [
        1,
        [2],
        [[3]],
        [[[4]]],
        [[[[5]]]],
    ]
    ARRAY_IRREGULAR_2 = [1, [2, [3, [4, [5, [6, [7, [8]]]]]]]]

    class RecursiveThrower(t.Iterable):
        def __init__(self, max_level=5):
            self.level = 0
            self.max_level = max_level

        def __iter__(self):
            yield self.level

            self.level += 1
            if self.level >= self.max_level:
                raise RecursionError

            yield [self]

    def test_flatten_2d_array(self):
        assert flatten(self.ARRAY_2D) == [1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test_flatten_3d_array(self):
        # fmt: off
        assert flatten(self.ARRAY_3D) == [
            1, 2, 3, 4, 5, 6, 7, 8, 9,
            11, 12, 13, 14, 15, 16, 17, 18, 19,
            21, 22, 23, 24, 25, 26, 27, 28, 29,
        ]
        # fmt: on

    def test_flatten_5d_array(self):
        assert flatten(self.ARRAY_5D) == [1, 2, 3, 4]

    @pytest.mark.parametrize(
        "limit_level, inp, expected",
        [
            (1, 0, [0]),
            (1, [], []),
            (None, 0, [0]),
            (None, [], []),
            (1, ARRAY_IRREGULAR, [1, 2, [3], [[4]], [[[5]]]]),
            (2, ARRAY_IRREGULAR, [1, 2, 3, [4], [[5]]]),
            (3, ARRAY_IRREGULAR, [1, 2, 3, 4, [5]]),
            (4, ARRAY_IRREGULAR, [1, 2, 3, 4, 5]),
            (5, ARRAY_IRREGULAR, [1, 2, 3, 4, 5]),
            (0, ARRAY_IRREGULAR, [1, 2, 3, 4, 5]),
            (None, ARRAY_IRREGULAR, [1, 2, 3, 4, 5]),
            (1, ARRAY_IRREGULAR_2, [1, 2, [3, [4, [5, [6, [7, [8]]]]]]]),
            (2, ARRAY_IRREGULAR_2, [1, 2, 3, [4, [5, [6, [7, [8]]]]]]),
            (3, ARRAY_IRREGULAR_2, [1, 2, 3, 4, [5, [6, [7, [8]]]]]),
            (4, ARRAY_IRREGULAR_2, [1, 2, 3, 4, 5, [6, [7, [8]]]]),
            (5, ARRAY_IRREGULAR_2, [1, 2, 3, 4, 5, 6, [7, [8]]]),
            (6, ARRAY_IRREGULAR_2, [1, 2, 3, 4, 5, 6, 7, [8]]),
            (7, ARRAY_IRREGULAR_2, [1, 2, 3, 4, 5, 6, 7, 8]),
            (0, ARRAY_IRREGULAR_2, [1, 2, 3, 4, 5, 6, 7, 8]),
            (None, ARRAY_IRREGULAR_2, [1, 2, 3, 4, 5, 6, 7, 8]),
        ],
        ids=format_test_params,
    )
    def test_flatten_irregular_array(self, limit_level: int, inp: t.List, expected: t.List):
        assert flatten(inp, limit_level) == expected

    def test_flatten_circular_references_tracked(self):
        a, b, c = [1, 2], [3, 4], [5, 6]
        a.append(b)
        b.append(c)
        c.append(a)
        assert flatten(a, track=True) == [1, 2, 3, 4, 5, 6]

    def test_flatten_self_references_tracked(self):
        a = [0]
        a = [a, 1]
        assert flatten(a, track=True) == [0, 1]

    def test_flatten_circular_references_untracked(self):
        a, b = [0], [1]
        a.append(b)
        b.append(a)
        assert flatten(a, level_limit=5, track=False) == [0, 1, 0, 1, 0, 1, [0, [1, a]]]

    def test_flatten_self_references_untracked(self):
        a = [0]
        a.extend([1, a])
        assert flatten(a, level_limit=5, track=False) == [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, a]

    def test_flatten_circular_references_catch(self):
        assert flatten(self.RecursiveThrower(), catch=True) == [0, 1, 2, 3, 4]

    @pytest.mark.xfail(raises=RecursionError)
    def test_flatten_circular_references_throw(self):
        flatten(self.RecursiveThrower(), catch=False)


class TestCharRange:
    # noinspection NonAsciiCharacters
    @pytest.mark.parametrize(
        "inp, expected",
        [
            (("a", "z"), "abcdefghijklmnopqrstuvwxyz"),
            (("!", "/"), "!\"#$%&'()*+,-./"),
            (("{", "\x80"), "{|}~\x7f\x80"),
            (("\u2d00", "ⴐ"), "ⴀⴁⴂⴃⴄⴅⴆⴇⴈⴉⴊⴋⴌⴍⴎⴏⴐ"),
            (("\U0010fffe", "\U0010ffff"), "􏿾􏿿"),
            (("z", "x"), ""),
            (("晦", "晨"), "晦晧晨"),
            (("🔨", "🔵"), "🔨🔩🔪🔫🔬🔭🔮🔯🔰🔱🔲🔳🔴🔵"),
            ((b"\xfa", "\u0103"), "\xfa\xfb\xfc\xfd\xfe\xffĀāĂă"),
            ((b"\0", "\a"), "\x00\x01\x02\x03\x04\x05\x06\x07"),
            ((b"\0", "\0"), "\x00"),
            (
                ("퟾", ""),
                "\ud7fe\ud7ff\ue000\ue001",
            ),  # UTF-16 surrogates shall be excluded
            pytest.param(("aaa", "bbb"), "", marks=pytest.mark.xfail(raises=TypeError)),
            pytest.param(("", ""), "", marks=pytest.mark.xfail(raises=TypeError)),
        ],
        ids=format_test_params,
    )
    def test_char_range(self, inp: tuple[str, str], expected: list):
        assert "".join(char_range(*inp)) == expected


class TestGetQName:
    T = t.TypeVar("T")

    def _empty_fn(self):
        pass

    @skip_pre_310_typing
    @pytest.mark.parametrize(
        "inp, expected",
        [
            ("avc", "str"),
            (b"avc", "bytes"),
            (b"a", "bytes"),
            (23, "int"),
            (23.0, "float"),
            (((),), "tuple"),
            ([], "list"),
            (OrderedDict(), "OrderedDict"),
            (TestCharRange, "<TestCharRange>"),
            (Iterable, "<Iterable>"),
            (str, "<str>"),
            (object, "<object>"),
            (ABCMeta, "<ABCMeta>"),
            (type, "<type>"),
            (type(type), "<type>"),
            (Color256, "<Color256>"),
            (None, "None"),
            (type(None), "<NoneType>"),
            (round, "builtin_function_or_method"),
            (pytest, "module"),
            ({}.keys(), "dict_keys"),
            (_empty_fn, "function"),
            (lambda: None, "function"),
            (lambda *_: _, "function"),
            (re.finditer("", ""), "callable_iterator"),
            (os.walk("."), "generator"),
            (staticmethod, "<staticmethod>"),
            (T, "<~T>"),
            (t.Generic, "<Generic>"),
            (IFilter, "<IFilter>"),
            (StringReplacer, "<StringReplacer>"),
            (StringReplacer("", ""), "StringReplacer"),
            (list(), "list"),
        ],
        ids=format_test_params,
    )
    def test_get_qname(self, inp: t.Any, expected: str | tuple[str]):
        if isinstance(expected, str):
            expected = [expected]
        print(get_qname(inp))
        print(expected)
        assert any(get_qname(inp) == ex for ex in expected)


class TestInstantiate:
    @pytest.mark.parametrize(
        "bound, subject, default, expected_type, msg",
        map(
            lambda p: (p + ["instance of subject should be returned"])[:5],
            [
                [
                    IRenderer,
                    SgrRenderer,
                    TmuxRenderer(),
                    SgrRenderer,
                ],
                [
                    IRenderer,
                    Color256,
                    NoopRenderer,
                    NoopRenderer,
                    "subject is not a subclass of bound: default should be returned",
                ],
                [
                    IRenderer,
                    Color256,
                    Color256,
                    type(None),
                    "default is not a subclass of bound, but subject is: instance of subject should be returned",
                ],
                [
                    IRenderer,
                    Color256,
                    None,
                    type(None),
                    "subject is not a subclass of bound: default (=None) should be returned",
                ],
                [
                    IRenderer,
                    Color256,
                    Color256,
                    type(None),
                    "neither of subject and default is a subclass of bound: None should be returned",
                ],
                [
                    IRenderer,
                    "SgrRenderer",
                    TmuxRenderer(),
                    SgrRenderer,
                ],
                [
                    logging.Handler,
                    "logging.StreamHandler",
                    None,
                    logging.StreamHandler,
                ],
                [
                    logging.Handler,
                    logging.StreamHandler,
                    None,
                    logging.StreamHandler,
                ],
                [
                    logging.Handler,
                    logging.StreamHandler(),
                    None,
                    logging.StreamHandler,
                    "the subject itself should be returned",
                ],
                [
                    IRenderer,
                    IRenderer,
                    NoopRenderer(),
                    NoopRenderer,
                    "subject cannot be instantiated: default should be returned",
                ],
                [
                    IRenderer,
                    "IRenderer",
                    NoopRenderer(),
                    NoopRenderer,
                    "subject cannot be instantiated: default should be returned",
                ],
                [
                    IRenderer,
                    "NotExistingClass",
                    NoopRenderer(),
                    NoopRenderer,
                    "subject cannot be found: default should be returned",
                ],
                [
                    IRenderer,
                    "logging.NotExistingClass",
                    NoopRenderer(),
                    NoopRenderer,
                    "subject cannot be found: default should be returned",
                ],
            ],
        ),
        ids=format_test_params,
    )
    def test_instantiate(self, bound, subject, default, expected_type, msg):
        result = instantiate(bound, subject, default)
        assert issubclass(type(result), expected_type), msg


class TestJoin:
    @pytest.mark.parametrize(
        "inp, sep, exp",
        [
            (["a", "b", "c"], "", "abc"),
            (["a", "b", "c"], " ", "a b c"),
            (["", "", ""], ",", ",,"),
        ],
        ids=format_test_params,
    )
    def test_filters(self, inp, sep, exp):
        assert joinn(*inp, sep=sep) == exp


class TestFiltersFV:
    # fmt: off
    FN_LIST_MAP = {
        'n': filtern,
        'f': filterf,
        'e': filtere,
    }
    FN_DICT_MAP = {
        'n': filternv,
        'f': filterfv,
        'e': filterev,
    }

    @pytest.mark.parametrize('inp, fn_exp_map', [
        (               None, {'n': False, 'f': False, 'e': False}),
        (              False, {'n':  True, 'f': False, 'e': False}),
        (               True, {'n':  True, 'f':  True, 'e':  True}),
        (                0.0, {'n':  True, 'f': False, 'e': False}),
        (                  0, {'n':  True, 'f': False, 'e': False}),
        (                  1, {'n':  True, 'f':  True, 'e':  True}),
        (           math.nan, {'n':  True, 'f':  True, 'e':  True}),
        (          -math.inf, {'n':  True, 'f':  True, 'e':  True}),
        ( sys.float_info.min, {'n':  True, 'f':  True, 'e':  True}),
        (                 "", {'n':  True, 'f': False, 'e': False}),
        (                " ", {'n':  True, 'f':  True, 'e': False}),
        (             "\t\n", {'n':  True, 'f':  True, 'e': False}),
        (                "0", {'n':  True, 'f':  True, 'e':  True}),
        (            "False", {'n':  True, 'f':  True, 'e':  True}),
        (                 [], {'n':  True, 'f': False, 'e': False}),
        (                 {}, {'n':  True, 'f': False, 'e': False}),
        (                [0], {'n':  True, 'f':  True, 'e':  True}),
        (                {0}, {'n':  True, 'f':  True, 'e':  True}),
        (               [""], {'n':  True, 'f':  True, 'e':  True}),
        (               {""}, {'n':  True, 'f':  True, 'e':  True}),
        (              [" "], {'n':  True, 'f':  True, 'e':  True}),
        (              {" "}, {'n':  True, 'f':  True, 'e':  True}),
    ], ids=format_test_params)
    # fmt: on
    def test_filters(self, inp: any, fn_exp_map: dict[str, bool]):
        for fn, kept in fn_exp_map.items():
            fnlist = self.FN_LIST_MAP.get(fn)
            fndict = self.FN_DICT_MAP.get(fn)
            assert len([*fnlist([inp])]) == [0, 1][kept]
            assert len({**fndict({"k": inp})}.values()) == [0, 1][kept]
