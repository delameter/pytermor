# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

import json
from os.path import join, dirname
from PIL.Image import Image
import PIL

from pytermor import color

# -----------------------------------------------------------------------------
# default colors:
# -----------------------------------------------------------------------------

colors16_map = {'#000000': 'BLACK', '#800000': 'RED', '#008000': 'GREEN', '#808000': 'YELLOW', '#000080': 'BLUE',
            '#800080': 'MAGENTA', '#008080': 'CYAN', '#c0c0c0': 'WHITE', '#808080': 'GRAY', '#ff0000': 'HI_RED',
            '#00ff00': 'HI_GREEN', '#ffff00': 'HI_YELLOW', '#0000ff': 'HI_BLUE', '#ff00ff': 'HI_MAGENTA',
            '#00ffff': 'HI_CYAN', '#ffffff': 'HI_WHITE', }

def find_color16(hex: str) -> str:
    if hex in colors16_map:
        name = colors16_map[hex]
        return name
    return ''

def get_color16_ref(name: str|None) -> str:
    if not name:
        return ''
    return '<code class="xref any py py-data docutils literal notranslate">' \
           '<span class="pre">{color_name}</span>' \
           '</code>'.format(color_name=name)
    # return '<a class="reference internal" href="presets.html#{color_name}">' \
    #        '<code class="xref any py py-data docutils literal notranslate">' \
    #        '<span class="pre">{color_name}</span>' \
    #        '</code>' \
    #        '</a>'.format(color_name=name)

COLORS_16 = [
    'BLACK', 'RED', 'GREEN', 'YELLOW',
    'BLUE', 'MAGENTA', 'CYAN', 'WHITE',
    'GRAY', 'HI_RED', 'HI_GREEN', 'HI_YELLOW',
    'HI_BLUE', 'HI_MAGENTA', 'HI_CYAN', 'HI_WHITE',
]

html_16_output = '''
<table class="xterm-colors docutils align-default">
    <tr>
        <th>Ex</th>
        <th>Fg code</th>
        <th>Bg code</th>
        <th class="smaller dense">RGB<br>hex code</th>
        <th>Fg preset</th>
        <th>Bg preset</th>
    </tr>
'''

for color_name in COLORS_16:
    color_ = getattr(color, color_name)
    html_16_output += '''
    <tr>
        <td class="xterm-color-cell" style="background-color: #{color.hex_value:06x}"></td>
        <td><pre>{color._code_fg}</pre></td>
        <td><pre>{color._code_bg}</pre></td>
        <td><pre>0x{color.hex_value:06x}</pre></td>
        <td><pre>{color_name}</pre></td>
        <td><pre>{bg_color_name}</pre></td>
    </tr>
'''.format(color=color_, 
           color_name=get_color16_ref(color_name),
           bg_color_name=get_color16_ref('BG_' + color_name))

html_16_output += '</table>\n'

with open('_include/xterm-colors-16-t.html', 'w') as output:
    output.write(html_16_output)


# -----------------------------------------------------------------------------
# indexed colors:
# -----------------------------------------------------------------------------

with open(join(dirname(__name__), '256-colors.json'), 'r') as f:
    config = json.load(f)

table_datas = []
for color in config:
    table_datas.append({
        'hexString': color['hexString'],
        'colorId': color['colorId'],
        'name': color['name'],
        'seq16': find_color16(color['hexString']),
    })

col_len = {
    k: 2 + max(len(str(r[k])) for r in table_datas) for k in table_datas[0].keys()
}
col_len_list = [col_len['colorId'], col_len['name'], col_len['seq16'], col_len['hexString']]

html_256_output = '''
<table class="xterm-colors docutils align-default">
    <tr>
        <th>Ex</th>
        <th>Code</th>
        <th class="smaller dense">RGB<br>hex code</th>
        <th>XTerm name</th>
        <th class="smaller dense">Default mode<br>counterpart</th>
    </tr>
'''

latex_separator = '   '
for col in col_len_list:
    latex_separator += '='*(col-1) + ' '
latex_separator += '\n'

latex_256_output = ''

latex_256_output += f'   {"Code":<{col_len_list[0]}s}{"XTerm name":<{col_len_list[1]}s}' \
                    f'{"Counterpart":<{col_len_list[2]}s}{"RGB hex":<{col_len_list[3]}s}\n' + latex_separator

for table_data in table_datas:
    html_256_output += '''
    <tr>
        <td class="xterm-color-cell" style="background-color: {hexString}"></td>
        <td><pre>{colorId}</pre></td>
        <td><pre>{hexString}</pre></td>
        <td>{name}</td>
        <td><pre>{seq16_name}</pre></td>
    </tr>
'''.format(**table_data,
           seq16_name=get_color16_ref(table_data['seq16']))

    latex_256_output += '   '
    for key in ['colorId', 'name', 'seq16', 'hexString']:
        latex_256_output += f'{table_data[key]:<{col_len[key]}}'
    latex_256_output += '\n'

    #im = PIL.Image.new('RGB', (591,591), table_data['hexString'])
    #im.save(f'_include/xterm-colors-256-t/color{table_data["colorId"]}.png')

html_256_output += '</table>\n'

with open('_include/xterm-colors-256-t.html', 'w') as output:
    output.write(html_256_output)
#with open('_include/xterm-colors-256-t.rst', 'w') as output:
#    output.write(latex_output)
