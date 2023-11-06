# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import os
import re
from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from typing import Optional, Union

import pytest

from pytermor import Color256, IFilter, StringReplacer
from pytermor.common import *
from pytermor.filter import IT, OT
from tests import format_test_params


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
        "input",
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
    def test_align(self, input: str | Align):
        assert isinstance(Align.resolve(input), (Align, str))


class TestCutAndFit:
    @pytest.mark.parametrize(
        "input, max_len, align, overflow, fillchar, expected_fit",
        [
            ("1234567890", 12, None, "‥", " ", "1234567890  "),
            ("1234567890", 10, None, "‥", " ", "1234567890"),
            ("1234567890", 9, None, "‥", " ", "12345678‥"),
            ("1234567890", 5, None, "‥", " ", "1234‥"),
            ("1234567890", 2, None, "‥", " ", "1‥"),
            ("1234567890", 1, None, "‥", " ", "‥"),
            ("1234567890", 0, None, "‥", " ", ""),
            ("", 0, None, "", " ", ""),
            ("1", 1, Align.LEFT, "‥", " ", "1"),
            ("12", 2, Align.LEFT, "‥", " ", "12"),
            ("123", 3, Align.LEFT, "‥", " ", "123"),
            ("1234", 3, Align.LEFT, "‥", " ", "12‥"),
            ("123", 4, Align.LEFT, "‥", " ", "123 "),
            ("1234567890", 12, Align.CENTER, "‥", " ", " 1234567890 "),
            ("1234567890", 10, Align.CENTER, "‥", " ", "1234567890"),
            ("1234567890", 9, Align.CENTER, "‥", " ", "1234‥7890"),
            ("1234567890", 5, Align.CENTER, "‥", " ", "12‥90"),
            ("1234567890", 2, Align.CENTER, "‥", " ", "‥0"),
            ("1234567890", 1, Align.CENTER, "‥", " ", "‥"),
            ("1234567890", 0, Align.CENTER, "‥", " ", ""),
            ("1234567890", 12, Align.RIGHT, "‥", " ", "  1234567890"),
            ("1234567890", 10, Align.RIGHT, "‥", " ", "1234567890"),
            ("1234567890", 9, Align.RIGHT, "‥", " ", "‥34567890"),
            ("1234567890", 5, Align.RIGHT, "‥", " ", "‥7890"),
            ("1234567890", 2, Align.RIGHT, "‥", " ", "‥0"),
            ("1234567890", 1, Align.RIGHT, "‥", " ", "‥"),
            ("1234567890", 0, Align.RIGHT, "‥", " ", ""),
            ("1234567890", 0, Align.LEFT, "...", " ", ""),
            ("1234567890", 1, Align.LEFT, "..?", " ", "."),
            ("1234567890", 2, Align.LEFT, "..?", " ", ".."),
            # overflow can also be a multi-character string:
            ("1234567890", 3, Align.LEFT, "..?", " ", "..?"),
            ("1234567890", 4, Align.LEFT, "..?", " ", "1..?"),
            ("1234567890", 5, Align.LEFT, "..?", " ", "12..?"),
            ("1234567890", 9, Align.LEFT, "..?", " ", "123456..?"),
            ("1234567890", 10, Align.LEFT, "..?", " ", "1234567890"),
            ("1234567890", 12, Align.LEFT, "..?", " ", "1234567890  "),
            ("1234567890", 12, Align.LEFT, "..?", "*", "1234567890**"),
            ("1234567890", 12, Align.LEFT, "..?", "][", "1234567890]["),
            # as well as an empty string:
            ("1234567890", 12, Align.LEFT, "", "-", "1234567890--"),
            ("1234567890", 8, Align.LEFT, "", "-", "12345678"),
            ("1234567890", 0, Align.CENTER, "...", " ", ""),
            ("1234567890", 1, Align.CENTER, "..?", " ", "?"),
            ("1234567890", 2, Align.CENTER, "..?", " ", ".?"),
            ("1234567890", 3, Align.CENTER, "..?", " ", "..?"),
            ("1234567890", 4, Align.CENTER, "..?", " ", "..?0"),
            ("1234567890", 5, Align.CENTER, "..?", " ", "1..?0"),
            ("1234567890", 9, Align.CENTER, "..?", " ", "123..?890"),
            ("1234567890", 10, Align.CENTER, "", " ", "1234567890"),
            # multichar fill is supported; note that exact char sequence depends
            # on length of fill part, and on which side it is, i.e. fill is asymmetric:
            ("1234567890", 16, Align.CENTER, "", "- ", "- -1234567890 - "),
            ("1234567890", 16, Align.CENTER, "", r"\/", r"\/\1234567890/\/"),
            ("THATS NICE", 12, Align.CENTER, "", "[]", "[THATS NICE]"),
            ("‥SOMETIMES", 13, Align.CENTER, "", "[]", "[‥SOMETIMES[]"),
            ("1234567890", 0, Align.CENTER, "...", " ", ""),
            ("1234567890", 1, Align.RIGHT, "..?", " ", "?"),
            ("1234567890", 2, Align.RIGHT, "..?", " ", ".?"),
            ("1234567890", 3, Align.RIGHT, "..?", " ", "..?"),
            ("1234567890", 4, Align.RIGHT, "..?", " ", "..?0"),
            ("1234567890", 5, Align.RIGHT, "..?", " ", "..?90"),
            ("1234567890", 9, Align.RIGHT, "..?", " ", "..?567890"),
            ("1234567890", 10, Align.RIGHT, "..?", " ", "1234567890"),
            ("1234567890", 12, Align.RIGHT, "..?", " ", "  1234567890"),
            ("1234567890", 12, Align.RIGHT, "..?", "<>", "<>1234567890"),
            ("1234567890", 12, Align.RIGHT, "..", "ы", "ыы1234567890"),
            ("1234567890", 8, Align.RIGHT, "х?й", " ", "х?й67890"),
            ("@", 6, Align.LEFT, "", "|¯|_", "@|¯|_|"),
            ("@", 6, Align.RIGHT, "", "|¯|_", "_|¯|_@"),
            ("@", 6, Align.CENTER, "", "|¯|_", "|¯@¯|_"),
            ("@", 2, Align.LEFT, "<|>", " ", "@ "),
            ("@@", 1, Align.LEFT, "<|>", " ", "<"),
            ("@@", 2, Align.LEFT, "<|>", " ", "@@"),
            ("@@@", 2, Align.LEFT, "<|>", " ", "<|"),
            ("@@@", 2, Align.RIGHT, "<|>", " ", "|>"),
            ("@@@", 2, Align.CENTER, "<|>", " ", "<>"),
            ("@@@@", 3, Align.CENTER, "<|>", " ", "<|>"),
            ("|", 7, Align.CENTER, "", "<>", "<><|><>"),
        ],
        ids=format_test_params,
    )
    def test_fit(
        self,
        input: str,
        max_len: int,
        align: Align | str,
        overflow: str,
        fillchar: str,
        expected_fit: str,
    ):
        actual_fit = fit(input, max_len, align, overflow, fillchar)
        assert len(actual_fit) <= max_len
        assert actual_fit == expected_fit

    @pytest.mark.parametrize(
        "input, max_len, align, overflow, expected_cut",
        [
            ("1234567890", 12, None, "‥", "1234567890"),
            ("1234567890", 10, None, "‥", "1234567890"),
            ("1234567890", 9, None, "‥", "12345678‥"),
            ("1234567890", 5, None, "‥", "1234‥"),
            ("1234567890", 2, None, "‥", "1‥"),
            ("1234567890", 1, None, "‥", "‥"),
            ("1234567890", 0, None, "‥", ""),
            ("1234567890", 12, Align.CENTER, "‥", "1234567890"),
            ("1234567890", 10, Align.CENTER, "‥", "1234567890"),
            ("1234567890", 9, Align.CENTER, "‥", "1234‥7890"),
            ("1234567890", 5, Align.CENTER, "‥", "12‥90"),
            ("1234567890", 2, Align.CENTER, "‥", "‥0"),
            ("1234567890", 1, Align.CENTER, "‥", "‥"),
            ("1234567890", 0, Align.CENTER, "‥", ""),
            ("1234567890", 12, Align.RIGHT, "‥", "1234567890"),
            ("1234567890", 10, Align.RIGHT, "‥", "1234567890"),
            ("1234567890", 9, Align.RIGHT, "‥", "‥34567890"),
            ("1234567890", 5, Align.RIGHT, "‥", "‥7890"),
            ("1234567890", 2, Align.RIGHT, "‥", "‥0"),
            ("1234567890", 1, Align.RIGHT, "‥", "‥"),
            ("1234567890", 0, Align.RIGHT, "‥", ""),
            ("1234567890", 0, Align.LEFT, "...", ""),
            ("1234567890", 1, Align.LEFT, "..?", "."),
            ("1234567890", 2, Align.LEFT, "..?", ".."),
            ("1234567890", 3, Align.LEFT, "..?", "..?"),
            ("1234567890", 4, Align.LEFT, "..?", "1..?"),
            ("1234567890", 5, Align.LEFT, "..?", "12..?"),
            ("1234567890", 9, Align.LEFT, "..?", "123456..?"),
            ("1234567890", 10, Align.LEFT, "..?", "1234567890"),
            ("1234567890", 12, Align.LEFT, "..?", "1234567890"),
            ("1234567890", 0, Align.CENTER, "...", ""),
            ("1234567890", 1, Align.CENTER, "..?", "?"),
            ("1234567890", 2, Align.CENTER, "..?", ".?"),
            ("1234567890", 3, Align.CENTER, "..?", "..?"),
            ("1234567890", 4, Align.CENTER, "..?", "..?0"),
            ("1234567890", 5, Align.CENTER, "..?", "1..?0"),
            ("1234567890", 9, Align.CENTER, "..?", "123..?890"),
            ("1234567890", 10, Align.CENTER, "..?", "1234567890"),
            ("1234567890", 12, Align.CENTER, "..?", "1234567890"),
            ("1234567890", 0, Align.CENTER, "...", ""),
            ("1234567890", 1, Align.RIGHT, "..?", "?"),
            ("1234567890", 2, Align.RIGHT, "..?", ".?"),
            ("1234567890", 3, Align.RIGHT, "..?", "..?"),
            ("1234567890", 4, Align.RIGHT, "..?", "..?0"),
            ("1234567890", 5, Align.RIGHT, "..?", "..?90"),
            ("1234567890", 9, Align.RIGHT, "..?", "..?567890"),
            ("1234567890", 10, Align.RIGHT, "..?", "1234567890"),
            ("1234567890", 12, Align.RIGHT, "..?", "1234567890"),
        ],
        ids=format_test_params,
    )
    def test_cut(
        self,
        input: str,
        max_len: int,
        align: Align | str,
        overflow: str,
        expected_cut: str,
    ):
        actual_cut = cut(input, max_len, align, overflow)
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
        assert ours(Iterable, [[1], {2}, {3: 4}, 5]) == [[1], {2}, {3: 4}]

    def test_others(self):
        assert others(Iterable, [[1], {2}, {3: 4}, 5]) == [5]


