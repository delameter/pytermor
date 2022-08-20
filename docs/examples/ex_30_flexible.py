from pytermor import Seqs, build

seq1 = build('hi_blue', 1)  # keys or integer codes
seq2 = build(seq1, Seqs.ITALIC)  # existing SGRs
seq3 = build('underlined', 'YELLOW')  # case-insensitive

msg = f'{seq1}Flexible{Seqs.RESET} ' + \
      f'{seq2}sequence{Seqs.RESET} ' + \
      str(seq3) + 'builder' + str(Seqs.RESET)
print(msg)
