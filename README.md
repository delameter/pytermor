# pytermor

https://github.com/delameter/pytermor

## Use cases

### Simple text coloring
```python
from pytermor.preset import fmt_green

print(fmt_green('Success'))
```

### Format overlapping
```python
from pytermor.preset import fmt_green, fmt_bold

msg = fmt_green('Build ' + fmt_bold('complete') + ' in 13 seconds')
print(msg)
```

### Flexible definitions
```python
from pytermor import build

fmt_caution = build('inverse', 'yellow')
fmt_date = build('red bold')
msg = fmt_date('06-Mar-2022: ') + fmt_caution('Caution: ') + 'Servers down'
print(msg)
```

### Custom formats
```python
from pytermor.format import Format
from pytermor.preset import BOLD, RED, HI_RED, RESET

fmt_error = Format(RED + BOLD, reset=True)
print(fmt_error('Error'))
print(Format(HI_RED + BOLD, RESET)('Panic!'))
```

### Fine tuning
```python
from pytermor.preset import fmt_inverse, fmt_underline

msg = f'{fmt_inverse.open}inversed'
      f'{fmt_underline.open} and'
      f'{fmt_inverse.close} underlined'
      f'{fmt_underline.close}'
print(msg)
```

### Low-level inlines
```python
from pytermor.preset import GREEN, UNDERLINED, UNDERLINED_OFF, RESET

msg = f'{GREEN.str}green;'
      f'{UNDERLINED.str}underlined;'
      f'{UNDERLINED_OFF.str}green;'
      f'{RESET.str}default'
print(msg)
```
