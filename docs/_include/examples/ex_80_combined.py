from pytermor import sequence
from pytermor.sequence import SequenceSGR

combined = SequenceSGR(1, 31) + SequenceSGR(4)
print(f'{combined}combined{sequence.RESET}', str(combined).encode())
