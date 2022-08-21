# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import sys
import traceback

from typing import TypeVar, Generic, TextIO


T = TypeVar('T')
""" Any """


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


def print_exception(e: Exception, file: TextIO = sys.stderr, with_trace: bool = True):
    """
    print_exception

    :param e:
    :param file:
    :param with_trace:
    :return:
    """
    from .render import Styles, Text
    tb_lines = [line.rstrip('\n') for line in traceback.format_exception(e.__class__, e, e.__traceback__)]

    error_text = Text()
    if with_trace:
        error_text += Text('\n'.join(tb_lines), Styles.ERROR) + '\n\n'

    error_text += (
        Text('ERROR:', Styles.ERROR_LABEL) +
        Text(f' {e}', Styles.ERROR_ACCENT))

    print(error_text.render(), file=file)


class LogicError(Exception):
    pass

