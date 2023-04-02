# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
"""
A
"""

from __future__ import annotations

import math
import os
import sys
import typing as t
import unicodedata
from collections import deque
from io import StringIO
from itertools import chain
from sys import getsizeof, stderr

from .ansi import (
    make_query_cursor_position,
    decompose_request_cursor_position,
    make_erase_in_line,
    make_set_cursor_x_abs,
)
from .common import UserAbort, UserCancel, HSV, RGB


# -----------------------------------------------------------------------------


def hex_to_rgb(hex_value: int) -> t.Tuple[int, int, int]:
    """
    Transforms ``hex_value`` in *int* format into a tuple of three
    integers corresponding to **red**, **blue** and **green** channel value
    respectively. Values are within [0; 255] range.

        >>> hex_to_rgb(0x80ff80)
        (128, 255, 128)

    :param hex_value: RGB value.
    :returns: R, G, B channel values correspondingly.
    """
    if not isinstance(hex_value, int):
        raise TypeError(f"Argument type should be 'int', got: {type(hex_value)}")

    return ((hex_value & 0xFF0000) >> 16, (hex_value & 0xFF00) >> 8, (hex_value & 0xFF))


def rgb_to_hex(r: int, g: int, b: int) -> int:
    """
    Transforms RGB value in a three-integers form ([0; 255], [0; 255], [0; 255])
    to an one-integer form.

        >>> hex(rgb_to_hex(0, 128, 0))
        '0x8000'

    :param r: value of red channel.
    :param g: value of green channel.
    :param b: value of blue channel.
    :return: RGB value.
    """
    return (r << 16) + (g << 8) + b


def hsv_to_rgb(h: float, s: float, v: float) -> RGB | t.Tuple[int, int, int]:
    """
    Transforms HSV value in three-floats form (where 0 <= h < 360, 0 <= s <= 1,
    and 0 <= v <= 1) into RGB three-integer form ([0; 255], [0; 255], [0; 255]).

        >>> hsv_to_rgb(270, 2/3, 0.75)
        (128, 64, 192)

    :param h: hue channel value.
    :param s: saturation channel value.
    :param v: value channel value.
    :return: R, G, B channel values correspondingly.
    """
    h = 0.0 if h == 360.0 else h / 60.0
    fract = h - math.floor(h)

    p = v * (1.0 - s)
    q = v * (1.0 - s * fract)
    t = v * (1.0 - s * (1.0 - fract))

    if 0.0 <= h < 1.0:
        r, g, b = v, t, p
    elif 1.0 <= h < 2.0:
        r, g, b = q, v, p
    elif 2.0 <= h < 3.0:
        r, g, b = p, v, t
    elif 3.0 <= h < 4.0:
        r, g, b = p, q, v
    elif 4.0 <= h < 5.0:
        r, g, b = t, p, v
    elif 5.0 <= h < 6.0:
        r, g, b = v, p, q
    else:
        r, g, b = 0, 0, 0

    r, g, b = (math.ceil(255 * c) for c in (r, g, b))
    return r, g, b


def rgb_to_hsv(r: int, g: int, b: int) -> t.Tuple[float, float, float]:
    """
    Transforms RGB value in a three-integers form ([0; 255], [0; 255], [0; 255]) to an
    HSV in three-floats form such as (0 <= h < 360, 0 <= s <= 1, and 0 <= v <= 1).

        >>> rgb_to_hsv(0, 0, 255)
        HSV(hue=240.0, saturation=1.0, value=1.0)

    :param r: value of red channel.
    :param g: value of green channel.
    :param b: value of blue channel.
    :returns: H, S, V channel values correspondingly.
    """
    # fmt: off
    # https://en.wikipedia.org/wiki/HSL_and_HSV#From_RGB

    rn, gn, bn = r / 255, g / 255, b / 255
    vmax = max(rn, gn, bn)
    vmin = min(rn, gn, bn)
    c = vmax - vmin
    v = vmax

    h = 0.0
    if c == 0: pass
    elif v == rn:  h = 60 * (0 + (gn - bn) / c)
    elif v == gn:  h = 60 * (2 + (bn - rn) / c)
    elif v == bn:  h = 60 * (4 + (rn - gn) / c)

    if v == 0:     s = 0
    else:          s = c / v

    if h < 0:      h += 360

    return HSV(h, s, v)
    # fmt: on


