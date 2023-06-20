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
import re
import sys
import typing as t
import unicodedata
from io import StringIO

from .ansi import (
    ColorTarget,
    IntCode,
    SequenceCSI,
    SequenceFp,
    SequenceOSC,
    SequenceSGR,
    SequenceST,
)
from .exception import UserAbort, UserCancel

RCP_REGEX = re.compile(R"\x1b\[(\d+);(\d+)R")
"""
Regular expression for :abbr:`RCP (Report Cursor Position)` sequence parsing. 
See `decompose_report_cursor_position()`.

:meta hide-value:
"""


# SGR sequences assembly ------------------------------------------------------


def make_color_256(code: int, target: ColorTarget = ColorTarget.FG) -> SequenceSGR:
    """
    Wrapper for creation of `SequenceSGR` that sets foreground
    (or background) to one of 256-color palette value.:

        >>> make_color_256(141)
        <SGR[38;5;141m]>

    .. seealso ::
        `Color256` class.

    :param code:  Index of the color in the palette, 0 -- 255.
    :param target:
    :example:     ``ESC [38;5;141m``
    """

    SequenceSGR.validate_extended_color(code)
    return SequenceSGR(target.open_code, IntCode.EXTENDED_MODE_256, code)


def make_color_rgb(
    r: int, g: int, b: int, target: ColorTarget = ColorTarget.FG
) -> SequenceSGR:
    """
    Wrapper for creation of `SequenceSGR` operating in True Color mode (16M).
    Valid values for ``r``, ``g`` and ``b`` are in range of [0; 255]. This range
    linearly translates into [:hex:`0x00`; :hex:`0xFF`] for each channel. The result
    value is composed as ":hex:`#RRGGBB`". For example, a sequence with color of
    :hex:`#ff3300` can be created with::

        >>> make_color_rgb(255, 51, 0)
        <SGR[38;2;255;51;0m]>

    .. seealso ::
        `ColorRGB` class.

    :param r:  Red channel value, 0 -- 255.
    :param g:  Blue channel value, 0 -- 255.
    :param b:  Green channel value, 0 -- 255.
    :param target:
    :example:  ``ESC [38;2;255;51;0m``
    """

    [SequenceSGR.validate_extended_color(color) for color in [r, g, b]]
    return SequenceSGR(target.open_code, IntCode.EXTENDED_MODE_RGB, r, g, b)


# CSI / Cursor position control sequences assembly ----------------------------


def make_reset_cursor() -> SequenceCSI:
    """
    Create :abbr:`CUP (Cursor Position)` sequence without params, which moves
    the cursor to top left corner of the screen. See `make_set_cursor()`.

    :example:  ``ESC [H``
    """
    return make_set_cursor()


def make_set_cursor(line: int = 1, column: int = 1) -> SequenceCSI:
    """
    Create :abbr:`CUP (Cursor Position)` sequence that moves the cursor to
    specified amount `line` and `column`. The values are 1-based, i.e. (1; 1)
    is top left corner of the screen.

    .. note ::
        Both sequence params are optional and defaults to 1 if omitted, e.g.
        ``ESC [;3H`` is effectively ``ESC [1;3H``, and ``ESC [4H`` is the
        same as ``ESC [4;H`` or ``ESC [4;1H``.

    :example:  ``ESC [9;15H``
    """
    SequenceCSI.validate_line_abs_value(line)
    SequenceCSI.validate_column_abs_value(column)
    return SequenceCSI("H", line, column, abbr="CUP")


def make_move_cursor_up(lines: int = 1) -> SequenceCSI:
    """
    Create :abbr:`CUU (Cursor Up)` sequence that moves the cursor up by
    specified amount of `lines`. If the cursor is already at the top of the
    screen, this has no effect.

    :example:  ``ESC [2A``
    """
    SequenceCSI.validate_line_rel_value(lines)
    return SequenceCSI("A", lines, abbr="CUU")


def make_move_cursor_down(lines: int = 1) -> SequenceCSI:
    """
    Create :abbr:`CUD (Cursor Down)` sequence that moves the cursor down by
    specified amount of `lines`. If the cursor is already at the bottom of the
    screen, this has no effect.

    :example:  ``ESC [3B``
    """
    SequenceCSI.validate_line_rel_value(lines)
    return SequenceCSI("B", lines, abbr="CUD")


def make_move_cursor_left(columns: int = 1) -> SequenceCSI:
    """
    Create :abbr:`CUB (Cursor Back)` sequence that moves the cursor left by
    specified amount of `columns`. If the cursor is already at the left edge of
    the screen, this has no effect.

    :example:  ``ESC [4D``
    """
    SequenceCSI.validate_column_rel_value(columns)
    return SequenceCSI("D", columns, abbr="CUB")


