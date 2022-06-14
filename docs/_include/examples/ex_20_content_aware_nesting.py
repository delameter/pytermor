from pytermor import Span

span1 = Span('blue', 'bold')
span2 = Span('cyan', 'inversed', 'underlined', 'italic')

msg = span1(f'Content{span2("-aware format")} nesting')
print(msg)
