# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

from abc import abstractmethod

import pytest

from pytermor.common import ExtendedEnum


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
