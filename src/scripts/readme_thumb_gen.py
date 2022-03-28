# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from readme_examples import _outpath, _print
from readme_examples import *
from pytermor.preset import GRAY, RESET

with open(_outpath, 'rt') as fp:
    for line in fp.readlines():
        line = line.strip()
        charlen = len(ReplaceSGRs('').invoke(line))
        pad = max(0, 50 - charlen)
        pad_left = pad//2
        pad_right = pad - pad_left
        fill = ' '
        if pad == 50:
            fill = '-'
        _print(f'{GRAY}+{fill*pad_left}{RESET}'
               f'{line}'
               f'{GRAY}{fill*pad_right}+{RESET}'
               )
os.remove(_outpath)
