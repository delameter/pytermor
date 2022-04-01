# pytermor

_(yet another)_ Python library designed for formatting terminal output using ANSI escape codes. Implements automatic closing sequence compose. Also provides a registry of ready-to-use SGR sequences and formats (=combined sequences).

## Motivation

Key feature of this library is providing necessary abstractions for building complex text sections with lots of formatting, while keeping the application code clear and readable.

## Installation

    pip install pytermor

## Use cases

> <img src="./doc/uc1.png"/>
>
> `Format` is a combination of two control sequences; it wraps specified string with pre-defined leading and trailing SGR definitions.
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
> Use `build_c256()` to set text/background color to any of [↗ xterm-256 colors](https://www.ditig.com/256-colors-cheat-sheet).
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
> Create your own SGR sequences with `build()` method, which accepts color/attribute keys, integer param values and even existing SGRs, in any amount and in any order. Key resolving is case-insensitive.
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
> It's possible to create custom wrapper presets as well, which represent two control sequences - opening and closing.
>
> ```python
> from pytermor.preset import *
> 
> fmt1 = Format(HI_BLUE + BOLD, hard_reset_after=True)
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

## Format soft reset

There are two ways to manage text color and attribute termination:
 
 - hard reset (SGR 0 | `\e[m`)
 - soft reset (SGR 22, 23, 24 etc.)

The main difference beetween them is that **hard** reset disables all formatting after itself, while **soft** reset disables only actually necessary attributes (i.e. used as opening sequence in _Format_ instance's context) and keeps the other.

That's what _Format_ class and `autof` method are designed for: to simplify creation of soft-resetting text spans, so that developer doesn't have to restore all previously applied formats after every closing sequence.

Example: we are given a text span which is initially **bold** and <u>underlined</u>. We want to recolor a few words inside of this span. By default this will result in losing all the formatting to the right of updated text span (because `RESET`|`\e[m` clears all text attributes).

However, there is an option to specify what attributes should be disabled (instead of disabling _all_ of them):

  ```python
  from pytermor.preset import *
  
  fmt_warn = Format(
    HI_YELLOW + UNDERLINED,  # sequences can be summed up, remember?
    COLOR_OFF + UNDERLINED_OFF,  # "counteractive" sequences
    hard_reset_after=False
  )
  orig_text = fmt_bold(f'{BG_BLACK}this is the original string{RESET}')
  updated_text = orig_text.replace('original', fmt_warn('updated'), 1)
  print(orig_text, '\n', updated_text)
  ```
  <img src="./doc/ex5.png"/>

As you can see, the update went well &mdash; we kept all the previously applied formatting. Of course, this method cannot be 100% applicable &mdash; for example, imagine that original text was colored blue. After the update "string" word won't be blue anymore, as we used `COLOR_OFF` escape sequence to neutralize our own red color. But it still can be helpful for a majority of cases (especially when text is generated and formatted by the same program and in one go).

## API [module]

### autof

Signature: `autof(*params str|int|SequenceSGR) -> Format`

Create new _Format_ with specified control sequence(s) as a opening/starter sequence and **automatically compose** closing sequence that will terminate attributes defined in opening sequence while keeping the others (soft reset). 

Resulting sequence params order is the same as argument order.

Each sequence param can be specified as:
- string key (see [API: Preset](#api-preset))
- integer param value
- existing _SequenceSGR_ instance (params will be extracted)

### build

Signature: `build(*params str|int|SequenceSGR) -> SequenceSGR`

Create new _SequenceSGR_ with specified params. Resulting sequence params order is the same as argument order. Parameter specification is the same as for `autof`.

### build_c256

Signature:`build_c256(color: int, bg: bool = False) -> SequenceSGR`

Create new _SequenceSGR_ that sets text color or background color, depending on _bg_ value, in 256-color mode. Valid values for _color_ argument: [0; 255], see more at [↗ xterm-256 colors](https://www.ditig.com/256-colors-cheat-sheet) page.
<br>

## API: SequenceSGR

Class describing SGR-mode ANSI escape sequence with varying amount of parameters.

You can use any of predefined sequences from `pytermor.preset` or create your own via standard constructor. Argument values as well as preset constants are described in [API: Preset](#api-preset) section.

### Applying the sequence

To get the resulting sequence chars simply cast instance to _str_:

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

### Combining SGRs

One instance of _SequenceSGR_ can be added to another. This will result in a new _SequenceSGR_ with combined params.
    
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
    from pytermor.string_filter import apply_filters, ReplaceNonAsciiBytes
    
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


- **name** &mdash; variable name defined in `pytermor.preset`;
- **keys** &mdash; strings that will be recognised by `build()` method;
- **params** &mdash; list of SGR params for specified seqeunce;
- **modifier groups** &mdash; list of modifier group the sequence is belong to; used for soft reset sequence autocomposing;
- **comment** &mdash; effect of applying the sequence and additional notes.

As a rule of a thumb, primary **key** equals to **name** in lower case. 

<table>
  <tr>
    <th> name </th>
    <th> keys </th>
    <th> params </th>
    <th> modifier groups </th>
    <th> comment </th>
  </tr>
  <tr>
    <td><code>RESET</code></td>
    <td><code>reset</code></td>
    <td align=center>0</td>
    <td>[breaker], super</td>
    <td>Reset all attributes and colors</td>
  </tr>
  <tr><td colspan="5">

  </td></tr>
  <tr><th colspan="5">group: attribute</th></tr>
  <tr>
    <td><code>BOLD</code></td>
    <td><code>bold</code>, <code>b</code></td>
    <td align=center>1</td>
    <td>bold</td>
    <td></td>
  </tr>
  <tr>
    <td><code>DIM</code></td>
    <td><code>dim</code></td>
    <td align=center>2</td>
    <td>dim</td>
    <td></td>
  </tr>
  <tr>
    <td><code>ITALIC</code></td>
    <td><code>italic</code>, <code>i</code></td>
    <td align=center>3</td>
    <td>italic</td>
    <td></td>
  </tr>
  <tr>
    <td><code>UNDERLINED</code></td>
    <td><code>underlined</code>, <code>u</code></td>
    <td align=center>4</td>
    <td>underlined</td>
    <td></td>
  </tr>
  <tr>
    <td><code>BLINK_SLOW</code></td>
    <td><code>blink_slow</code></td>
    <td align=center>5</td>
    <td>blink</td>
    <td></td>
  </tr>
  <tr>
    <td><code>BLINK_FAST</code></td>
    <td><code>blink_fast</code></td>
    <td align=center>6</td>
    <td>blink</td>
    <td></td>
  </tr>
  <tr>
    <td><code>INVERSED</code></td>
    <td><code>inversed</code>, <code>inv</code></td>
    <td align=center>7</td>
    <td>inversed</td>
    <td></td>
  </tr>
  <tr>
    <td><code>HIDDEN</code></td>
    <td><code>hidden</code></td>
    <td align=center>8</td>
    <td>inversed</td>
    <td></td>
  </tr>
  <tr>
    <td><code>CROSSLINED</code></td>
    <td><code>crosslined</code></td>
    <td align=center>9</td>
    <td>crosslined</td>
    <td></td>
  </tr>
  <tr>
    <td><code>DOUBLE_UNDERLINED</code></td>
    <td><code>double_underlined</code></td>
    <td align=center>21</td>
    <td>underlined</td>
    <td></td>
  </tr>
  <tr>
    <td><code>OVERLINED</code></td>
    <td><code>overlined</code></td>
    <td align=center>53</td>
    <td>overlined</td>
    <td></td>
  </tr>
  <tr>
    <td><code>BOLD_DIM_OFF</code></td>
    <td><code>bold_dim_off</code></td>
    <td align=center>22</td>
    <td>[breaker], bold, dim</td>
    <td><i>Special aspects... It's impossible to disable them separately.</i></td>
  </tr>
  <tr>
    <td><code>ITALIC_OFF</code></td>
    <td><code>italic_off</code></td>
    <td align=center>23</td>
    <td>[breaker], italic</td>
    <td></td>
  </tr>
  <tr>
    <td><code>UNDERLINED_OFF</code></td>
    <td><code>underlined_off</code></td>
    <td align=center>24</td>
    <td>[breaker], underlined</td>
    <td></td>
  </tr>
  <tr>
    <td><code>BLINK_OFF</code></td>
    <td><code>blink_off</code></td>
    <td align=center>25</td>
    <td>[breaker], blink</td>
    <td></td>
  </tr>
  <tr>
    <td><code>INVERSED_OFF</code></td>
    <td><code>inversed_off</code></td>
    <td align=center>27</td>
    <td>[breaker], inversed</td>
    <td></td>
  </tr>
  <tr>
    <td><code>HIDDEN_OFF</code></td>
    <td><code>hidden_off</code></td>
    <td align=center>28</td>
    <td>[breaker], hidden</td>
    <td></td>
  </tr>
  <tr>
    <td><code>CROSSLINED_OFF</code></td>
    <td><code>crosslined_off</code></td>
    <td align=center>29</td>
    <td>[breaker], crosslined</td>
    <td></td>
  </tr>
  <tr>
    <td><code>OVERLINED_OFF</code></td>
    <td><code>overlined_off</code></td>
    <td align=center>55</td>
    <td>[breaker], overlined</td>
    <td></td>
  </tr>
  <tr><td colspan="5">

  </td></tr>
  <tr><th colspan="5">group: color</th></tr>
  <tr>
    <td><code>BLACK</code></td>
    <td><code>black</code></td>
    <td align=center>30</td>
    <td>color</td>
    <td></td>
  </tr>
  <tr>
    <td><code>RED</code></td>
    <td><code>red</code></td>
    <td align=center>31</td>
    <td>color</td>
    <td></td>
  </tr>
  <tr>
    <td><code>GREEN</code></td>
    <td><code>green</code></td>
    <td align=center>32</td>
    <td>color</td>
    <td></td>
  </tr>
  <tr>
    <td><code>YELLOW</code></td>
    <td><code>yellow</code></td>
    <td align=center>33</td>
    <td>color</td>
    <td></td>
  </tr>
  <tr>
    <td><code>BLUE</code></td>
    <td><code>blue</code></td>
    <td align=center>34</td>
    <td>color</td>
    <td></td>
  </tr>
  <tr>
    <td><code>MAGENTA</code></td>
    <td><code>magenta</code></td>
    <td align=center>35</td>
    <td>color</td>
    <td></td>
  </tr>
  <tr>
    <td><code>CYAN</code></td>
    <td><code>cyan</code></td>
    <td align=center>36</td>
    <td>color</td>
    <td></td>
  </tr>
  <tr>
    <td><code>WHITE</code></td>
    <td><code>white</code></td>
    <td align=center>37</td>
    <td>color</td>
    <td></td>
  </tr>
  <tr>
    <td><code>MODE24_START</code></td>
    <td><code>mode24_start</code>, <code>text_rgb</code></td>
    <td align=center>38;2;<code>r</code>;<code>g</code>;<code>b</code></td>
    <td>color</td>
    <td>Set text color to <code>rrggbb</code> translated. Valid values (for all): [0-255]</td>
  </tr>
  <tr>
    <td><code>MODE8_START</code></td>
    <td><code>mode8_start</code>, <code>text_256</code></td>
    <td align=center>38;5;<code>color</code></td>
    <td>color</td>
    <td>Set text color to <code>code</code>. Valid values: [0-255]</td>
  </tr>
  <tr>
    <td><code>COLOR_OFF</code></td>
    <td><code>color_off</code></td>
    <td align=center>39</td>
    <td>[breaker], color</td>
    <td>Reset text color</td>
  </tr>
  <tr><td colspan="5">

  </td></tr>
  <tr><th colspan="5">group: background color</th></tr>
  <tr>
    <td><code>BG_BLACK</code></td>
    <td><code>bg_black</code></td>
    <td align=center>40</td>
    <td>bg_color</td>
    <td></td>
  </tr>
  <tr>
    <td><code>BG_RED</code></td>
    <td><code>bg_red</code></td>
    <td align=center>41</td>
    <td>bg_color</td>
    <td></td>
  </tr>
  <tr>
    <td><code>BG_GREEN</code></td>
    <td><code>bg_green</code></td>
    <td align=center>42</td>
    <td>bg_color</td>
    <td></td>
  </tr>
  <tr>
    <td><code>BG_YELLOW</code></td>
    <td><code>bg_yellow</code></td>
    <td align=center>43</td>
    <td>bg_color</td>
    <td></td>
  </tr>
  <tr>
    <td><code>BG_BLUE</code></td>
    <td><code>bg_blue</code></td>
    <td align=center>44</td>
    <td>bg_color</td>
    <td></td>
  </tr>
  <tr>
    <td><code>BG_MAGENTA</code></td>
    <td><code>bg_magenta</code></td>
    <td align=center>45</td>
    <td>bg_color</td>
    <td></td>
  </tr>
  <tr>
    <td><code>BG_CYAN</code></td>
    <td><code>bg_cyan</code></td>
    <td align=center>46</td>
    <td>bg_color</td>
    <td></td>
  </tr>
  <tr>
    <td><code>BG_WHITE</code></td>
    <td><code>bg_white</code></td>
    <td align=center>47</td>
    <td>bg_color</td>
    <td></td>
  </tr>
  <tr>
    <td><code>BG_MODE24_START</code></td>
    <td><code>bg_mode24_start</code>, <code>bg_rgb</code></td>
    <td align=center>48;2;<code>r</code>;<code>g</code>;<code>b</code></td>
    <td>bg_color</td>
    <td>Set bg color to <code>rrggbb</code> (translated). Valid values (for all): [0-255]</td>
  </tr>
  <tr>
    <td><code>BG_MODE8_START</code></td>
    <td><code>bg_mode8_start</code>, <code>bg_256</code></td>
    <td align=center>48;5;<code>color</code></td>
    <td>bg_color</td>
    <td>Set bg color to <code>code</code>. Valid values: [0-255]</td>
  </tr>
  <tr>
    <td><code>BG_COLOR_OFF</code></td>
    <td><code>bg_color_off</code></td>
    <td align=center>49</td>
    <td>[breaker], bg_color</td>
    <td>Reset bg color</td>
  </tr>
  <tr><td colspan="5">

  </td></tr>
  <tr><th colspan="5">group: high intensity color</th></tr>
  <tr>
    <td><code>GRAY</code></td>
    <td><code>gray</code></td>
    <td align=center>90</td>
    <td>color</td>
    <td></td>
  </tr>
  <tr>
    <td><code>HI_RED</code></td>
    <td><code>hi_red</code></td>
    <td align=center>91</td>
    <td>color</td>
    <td></td>
  </tr>
  <tr>
    <td><code>HI_GREEN</code></td>
    <td><code>hi_green</code></td>
    <td align=center>92</td>
    <td>color</td>
    <td></td>
  </tr>
  <tr>
    <td><code>HI_YELLOW</code></td>
    <td><code>hi_yellow</code></td>
    <td align=center>93</td>
    <td>color</td>
    <td></td>
  </tr>
  <tr>
    <td><code>HI_BLUE</code></td>
    <td><code>hi_blue</code></td>
    <td align=center>94</td>
    <td>color</td>
    <td></td>
  </tr>
  <tr>
    <td><code>HI_MAGENTA</code></td>
    <td><code>hi_magenta</code></td>
    <td align=center>95</td>
    <td>color</td>
    <td></td>
  </tr>
  <tr>
    <td><code>HI_CYAN</code></td>
    <td><code>hi_cyan</code></td>
    <td align=center>96</td>
    <td>color</td>
    <td></td>
  </tr>
  <tr>
    <td><code>HI_WHITE</code></td>
    <td><code>hi_white</code></td>
    <td align=center>97</td>
    <td>color</td>
    <td></td>
  </tr>
  <tr><td colspan="5">

  </td></tr>
  <tr><th colspan="5">group: high intensity background color</th></tr>
  <tr>
    <td><code>BG_GRAY</code></td>
    <td><code>bg_gray</code></td>
    <td align=center>100</td>
    <td>bg_color</td>
    <td></td>
  </tr>
  <tr>
    <td><code>BG_HI_RED</code></td>
    <td><code>bg_hi_red</code></td>
    <td align=center>101</td>
    <td>bg_color</td>
    <td></td>
  </tr>
  <tr>
    <td><code>BG_HI_GREEN</code></td>
    <td><code>bg_hi_green</code></td>
    <td align=center>102</td>
    <td>bg_color</td>
    <td></td>
  </tr>
  <tr>
    <td><code>BG_HI_YELLOW</code></td>
    <td><code>bg_hi_yellow</code></td>
    <td align=center>103</td>
    <td>bg_color</td>
    <td></td>
  </tr>
  <tr>
    <td><code>BG_HI_BLUE</code></td>
    <td><code>bg_hi_blue</code></td>
    <td align=center>104</td>
    <td>bg_color</td>
    <td></td>
  </tr>
  <tr>
    <td><code>BG_HI_MAGENTA</code></td>
    <td><code>bg_hi_magenta</code></td>
    <td align=center>105</td>
    <td>bg_color</td>
    <td></td>
  </tr>
  <tr>
    <td><code>BG_HI_CYAN</code></td>
    <td><code>bg_hi_cyan</code></td>
    <td align=center>106</td>
    <td>bg_color</td>
    <td></td>
  </tr>
  <tr>
    <td><code>BG_HI_WHITE</code></td>
    <td><code>bg_hi_white</code></td>
    <td align=center>107</td>
    <td>bg_color</td>
    <td></td>
  </tr>
</table>

</details>
<br>


<details>
<summary><b>SGR formats</b> <i>(click)</i></summary>

</details>

## References

- https://en.wikipedia.org/wiki/ANSI_escape_code
