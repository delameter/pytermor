# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import json
from os.path import join, dirname
from PIL.Image import Image
import PIL

with open(join(dirname(__name__), '256-colors.json'), 'r') as f:
    config = json.load(f)

colors16 = {'#000000': 'BLACK', '#800000': 'RED', '#008000': 'GREEN', '#808000': 'YELLOW', '#000080': 'BLUE',
            '#800080': 'MAGENTA', '#008080': 'CYAN', '#c0c0c0': 'WHITE', '#808080': 'GRAY', '#ff0000': 'HI_RED',
            '#00ff00': 'HI_GREEN', '#ffff00': 'HI_YELLOW', '#0000ff': 'HI_BLUE', '#ff00ff': 'HI_MAGENTA',
            '#00ffff': 'HI_CYAN', '#ffffff': 'HI_WHITE', }


def find_color16(hex: str) -> str:
    if hex in colors16:
        name = colors16[hex]
        return name
    return ''

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

html_output = '<table class="xterm-colors docutils align-default">' \
              '<tr>' \
              '<th>Ex</th>' \
              '<th>Code</th>' \
              '<th class="smaller dense">RGB<br>hex code</th>' \
              '<th>XTerm name</th>' \
              '<th class="smaller dense">Default mode<br>counterpart</th>' \
              '</tr>'

latex_separator = '   '
for col in col_len_list:
    latex_separator += '='*(col-1)+ ' '
latex_separator += '\n'

#latex_output = """.. table::\n\n"""
latex_output = ''

latex_output += f'   {"Code":<{col_len_list[0]}s}{"XTerm name":<{col_len_list[1]}s}' \
               f'{"Counterpart":<{col_len_list[2]}s}{"RGB hex":<{col_len_list[3]}s}\n' + latex_separator

for table_data in table_datas:
    html_output += '<tr>' \
                   '<td class="xterm-color-cell" style="background-color: {hexString}"></td>' \
                   '<td><pre>{colorId}</pre></td>' \
                   '<td><pre>{hexString}</pre></td>' \
                   '<td>{name}</td>' \
                   '<td>'.format(**table_data)
    if table_data['seq16']:
        html_output += '<a class="reference internal" ' \
                       'href="../apidoc/sequence.html#pytermor.sequence.{seq16}" ' \
                       'title="pytermor.sequence.{seq16}">' \
                       '<code class="xref any py py-data docutils literal notranslate">' \
                       '<span class="pre">{seq16}</span>' \
                       '</code>' \
                       '</a>' \
                       '</td>'.format(**table_data)
    html_output += '</tr>'

    latex_output += '   '
    for key in ['colorId', 'name', 'seq16', 'hexString']:
        latex_output += f'{table_data[key]:<{col_len[key]}}'
    latex_output += '\n'

    #im = PIL.Image.new('RGB', (591,591), table_data['hexString'])
    #im.save(f'_include/xterm-colors-table/color{table_data["colorId"]}.png')

html_output += '</table>'

with open('_include/xterm-colors-table.html', 'w') as output:
    output.write(html_output)
#with open('_include/xterm-colors-table.rst', 'w') as output:
#    output.write(latex_output)
