from pytermor import seq, SequenceSGR

combined = SequenceSGR(1, 31) + SequenceSGR(4)
print(f'{combined}combined{seq.RESET}', str(combined).encode())
