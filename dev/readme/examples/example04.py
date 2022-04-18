from pytermor import build_c256, seq, autof

txt = '256 colors support'
start_color = 41
msg = ''
for idx, c in enumerate(range(start_color, start_color+(36*6), 36)):
    msg += f'{build_c256(c)}{txt[idx*3:(idx+1)*3]}{seq.COLOR_OFF}'

print(autof(seq.BOLD).wrap(msg))
