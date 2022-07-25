# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

import re
from os.path import join, dirname

import yaml
from yaml import SafeLoader


class PyModuleIntGenerator:
    def run(self, f, cfg_indexed):
        print('# ---------------------------------- GENERATED ---------------------------------\n', file=f)
        for cc in cfg_indexed:
            print(f'{cc["name_idx"]} = {cc["id"]}', file=f)


class PyModuleColorGenerator:
    def run(self, f, cfg_indexed):
        print('# ---------------------------------- GENERATED ---------------------------------\n', file=f)
        for cc in sorted(cfg_indexed, key=lambda v: v['name_idx']):
            print(
                f'{cc["name_idx"]} = ColorIndexed(0x{cc["value"]:06x}, intcode.'
                f'{cc["name_idx"]})  # {cc["id"]} {cc["renamed_from"]}',
                file=f)


class PresetListIndexedGenerator:
    def print_sep(self, s='-', b='+'):
        print(self.offset * ' ', file=self.f, end=b)
        for w in self.widths:
            print(w * s, file=self.f, end=b)
        print('', file=self.f)

    def print_sep_merged(self):
        print(f'{self.offset * " "}|{self.wt * " "}|', file=self.f)

    def print_header(self):
        print(self.offset * ' ', file=self.f, end='|')
        for i, w in enumerate(self.widths):
            v = f'{self.header[i]:^{w}s}'
            if len(v) > w:
                raise OverflowError(w, len(v), v)
            print(v, file=self.f, end='|')
        print('', file=self.f)

    def print_row(self, cf):
        for ll in self.lines:
            print(self.offset * ' ', file=self.f, end='|')
            for i, w in enumerate(self.widths):
                v = ll[i] if len(ll) > i else ''
                v = f' {v.format(**cf):<{w - 1}s}'
                if len(v) > w:
                    raise OverflowError(w, len(v), v)
                print(v, file=self.f, end='|')
            print('', file=self.f)

    def run(self, f, cfg_indexed):
        self.f = f

        self.offset = 3
        self.beginning = """
.. table::
   :widths: 8 60 12 11 11 11 11 30 46
   :class: presets preset-colors
"""
        self.widths = (74, 30, 9, 5, 5, 9, 17, 22, 48)
        self.wt = sum(self.widths) + len(self.widths) - 1
        self.header = ['', '**Name**', '|int|', '|seq|', '|spn|', '|clr|', '|sty|',
                       '**RGB code**', '**XTerm name**']
        self.lines = [['.. image:: /_generated/preset-samples/color{id}.png',
                       '``{name_idx}``{first}', '``{id}``', '', '', '**V**', '',
                       '``#{value:06x}``', '{original_name}{first_rename}'],
                      ['    :height: 60px'], ['    :class: no-scaled-link']]
        with open(join(dirname(__name__), '..', 'docs', '_generated', 'preset-table',
                       'input.rst_'), 'rt') as ff:
            footnotes = [fl.strip() for fl in ff.readlines()]

        print(self.beginning, file=f)
        self.print_sep()
        self.print_header()
        self.print_sep('=', '+')
        for cc in cfg_indexed:
            self.print_row(cc)
            self.print_sep()

        self.print_sep_merged()
        for fo in footnotes:
            print(f'{" " * self.offset}| {fo:<{self.wt - 1}s}|', file=f)
            self.print_sep_merged()
        self.print_sep()


# -----------------------------------------------------------------------------

class Main:
    def run(self):
        with open(join(dirname(__name__), 'indexed.yml'), 'r') as f:
            cfg_indexed = yaml.load(f, SafeLoader)

        first = True
        first_rename = True
        for c in cfg_indexed:
            c['name'] = c.get('override_name', c['original_name'])
            c['first_rename'] = ''
            c['renamed_from'] = ''
            if c['name'] != c['original_name']:
                c['renamed_from'] = f'(orig. {c["original_name"]})'
                c['original_name'] = f'**{c["original_name"]}**'
                c['first_rename'] = ' [4]_' if first_rename else ''
                first_rename = False
            c['name_idx'] = re.sub(r'([a-z]|^)([A-Z0-9])', r'\1_\2',
                                   'idx' + c['name']).upper()
            c['first'] = ' [3]_' if first else ''
            first = False

        with open(join(dirname(__name__), '..', 'docs', '_generated', 'preset-table',
                       'output.rst_'), 'wt') as f:
            PresetListIndexedGenerator().run(f, cfg_indexed)

        with open(join(dirname(__name__), '..', 'docs', '_generated', 'preset-code',
                       'intcode.py_'), 'wt') as f:
            PyModuleIntGenerator().run(f, cfg_indexed)

        with open(join(dirname(__name__), '..', 'docs', '_generated', 'preset-code',
                       'color.py_'), 'wt') as f:
            PyModuleColorGenerator().run(f, cfg_indexed)


if __name__ == '__main__':
    Main().run()