class TestChunk:
    @pytest.mark.parametrize(
        "size, input, expected",
        [
            (0, range(3), []),
            (1, range(3), [(0,), (1,), (2,)]),
            (2, range(5), [(0, 1), (2, 3), (4,)]),
            (3, range(11), [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9, 10)]),
            (5, range(5), [(0, 1, 2, 3, 4)]),
        ],
        ids=format_test_params,
    )
    def test_chunk(self, size: int, input: Iterable, expected: list):
        assert [*chunk(input, size)] == expected


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
        "limit_level, input, expected",
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
    def test_flatten_irregular_array(
        self, limit_level: int, input: t.List, expected: t.List
    ):
        assert flatten(input, limit_level) == expected


class TestCharRange:
    @pytest.mark.parametrize(
        "input, expected",
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
    def test_char_range(self, input: tuple[str, str], expected: list):
        assert "".join(char_range(*input)) == expected


class TestGetQName:
    T = t.TypeVar("T")

    def _empty_fn(self):
        pass

    @pytest.mark.parametrize(
        "input, expected",
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
            (t.Generic[T], "<typing.Generic[~T]>"),
            (t.Generic[T](), "Generic"),
            (IFilter, "<IFilter>"),
            (StringReplacer, "<StringReplacer>"),
            (StringReplacer("", ""), "StringReplacer"),
            (list[T], "<list>"),
            (list[T](), "list"),
            (Optional[IT], "<typing.Optional[~IT]>"),
            (Union[FT, None], "<typing.Optional[~FT]>"),
            (Union[RT, OT], "<typing.Union[~RT, ~OT]>"),
        ],
        ids=format_test_params,
    )
    def test_get_qname(self, input: t.Any, expected: str):
        assert get_qname(input) == expected


