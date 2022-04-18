from pytermor import SequenceSGR

seq = SequenceSGR(4, 7)
msg = f'({seq})'
print(msg + f'{SequenceSGR(0).print()}', str(msg.encode()), msg.encode().hex(':'))
