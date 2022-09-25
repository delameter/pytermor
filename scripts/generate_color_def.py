# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

import re
from os.path import join, dirname, abspath
from random import random
from typing import Dict, Set

import yaml
from yaml import SafeLoader

from pytermor import ColorIndexed256, ColorIndexed16, NOOP_STYLE
from pytermor.color import Colors, Color
from pytermor.render import Style, Text
from pytermor.render import RendererManager, HtmlRenderer, SgrRenderer


class PyModuleColorGenerator:
    def run(self, f, cfg_color):
        print('# ---------------------------------- GENERATED '
              '---------------------------------\n', file=f)
        [self.process_indexed_16(cc, f) for cc in cfg_color.get('indexed_16')]
        print(file=f)
        [self.process_indexed_256(cc, f) for cc in cfg_color.get('indexed_256')]
        print(file=f)
        [self.process_indexed_rgb(cc, f) for cc in cfg_color.get('rgb')]
        print(f.name)

    @staticmethod
    def process_indexed_16(cc, f):
        cc['aliases'] = cc.get('aliases', [])
        print('{const_name} = ColorIndexed16(0x{hex_value:06x}, '
              'IntCodes.{code_fg}, IntCodes.{code_bg}, {index_256}, {aliases})'.format(**cc), file=f)

    @staticmethod
    def process_indexed_256(cc, f):
        cc['aliases'] = cc.get('aliases')
        print('{const_name} = ColorIndexed256(0x{hex_value:06x}, {code}, {aliases})'.format(**cc), file=f)

    @staticmethod
    def process_indexed_rgb(cc, f):
        cc['aliases'] = cc.get('aliases')
        print('{const_name} = ColorRGB(0x{hex_value:06x}, {aliases})'.format(**cc), file=f)


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
    @classmethod
    def name_to_abbr(cls, s: str) -> str:
        r =  re.sub('[a-z]', '', s)
        if not r:
            return re.sub('\b(.).+?\b', '\\1', s)
        return r

    def ascii_indic(self, v: float) -> str:
        s = '▁▂▃▄▅▆▇█'
        if v <= 0: return '₀'
        if v >= 1: return '¹'
        k = round(max(0.0, min(1.0, v)) * (len(s)-1))
        return s[k]

    def run(self, f, cfg_indexed):
        RendererManager.set_up(HtmlRenderer)
        #RendererManager.set_up(SgrRenderer)

        html = Text('''<html><head><style>
            html {
                min-height: 100%;
            }
            body {
                background: linear-gradient(#404040, #202020);
                background-repeat: no-repeat;
                background-attachment: fixed;
                font-family: \'Iose7ka Web\', monospace;
                font-size: 1rem;
                display: flex;
                flex-wrap: wrap;
                box-sizing: border-box;
                height: 100%;
                margin: 0;
                padding: .05rem;
                
                //flex-direction: column;
                //align-content: flex-start;
                
                flex-direction: column;
                justify-content: center;
                align-content: flex-start;
                row-gap: .25rem;
                column-gap: .125rem;
            }
            body > * {
                box-sizing: border-box;
            }
            .container {
                font-stretch: condensed;
                padding: .25rem .25rem;
                border-radius: .5rem;
                max-width: 16rem;
                background-color: rgba(16,16,16,25%);
                display: flex;
                flex-direction: row;
                overflow-x: hidden;
                flex-wrap: nowrap;
                align-items: center;
                column-gap: .25rem;
            }
            .example {
                box-shadow: 2px 2px 0px rgba(0, 0, 0, .5);
                text-shadow: none;
                border-radius: .25rem;
                padding-inline: .25rem;
                margin-inline-end: .25rem;
            }
            .id {
            }
            .value {
                font-size: .8rem;
                border-radius: .25rem;
                text-shadow: 2px 2px 1px rgba(0, 0, 0, .5);
                outline-style: inset;
                outline-width: thin;
                padding-inline-end: .25rem;
            }
            .name {
                text-shadow: 2px 2px 1px rgba(0, 0, 0, .5);
                overflow-x: hidden;
                text-overflow: ellipsis;
            }
            .comment {
                font-size: .8rem;
                font-stretch: condensed;
                overflow-x: hidden;
                text-shadow: 2px 2px 1px rgba(0, 0, 0, .25);
            }
        </style></head>
        <body>''')

        key_max_index: Dict[str, int] = dict()
        names: Set[str] = set()
        longest_name_len = len(
            sorted(cfg_indexed, key=lambda c: -len(c['name']))[0]['name'])
        longest_abbr_len = len(self.name_to_abbr(sorted(cfg_indexed, key=lambda c:
            -len(self.name_to_abbr(c['original_name'])))[0]['original_name']))

        for cc in cfg_indexed:
            is_renamed = len(cc.get('renamed_from', '')) > 0
            is_duplicate = (cc['name'] in names)

            variation_str = ""
            if "variation" in cc.keys():
                is_duplicate = False
                variation_str = cc.get("variation")

            names.add(cc['name'])
            if cc.get('key'):
                if cc['key'] not in key_max_index.keys():
                    key_max_index[cc['key']] = 0
                key_max_index[cc['key']] += 1

            container_style = Style(class_name='container')
            id_style = Style(fg='white', class_name='id')
            name_style = Style(fg='white', blink=is_duplicate, class_name='name')
            value_style = Style(fg=cc['value'], class_name='value')
            comment_label_style = Style(fg=Colors.RGB_GREY_35, italic=True, class_name='comment')
            #comment_value_style = Style(fg='gray', italic=True, dim=True)
            example_style = Style(bg=cc['value'], fg=0x0, class_name='example')
            example_style.autopick_fg()

            id_str = f'{cc["id"]:d}'
            example_str = f'__'
            value_str = f'{cc["value"]:06x}'
            # value_str += ' '+ ''.join((self.ascii_indic(f) if i>0 else self.ascii_indic(f/360))
            #                      for i, f in enumerate(ColorIndexed.hex_value_to_hsv_channels(cc["value"])))
            name_str = f'{cc["name"]:s}'
            comment_str = ''

            if is_renamed:
                comment_squashed = self.name_to_abbr(cc['original_name'])
                comment_str = (
                    comment_label_style.text(f"{comment_squashed:_<s}"))
                    #comment_value_style._render('<br>' + '_'*9 + 'sugg' + '_'*3) +
                    #comment_value_style._render(f"{cc['key'] + str(key_max_index.get(cc['key'])):_<{max_name_len}s}")

                # different approach (output is Text, while in prev. example it is already str)
                # comment_str += (
                #     f"{Text('<br>' + '_'*10 + 'was' + '_'*3, comment_label_style)}"
                #     f"{Text(cc['original_name'], comment_value_style):_<{max_name_len}s}"
                #     f"{Text('<br>' + '_'*9 + 'sugg' + '_'*3, comment_label_style)}"
                #     f"{Text(cc['key'] + str(key_max_index.get(cc['key'])), comment_value_style)}:_<{max_name_len}s"
                # )
            # def repl():
            #     return chr(round(random() * 0x1fff))
            # id_str= re.sub('.', lambda m: repl(), id_str)
            # value_str= re.sub('.', lambda m: repl(), value_str)
            # name_str= re.sub('.', lambda m: repl(), name_str)
            # variation_str= re.sub('.', lambda m: repl(), variation_str)

            if value_style.fg.hex_value is not None:
                value2_style = Style(value_style, bg=ColorIndexed256.find_closest(value_style.fg.hex_value))
                value3_style = Style(value_style, bg=ColorIndexed16.find_closest(value_style.fg.hex_value))
            else:
                value2_style = NOOP_STYLE
                value3_style = NOOP_STYLE
            html += ('\n<div>' + id_str +
                    value_style.flip().autopick_fg().text((f'{value_str}')) +
                    value2_style.autopick_fg().text((f'{value2_style.bg.format_value("")}')) +
                    value3_style.autopick_fg().text((f'{value3_style.bg.format_value("")}')  ) +
                  container_style.text(  name_style.text(name_str) +
                    comment_str +
                    comment_label_style.text(variation_str)
                    + '</div>'))

        html += '\n</body></html>'
        html = str(html).replace('_', ' ')
        f.write(html)
        #print(html)
        RendererManager.set_up(SgrRenderer)
        print(f'Wrote {Text(len(html), Style(bold=True))} bytes to {Text(f.name, "blue")}')


