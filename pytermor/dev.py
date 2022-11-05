# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

from .color import Color256
from . import index_256, ColorRGB, Renderable
from abc import abstractmethod, ABCMeta
from typing import List, Tuple, Type, Dict


class Class(metaclass=ABCMeta):
    PUBLIC_STATIC_CONST = 3
    _PRIVATE_STATIC_CONST  = 4
    """ OLOLO """

    def __init__(self):
        self.public_field = "field"
        self._private_field = 3232

    def method(self, arg1:int , arg2: float) -> Tuple[str, List[Type]]:
        """
        Some description

        :param arg1: Some data
        :param arg2: Some data
        """
        return str(arg1), [type(arg2)]

    @property
    def getter(self) -> str:
        """
        Getter
        """
        return self.__class__.__qualname__

    @classmethod
    def class_method(cls, e: Exception) -> int:
        """
        Class
        :param e:
        """
        return 1 + 2

    @staticmethod
    def static_method() -> List[int, float]|Dict[float]|None:
        """
        Static
        """
        return None

    @abstractmethod
    def abstract_method(self) -> None:
        """
        abs
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def abstract_property(self) -> str:
        """ abs meth """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def abstract_class_method(cls):
        """ abs c;lass meth """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def abstract_static_method() -> Color256:
        """ abs STATIC meth """
        raise NotImplementedError

    def _protected(self) -> int:
        """
        PROTEC
        :return:
        """
        return 2

class SubClass(Class):
    def abstract_method(self) -> None:
        """
        concrete method
        """
        return None

    @property
    def abstract_property(self) -> str:
        """
        concrete prop
        """
        return super().__class__.__qualname__

    @classmethod
    def abstract_class_method(cls):
        pass

    @staticmethod
    def abstract_static_method() -> Color256:
        return index_256.GRAY_82

    @property
    def getter(self) -> str:
        """
        SUPA GGETTA
        """
        return super().getter()


MODULE_LEVEL_CONST_PUBLIC = ColorRGB({2, 3}.pop())
"""
PUBLIC
"""

_MODULE_LEVEL_CONST_PRIVUATE = min(3,8)

_MODULE_LEVEL_CONST_PRIVUATE_DOCS = max(212,32)
"""
SASADSA
"""

def fn() -> int:
    """
    SASAC
    """
    ds = 2
    def yyy() -> int:
        """
        NESTED YYY
        :return: d
        """
        return 3

    return yyy() + _MODULE_LEVEL_CONST_PRIVUATE_DOCS


class Ex(Exception):
    pass


class Level1Class:
    """dscsd"""
    class Level2Class():
        """ asc
        saca'

        """
        class Level3Class():
            """
            .. warning ::

                allahu akbar
            """
            class _Level4Class(Renderable):
                """
                AA
                """
                print('4')

    def prissant(self):
        print('сновымодомэ')

class Level4Class2(Level1Class.Level2Class.Level3Class._Level4Class):
    def raw(self) -> str: return ""

    class R(Exception): pass
