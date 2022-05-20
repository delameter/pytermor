# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import io
from contextlib import redirect_stdout

from pytermor import autocomplete, sequence
from pytermor.util import ReplaceSGR


class Cycle:
    def __init__(self, *args):
        self._elems = list(args)

    def next(self):
        el = self._elems.pop(0)
        self._elems.append(el)
        return el


f = io.StringIO()
with redirect_stdout(f):
    import run_examples
s = f.getvalue()

MAX_LEN = 50
corners = Cycle(
    Cycle('└', '┘'),
    Cycle('┌', '┐'),
)
lineseps = Cycle('│', '│')
span_sep = autocomplete(sequence.GRAY + sequence.DIM)

for line in s.splitlines(keepends=True):
    line = line.strip()
    if line:
        line = ' '+line
        fill = ' '
        sep = lineseps
    else:
        fill = '─'
        sep = corners.next()

    linelen = len(ReplaceSGR('').apply(line))
    pad = max(0, MAX_LEN - linelen)

    print(
        f'>{line}{"":{pad}}{fill}{"<":6}' +
        span_sep(sep.next()) + line + span_sep((fill * pad) + sep.next())
    )
