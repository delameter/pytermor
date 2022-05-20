from pytermor import autocomplete

span1 = autocomplete('hi_cyan', 'bold')
span2 = autocomplete('bg_black', 'inversed', 'underlined', 'italic')

msg = span1(f'Content{span2("-aware format")} nesting')
print(msg)
