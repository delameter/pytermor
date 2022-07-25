from pytermor import sequence, build

seq1 = build('hi_blue', 1)  # keys or integer codes
seq2 = build(seq1, sequence.ITALIC)  # existing SGRs
seq3 = build('underlined', 'YELLOW')  # case-insensitive

msg = f'{seq1}Flexible{sequence.RESET} ' + \
      f'{seq2}sequence{sequence.RESET} ' + \
      str(seq3) + 'builder' + str(sequence.RESET)
print(msg)
