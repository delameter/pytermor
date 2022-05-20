from pytermor import sequence, SequenceSGR

combined = SequenceSGR(1, 31) + SequenceSGR(4)
print(f'{combined}combined{sequence.RESET}', str(combined).encode())
