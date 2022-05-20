from pytermor import color_rgb, sequence, span

txt = 'True color support'
msg = ''
for idx, c in enumerate(range(0, 256, 256//18)):
    r = max(0, 255-c)
    g = max(0, min(255, 127-(c*2)))
    b = c
    msg += f'{color_rgb(r, g, b)}{txt[idx:(idx+1)]}{sequence.COLOR_OFF}'

print(span.bold(msg))
