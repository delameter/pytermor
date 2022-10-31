from pytermor import SequenceSGR, SeqIndex

combined = SequenceSGR(1, 31) + SequenceSGR(4)
print(f'{combined}combined{SeqIndex.RESET}', str(combined).assemble())
