import sys

from pytermor import fmt


def is_verbose_mode() -> bool:
    return any([opt in sys.argv for opt in ['-v', '--verbose']])


def print_verbose(value='', **argv):
    if not is_verbose_mode():
        return
    print(fmt.cyan(value or ""), flush=True, **argv)
