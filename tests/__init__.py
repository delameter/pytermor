# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from pytermor import fmt, Format, autof, seq

__all__ = [
    'VERBOSITY_LEVEL',
    'verb_print',
    'verb_print_info',
    'verb_print_header',
    'verb_print_subtests',
]

VERBOSITY_LEVEL = 1


def verb_print(msg: str, _fmt: Format = fmt.noop, **argv):
    print(_fmt(msg or ''), flush=True, **argv)


def verb_print_header(msg: str = ''):
    if VERBOSITY_LEVEL <= 2:
        return
    verb_print(f'{"":8s}{msg}', autof(seq.HI_CYAN))


def verb_print_info(msg: str = ''):
    if VERBOSITY_LEVEL <= 2:
        return
    verb_print(f'{"":12s}{msg}', fmt.cyan)


def verb_print_subtests(count: int):
    if VERBOSITY_LEVEL <= 1:
        return
    verb_print(f'({count:d} subtests)', fmt.green, end=' ')
