# pytermor

@TODO

## Use cases

### Basic text coloring

```python
from pytermor.preset import fmt_bg_blue, fmt_yellow, fmt_green

print(fmt_yellow('Basic'),
      fmt_bg_blue('text'),
      fmt_green('coloring'))
```
<img src=".doc/uc1.png"/>


<details><summary><h3>Nested formats</h3></summary>

```python
from pytermor.preset import fmt_green, fmt_inverse, fmt_underline

msg = fmt_green('Nes' + fmt_inverse('te' + fmt_underline('d fo') + 'rm') + 'ats')
print(msg)
``` 
<img src=".doc/uc2.png"/>
</details>
<details><summary><h3>256 colors support</h3></summary>

```python
from pytermor import build_c256, build
from pytermor.preset import COLOR_OFF

txt = '256 colors support'
msg = f'{build("bold")}'
for idx, c in enumerate([27, 63, 99, 135, 171, 207]):
    msg += f'{build_c256(c)}'
    msg += f'{txt[idx*3:(idx+1)*3]}{COLOR_OFF}'
print(msg)
```
<img src=".doc/uc3.png"/>
</details>
<details><summary><h3>Flexible sequnce builder</h3></summary>


```python
from pytermor import build
from pytermor.preset import RESET, UNDERLINED
# create your own reusable sequences with pytermor.build():

seq1 = build('red', 1, UNDERLINED)  # keys, integer codes or existing sequences
seq2 = build('inversed', 'YELLOW')  # keys are case-insensitive

msg = f'{seq1}Flexible{RESET} ' +
      f'{build(seq1, 3)}sequence{RESET} ' +
      str(seq2) + 'builder' + str(RESET)
print(msg) 
```
<img src=".doc/uc4.png"/>
</details>
<details><summary><h3>Custom nestable formats</h3></summary>

```python
from pytermor.preset import *

fmt1 = Format(HI_BLUE + BOLD, reset_after=True)
fmt2 = Format(BG_BLACK + INVERSED + UNDERLINED + ITALIC,
              BG_COLOR_OFF + INVERSED_OFF + UNDERLINED_OFF + ITALIC_OFF)
msg = fmt1(f'Custom n{fmt2("establ")}e formats')
print(msg)
```
<img src=".doc/uc5.png"/>
</details>
<details><summary><h3>Low-level format control</h3></summary>

```python
from pytermor.preset import *
from pytermor.sequence import SGRSequence

msg = f'L{GREEN}ow {fmt_inverse.open}-{ITALIC}le{fmt_inverse.close}ve{ITALIC_OFF}l '
      f'f{BG_HI_YELLOW}o{fmt_underline.open}r{BG_COLOR_OFF}ma{fmt_underline.close}t '
      f'c{RESET}{SGRSequence(38, 5, 214)}on{SGRSequence(38, 5, 208)}tr{SGRSequence(38, 5, 202)}ol'
      f'{RESET}'
print(msg)
```
<img src=".doc/uc6.png"/>
</details>
<br>

## API | `pytermor` module

### build()

@TODO

### build_c256()

@TODO
<br>

## API | `SGRSequence` class

Class describing SGR-mode ANSI escape sequence with varying amount of parameters. To get the resulting sequence simply cast instance to `str`, like here:

<table><tr>
 <td rowspan="2">

1st part consists of "applied" escape sequences; 2nd part shows up one of the sequences in raw mode, as if it was ignored by the terminal; 3rd part is hexademical sequence byte values.

</td><th>
 <img src=".doc/ex1.png"/>
</th></tr><tr><td>

```python3
from pytermor.sequence import SGRSequence
from pytermor.preset import BG_GREEN, RESET

seq1 = 'A' + str(SGRSequence(1, 4)) + 'B'
seq2 = f'text{BG_GREEN}text'
print(seq1, seq2, str(RESET), '', seq1.encode())
```

</td></tr>
<tr><td colspan="2">

`\x1b` is ESC _control character_, which opens a control sequence (can also be written as `\e`|`\033`|`ESC`).

