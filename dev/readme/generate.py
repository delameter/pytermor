# -----------------------------------------------------------------------------
# es7s/pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import re
from os.path import dirname, abspath, join

project_dir = abspath(join(dirname(__file__), '..', '..'))
README_TPL_PATH = join(project_dir, 'dev', 'readme', 'README.tpl.md')
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
with open(README_PATH, 'wt', encoding='utf8') as f:
    length = f.write(result)
    print(f'Wrote {length:d} bytes to "{README_PATH:s}"')
