# pytermor

Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt.

Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur?

## Use cases

> <img src="./doc/uc1.png"/>
>
> ```python
> from pytermor.preset import fmt_yellow, fmt_green, fmt_bg_blue
>
>  print(fmt_yellow('Basic'),
>       fmt_bg_blue('text'),
>       fmt_green('coloring'))
> ```

> <img src="./doc/uc2.png"/>
>
> ```python
> from pytermor.preset import fmt_green, fmt_inverse, fmt_underline
> 
> msg = fmt_green('Nes' + fmt_inverse('te' + fmt_underline('d fo') + 'rm') + 'ats')
> print(msg)
> ``` 

> <img src="./doc/uc3.png"/>
> <details><summary><b>code</b> <i>(click)</i></summary>
>
> ```python
> from pytermor import build_c256, build
> from pytermor.preset import COLOR_OFF
> 
> txt = '256 colors support'
> msg = f'{build("bold")}'
> start_color = 41
> for idx, c in enumerate(range(start_color, start_color+(36*6), 36)):
>     msg += f'{build_c256(c)}'
>     msg += f'{txt[idx*3:(idx+1)*3]}{COLOR_OFF}'
> print(msg)
> ```
> </details>

> <img src="./doc/uc4.png"/>
> <details><summary><b>code</b> <i>(click)</i></summary>
>
> ```python
> from pytermor import build
> from pytermor.preset import RESET, UNDERLINED
> # create your own reusable sequences with pytermor.build():
> 
> seq1 = build('red', 1, UNDERLINED)  # keys, integer codes or existing sequences
> seq2 = build('inversed', 'YELLOW')  # keys are case-insensitive
> 
> msg = f'{seq1}Flexible{RESET} ' +
>       f'{build(seq1, 3)}sequence{RESET} ' +
>       str(seq2) + 'builder' + str(RESET)
> print(msg) 
> ```
> </details>

> <img src="./doc/uc5.png"/>
> <details><summary><b>code</b> <i>(click)</i></summary>
>
> ```python
> from pytermor.preset import *
> 
> fmt1 = Format(HI_BLUE + BOLD, reset_after=True)
> fmt2 = Format(BG_BLACK + INVERSED + UNDERLINED + ITALIC,
>               BG_COLOR_OFF + INVERSED_OFF + UNDERLINED_OFF + ITALIC_OFF)
> msg = fmt1(f'Custom n{fmt2("establ")}e formats')
> print(msg)
> ```
> </details>

> <img src="./doc/uc6.png"/>
> <details><summary><b>code</b> <i>(click)</i></summary>
>
> ```python
> from pytermor.preset import *
> from pytermor.sequence import SequenceSGR
> 
> msg = f'{CYAN}L{GREEN}ow-{fmt_inverse.open}l{ITALIC}e{fmt_inverse.close}ve{ITALIC_OFF}l '
>       f'{BG_HI_YELLOW}fo{fmt_underline.open}rm{BG_COLOR_OFF}at '
>       f'c{SequenceSGR(*MODE8_START.params, 214)}on{RESET}'
>       f'{SequenceSGR(*MODE8_START.params, 208)}t{fmt_underline.close}r{RESET}'
>       f'{SequenceSGR(*MODE8_START.params, 202)}ol{RESET}'
> print(msg)
> ```
> </details>
<br>

## API | `pytermor` module

### build()

Sed rutrum nibh id suscipit cursus. Integer fermentum pretium purus vitae lacinia. Aenean ullamcorper mattis urna vitae varius. Morbi sed imperdiet lorem. Nulla scelerisque justo est. Quisque non tincidunt sem, sit amet vulputate ligula. Vivamus nec justo nibh. Vestibulum elementum sodales neque, sed mollis tellus pharetra non. Fusce accumsan nunc vitae tincidunt vestibulum.

### build_c256()

In dictum risus mauris, sit amet finibus elit iaculis a. Quisque non felis nibh. Fusce condimentum ligula id ligula ultrices, a pharetra justo malesuada. In id mi quis dui lobortis sollicitudin at at elit. Donec laoreet tincidunt magna in lacinia. Duis felis lacus, vestibulum et lobortis nec, pellentesque ac tellus. In tempus vestibulum feugiat.
<br><br>

## API | `SequenceSGR` class

Class describing SGR-mode ANSI escape sequence with varying amount of parameters.

