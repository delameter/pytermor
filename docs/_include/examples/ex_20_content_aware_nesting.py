from pytermor import autospan

span1 = autospan('blue', 'bold')
span2 = autospan('cyan', 'inversed', 'underlined', 'italic')

msg = span1(f'Content{span2("-aware format")} nesting')
print(msg)
