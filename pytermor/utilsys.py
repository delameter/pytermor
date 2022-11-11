# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""

.. testsetup:: *

    from pytermor.utilsys import *

"""
from __future__ import annotations

import os
import sys
import typing as t
from collections import deque
from itertools import chain
from sys import getsizeof, stderr


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


def get_preferable_wrap_width(force_width: int|bool) -> int:
    if isinstance(force_width, int) and force_width > 1:
        return force_width
    return min(120, get_terminal_width())


def wait_key() -> t.AnyStr | None:
    """
    Wait for a key press on the console and return it.
    """
    if os.name == "nt":
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


# -----------------------------------------------------------------------------
# origin: https://code.activestate.com/recipes/577504/

try:
    from reprlib import repr
except ImportError:
    pass


def total_size(o: t.Any, handlers: t.Dict[t.Any, t.Iterator] = None, verbose: bool = False) -> int:
    """Returns the approximate memory footprint an object and all of its contents.

    Automatically finds the contents of the following builtin containers and
    their subclasses:  tuple, list, deque, dict, set and frozenset.
    To search other containers, add handlers to iterate over their contents:

        handlers = {SomeContainerClass: iter,
                    OtherContainerClass: OtherContainerClass.get_elements}

    """
    dict_handler = lambda d: chain.from_iterable(d.items())
    all_handlers = {
        tuple: iter,
        list: iter,
        deque: iter,
        dict: dict_handler,
        set: iter,
        frozenset: iter,
    }
    all_handlers.update(handlers or {})  # user handlers take precedence
    seen = set()  # track which object id's have already been seen
    default_size = getsizeof(0)  # estimate sizeof object without __sizeof__

    def sizeof(o):
        if id(o) in seen:  # do not double count the same object
            return 0
        seen.add(id(o))
        s = getsizeof(o, default_size)

        if verbose:
            print(s, type(o), repr(o), file=stderr)

        for typ, handler in all_handlers.items():
            if isinstance(o, typ):
                s += sum(map(sizeof, handler(o)))
                break
        return s

    return sizeof(o)
