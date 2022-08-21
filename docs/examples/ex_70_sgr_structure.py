from pytermor import SequenceSGR

seq = SequenceSGR(4, 7)
msg = f'({seq})'

print(msg + f'{SequenceSGR(0).assemble()}')
print(str(msg.assemble()))
print(msg.assemble().hex(':'))
