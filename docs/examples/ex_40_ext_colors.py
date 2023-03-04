from pytermor import SequenceSGR, SeqIndex

start_color = 41
for idx, c in enumerate(range(start_color, start_color+(36*6), 36)):
    print(f'{SequenceSGR.new_color_256(c)}███{SeqIndex.COLOR_OFF}', end='')

print('\n')
for idx, c in enumerate(range(0, 256, 256//17)):
    r = max(0, 255-c)
    g = max(0, min(255, 127-(c*2)))
    b = c
    print(f'{SequenceSGR.new_color_rgb(r, g, b)}█{SeqIndex.COLOR_OFF}', end='')