class TestFiltersFV:
    def test_filterf(self):
        assert [*filterf([
            True, False, 0, 1, '', "0", "False", None, [], {}, [0], {0},
        ])] == [
            True, 1, '0', "False", [0], {0},
        ]

    def test_filtern(self):
        assert [*filtern([
            True, False, 0, 1, '', "0", "False", None, [], {}, [0], {0},
        ])] == [
            True, False, 0, 1, '', "0", "False", [], {}, [0], {0},
        ]

    def test_filterfv(self):
        assert {**filterfv({
            'a': 0, 'b': 1, 'c': True, 'd': False, 'e': '', 'f': 'False',
            'h': [], 'i': {}, 'j': [0], 'k': {0},
        })} == {
            'a': 0, 'b': 1, 'c': True, 'd': False, 'e': '', 'f': 'False',
            'h': [], 'i': {}, 'j': [0], 'k': {0},
        }

    def test_filternv(self):
        assert {**filternv({
            'a': 0, 'b': 1, 'c': True, 'd': False, 'e': '', 'f': 'False',
            'g': None, 'h': [], 'i': {}, 'j': [0], 'k': {0},
        })} == {
            'a': 0, 'b': 1, 'c': True, 'd': False, 'e': '', 'f': 'False',
            'h': [], 'i': {}, 'j': [0], 'k': {0},
        }
