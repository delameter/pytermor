# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

import os
import sys
from abc import ABCMeta, abstractmethod
import typing as t
import logging

logger = logging.getLogger('pytermor')
logger.addHandler(logging.NullHandler())


T = t.TypeVar('T')
""" Any """


def get_terminal_width(default: int = 80, padding: int = 2) -> int:
    """
    get_terminal_width
    :return:  terminal_width
    """
    try:
        import shutil as _shutil
        return _shutil.get_terminal_size().columns - padding
    except ImportError:
        return int(os.environ.get("COLUMNS", default))


def wait_key() -> t.AnyStr|None:
    """
    Wait for a key press on the console and return it.
    """
    if os.name == 'nt':
        import msvcrt
        return msvcrt.getch()

    import termios
    fd = sys.stdin.fileno()

    oldterm = termios.tcgetattr(fd)
    newattr = termios.tcgetattr(fd)
    newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(fd, termios.TCSANOW, newattr)

    result = None
    try:
        result = sys.stdin.read(1)
    except IOError:
        pass
    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
    return result


class LogicError(Exception):
    pass


class Renderable(t.Sized, metaclass=ABCMeta):
    """
    Renderable abstract class. Can be inherited if the default style
    overlaps resolution mechanism implemented in `Text` is not good enough
    and you want to implement your own.
    """

    @abstractmethod
    def render(self, renderer=None) -> str:
        raise NotImplemented

    @abstractmethod
    def raw(self) -> str:
        raise NotImplemented

    @abstractmethod
    def __len__(self) -> int:
        raise NotImplemented
