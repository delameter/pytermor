# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import os
import re
import typing as t
from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from collections.abc import Iterable
from typing import Optional, Union

import pytest

from pytermor import Align, Color256, IFilter, StringReplacer, FT, RT
from pytermor.common import ExtendedEnum, but, char_range, chunk, flatten, get_qname, \
    only, others, \
    ours
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
    @pytest.mark.parametrize("input", [
        Align.LEFT,
        Align.CENTER,
        Align.RIGHT,
        '<',
        None,
        'LEFT',
        pytest.param(2, marks=pytest.mark.xfail(raises=KeyError)),
    ])
    def test_align(self, input:str|Align):
        assert isinstance(Align.resolve(input), (Align, str))

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
    @pytest.mark.parametrize("size, input, expected", [
        (0, range(3), []),
        (1, range(3), [(0,), (1,), (2,)]),
        (2, range(5), [(0, 1), (2, 3), (4,)]),
        (3, range(11), [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9, 10)]),
        (5, range(5), [(0, 1, 2, 3, 4)]),
    ], ids=format_test_params)
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
    @pytest.mark.parametrize("input, expected", [
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
        (("퟾", ""), "\ud7fe\ud7ff\ue000\ue001"),  # UTF-16 surrogates shall be excluded
        pytest.param(("aaa", "bbb"), "", marks=pytest.mark.xfail(raises=TypeError)),
        pytest.param(("", ""), "", marks=pytest.mark.xfail(raises=TypeError)),
    ], ids=format_test_params)
    def test_char_range(self, input: tuple[str, str], expected: list):
        assert ''.join(char_range(*input)) == expected


class TestGetQName:
    T = t.TypeVar("T")

    def _empty_fn(self):
        pass

    @pytest.mark.parametrize('input, expected', [
        ("avc", "str"),
        (b"avc", "bytes"),
        (b"a", "bytes"),
        (23, "int"),
        (23., "float"),
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
    ], ids=format_test_params)
    def test_get_qname(self, input: t.Any, expected: str):
        assert get_qname(input) == expected
