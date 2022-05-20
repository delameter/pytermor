from pytermor import color_indexed, sequence, autocomplete

txt = '256 colors support'
start_color = 41
msg = ''
for idx, c in enumerate(range(start_color, start_color+(36*6), 36)):
    msg += f'{color_indexed(c)}{txt[idx*3:(idx+1)*3]}{sequence.COLOR_OFF}'

print(autocomplete(sequence.BOLD).wrap(msg))
