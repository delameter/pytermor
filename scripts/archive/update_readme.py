# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import os
import re
import stat
from os.path import dirname, abspath, join

from pytermor import Spans, Seqs
from pytermor.util import format_thousand_sep

project_dir = abspath(join(dirname(__file__), '../..'))
README_TPL_PATH = join(project_dir, 'dev', 'README.tpl.md')
README_PATH = join(project_dir, 'README.md')


def read_file(path: str) -> str:
    with open(path, 'rt', encoding='utf8') as f:
        return f.read()


def include_file(path: str) -> str:
    content = read_file(join(project_dir, path)).rstrip('\n')
    return '\n'.join([
        '```python3',
        content,
        '```',
    ])


tpl = read_file(README_TPL_PATH)
result = re.sub('@{(.+)}', lambda m: include_file(m.group(1)), tpl)

os.remove(README_PATH)

with open(README_PATH, 'wt', encoding='utf8') as f:
    length = f.write(result)
    print(f'Wrote {Spans.BOLD.wrap(format_thousand_sep(length))} bytes '
          f'to {Seqs.BLUE(README_PATH)}')

mode = os.stat(README_PATH).st_mode
ro_mask = 0o777 ^ (stat.S_IWRITE | stat.S_IWGRP | stat.S_IWOTH)
os.chmod(README_PATH, mode & ro_mask)
