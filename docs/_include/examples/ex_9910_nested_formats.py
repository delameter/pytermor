from pytermor import color, ColorIndexed, Style
from pytermor.renderer import HtmlRenderer, SGRRenderer

default = Style(fg_color='hi_white')
HtmlRenderer.set_as_default()

html = '<html><body style="background-color: #161616; font-family: monospace; font-size: 1.2em;">'
for name in ColorIndexed._name_map.keys():
    q = ColorIndexed._name_map[name]
    dup = (len(q) >= 2)
    for c in q:
        html += default.render(f'[{c._code:_>3d}] {c.format_value()}')
        if dup:
            html += default.render(' *')
        html += ' ' + Style(bg_color=c, auto_fg=True).render(name)
        html += '<br>'

html += '</body></html>'
output_path = '/tmp/test.html'
with open(output_path, 'wt') as f:
    bytes_wrote = f.write(html)

SGRRenderer.set_as_default()
print('Wrote {0} bytes to "{1}"'.format(
    Style(bold=True).render(bytes_wrote),
    Style(fg_color=color.BLUE).render(output_path)))
