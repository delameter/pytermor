from pytermor import SeqIndex, SequenceSGR

seq1 = SequenceSGR('hi_blue', 1)  # keys or integer codes
seq2 = SequenceSGR(seq1, SeqIndex.ITALIC)  # existing SGRs
seq3 = SequenceSGR('underlined', 'YELLOW')  # case-insensitive

msg = f'{seq1}Flexible{SeqIndex.RESET} ' + \
      f'{seq2}sequence{SeqIndex.RESET} ' + \
      str(seq3) + 'builder' + str(SeqIndex.RESET)
print(msg)
