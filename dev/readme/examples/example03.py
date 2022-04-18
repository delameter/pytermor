from pytermor import seq, build

seq1 = build('red', 1)  # keys or integer codes
seq2 = build(seq1, seq.ITALIC)  # existing SGRs as part of a new one
seq3 = build('underlined', 'YELLOW')  # case-insensitive

msg = f'{seq1}Flexible{seq.RESET} ' + \
      f'{seq2}sequence{seq.RESET} ' + \
      str(seq3) + 'builder' + str(seq.RESET)
print(msg)
