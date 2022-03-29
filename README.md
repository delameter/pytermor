# PyTermor

(yet another) Python library designed for formatting terminal output using ANSI escape codes. Provides a registry with most useful SGR sequences and predefined formats.

## Motivation

Key feature of this library is providing necessary abstractions for building complex text sections with lots of formatting, while keeping the application code clear and readable. 

## Installation

    pip install pytermor

## Use cases

> <img src="./doc/uc1.png"/>
>
> `Format` instances are callable; they wraps specified string with preset leading and trailing control sequences.
> 
> ```python
> from pytermor.preset import fmt_yellow, fmt_green, fmt_bg_blue
>
> print(fmt_yellow('Basic'), fmt_bg_blue('text'), fmt_green('coloring'))
> ```

> <img src="./doc/uc2.png"/>
>
> Preset formats can safely overlap with each other (as long as they belong to different _modifier groups_).
>
> ```python
> from pytermor.preset import fmt_green, fmt_inverse, fmt_underline
> 
> msg = fmt_green('Nes' + fmt_inverse('te' + fmt_underline('d fo') + 'rm') + 'ats')
> print(msg)
> ``` 

> <img src="./doc/uc3.png"/>
>
> <details><summary><b>code</b> <i>(click)</i></summary>
>
> Use `build_c256()` to change text (or background) color to any of [xterm-256 colors](https://www.ditig.com/256-colors-cheat-sheet).
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
> Create your own SGR sequences with `build()` method, which accepts color/attribute keys, integer param values and even existing SGRs in any order. Keys can be specified using any case. 
> 
> ```python
> from pytermor import build
> from pytermor.preset import RESET, UNDERLINED
> 
> seq1 = build('red', 1, UNDERLINED)  # keys, integer codes or existing sequences
> seq2 = build('inversed', 'YELLOW')  # case-insensitive
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
> It's also possible to create custom wrapper presets which include both starting and ending control sequences.
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
> Mix high-level and low-level abstractions if necessary.
>
> ```python
> from pytermor.preset import *
> from pytermor.sequence import SequenceSGR
>
> msg = f'{CYAN}L{GREEN}ow-{fmt_inverse("l"+str(ITALIC)+"e")}ve{ITALIC_OFF}l ' \
>       f'{BG_HI_YELLOW}fo{fmt_underline.open}rm{BG_COLOR_OFF}at ' \
>       f'c{SequenceSGR(*MODE8_START.params, 214)}on{RESET}' \
>       f'{SequenceSGR(*MODE8_START.params, 208)}t{fmt_underline.close}r{RESET}' \
>       f'{SequenceSGR(*MODE8_START.params, 202)}ol{RESET}'
> print(msg)
> ```
> </details>


## API [module]

### `build(*params str|int|SequenceSGR) -> SequenceSGR`

Creates new `SequenceSGR` instance with specified params. Resulting sequence params order is the same as argument order. Each param can be specified as:
- string key (see [API: Preset](#api-preset))
- integer param value
- existing `SequenceSGR` instance (params will be extracted)

### `build_c256(color: int, bg: bool = False) -> SequenceSGR`

Creates new `SequenceSGR` instance either of `MODE8_START` type (set text color to `color`), or `BG_MODE8_START` type (same, but for background color), depending on `bg` value.
<br>

## API: SequenceSGR

Class describing SGR-mode ANSI escape sequence with varying amount of parameters.

<details>
<summary><b>Details</b> <i>(click)</i></summary>

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
<br>
</details>

## API: Format

`Format` is a wrapper class that contains starting (i.e. opening) `SequenceSGR` and (optionally) closing `SequenceSGR`.

<details>
<summary><b>Details</b> <i>(click)</i></summary>

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
<br>
</details>

## API: StringFilter

Common string modifier interface with dynamic configuration support.

<details>
<summary><b>Details</b> <i>(click)</i></summary>

### Subclasses

- `ReplaceSGR`
- `ReplaceCSI`
- `ReplaceNonAsciiBytes`

### Standalone usage

- Can be executed with `.invoke()` method or with direct call.
    
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

- `apply_filters` accepts both `StringFilter` (and subclasses) instances and subclass types, but latter is not configurable and will be invoked using default settings.
    
    ```python
    from pytermor import apply_filters
    from pytermor.string_filter import ReplaceNonAsciiBytes
    
    ascii_and_binary = b'\xc0\xff\xeeQWE\xffRT\xeb\x00\xc0\xcd\xed'
    
    # can either provide filter by type:
    # result = apply_filters(ascii_and_binary, ReplaceNonAsciiBytes)
    # ..or instantiate and configure it:
    result = apply_filters(ascii_and_binary, ReplaceNonAsciiBytes(b'.'))
    
    print(ascii_and_binary, '\n', result)
    ``` 
    <img src="./doc/ex7.png"/>

<br>
</details>

## API: Preset

Sequence and format registry.

<details>
<summary><b>SGR sequences</b> <i>(click)</i></summary>


- `var` &mdash; variable name defined in `pytermor.preset`;
- `key` &mdash; string that will be recognised by `build()` method;
- `params` &mdash; list of default CSI params for specified seqeunce.


| var | key | params | comment |
|---|-----|:---:|---|
| `RESET` | `"reset"` | 0 | disables all colors and attributes | |
| **attributes**
| `BOLD` | `"bold"` | 1 | | 
| `DIM` | `"dim"` | 2 | | 
| `ITALIC` | `"italic"` | 3 | | 
| `UNDERLINED` | `"underlined"` | 4 | | 
| `BLINK_SLOW` | `"blink_slow"` | 5 | | 
| `BLINK_FAST` | `"blink_fast"` | 6 | | 
| `INVERSED` | `"inversed"` | 7 | | 
| `HIDDEN` | `"hidden"` | 8 | | 
| `CROSSLINED` | `"crosslined"` | 9 | | 
| `DOUBLE_UNDERLINED` | `"double_underlined"` | 21 | | 
| `OVERLINED` | `"overlined"` | 53 | | 
| `DIM_BOLD_OFF` | `"dim_bold_off"` | 22 | | 
| `ITALIC_OFF` | `"italic_off"` | 23 | | 
| `UNDERLINED_OFF` | `"underlined_off"` | 24 | | 
| `BLINK_OFF` | `"blink_off"` | 25 | | 
| `INVERSED_OFF` | `"inversed_off"` | 27 | | 
| `HIDDEN_OFF` | `"hidden_off"` | 28 | | 
| `CROSSLINED_OFF` | `"crosslined_off"` | 29 | | 
| `OVERLINED_OFF` | `"overlined_off"` | 55 | | 
|**text colors**
| `BLACK` | `"black"` | 30 | | 
| `RED` | `"red"` | 31 | | 
| `GREEN` | `"green"` | 32 | | 
| `YELLOW` | `"yellow"` | 33 | | 
| `BLUE` | `"blue"` | 34 | | 
| `MAGENTA` | `"magenta"` | 35 | | 
| `CYAN` | `"cyan"` | 36 | | 
| `WHITE` | `"white"` | 37 | | 
| `MODE24_START` | `"mode24_start"` | 38 2 | set text color to specified;<br> 3 more params required: `r`,`g`,`b`<br> valid values: [0-255] | |
| `MODE8_START` | `"mode8_start"` | 38 5 | set text color to specified;<br> 1 more param required: `code`<br> valid value: [0-255] | | 
| `COLOR_OFF` | `"color_off"` | 39 | reset text color | 
|**background colors**
| `BG_BLACK` | `"bg_black"` | 40 | | 
| `BG_RED` | `"bg_red"` | 41 | | 
| `BG_GREEN` | `"bg_green"` | 42 | | 
| `BG_YELLOW` | `"bg_yellow"` | 43 | | 
| `BG_BLUE` | `"bg_blue"` | 44 | | 
| `BG_MAGENTA` | `"bg_magenta"` | 45 | | 
| `BG_CYAN` | `"bg_cyan"` | 46 | | 
| `BG_WHITE` | `"bg_white"` | 47 | | 
| `BG_MODE24_START` | `"bg_mode24_start"` | 48 2 |  set bg color to specified;<br> 3 more params required: `r`,`g`,`b`<br> valid values: [0-255] | |
| `BG_MODE8_START` | `"bg_mode8_start"` | 48 5 | set bg color to specified;<br> 1 more param required: `code`<br> valid value: [0-255] (color code) |
| `BG_COLOR_OFF` | `"bg_color_off"` | 49 | reset bg color | 
|**high intensity text colors**
| `GRAY` | `"gray"` | 90 | | 
| `HI_RED` | `"hi_red"` | 91 | | 
| `HI_GREEN` | `"hi_green"` | 92 | | 
| `HI_YELLOW` | `"hi_yellow"` | 93 | | 
| `HI_BLUE` | `"hi_blue"` | 94 | | 
| `HI_MAGENTA` | `"hi_magenta"` | 95 | | 
| `HI_CYAN` | `"hi_cyan"` | 96 | | 
| `HI_WHITE` | `"hi_white"` | 97 | | 
|**high intensity bg colors**
| `BG_GRAY` | `"bg_gray"` | 100 | | 
| `BG_HI_RED` | `"bg_hi_red"` | 101 | | 
| `BG_HI_GREEN` | `"bg_hi_green"` | 102 | | 
| `BG_HI_YELLOW` | `"bg_hi_yellow"` | 103 | | 
| `BG_HI_BLUE` | `"bg_hi_blue"` | 104 | | 
| `BG_HI_MAGENTA` | `"bg_hi_magenta"` | 105 | | 
| `BG_HI_CYAN` | `"bg_hi_cyan"` | 106 | | 
| `BG_HI_WHITE` | `"bg_hi_white"` | 107 | |
</details>
<br>


<details>
<summary><b>SGR formats</b> <i>(click)</i></summary>

</details>

## References

- https://en.wikipedia.org/wiki/ANSI_escape_code