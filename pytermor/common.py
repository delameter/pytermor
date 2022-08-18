# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import sys
import traceback

from typing import TextIO


def get_terminal_width() -> int:
    try:
        import shutil as _shutil
        return _shutil.get_terminal_size().columns - 2
    except ImportError:
        return 80


def print_exception(e: Exception, file: TextIO = sys.stderr, with_trace: bool = True):
    from . import color, Style, Text
    tb_lines = [line.rstrip('\n') for line in traceback.format_exception(e.__class__, e, e.__traceback__)]

    error_style = Style(fg=color.RED)
    error_msg_style = Style(fg=color.HI_RED)

    error_text = Text('ERROR: ', Style(error_msg_style, bold=True)) + Text(e, error_msg_style)

    if with_trace:
        error_text = Text('\n'.join(tb_lines), error_style) + '\n\n' + error_text

    print(error_text.render(), file=file)
