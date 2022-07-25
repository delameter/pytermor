from pytermor.sequence import SequenceSGR

seq = SequenceSGR(4, 7)
msg = f'({seq})'

print(msg + f'{SequenceSGR(0).encode()}')
print(str(msg.encode()))
print(msg.encode().hex(':'))
