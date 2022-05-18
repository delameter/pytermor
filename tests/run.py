# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import sys
import unittest

from blessings import Terminal
from colour_runner.result import ColourTextTestResult
from colour_runner.runner import ColourTextTestRunner
from pygments.formatters.terminal256 import Terminal256Formatter
from pygments.style import Style
from pygments.token import Name, Generic, Literal

from pytermor import autof, seq, fmt
import tests


class CustomOutputStyle(Style):
    default_style = ""
    styles = {
        Generic.Traceback: 'ansigray',
        Generic.Error:     'ansibrightred bold',
        Literal:           'ansiyellow bold',
        Name.Builtin:      'bold',
    }
    # /pygments/lexers/python.py:714
    # /pygments/style.py:14


class CustomColourTextTestResult(ColourTextTestResult):
    _terminal = Terminal()
    formatter = Terminal256Formatter(style=CustomOutputStyle)
    colours = {
        None: str,
        'error': autof(seq.RED),
        'expected': autof(seq.YELLOW),
        'fail': autof(seq.HI_RED + seq.BOLD),
        'fail_label': autof(seq.RED + seq.INVERSED),
        'skip': str,
        'success': autof(seq.GREEN),
        'title': autof(seq.YELLOW),
        'unexpected': autof(seq.RED),
    }
    separator1 = ('=' * 70)
    separator2 = fmt.gray('-' * 70)

    def addFailure(self, test, err):
        super(ColourTextTestResult, self).addFailure(test, err)
        self.printResult('F', 'FAIL', 'fail_label')


if __name__ == '__main__':
    while len(sys.argv) > 0:
        arg = sys.argv.pop(0)
        if arg in ['-v', '-verbose']:
            tests.VERBOSITY_LEVEL += 1
        elif arg == '-vv':
            tests.VERBOSITY_LEVEL += 2

    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir)
    runner = ColourTextTestRunner(resultclass=CustomColourTextTestResult)
    runner.verbosity = tests.VERBOSITY_LEVEL
    runner.run(suite)