`[` is sequence _introducer_, it determines the type of control sequence (in this case it's CSI, or "Control Sequence Introducer").

`1` and `4` are _parameters_ of the escape sequence; they mean "bold text" and "underlined text" respectively. Those parameters must be separated by `;`.

`m` is sequence _terminator_; it also determines the sub-type of sequence, in our case SGR, or "Select Graphic Rendition". Sequences of this kind are most commonly encountered.

</td></tr>
<tr><td colspan="2"></td></tr>
<tr><td rowspan="2">

One instance of `SGRSequence` can be added to another. This will result in a new `SGRSequence` instance with combined params.

 </td>
 <th>
 <img src=".doc/ex2.png"/> 
 </th>
</tr><tr>
 <td>

```python
from pytermor import SGRSequence
from pytermor.preset import RESET

new_seq = SGRSequence(1, 31) + SGRSequence(4)
print(f'{new_seq}test{RESET}', '', f'{new_seq}'.encode())
```

 </td>
</tr><tr>
 <td rowspan="2">

Pretty much all single-param sequences (that can be used at least for _something_) are specified in `pytermor.preset` module. Example usage is to the left.

*Complete list is given at the end of this document.*

 </td>
 <th>
  <img src=".doc/ex3.png"/>
 </th>
</tr><tr>
 <td>

```python
from pytermor.preset import BLACK, BG_HI_GREEN, RESET

print(f'{BLACK}{BG_HI_GREEN}', 'Example text', str(RESET))
```

</td></tr></table>
<br>

## API | `Format` class

`Format` is a wrapper class that contains starting (i.e. opening) `SGRSequence` and (optionally) closing `SGRSequence`.

<table><tr>
 <td>

You can define your own reusable formats or import predefined ones from `pytermor.preset`:
</td><th width="50%">
  <img src=".doc/ex4.png"/>
 </th>
</tr>
<tr>
 <td colspan="2">

```python
from pytermor.format import Format
from pytermor.preset import HI_RED, fmt_overline

fmt_error = Format(HI_RED, reset_after=True)
print(fmt_error('ERROR!'))
print(fmt_overline.open +
      'overline might not work because'
      ' its not fully supported :(' +
      fmt_overline.close)
```

 </td>
</tr></table>

The main purpose of `Format` is to simplify creation of non-resetting text spans, so that developer doesn't have to restore all previously applied formats after every closing sequence (which usually consists of `RESET`).


Example: we are given a text span which is initially **bold** and <u>underlined</u>. We want to recolor a few words inside of this span. By default this will result in losing all the formatting to the right of updated text span (because `RESET`|`\e[m` clears all text attributes).

<table><tr>
 <td>

However, there is an option to specify what attributes should be disabled (instead of disabling _all_ of them):
</td><th width="50%">
 <img src=".doc/ex5.png"/>
 </th>
</tr>
<tr>
 <td colspan="2">

```python
from pytermor.format import Format
from pytermor.preset import HI_RED, COLOR_OFF, OVERLINED, OVERLINED_OFF, fmt_bold, fmt_underline

fmt_error = Format(
    HI_RED + OVERLINED,  # sequences can be summed up, remember?
    COLOR_OFF + OVERLINED_OFF,  # "counteractive" sequences
    reset_after=False
)
orig_text = fmt_bold(fmt_underline(
    'this is the original string'
))
updated_text = orig_text.replace('original', fmt_error('updated'), 1)
print(orig_text)
print(updated_text)
```

 </td>
</tr></table>

As you can see, the update went well &mdash; we kept all the previously applied formatting. Of course, this method cannot be 100% applicable &mdash; for example, imagine that original text was colored blue. After the update "string" word won't be blue anymore, as we used `COLOR_OFF` escape sequence to neutralize our own red color. But it still can be helpful for a majority of cases (especially when text is generated and formatted by the same program and in one go).
<br><br>

## API | `StringFilter` superclass

**Purpose:** to provide common string modifier interface with dynamic configuration support.

### Subclasses

- `ReplaceSGRSequences`
- `ReplaceCSISequences`
- `ReplaceNonAsciiBytes`

<table>
<tr>
 <td><h3>Standalone usage</h3></td>
 <th><img src=".doc/ex6.png"/></th>
</tr>
<tr>
 <td colspan="2" width="1000px">

 ```python
from pytermor.preset import fmt_red
from pytermor.string_filter import ReplaceSGRs

formatted = fmt_red('this text is red')
print(formatted)
print(ReplaceSGRs('[LIE]').invoke(formatted))
# or:
# ReplaceSGRSequences('[E]')(formatted)
```

 </td>
</tr>
<tr>
 <td>
 <h3>Usage with <code>apply_filters</code></h3>
 </td>
 <th><img src=".doc/ex7.png"/></th>
</tr>
<tr>
 <td colspan="2">

```python
from pytermor import apply_filters
from pytermor.string_filter import ReplaceNonAsciiBytes

ascii_and_binary = b'\xc0\xff\xeeABC\xffDEF\xeb\x00\xc0\xcd\xed\xa7\xde'

# can either provide filter by type (default settings will be used):
# result = apply_filters(ascii_and_binary, ReplaceNonAsciiBytes)
# ..or instantiate and configure it:
result = apply_filters(ascii_and_binary, ReplaceNonAsciiBytes(b'.'))

print(result)
```

 </td>
</tr></table>
<br>

## Presets

@TODO

* Prefix `BG_*` indicates that this sequence changes background color, not the text color.
* Prefix `HI_*` means "high intensity" &mdash; brighter versions of default colors.
