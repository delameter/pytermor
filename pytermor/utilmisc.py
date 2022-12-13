# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""

.. testsetup:: *

    from pytermor.utilmisc import *

"""
from __future__ import annotations

import itertools
import os
import sys
import typing as t
from collections import deque
from io import StringIO
from itertools import chain
from sys import getsizeof, stderr

from .common import UserAbort, UserCancel


def get_qname(obj: t.Any) -> str:
    if isinstance(obj, type):
        return obj.__qualname__
    if isinstance(obj, object):
        return obj.__class__.__qualname__
    return str(obj)


def chunk(arr_range, arr_size):
    arr_range = iter(arr_range)
    return iter(lambda: tuple(itertools.islice(arr_range, arr_size)), ())


def get_terminal_width(default: int = 80, padding: int = 2) -> int:
    """
    Return current terminal width with an optional "safety buffer".
    """
    try:
        import shutil as _shutil

        return _shutil.get_terminal_size().columns - padding
    except ImportError:
        return int(os.environ.get("COLUMNS", default))


def get_preferable_wrap_width(force_width: int = None) -> int:
    """
    Return preferable terminal width for comfort reading of wrapped text.
    """
    if isinstance(force_width, int) and force_width > 1:
        return force_width
    return min(120, get_terminal_width())


def wait_key() -> t.AnyStr | None:
    """
    Wait for a key press on the console and return it.

    :raises: EOFError
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


def confirm(
    attempts: int = 1,
    default: bool = False,
    keymap: t.Mapping[str, bool] = None,
    prompt: str = None,
    quiet: bool = False,
    required: bool = False,
) -> bool:
    """
    Ensure the next action is manually confirmed by user. Print the terminal
    prompt with ``prompt`` text and wait for a keypress. Return *True*
    if user pressed :kbd:`Y` and *False* in all the other cases (by default).

    Valid keys are :kbd:`Y` and :kbd:`N` (case insensitive), while all the other keys
    and combinations are considered invalid, and will trigger the return of the
    ``default`` value, which is *False* if not set otherwise. In other words,
    by default the user is expected to press either :kbd:`Y` or :kbd:`N`, and if
    that's not the case, the confirmation request will be automatically failed.

    :kbd:`Ctrl+C` instantly aborts the confirmation process regardless of attempts
    count and raises `UserAbort`.

    Example keymap (default one)::

        keymap = {"y": True, "n": False}

    :param attempts:  Set how many times the user is allowed to perform the
                      input before auto-cancellation (or auto-confirmation) will
                      occur. 1 means there will be only one attempt, the first one.
                      When set to -1, allows to repeat the input infinitely.
    :param default:   Default value that will be returned when user presses invalid
                      key (e.g. :kbd:`Backspace`, :kbd:`Ctrl+Q` etc.) and his
                      ``attempts`` counter decreases to 0. Setting this to *True*
                      effectively means that the user's only way to deny the request
                      is to press :kbd:`N` or :kbd:`Ctrl+C`, while all the other
                      keys are treated as :kbd:`Y`.
    :param keymap:    Key to result mapping.
    :param prompt:    String to display before each input attempt. Default is:
                      ``"Press Y to continue, N to cancel, Ctrl+C to abort: "``
    :param quiet:     If set to *True*, suppress all messages to stdout and work
                      silently.
    :param required:  If set to *True*, raise `UserCancel` or `UserAbort` when
                      user rejects to confirm current action. If set to *False*,
                      do not raise any exceptions, just return *False*.
    :returns:         *True* if there was a confirmation by user's input or
                      automatically, *False* otherwise.
    :raises: UserAbort
    :raises: UserCancel
    """

    def check_required(v: bool, exc: t.Type = UserCancel):
        if v is False and required:
            raise exc
        return v

    if not keymap:
        keymap = {"y": True, "n": False}
    if prompt is None:
        prompt = "Press Y to continue, N to cancel, Ctrl+C to abort: "

    file = sys.stdout
    if quiet:
        file = StringIO()

    while attempts != 0:
        print(prompt, end="", flush=True, file=file)
        try:
            inp = wait_key()
        except EOFError:
            inp = None
        except KeyboardInterrupt:
            return check_required(False, UserAbort)

        inp = (inp or "").lower()
        print(inp, file=file)
        if inp in keymap.keys():
            return check_required(keymap.get(inp))

        print("Invalid key", file=file)
        attempts -= 1

    print(f"Auto-{'confirming' if default else 'cancelling'} the action", file=file)
    return check_required(default)


# -----------------------------------------------------------------------------
# origin: https://code.activestate.com/recipes/577504/

try:
    from reprlib import repr
except ImportError:
    pass


def total_size(
    o: t.Any, handlers: t.Dict[t.Any, t.Iterator] = None, verbose: bool = False
) -> int:
    """Returns the approximate memory footprint of an object and all of its contents.

    Automatically finds the contents of the following builtin containers and
    their subclasses:  tuple, list, deque, dict, set and frozenset.
    To search other containers, add handlers to iterate over their contents::

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