# -----------------------------------------------------------------------------

class Main:
    INDEXED_PRESET_PREFIX = ''

    def sorter_by_color(self, cfg):
        h, s, v = Color.hex_value_to_hsv_channels(cfg['value'])
        return s>0,  h//18, -s*10//4, v

    def run(self):
        project_root = abspath(join(dirname(__file__), '..'))
        configs_path = join(project_root, 'config')

        with open(join(configs_path, 'color.yml'), 'r') as f:
            cfg_color = yaml.load(f, SafeLoader)

        d = dict()
        first = True
        first_rename = True
        for ctype in cfg_color:
            for c in cfg_color[ctype]:
                c['primary_name'] = c.get('override_name', c.get('original_name'))
                c['first_rename'] = ''
                if c['primary_name'] != c['original_name'] and first_rename:
                    c['first_rename'] = ' [4]_'
                    first_rename = False
                c['const_name'] = re.sub(r'([a-z])([A-Z0-9])', r'\1_\2', self.INDEXED_PRESET_PREFIX + c['primary_name']).upper()
                c['first'] = ' [3]_' if first else ''
                first = False

        #cfg_indexed_sort_by_key = sorted(cfg_color, key=lambda v: (
        #    v['const_name'], -sum(Color.hex_value_to_rgb_channels(v['hex_value']))))

        # cfg_indexed_sort_by_color = sorted(cfg_color, key=lambda v: self.sorter_by_color(v))

        # generated_docs_dir = join(project_root, 'docs', '_generated')
        # with open(join(generated_docs_dir, 'preset-table', 'output.rst_'), 'wt') as f:
        #     PresetListIndexedGenerator().run(f, cfg_color)

        generated_code_dir = join(project_root, 'scripts', 'generated')
        with open(join(generated_code_dir, 'color.py_'), 'wt') as f:
            PyModuleColorGenerator().run(f, cfg_color)

        # with open(join('/tmp', 'indexed-by-color.html'), 'wt') as f:
        #     HtmlTableGenerator().run(f, cfg_indexed_sort_by_color)
        # with open(join('/tmp', 'indexed-by-name.html'), 'wt') as f:
        #     HtmlTableGenerator().run(f, cfg_indexed_sort_by_key)
        #
        with open(join(configs_path, 'named.yml'), 'rt') as f:
            named = yaml.safe_load(f)
            for idx, n in enumerate(named):
                n['id'] = idx
        with open(join('/tmp', 'named-by-color.html'), 'wt') as f:
            HtmlTableGenerator().run(f, sorted(named, key=lambda v: self.sorter_by_color(v)))
        with open(join('/tmp', 'named-by-name.html'), 'wt') as f:
            HtmlTableGenerator().run(f, sorted(named, key=lambda v: v['name']+' '+v.get('variation', '')))


if __name__ == '__main__':
    Main().run()
