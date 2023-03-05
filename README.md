<h1 align="center">
   <img src="https://user-images.githubusercontent.com/50381946/167745623-66bcb825-f787-4f8a-a317-18775d3f104a.png" width="96" height="96"><br>
   <img src="https://user-images.githubusercontent.com/50381946/219900171-660d4309-c290-424d-95f8-8d0e5958511d.png" width="400" height="64">
</h1>

<div align="center">
  <img src="https://img.shields.io/badge/python-3.8-3776AB?logo=python&logoColor=white&labelColor=333333">
  <a href="https://pypi.org/project/pytermor/">
    <img alt="PyPI" src="https://img.shields.io/pypi/v/pytermor">
  </a>
  <a href="https://pepy.tech/project/pytermor/">
    <img alt="Downloads" src="https://pepy.tech/badge/pytermor">
  </a>
  <br>
  <a href='https://coveralls.io/github/delameter/pytermor?branch=dev'>
    <img src='https://coveralls.io/repos/github/delameter/pytermor/badge.svg?branch=dev' alt='Coverage Status' />
  </a>
  <a href="https://github.com/psf/black">
    <img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg">
  </a>
</div>

<h4 align="center">
    <a href="https://pytermor.dlup.link">
      [Documentation]
    </a>
    |
    <a href="CHANGES.rst">
      [Changelog]
    </a>
</h4>
<hr>

_(yet another)_ Python library initially designed for formatting terminal output using ANSI escape codes.

Provides [high-level](guide.high-level) methods for working with text sections, colors, formats, alignment and wrapping, as well as [low-level](guide.low-level) `ansi` module which allows operating with [SGR sequences](SequenceSGR) and also implements automatic "soft" format termination. Depending on the context and technical requirements either approach can be used. Also includes a set of additional number/string/date formatters for pretty output.


## Motivation

Key feature of this library is extendability and a variety of formatters (called [renderers](guide.renderers)), which determine the output syntax:

- [`SgrRenderer`](SgrRenderer) (global default)
- `TmuxRenderer`
- `HtmlRenderer`
- `SgrDebugger` (mostly for development)
- etc.

No dependencies required, only Python Standard Library _(there are some for testing and docs building, though)._


## Installation

    pip install pytermor


## Features

_Span_ is a combination of two control sequences; it wraps specified string with pre-defined leading and trailing SGR definitions.

```python3
from pytermor import span

print(span.red('Feat') + span.bold('ures'))
```


## * ![image](https://user-images.githubusercontent.com/50381946/161387692-4374edcb-c1fe-438f-96f1-dae3c5ad4088.png)

Preset spans can safely overlap with each other (as long as they require different **breaker** sequences to reset).

```python3
from pytermor import span

print('... ' +
      span.blue(span.underlined('nested') +
                span.bold(' styles')) + ' in...')
```

## * ![image](https://user-images.githubusercontent.com/50381946/161387711-23746520-419b-4917-9401-257854ff2d8a.png)

Compose text spans with automatic content-aware format termination.

```python3
from pytermor import autocomplete

span1 = autocomplete('blue', 'bold')
span2 = autocomplete('cyan', 'inversed', 'underlined', 'italic')

msg = span1(f'Content{span2("-aware format")} nesting')
print(msg)
```

## * ![image](https://user-images.githubusercontent.com/50381946/161387734-677d5b10-15c1-4926-933f-b1144b0ce5cb.png)

Create your own _SGR_ _sequences_ with `build()` method, which accepts color/attribute keys, integer codes and even existing _SGRs_, in any amount and in any order. Key resolving is case-insensitive.

```python3
from pytermor import sequence, build

seq1 = build('red', 1)  # keys or integer codes
seq2 = build(seq1, sequence.ITALIC)  # existing SGRs
seq3 = build('underlined', 'YELLOW')  # case-insensitive

msg = f'{seq1}Flexible{sequence.RESET} ' + \
      f'{seq2}sequence{sequence.RESET} ' + \
      str(seq3) + 'builder' + str(sequence.RESET)
print(msg)
```

## * ![image](https://user-images.githubusercontent.com/50381946/161387746-0a94e3d2-8295-478c-828c-333e99e5d50a.png)

Use `color_indexed()` to set foreground/background color to any of [↗ xterm-256 colors](https://www.ditig.com/256-colors-cheat-sheet).

```python3
from pytermor import color_indexed, sequence, autocomplete

txt = '256 colors support'
start_color = 41
msg = ''
for idx, c in enumerate(range(start_color, start_color+(36*6), 36)):
    msg += f'{color_indexed(c)}{txt[idx*3:(idx+1)*3]}{sequence.COLOR_OFF}'

print(autocomplete(sequence.BOLD).wrap(msg))
```

## * ![image](https://user-images.githubusercontent.com/50381946/161411577-743b9a81-eac3-47c0-9b59-82b289cc0f45.png)

It's also possible to use 16M-color mode (or True color) &mdash; with `color_rgb()` wrapper method.

```python3
from pytermor import color_rgb, sequence, span

txt = 'True color support'
msg = ''
for idx, c in enumerate(range(0, 256, 256//18)):
    r = max(0, 255-c)
    g = max(0, min(255, 127-(c*2)))
    b = c
    msg += f'{color_rgb(r, g, b)}{txt[idx:(idx+1)]}{sequence.COLOR_OFF}'

print(span.bold(msg))
```

Proceed to [documentation](wip).
