# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from copy import copy

from readme_examples import _outpath, _print
from readme_examples import *
from pytermor.preset import GRAY, RESET

corner=[
    ['└', '┘', '└', '┘'],
    ['┌', '┐', '┌', '┐'],
]
with open(_outpath, 'rt') as fp:
    for line in fp.readlines() + ['', '']:
        line = line.strip()
        charlen = len(ReplaceSGR('').invoke(line))
        pad = max(0, 50 - charlen)
        pad_left = pad//2
        pad_right = pad - pad_left
        sep=['│', '│', '│', '│']
        fill = ' '
        if pad == 50:
            sep=corner.pop(0)
            corner.append(copy(sep))
            fill = '─'
        _print(f'{GRAY}{sep.pop(0)}{fill*pad_left}{RESET}'
               f'{line}'
               f'{GRAY}{fill*pad_right}{sep.pop(0)}{RESET}'
               '   '
               f'{GRAY}{sep.pop(0)}{RESET}'
               f'{line}'
               f'{GRAY}{fill*pad}{sep.pop(0)}{RESET}'
               )
os.remove(_outpath)
