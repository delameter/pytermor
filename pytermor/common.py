# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod
from typing import TypeVar, Generic, AnyStr, Sized

T = TypeVar('T')
""" Any """

Printable = TypeVar('Printable', str, bytes, 'Renderable')


class Renderable(Sized, metaclass=ABCMeta):
    @abstractmethod
    def render(self) -> str:
        raise NotImplemented

    def __str__(self) -> str:
        return self.render()


class Registry(Generic[T]):
    """
    Registry of elements of specified type.
    """
    @classmethod
    def resolve(cls, name: str) -> T:
        """
        Case-insensitive search through registry contents.

        :param name: name of the value to look up for.
        :return:     value or KeyError if nothing found.
        """
        name_norm = name.upper()
        if (value := getattr(cls, name_norm, None)) is not None:
            return value
        raise KeyError(f'No item named "{name_norm}" (<- "{name}") is found '
                       f'in {cls.__name__} registry')


def get_terminal_width() -> int:
    """
    get_terminal_width
    :return:  terminal_width
    """
    try:
        import shutil as _shutil
        return _shutil.get_terminal_size().columns - 2
    except ImportError:
        return 80


class LogicError(Exception):
    pass