- To get the resulting sequence simply cast instance to `str`:

    ```python
    from pytermor.sequence import SequenceSGR
    
    seq = str(SequenceSGR(4, 7))   # direct transform with str()
    msg = f'({seq})'               # f-string var substitution
    print(msg + f'{SequenceSGR(0)}',  # f-string value
          str(seq.encode()),
          seq.encode().hex(':'))
    ```
    <img src="./doc/ex1.png"/>

  1st part consists of "applied" escape sequences; 2nd part shows up one of the sequences in raw mode, as if it was ignored by the terminal; 3rd part is hexademical sequence byte values.

    <details>
    <summary><b>SGR sequence structure</b> <i>(click)</i></summary>

  1. `\x1b`|`1b` is ESC _control character_, which opens a control sequence.

  2. `[` is sequence _introducer_, it determines the type of control sequence (in this case it's CSI, or "Control Sequence Introducer").

  3. `4` and `7` are _parameters_ of the escape sequence; they mean "underlined" and "inversed" attributes respectively. Those parameters must be separated by `;`.

  4. `m` is sequence _terminator_; it also determines the sub-type of sequence, in our case SGR, or "Select Graphic Rendition". Sequences of this kind are most commonly encountered.
    </details>


- One instance of `SequenceSGR` can be added to another. This will result in a new `SequenceSGR` instance with combined params.
    
    ```python
    from pytermor import SequenceSGR
    from pytermor.preset import RESET
      
    mixed = SequenceSGR(1, 31) + SequenceSGR(4)
    print(f'{mixed}combined{RESET}', str(mixed).encode())
    ```
    <img src="./doc/ex2.png"/> 

- Pretty much all single-param sequences (that can be used at least for _something_) are specified in `pytermor.preset` module. Example usage:
    
    ```python
    from pytermor.preset import BLACK, BG_HI_GREEN, RESET
      
    print(f'{BLACK}{BG_HI_GREEN}', 'Example text', str(RESET))
    ```
    <img src="./doc/ex3.png"/>

  <i>Complete list is given at the end of this document.</i>
  <br><br>

## API | `Format` class

`Format` is a wrapper class that contains starting (i.e. opening) `SequenceSGR` and (optionally) closing `SequenceSGR`.

- You can define your own reusable formats or import predefined ones from `pytermor.preset`:

    ```python
    from pytermor.format import Format
    from pytermor.preset import HI_RED, COLOR_OFF, fmt_overline
    
    fmt_error = Format(HI_RED, COLOR_OFF)
    print(fmt_overline.open +
        'overline might not work ' +
        fmt_error('>') + ':(' +
        fmt_overline.close)
    ```
    <img src="./doc/ex4.png"/>


- The main purpose of `Format` is to simplify creation of non-resetting text spans, so that developer doesn't have to restore all previously applied formats after every closing sequence (which usually consists of `RESET`).


- Example: we are given a text span which is initially **bold** and <u>underlined</u>. We want to recolor a few words inside of this span. By default this will result in losing all the formatting to the right of updated text span (because `RESET`|`\e[m` clears all text attributes).


- However, there is an option to specify what attributes should be disabled (instead of disabling _all_ of them):

    ```python
    from pytermor.preset import *
    
    fmt_warn = Format(
      HI_YELLOW + UNDERLINED,  # sequences can be summed up, remember?
      COLOR_OFF + UNDERLINED_OFF,  # "counteractive" sequences
      reset_after=False
    )
    orig_text = fmt_bold(f'{BG_BLACK}this is the original string{RESET}')
    updated_text = orig_text.replace('original', fmt_warn('updated'), 1)
    print(orig_text, '\n', updated_text)
    ```
    <img src="./doc/ex5.png"/>


- As you can see, the update went well &mdash; we kept all the previously applied formatting. Of course, this method cannot be 100% applicable &mdash; for example, imagine that original text was colored blue. After the update "string" word won't be blue anymore, as we used `COLOR_OFF` escape sequence to neutralize our own red color. But it still can be helpful for a majority of cases (especially when text is generated and formatted by the same program and in one go).
  <br><br>

## API | `StringFilter` superclass

Common string modifier interface with dynamic configuration support.

<details>
<summary><b>Details</b> <i>(click)</i></summary>

### Subclasses

- `ReplaceSGR`
- `ReplaceCSI`
- `ReplaceNonAsciiBytes`

### Standalone usage

```python
from pytermor.preset import fmt_red
from pytermor.string_filter import ReplaceSGR

formatted = fmt_red('this text is red')
replaced = ReplaceSGR('[LIE]').invoke(formatted)
# or directly:
# replaced = ReplaceSequenceSGRs('[LIE]')(formatted)

print(formatted, '\n', replaced)
``` 
<img src="./doc/ex6.png"/>


### Usage with `apply_filters`

```python
from pytermor import apply_filters
from pytermor.string_filter import ReplaceNonAsciiBytes

ascii_and_binary = b'\xc0\xff\xeeQWE\xffRT\xeb\x00\xc0\xcd\xed'

# can either provide filter by type (default settings will be used):
# result = apply_filters(ascii_and_binary, ReplaceNonAsciiBytes)
# ..or instantiate and configure it:
result = apply_filters(ascii_and_binary, ReplaceNonAsciiBytes(b'.'))

print(ascii_and_binary, '\n', result)
``` 
<img src="./doc/ex7.png"/>
</details>
<br>

## Presets

At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident, similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga. Et harum quidem rerum facilis est et expedita distinctio. Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil impedit quo minus id quod maxime placeat facere possimus, omnis voluptas assumenda est, omnis dolor repellendus. Temporibus autem quibusdam et aut officiis debitis aut rerum necessitatibus saepe eveniet ut et voluptates repudiandae sint et molestiae non recusandae. Itaque earum rerum hic tenetur a sapiente delectus, ut aut reiciendis voluptatibus maiores alias consequatur aut perferendis doloribus asperiores repellat.

* Prefix `BG_*` indicates that this sequence changes background color, not the text color.
* Prefix `HI_*` means "high intensity" &mdash; brighter versions of default colors.
