from pytermor import autof

fmt1 = autof('hi_cyan', 'bold')
fmt2 = autof('bg_black', 'inversed', 'underlined', 'italic')

msg = fmt1(f'Content{fmt2("-aware format")} nesting')
print(msg)