def hex_to_hsv(hex_value: int) -> HSV:
    """
    Transforms ``hex_value`` in *int* form into named tuple consisting of three floats
    corresponding to **hue**, **saturation** and **value** channel values respectively.
    Hue is within [0, 359] range, both saturation and value are within [0; 1] range.

        >>> hex_to_hsv(0x999999)
        HSV(hue=0.0, saturation=0.0, value=0.6)

    :param hex_value: RGB value.
    :returns: named tuple with H, S and V channel values
    """
    return rgb_to_hsv(*hex_to_rgb(hex_value))


def hsv_to_hex(h: float, s: float, v: float) -> int:
    """
    Transforms HSV value in three-floats form (where 0 <= h < 360, 0 <= s <= 1,
    and 0 <= v <= 1) into an one-integer form.

        >>> hex(hsv_to_hex(90, 0.5, 0.5))
        '0x608040'

    :param h: hue channel value.
    :param s: saturation channel value.
    :param v: value channel value.
    :return: RGB value.
    """
    return rgb_to_hex(*hsv_to_rgb(h, s, v))


def lab_to_rgb(l_s: float, a_s: float, b_s: float) -> t.Tuple[int, int, int]:
    """
    @TODO

    :param l_s:
    :param a_s:
    :param b_s:
    :return:
    """
    var_Y: float = (l_s + 16.) / 116.
    var_X: float = a_s / 500. + var_Y
    var_Z: float = var_Y - b_s / 200.

    if pow(var_Y, 3) > 0.008856:
        var_Y = pow(var_Y, 3)
    else:
        var_Y = (var_Y - 16. / 116.) / 7.787
    if pow(var_X, 3) > 0.008856:
        var_X = pow(var_X, 3)
    else:
        var_X = (var_X - 16. / 116.) / 7.787
    if pow(var_Z, 3) > 0.008856:
        var_Z = pow(var_Z, 3)
    else:
        var_Z = (var_Z - 16. / 116.) / 7.787

    X: float = 95.047 * var_X  # ref_X =  95.047     Observer= 2°, Illuminant= D65
    Y: float = 100.000 * var_Y  # ref_Y = 100.000
    Z: float = 108.883 * var_Z  # ref_Z = 108.883

    var_X = X / 100.  # X from 0 to  95.047      (Observer = 2°, Illuminant = D65)
    var_Y = Y / 100.  # Y from 0 to 100.000
    var_Z = Z / 100.  # Z from 0 to 108.883

    var_R: float = var_X * 3.2406 + var_Y * -1.5372 + var_Z * -0.4986
    var_G: float = var_X * -0.9689 + var_Y * 1.8758 + var_Z * 0.0415
    var_B: float = var_X * 0.0557 + var_Y * -0.2040 + var_Z * 1.0570

    if var_R > 0.0031308:
        var_R = 1.055 * pow(var_R, (1 / 2.4)) - 0.055
    else:
        var_R = 12.92 * var_R
    if var_G > 0.0031308:
        var_G = 1.055 * pow(var_G, (1 / 2.4)) - 0.055
    else:
        var_G = 12.92 * var_G
    if var_B > 0.0031308:
        var_B = 1.055 * pow(var_B, (1 / 2.4)) - 0.055
    else:
        var_B = 12.92 * var_B

    return round(var_R * 255.), round(var_G * 255.), round(var_B * 255.)


# -----------------------------------------------------------------------------

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
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags|os.O_NONBLOCK)

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

    cha_seq = make_set_cursor_x_abs(1).assemble()
    qcp_seq = make_query_cursor_position().assemble()

    sys.stdout.write(cha_seq)
    sys.stdout.write(char)
    sys.stdout.write(qcp_seq)
    sys.stdout.write("\r")

    response = ""
    while (pos := decompose_request_cursor_position(response)) is None:
        response += wait_key(block=True) or ""

    if clear_after:
        sys.stdout.write(make_erase_in_line(2).assemble())

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


# -----------------------------------------------------------------------------

try:
    from reprlib import repr
except ImportError:
    pass


def total_size(
    o: t.Any, handlers: t.Dict[t.Any, t.Iterator] = None, verbose: bool = False
) -> int:
    """
    Return the approximate memory footprint of an object and all of its contents.

    Automatically finds the contents of the following builtin containers and
    their subclasses: *tuple, list, deque, dict, set* and *frozenset*.
    To search other containers, add handlers to iterate over their contents::

        handlers = {ContainerClass: iter, ContainerClass2: ContainerClass2.get_elements}

    :param o:
    :param handlers:
    :param verbose:
    """
    # origin: https://code.activestate.com/recipes/577504/

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