def make_move_cursor_right(columns: int = 1) -> SequenceCSI:
    """
    Create :abbr:`CUF (Cursor Forward)` sequence that moves the cursor right by
    specified amount of `columns`. If the cursor is already at the right edge
    of the screen, this has no effect.

    :example:  ``ESC [5C``
    """
    SequenceCSI.validate_column_rel_value(columns)
    return SequenceCSI("C", columns, abbr="CUF")


def make_move_cursor_up_to_start(lines: int = 1) -> SequenceCSI:
    """
    Create :abbr:`CPL (Cursor Previous Line)` sequence that moves the cursor
    to the beginning of the line and up by specified amount of `lines`.

    :example:  ``ESC [2F``
    """
    SequenceCSI.validate_line_rel_value(lines)
    return SequenceCSI("F", lines, abbr="CPL")


def make_move_cursor_down_to_start(lines: int = 1) -> SequenceCSI:
    """
    Create :abbr:`CNL (Cursor Next Line)` sequence that moves the cursor
    to the beginning of the line and down by specified amount of `lines`.

    :example:  ``ESC [3E``
    """
    SequenceCSI.validate_line_rel_value(lines)
    return SequenceCSI("E", lines, abbr="CNL")


def make_set_cursor_line(line: int = 1) -> SequenceCSI:
    """
    Create :abbr:`VPA (Vertical Position Absolute)` sequence that sets
    cursor vertical position to `line`.

    :example:       ``ESC [9d``
    """
    SequenceCSI.validate_line_abs_value(line)
    return SequenceCSI("d", line, abbr="VPA")


def make_set_cursor_column(column: int = 1) -> SequenceCSI:
    """
    Create :abbr:`CHA (Cursor Character Absolute)` sequence that sets
    cursor horizontal position to `column`.

    :param column:  New cursor horizontal position.
    :example:       ``ESC [15G``
    """
    SequenceCSI.validate_column_abs_value(column)
    return SequenceCSI("G", column, abbr="CHA")


def make_query_cursor_position() -> SequenceCSI:
    """
    Create :abbr:`QCP (Query Cursor Position)` sequence that requests an output
    device to respond with a structure containing current cursor coordinates
    (`RCP <decompose_request_cursor_position()>`).

    .. warning ::

        Sending this sequence to the terminal may **block** infinitely. Consider
        using a thread or set a timeout for the main thread using a signal.

    :example:   ``ESC [6n``
    """

    return SequenceCSI("n", 6, abbr="QCP")


# CSI / Erase sequences assembly ----------------------------------------------


def make_erase_in_display(mode: int = 0) -> SequenceCSI:
    """
    Create :abbr:`ED (Erase in Display)` sequence that clears a part of the screen
    or the entire screen. Cursor position does not change.

    :param mode:  .. ::

                  Sequence operating mode.

                     - If set to 0, clear from cursor to the end of the screen.
                     - If set to 1, clear from cursor to the beginning of the screen.
                     - If set to 2, clear the entire screen.
                     - If set to 3, clear terminal history (xterm only).

    :example:     ``ESC [0J``
    """
    if not (0 <= mode <= 3):
        raise ValueError(f"Invalid mode: {mode}, expected [0;3]")
    return SequenceCSI("J", mode, abbr="ED")


def make_clear_display_after_cursor() -> SequenceCSI:
    """
    Create :abbr:`ED (Erase in Display)` sequence that clears a part of the screen
    from cursor to the end of the screen. Cursor position does not change.

    :example:     ``ESC [0J``
    """
    return make_erase_in_display(0)


def make_clear_display_before_cursor() -> SequenceCSI:
    """
    Create :abbr:`ED (Erase in Display)` sequence that clears a part of the screen
    from cursor to the beginning of the screen. Cursor position does not change.

    :example:     ``ESC [1J``
    """
    return make_erase_in_display(1)


def make_clear_display() -> SequenceCSI:
    """
    Create :abbr:`ED (Erase in Display)` sequence that clears an entire screen.
    Cursor position does not change.

    :example:     ``ESC [2J``
    """
    return make_erase_in_display(2)


def make_clear_history() -> SequenceCSI:
    """
    Create :abbr:`ED (Erase in Display)` sequence that clears history, i.e.,
    invisible lines on the top that can be scrolled back down. Cursor position
    does not change. This is a xterm extension.

    :example:     ``ESC [3J``
    """
    return make_erase_in_display(3)


