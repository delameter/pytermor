# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import re

import yaml

from pytermor import Styles, ColorRGB, Style, Colors
from pytermor.util import ljust_sgr

with open('named_sources.yml', 'rt') as f:
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
                print(Styles.WARNING._render(f'Unresolvable conflict: {parts}, skipping'))
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

with open('named.yml', 'wt') as f:
    yaml.dump(colors, f, allow_unicode=True, indent=2, encoding='utf8')

max_name_len = max(len(c["name"]+' '+(c.get("variation", '') or "")) for c in colors)
orig_name_len = max(len(c["orig_name"]) for c in colors)
var_style = Style(fg=Colors.RGB_GRAY_40)
orig_style = Style(fg=Colors.RGB_GRAY_30)
for idx, c in enumerate(list(sorted(colors, key=lambda v: v["value"]))):
    style = Style(bg=ColorRGB(c['value']))
    style.autopick_fg()
    style2 = Style(fg=ColorRGB(c['value']))
    print(' ' + style._render(f" {idx:>4d} ") +
          '  0x' + style2._render(f"{c['value']:06x}"),
          '  ', ljust_sgr(c["name"] +" " + var_style._render(c.get("variation", "")), max_name_len) + orig_style._render(f'{c["orig_name"]:<{orig_name_len}s}')
          )

