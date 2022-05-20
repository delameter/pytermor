from pytermor import sequence, build

seq1 = build('red', 1)  # keys or integer codes
seq2 = build(seq1, sequence.ITALIC)  # existing SGRs as part of a new one
seq3 = build('underlined', 'YELLOW')  # case-insensitive

msg = f'{seq1}Flexible{sequence.RESET} ' + \
      f'{seq2}sequence{sequence.RESET} ' + \
      str(seq3) + 'builder' + str(sequence.RESET)
print(msg)
