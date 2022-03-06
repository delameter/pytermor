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

msg = '{}inversed {}and{} underlined{}'.format(
    fmt_inverse.open,
    fmt_underline.open,
    fmt_inverse.close,
    fmt_underline.close
)
print(msg)
```

### Low-level inlines
```python
from pytermor.preset import GREEN, UNDERLINE, RESET

msg = '{}green; {}underlined; {}clean'.format(
    GREEN.str,
    UNDERLINE.str,
    RESET.str
)
print(msg)
```
