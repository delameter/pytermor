# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from copy import copy

import pytermor.seq
from readme_examples import _outpath, _print
from readme_examples import *

MAX_LEN = 50
corner = [
    ['└', '┘', '└', '┘'],
    ['┌', '┐', '┌', '┐'],
]
with open(_outpath, 'rt') as fp:
    for line in fp.readlines() + ['', '']:
        line = line.strip()
        if line:
            line = ' ' + line
        charlen = len(ReplaceSGR('').apply(line))
        pad = max(0, MAX_LEN - charlen)
        pad_left = pad//2
        pad_right = pad - pad_left
        sep = ['│', '│', '│', '│']
        fill = ' '
        if pad == MAX_LEN:
            sep = corner.pop(0)
            corner.append(copy(sep))
            fill = '─'
        _print(
               f'>{line}'
               f'{" "*pad}{fill}<'
               f'     '
               f'{pytermor.seq.GRAY}{pytermor.seq.DIM}{sep.pop(0)}{pytermor.seq.RESET}'
               f'{line}'
               f'{pytermor.seq.GRAY}{pytermor.seq.DIM}{fill * pad}{sep.pop(0)}{pytermor.seq.RESET}'
               )
os.remove(_outpath)
