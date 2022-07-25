# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

import re
from os.path import join, dirname

import yaml
from yaml import SafeLoader

def generate_pyc_int(config):
    pass


def generate_pyc_color(config):
    pass


def generate_preset_list_indexed(cfg_indexed, f):
    def print_sep(s='-', b='+'):
        print(offset * ' ', file=f, end=b)
        for w in widths:
            print(w * s, file=f, end=b)
        print('', file=f)

    def print_sep_merged():
        print(f'{offset * " "}|{wt * " "}|', file=f)

    def print_header():
        print(offset * ' ', file=f, end='|')
        for i, w in enumerate(widths):
            v = f'{header[i]:^{w}s}'
            if len(v) > w:
                raise OverflowError(w, len(v), v)
            print(v, file=f, end='|')
        print('', file=f)

    def print_row(c):
        for l in lines:
            print(offset * ' ', file=f, end='|')
            for i, w in enumerate(widths):
                v = l[i] if len(l) > i else ''
                v = f' {v.format(**c):<{w-1}s}'
                if len(v) > w:
                    raise OverflowError(w, len(v), v)
                print(v, file=f, end='|')
            print('', file=f)

    offset = 3
    beginning = """
.. table::
   :widths: 8 60 12 11 11 11 11 30 46
   :class: presets preset-colors
"""
    widths = (74, 30, 9, 5, 5, 9, 17, 22, 48)
    wt = sum(widths) + len(widths) - 1
    header = ['', '**Name**', '|int|', '|seq|', '|spn|', '|clr|', '|sty|',
              '**RGB code**', '**XTerm name**']
    lines = [['.. image:: /_generated/preset-samples/color{id}.png', '``{name_idx}``{first}',
              '``{id}``', '', '', '**V**', '', '``#{value:06x}``', '{original_name}{first_rename}'],
             ['    :height: 60px'], ['    :class: no-scaled-link']]
    with open(join(dirname(__name__), '..', 'docs', '_generated', 'preset-table', 'input.rsti'), 'rt') as ff:
        footnotes = [fl.strip() for fl in ff.readlines()]

    print(beginning, file=f)
    print_sep()
    print_header()
    print_sep('=', '+')
    for c in cfg_indexed:
        print_row(c)
        print_sep()

    print_sep_merged()
    for fo in footnotes:
        print(f'{" " * offset}| {fo:<{wt-1}s}|', file=f)
        print_sep_merged()
    print_sep()


# -----------------------------------------------------------------------------

with open(join(dirname(__name__), 'indexed.yml'), 'r') as f:
    cfg_indexed = yaml.load(f, SafeLoader)

first = True
first_rename = True
for c in cfg_indexed:
    c['name'] = c.get('override_name', c['original_name'])
    c['first_rename'] = ''
    if c['name'] != c['original_name']:
        c['original_name'] = f'**{c["original_name"]}**'
        c['first_rename'] = ' [4]_' if first_rename else ''
        first_rename = False
    c['name_idx'] = re.sub(r'([a-z]|^)([A-Z0-9])', r'\1_\2', 'idx' + c['name']).upper()
    c['first'] = ' [3]_' if first else ''
    first = False

with open(join(dirname(__name__), '..', 'docs', '_generated', 'preset-table', 'output.rsti'), 'wt') as f:
    generate_preset_list_indexed(cfg_indexed, f)