def make_erase_in_line(mode: int = 0) -> SequenceCSI:
    """
    Create :abbr:`EL (Erase in Line)` sequence that clears a part of the line
    or the entire line at the cursor position. Cursor position does not change.

    :param mode:  .. ::

                  Sequence operating mode.

                     - If set to 0, clear from cursor to the end of the line.
                     - If set to 1, clear from cursor to the beginning of the line.
                     - If set to 2, clear the entire line.

    :example:     ``ESC [0K``
    """
    if not (0 <= mode <= 2):
        raise ValueError(f"Invalid mode: {mode}, expected [0;2]")
    return SequenceCSI("K", mode, abbr="EL")


def make_clear_line_after_cursor() -> SequenceCSI:
    """
    Create :abbr:`EL (Erase in Line)` sequence that clears a part of the line
    from cursor to the end of the same line. Cursor position does not change.

    :example:     ``ESC [0K``
    """
    return make_erase_in_line(0)


def make_clear_line_before_cursor() -> SequenceCSI:
    """
    Create :abbr:`EL (Erase in Line)` sequence that clears a part of the line
    from cursor to the beginning of the same line. Cursor position does not
    change.

    :example:     ``ESC [1K``
    """
    return make_erase_in_line(1)


def make_clear_line() -> SequenceCSI:
    """
    Create :abbr:`EL (Erase in Line)` sequence that clears an entire line
    at the cursor position. Cursor position does not change.

    :example:     ``ESC [2K``
    """
    return make_erase_in_line(2)


# CSI / Private mode sequences assembly ---------------------------------------


def make_show_cursor() -> SequenceCSI:
    """
    C
    """
    return SequenceCSI("h", 25, interm="?")


def make_hide_cursor() -> SequenceCSI:
    """
    C
    """
    return SequenceCSI("l", 25, interm="?")


def make_save_screen() -> SequenceCSI:
    """
    C
    """
    return SequenceCSI("h", 47, interm="?")


def make_restore_screen() -> SequenceCSI:
    """
    C
    """
    return SequenceCSI("l", 47, interm="?")


def make_enable_alt_screen_buffer() -> SequenceCSI:
    """
    C
    """
    return SequenceCSI("h", 1049, interm="?")


def make_disable_alt_screen_buffer() -> SequenceCSI:
    """
    C
    """
    return SequenceCSI("l", 1049, interm="?")


# OSC sequences assembly ------------------------------------------------------


def make_hyperlink() -> SequenceOSC:
    """
    Create a hyperlink in the text *(supported by limited amount of terminals)*.
    Note that a complete set of commands to define a hyperlink consists of 4
    oh them (two `OSC-8 <SequenceOSC>` and two `ST <SequenceST>`).

    .. seealso ::
        compose_hyperlink()`.
    """
    return SequenceOSC(8, "", "")


# Fp sequences assembly -------------------------------------------------------


def make_save_cursor_position() -> SequenceFp:
    """
    :example:  ``ESC 7``
    """
    return SequenceFp("7", abbr="DECSC")


def make_restore_cursor_position() -> SequenceFp:
    """
    :example:  ``ESC 8``
    """
    return SequenceFp("8", abbr="DECRC")


# Sequence composites ---------------------------------------------------------


def compose_clear_line_fill_bg(basis: SequenceSGR, line: int = None) -> str:
    """

    :param basis:
    :param line:
    """
    if line is not None:
        result = make_set_cursor(line, 1)
    else:
        result = make_set_cursor_column(1)
    return f"{result}{basis}{make_clear_line()}"


def compose_hyperlink(url: str, label: str = None) -> str:
    """
    Syntax: ``(OSC 8 ; ;) (url) (ST) (label) (OSC 8 ; ;) (ST)``, where
    `OSC <SequenceOSC>` is ``ESC ]``.

    :param url:
    :param label:
    :example:  ``ESC ]8;;http://localhost ESC \\Text ESC ]8;; ESC \\``
    """

    return (
        f"{make_hyperlink()}{url}{SequenceST()}{label or url}"
        f"{make_hyperlink()}{SequenceST()}"
    )


def decompose_report_cursor_position(string: str) -> t.Tuple[int, int] | None:
    """
    Parse :abbr:`RCP (Report Cursor Position)` sequence that usually comes from
    a terminal as a response to `QCP <make_query_cursor_position>` sequence and
    contains a cursor's current line and column.

    .. note ::
        As the library in general provides sequence assembling methods, but not
        the disassembling ones, there is no dedicated class for RCP sequences yet.

    >>> decompose_report_cursor_position('\x1b[9;15R')
    (9, 15)

    :param string:  Terminal response with a sequence.
    :return:        Current line and column if the expected sequence exists
                    in ``string``, *None* otherwise.
    """
    if match := RCP_REGEX.match(string):
        return int(match.group(1)), int(match.group(2))
    return None


# Utility ---------------------------------------------------------


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
