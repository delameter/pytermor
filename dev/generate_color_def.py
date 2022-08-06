# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

import re
from os.path import join, dirname
from typing import Dict, Set

import yaml
from yaml import SafeLoader

from pytermor import Style, ColorIndexed, color, Text, span
from pytermor.renderer import RendererManager, HtmlRenderer, SGRRenderer


class PyModuleIntGenerator:
    def run(self, f, cfg_indexed):
        print('# ---------------------------------- GENERATED '
              '---------------------------------\n', file=f)
        for cc in cfg_indexed:
            print(f'{cc["name_idx"]} = {cc["id"]}', file=f)

        print(f.name)


class PyModuleColorGenerator:
    def run(self, f, cfg_indexed):
        print('# ---------------------------------- GENERATED '
              '---------------------------------\n', file=f)
        for cc in cfg_indexed:
            print(f'{cc["name_idx"]} = ColorIndexed(0x{cc["value"]:06x}, intcode.'
                  f'{cc["name_idx"]})  # {cc["id"]} {cc["renamed_from"]}', file=f)
        print(f.name)


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
                       '``#{value:06x}``', '{original_name_rst}{first_rename}'],
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
        print(f.name)


class HtmlTableGenerator:
    def run(self, f, cfg_indexed):
        RendererManager.set_up(HtmlRenderer)

        html = '''<html><head><style>
            body {
                background-color: #161616;
                font-family: \'Iose7ka Editor\', monospace;
                font-size: 1rem;
                line-height: 1.4;
                display: flex;
                flex-wrap: wrap;
                flex-direction: column;
                box-sizing: border-box;
                height: 100%;
                margin: 0;
                padding: 1em;
                align-content: space-between;
            }
            body > * {
                box-sizing: border-box;
            }
        </style></head>
        <body>'''

        key_max_index: Dict[str, int] = dict()
        names: Set[str] = set()
        max_name_len = max(len(cc['name']) for cc in cfg_indexed)

        for cc in cfg_indexed:
            is_renamed = len(cc['renamed_from']) > 0
            is_duplicate = (cc['name'] in names)

            names.add(cc['name'])
            if cc['key'] not in key_max_index.keys():
                key_max_index[cc['key']] = 0
            key_max_index[cc['key']] += 1

            id_style = Style(fg='hi_white', bold=True)
            name_style = Style(fg=cc['value'], blink=is_duplicate)
            comment_label_style = Style(fg='gray', italic=True)
            comment_value_style = Style(fg='gray', italic=True, dim=True)
            value_style = Style(bg=cc['value'], fg=0x0)
            value_style.autopick_fg()
            if value_style.fg.hex_value != 0x0:
                name_style.fg = value_style.fg

            id_str = f'{cc["id"]:_>3d}'
            value_str = f'_#{cc["value"]:06x}_'
            name_str = f'{cc["name"]:_<{max_name_len + 1}s}'
            comment_str = ''

            if is_renamed:
                comment_str += (
                    comment_label_style.render('<br>' + '_'*10 + 'was' + '_'*3) +
                    comment_label_style.render(f"{cc['original_name']:_<{max_name_len}s}") +
                    comment_value_style.render('<br>' + '_'*9 + 'sugg' + '_'*3) +
                    comment_value_style.render(f"{cc['key'] + str(key_max_index.get(cc['key'])):_<{max_name_len}s}")
                )

                # different approach (output is Text, while in prev. example it is already str)
                # comment_str += (
                #     f"{Text('<br>' + '_'*10 + 'was' + '_'*3, comment_label_style)}"
                #     f"{Text(cc['original_name'], comment_value_style):_<{max_name_len}s}"
                #     f"{Text('<br>' + '_'*9 + 'sugg' + '_'*3, comment_label_style)}"
                #     f"{Text(cc['key'] + str(key_max_index.get(cc['key'])), comment_value_style)}:_<{max_name_len}s"
                # )

            html += ('\n<div>' + id_style.render(id_str) +
                     '_' + value_style.render(value_str) +
                     '__' + name_style.render(name_str) +
                     '_' + comment_str +
                     '</div>')

        html += '\n</body></html>'
        html = html.replace('_', '&nbsp;')
        f.write(html)

        RendererManager.set_up(SGRRenderer)
        print(f'Wrote {Text(len(html), Style(bold=True))} bytes to {Text(f.name, "blue")}')


# -----------------------------------------------------------------------------

class Main:
    def run(self):
        with open(join(dirname(__name__), 'indexed.yml'), 'r') as f:
            cfg_indexed = yaml.load(f, SafeLoader)

        d = dict()
        d.update()
        first = True
        first_rename = True
        for c in cfg_indexed:
            c['name'] = c.get('override_name', c['original_name'])
            c['key'] = re.sub(r'\d|_', '', c['name'])
            c['first_rename'] = ''
            c['original_name_rst'] = ''
            c['renamed_from'] = ''
            if c['name'] != c['original_name']:
                c['renamed_from'] = f'(orig. {c["original_name"]})'
                c['original_name_rst'] = f'**{c["original_name"]}**'
                c['first_rename'] = ' [4]_' if first_rename else ''
                first_rename = False
            c['name_idx'] = re.sub(r'([a-z]|^)([A-Z0-9])', r'\1_\2',
                                   'idx' + c['name']).upper()
            c['first'] = ' [3]_' if first else ''
            first = False

        cfg_name_sorted = sorted(cfg_indexed, key=lambda v: (
            v['key'], -sum(ColorIndexed.hex_value_to_rgb_channels(v['value']))))

        generated_dir = join(dirname(__name__), '..', 'docs', '_generated')
        with open(join(generated_dir, 'preset-table', 'output.rst_'), 'wt') as f:
            PresetListIndexedGenerator().run(f, cfg_indexed)

        with open(join(generated_dir, 'preset-code', 'intcode.py_'), 'wt') as f:
            PyModuleIntGenerator().run(f, cfg_indexed)

        with open(join(generated_dir, 'preset-code', 'color.py_'), 'wt') as f:
            PyModuleColorGenerator().run(f, cfg_name_sorted)

        with open(join('/tmp', 'presets.html'), 'wt') as f:
            HtmlTableGenerator().run(f, cfg_name_sorted)


if __name__ == '__main__':
    Main().run()
