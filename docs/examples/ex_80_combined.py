from pytermor import SequenceSGR, Seqs

combined = SequenceSGR(1, 31) + SequenceSGR(4)
print(f'{combined}combined{Seqs.RESET}', str(combined).encode())
