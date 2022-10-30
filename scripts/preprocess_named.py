# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from os.path import abspath, join, dirname
import re

import yaml

from pytermor import Styles, ColorRGB, Style, Colors, Text
from pytermor.color import ColorIndexed256
from pytermor.util import ljust_sgr

project_root = abspath(join(dirname(__file__), '..'))
configs_path = join(project_root, 'config')

with open(join(configs_path, 'named_sources.yml'), 'rt') as f:
    named = yaml.safe_load(f)['named_colors']

ids = set()  # tuple(name, lvl1var, lvl2var...)
colors = []

for cfg in named:
    parts = []
    for raw_part in re.split(r"\s*[()#]\s*", cfg["name"].strip()):
        part = re.sub('[^\w]+', '-',
                      raw_part.strip().lower().replace('\'', ''))\
            .strip('-')
        part = re.sub('-color(ed)?$', '', part)
        if part:
            parts.append(part)

    for idx in range(0, len(parts)):
        possible_id = tuple(parts[:idx+1])
        if possible_id in ids:
            if idx == len(parts) - 1:
                print(Text(f'Unresolvable conflict: {parts}, skipping', Styles.WARNING))
            continue
        else:
            ids.add(possible_id)
            #name = re.sub('-([^\d])', ' \\1', ' '.join(name_parts))
            color = {
                "value": cfg["value"],
                "name": parts[0].replace('-', ' '),
                "original_name": cfg["name"],
            }
            if (v := ('-'.join(parts[1:idx+1]))) != '':
                color["variation"] = v
            colors.append(color)

            break

def hexint_presenter(dumper, data):
    return dumper.represent_int(f'0x{data:06x}')
yaml.add_representer(int, hexint_presenter)

with open(join(configs_path, 'named.yml'), 'wt') as f:
    yaml.dump(colors, f, allow_unicode=True, indent=2, encoding='utf8')

max_name_len = max(len(c["name"]+' '+(c.get("variation", '') or "")) for c in colors)
orig_name_len = max(len(c.get("orig_name", "")) for c in colors)
var_style = Style(fg=ColorIndexed256.GRAY_42.value)
orig_style = Style(fg=ColorIndexed256.GRAY_30.value)
for idx, c in enumerate(list(sorted(colors, key=lambda v: v["value"]))):
    style = Style(bg=ColorRGB(c['value']))
    style.autopick_fg()
    style2 = Style(fg=ColorRGB(c['value']))
    print(' ' + style.text(f" {idx:>4d} ") +
          ' ' + style2.text(f"0x{c['value']:06x}"),
          '  ', ljust_sgr(c["name"] +" " + var_style.render(c.get("variation", "")), max_name_len)
          + orig_style.text(f'{c.get("orig_name", ""):<{orig_name_len}s}')
          )

