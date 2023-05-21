# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
"""
A
"""

from __future__ import annotations

import os
import sys
import typing as t
import unicodedata
from io import StringIO

from .ansi import (
    make_query_cursor_position,
    make_set_cursor_column,
    make_clear_line,
)
from .exception import UserCancel, UserAbort
from .parser import decompose_report_cursor_position


def get_terminal_width(fallback: int = 80, pad: int = 2) -> int:
    """
    Return current terminal width with an optional "safety buffer", which
    ensures that no unwanted line wrapping will happen.

    :param fallback: Default value when shutil is unavailable and environment
                     variable COLUMNS is unset.
    :param pad:      Additional safety space to prevent unwanted line wrapping.
    """
    try:
        import shutil as _shutil

        return _shutil.get_terminal_size().columns - pad
    except ImportError:
        pass

    try:
        return int(os.environ.get("COLUMNS", fallback))
    except ValueError:
        pass

    return fallback


def get_preferable_wrap_width(force_width: int = None) -> int:
    """
    Return preferable terminal width for comfort reading of wrapped text (max=120).

    :param force_width:
               Ignore current terminal width and use this value as a result.
    """
    if isinstance(force_width, int) and force_width > 1:
        return force_width
    return min(120, get_terminal_width())


def wait_key(block: bool = True) -> t.AnyStr | None:
    """
    Wait for a key press on the console and return it.

    :param block: Determines setup of O_NONBLOCK flag.
    """
    # http://love-python.blogspot.com/2010/03/getch-in-python-get-single-character.html
    import sys, termios, fcntl

    if os.name == "nt":
        import msvcrt

        return msvcrt.getch()

    fd = sys.stdin.fileno()

    oldterm = termios.tcgetattr(fd)
    newattr = termios.tcgetattr(fd)
    newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(fd, termios.TCSANOW, newattr)

    oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
    if not block:
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

    result = None
    try:
        result = sys.stdin.read(1)
    except IOError:
        pass
    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
        if not block:
            fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)

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

    :param attempts:    Set how many times the user is allowed to perform the
                        input before auto-cancellation (or auto-confirmation) will
                        occur. 1 means there will be only one attempt, the first one.
                        When set to -1, allows to repeat the input infinitely.
    :param default:     Default value that will be returned when user presses invalid
                        key (e.g. :kbd:`Backspace`, :kbd:`Ctrl+Q` etc.) and his
                        ``attempts`` counter decreases to 0. Setting this to *True*
                        effectively means that the user's only way to deny the request
                        is to press :kbd:`N` or :kbd:`Ctrl+C`, while all the other
                        keys are treated as :kbd:`Y`.
    :param keymap:      Key to result mapping.
    :param prompt:      String to display before each input attempt. Default is:
                        ``"Press Y to continue, N to cancel, Ctrl+C to abort: "``
    :param quiet:       If set to *True*, suppress all messages to stdout and work
                        silently.
    :param required:    If set to *True*, raise `UserCancel` or `UserAbort` when
                        user rejects to confirm current action. If set to *False*,
                        do not raise any exceptions, just return *False*.
    :raises UserAbort:  On corresponding event, if `required` is *True*.
    :raises UserCancel: On corresponding event, if `required` is *True*.
    :returns:           *True* if there was a confirmation by user's input or
                        automatically, *False* otherwise.
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


def get_char_width(char: str, block: bool) -> int:
    """
    General-purpose method for getting width of a character in terminal columns.

    Uses `guess_char_width()` method based on `unicodedata` package,
    or/and QCP-RCP ANSI control sequence communication protocol.

    :param char:  Input char.
    :param block: Set to *True* if you prefer slow, but 100% accurate
                  `measuring <measure_char_width>` (which **blocks** and
                  requires an output tty), or *False* for a device-independent,
                  deterministic and non-blocking `guessing <guess_char_width>`,
                  which works most of the time, although there could be rare
                  cases when it is not precise enough.
    """
    if block:
        return measure_char_width(char)
    return guess_char_width(char)


def measure_char_width(char: str, clear_after: bool = True) -> int:
    """
    Low-level function that returns the exact character width in terminal columns.

    The main idea is to reset a cursor position to 1st column, print the required
    character and `QCP <make_query_cursor_position()>` control sequence; after that
    wait for the response and `parse <decompose_request_cursor_position()>` it.
    Normally it contains the cursor coordinates, which can tell the exact width of a
    character in question.

    After reading the response clear it from the screen and reset the cursor to
    column 1 again.

    .. important ::

        The ``stdout`` must be a tty. If it is not, consider using
        `guess_char_width()` instead, or ``IOError`` will be raised.

    .. warning ::

        Invoking this method produces a bit of garbage in the output stream,
        which looks like this: ``⠁\x1b[3;2R``. By default, it is hidden using
        screen line clearing (see ``clear_after``).

    .. warning ::

        Invoking this method may **block** infinitely. Consider using a thread
        or set a timeout for the main thread using a signal if that is unwanted.

    :param char:        Input char.
    :param clear_after: Send `EL <make_erase_in_line()>` control sequence after the
                        terminal response to hide excessive utility information from
                        the output if set to *True*, or leave it be otherwise.
    :raises IOError:    If ``stdout`` is not a terminal emulator.
    """
    if not sys.stdout.isatty():
        raise IOError("Output device should be a terminal emulator")

    cha_seq = make_set_cursor_column(1).assemble()
    qcp_seq = make_query_cursor_position().assemble()

    sys.stdout.write(cha_seq)
    sys.stdout.write(char)
    sys.stdout.write(qcp_seq)
    sys.stdout.write("\r")

    response = ""
    while (pos := decompose_report_cursor_position(response)) is None:
        response += wait_key(block=True) or ""

    if clear_after:
        sys.stdout.write(make_clear_line().assemble())

    pos_y, pos_x = pos
    return pos_x - 1  # 1st coordinate is the start of X-axis


def guess_char_width(c: str) -> int:
    """
    Determine how many columns are needed to display a character in a terminal.

    Returns -1 if the character is not printable.
    Returns 0, 1 or 2 for other characters.

    Utilizes `unicodedata` table. A terminal emulator is unnecessary.

    :param c:
    """
    # origin: _pytest._io.wcwidth <https://pypi.org/project/pytest>

    o = ord(c)

    # ASCII fast path.
    if 0x20 <= o < 0x07F:
        return 1

    # Some Cf/Zp/Zl characters which should be zero-width.
    if (
        o == 0x0000
        or 0x200B <= o <= 0x200F
        or 0x2028 <= o <= 0x202E
        or 0x2060 <= o <= 0x2063
    ):
        return 0

    category = unicodedata.category(c)

    # Control characters.
    if category == "Cc":
        return -1

    # Combining characters with zero width.
    if category in ("Me", "Mn"):
        return 0

    # Full/Wide east asian characters.
    if unicodedata.east_asian_width(c) in ("F", "W"):
        return 2

    return 1


