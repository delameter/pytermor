# pytermor

_(yet another)_ Python library designed for formatting terminal output using ANSI escape codes. Implements automatic "soft" format termination. Provides a registry of ready-to-use SGR sequences and formats (=combined sequences).

## Motivation

Key feature of this library is providing necessary abstractions for building complex text sections with lots of formatting, while keeping the application code clear and readable.

## Installation

    pip install pytermor



## Use cases

_Format_ is a combination of two control sequences; it wraps specified string with pre-defined leading and trailing SGR definitions.

```python3
from pytermor import fmt

print(fmt.blue('Use'), fmt.cyan('cases'))
```

<details>
<summary><b>Examples</b> <i>(click)</i></summary>

## * ![image](https://user-images.githubusercontent.com/50381946/161387692-4374edcb-c1fe-438f-96f1-dae3c5ad4088.png)

Preset formats can safely overlap with each other (as long as they require different **breaker** sequences to reset).

```python3
from pytermor import fmt

print(fmt.blue(fmt.underlined('Nested') + fmt.bold(' formats')))
```

## * ![image](https://user-images.githubusercontent.com/50381946/161387711-23746520-419b-4917-9401-257854ff2d8a.png)

Compose text formats with automatic content-aware format termination.

```python3
from pytermor import autof

fmt1 = autof('hi_cyan', 'bold')
fmt2 = autof('bg_black', 'inversed', 'underlined', 'italic')

msg = fmt1(f'Content{fmt2("-aware format")} nesting')
print(msg)
```

## * ![image](https://user-images.githubusercontent.com/50381946/161387734-677d5b10-15c1-4926-933f-b1144b0ce5cb.png)

Create your own _SGR_ _sequences_ with `build()` method, which accepts color/attribute keys, integer codes and even existing _SGRs_, in any amount and in any order. Key resolving is case-insensitive.

```python3
from pytermor import seq, build

seq1 = build('red', 1)  # keys or integer codes
seq2 = build(seq1, seq.ITALIC)  # existing SGRs as part of a new one
seq3 = build('underlined', 'YELLOW')  # case-insensitive

msg = f'{seq1}Flexible{seq.RESET} ' + \
      f'{seq2}sequence{seq.RESET} ' + \
      str(seq3) + 'builder' + str(seq.RESET)
print(msg)
```

## * ![image](https://user-images.githubusercontent.com/50381946/161387746-0a94e3d2-8295-478c-828c-333e99e5d50a.png)

Use `build_c256()` to set foreground/background color to any of [↗ xterm-256 colors](https://www.ditig.com/256-colors-cheat-sheet).

```python3
from pytermor import build_c256, seq, autof

txt = '256 colors support'
start_color = 41
msg = ''
for idx, c in enumerate(range(start_color, start_color+(36*6), 36)):
    msg += f'{build_c256(c)}{txt[idx*3:(idx+1)*3]}{seq.COLOR_OFF}'

print(autof(seq.BOLD).wrap(msg))
```

## * ![image](https://user-images.githubusercontent.com/50381946/161411577-743b9a81-eac3-47c0-9b59-82b289cc0f45.png)

It's also possible to use 16M-color mode (or True color) &mdash; with `build_rgb()` wrapper method.

```python3
from pytermor import build_rgb, seq, fmt

txt = 'True color support'
msg = ''
for idx, c in enumerate(range(0, 256, 256//18)):
    r = max(0, 255-c)
    g = max(0, min(255, 127-(c*2)))
    b = c
    msg += f'{build_rgb(r, g, b)}{txt[idx:(idx+1)]}{seq.COLOR_OFF}'

print(fmt.bold(msg))
```

</details>


## Format soft reset

There are two ways to manage color and attribute termination:

- hard reset (SGR 0 | `\e[0m`)
- soft reset (SGR 22, 23, 24 etc.)

The main difference between them is that **hard** reset disables all formatting after itself, while **soft** reset disables only actually necessary attributes (i.e. used as opening sequence in _Format_ instance's context) and keeps the other.

That's what _Format_ class and `autof` method are designed for: to simplify creation of soft-resetting text spans, so that developer doesn't have to restore all previously applied formats after every closing sequence.

Example: we are given a text span which is initially **bold** and <u>underlined</u>. We want to recolor a few words inside of this span. By default this will result in losing all the formatting to the right of updated text span (because `RESET`|`\e[0m` clears all text attributes).

However, there is an option to specify what attributes should be disabled or let the library do that for you:

```python3
from pytermor import seq, fmt, autof, Format

# automatically:
fmt_warn = autof(seq.HI_YELLOW + seq.UNDERLINED)
# or manually:
fmt_warn = Format(
    seq.HI_YELLOW + seq.UNDERLINED,  # sequences can be summed up, remember?
    seq.COLOR_OFF + seq.UNDERLINED_OFF,  # "counteractive" sequences
    hard_reset_after=False
)

orig_text = fmt.bold(f'this is {seq.BG_GRAY}the original{seq.RESET} string')
updated_text = orig_text.replace('original', fmt_warn('updated'), 1)
print(orig_text, '\n', updated_text)
```
> ![image](https://user-images.githubusercontent.com/50381946/163714299-1f7d3d52-0b9a-4d3e-91bf-26e8cce9b1f1.png)

As you can see, the update went well &mdash; we kept all the previously applied formatting. Of course, this method cannot be 100% applicable &mdash; for example, imagine that original text was colored blue. After the update "string" word won't be blue anymore, as we used `COLOR_OFF` escape sequence to neutralize our own yellow color. But it still can be helpful for a majority of cases (especially when text is generated and formatted by the same program and in one go).


## API: module

### autof

Signature: `autof(*params str|int|SequenceSGR) -> Format`

Create new _Format_ with specified control sequence(s) as a opening/starter sequence and **automatically compose** closing sequence that will terminate attributes defined in opening sequence while keeping the others (soft reset).

Resulting sequence params' order is the same as argument's order.

Each sequence param can be specified as:
- string key (see [API: Registries](#api-registries))
- integer param value
- existing _SequenceSGR_ instance (params will be extracted)

### build

Signature: `build(*params str|int|SequenceSGR) -> SequenceSGR`

Create new _SequenceSGR_ with specified params. Resulting sequence params order is the same as argument order. Parameter specification is the same as for `autof`.

_SequenceSGR_ with zero params was specifically implemented to translate into empty string and not into `\e[m`, which wolud make sense, but also would be very entangling, as it's equivavlent of `\e[0m` &mdash; **hard reset** sequence.

### build_c256

Signature:`build_c256(color: int, bg: bool = False) -> SequenceSGR`

Create new _SequenceSGR_ that sets foreground color or background color, depending on `bg` value, in 256-color mode. Valid values for `color` are [0; 255], see more at [↗ xterm-256 colors](https://www.ditig.com/256-colors-cheat-sheet) page.

### build_rgb

Signature:`build_rgb(r: int, g: int, b: int, bg: bool = False) -> SequenceSGR`

Create new _SequenceSGR_ that sets foreground color or background color, depending on `bg` value, in 16M-color mode. Valid values for `r`, `g` and `b` are [0; 255]; this range is linearly translated into [0x00; 0xFF] for each channel; the result value is composed as #RRGGBB.


## API: SGR sequences

Class representing SGR-mode ANSI escape sequence with varying amount of parameters.

<details>
<summary><b>Details</b> <i>(click)</i></summary>

### Creating the sequence

You can use any of predefined sequences from `pytermor.seq` or create your own via standard constructor (see below). Valid argument values as well as preset constants are described in [API: Registries](#api-registries) section.

### Applying the sequence

To get the resulting sequence chars use `print()` method or cast instance to _str_:

```python3
from pytermor import SequenceSGR

seq = SequenceSGR(4, 7)
msg = f'({seq})'
print(msg + f'{SequenceSGR(0).print()}', str(msg.encode()), msg.encode().hex(':'))
```
> ![image](https://user-images.githubusercontent.com/50381946/161387861-5203fff8-86c8-4c52-8518-63a5525c09f7.png)

1st part is "applied" escape sequence; 2nd part shows up a sequence in raw mode, as if it was ignored by the terminal; 3rd part is hexademical sequence byte values.

<details>
<summary><b>SGR sequence structure</b> <i>(click)</i></summary>

1. `\x1b`|`1b` is ESC **control character**, which opens a control sequence.

2. `[` is sequence **introducer**, it determines the type of control sequence (in this case it's _CSI_, or "Control Sequence Introducer").

3. `4` and `7` are **parameters** of the escape sequence; they mean "underlined" and "inversed" attributes respectively. Those parameters must be separated by `;`.

4. `m` is sequence **terminator**; it also determines the sub-type of sequence, in our case _SGR_, or "Select Graphic Rendition". Sequences of this kind are most commonly encountered.

</details>

### Combining SGRs

One instance of _SequenceSGR_ can be added to another. This will result in a new _SequenceSGR_ with combined params.

```python3
from pytermor import seq, SequenceSGR

combined = SequenceSGR(1, 31) + SequenceSGR(4)
print(f'{combined}combined{seq.RESET}', str(combined).encode())
```
> ![image](https://user-images.githubusercontent.com/50381946/161387867-808831e5-784b-49ec-9c24-490734ef4eab.png)

</details>

## API: Formats

_Format_ is a wrapper class that contains starting (i.e. opening) _SequenceSGR_ and (optionally) closing _SequenceSGR_.

<details>
<summary><b>Details</b> <i>(click)</i></summary>

### Creating the format

You can define your own reusable <i>Format</i>s (see below) or import predefined ones from `pytermor.fmt` (see [API: Registries](#api-registries) section).

### Applying the format

Use `wrap()` method of _Format_ instance or call the instance itself to enclose specified string in starting/terminating SGR sequences:

```python3
from pytermor import seq, fmt, Format

fmt_error = Format(seq.BG_HI_RED + seq.UNDERLINED, seq.BG_COLOR_OFF + seq.UNDERLINED_OFF)
msg = fmt.italic.wrap('italic might ' + fmt_error('not') + ' work')
print(msg)
```
> ![image](https://user-images.githubusercontent.com/50381946/161387874-5c25a493-253b-4f9e-8dbf-8328add2e5d5.png)

</details>


## API: String filters

_StringFilter_ is common string modifier interface with dynamic configuration support.

<details>
<summary><b>Details</b> <i>(click)</i></summary>

### Implementations

- ReplaceSGR
- ReplaceCSI
- ReplaceNonAsciiBytes

### Standalone usage

Can be applied using `.apply()` method or with direct call.

```python3
from pytermor import fmt, ReplaceSGR

formatted = fmt.red('this text is red')
replaced = ReplaceSGR('[LIE]').apply(formatted)
# replaced = ReplaceSequenceSGRs('[LIE]')(formatted)

print(formatted, '\n', replaced)
```
> ![image](https://user-images.githubusercontent.com/50381946/161387885-0fc0fcb5-09aa-4258-aa25-312220e7f994.png)


### Usage with helper

Helper function `apply_filters` accepts both `StringFilter` implementation instances and types, but latter is not configurable and will be invoked using default settings.

```python3
from pytermor import apply_filters, ReplaceNonAsciiBytes

ascii_and_binary = b'\xc0\xff\xeeQWE\xffRT\xeb\x00\xc0\xcd\xed'
result = apply_filters(ascii_and_binary, ReplaceNonAsciiBytes)
print(ascii_and_binary, '\n', result)
```
> ![image](https://user-images.githubusercontent.com/50381946/161387889-a1920f13-f5fc-4d10-b535-93f1a1b1aa5c.png)

</details>


## API: Registries

<details>
<summary><b>Sequences</b> <i>(click)</i></summary>


- **code** &mdash; SGR integer code(s) for specified sequence (order is important)
- **name** &mdash; variable name; usage: `from pytermor.seq import RESET`
- **key** &mdash; string that will be recognised by `build()`|`autof()` etc.
- **description** &mdash; effect of applying the sequence / additional notes

As a rule of a thumb, **key** equals to **name** in lower case.

<table>
  <tr>
    <th>code</th>
    <th>name</th>
    <th>key</th>
    <th>description</th>
  </tr>
  <tr>
    <td align=center>0</td>
    <td><code>RESET</code></td>
    <td><code>reset</code></td>
    <td>Reset all attributes and colors</td>
  </tr>

  <tr><td colspan="4"><br><b>attributes</b></td></tr>
  <tr>
    <td align=center>1</td>
    <td><code>BOLD</code></td>
    <td><code>bold</code></td>
    <td>Bold or increased intensity</td>
  </tr>
  <tr>
    <td align=center>2</td>
    <td><code>DIM</code></td>
    <td><code>dim</code></td>
    <td>Faint, decreased intensity</td>
  </tr>
  <tr>
    <td align=center>3</td>
    <td><code>ITALIC</code></td>
    <td><code>italic</code></td>
    <td>Italic; not widely supported</td>
  </tr>
  <tr>
    <td align=center>4</td>
    <td><code>UNDERLINED</code></td>
    <td><code>underlined</code></td>
    <td>Underline</td>
  </tr>
  <tr>
    <td align=center>5</td>
    <td><code>BLINK_SLOW</code></td>
    <td><code>blink_slow</code></td>
    <td>Sets blinking to &lt; 150 cpm</td>
  </tr>
  <tr>
    <td align=center>6</td>
    <td><code>BLINK_FAST</code></td>
    <td><code>blink_fast</code></td>
    <td>150+ cpm; not widely supported</td>
  </tr>
  <tr>
    <td align=center>7</td>
    <td><code>INVERSED</code></td>
    <td><code>inversed</code></td>
    <td>Swap foreground and background colors</td>
  </tr>
  <tr>
    <td align=center>8</td>
    <td><code>HIDDEN</code></td>
    <td><code>hidden</code></td>
    <td>Conceal characters; not widely supported</td>
  </tr>
  <tr>
    <td align=center>9</td>
    <td><code>CROSSLINED</code></td>
    <td><code>crosslined</code></td>
    <td>Strikethrough</td>
  </tr>
  <tr>
    <td align=center>21</td>
    <td><code>DOUBLE_UNDERLINED</code></td>
    <td><code>double_underlined</code></td>
    <td>Double-underline; on several terminals disables <code>BOLD</code> instead</td>
  </tr>
  <tr>
    <td align=center>53</td>
    <td><code>OVERLINED</code></td>
    <td><code>overlined</code></td>
    <td>Not widely supported</td>
  </tr>

  <tr><td colspan="4"><br><b>breakers</b></td></tr>
  <tr>
    <td align=center>22</td>
    <td><code>BOLD_DIM_OFF</code></td>
    <td><code>bold_dim_off</code></td>
    <td>Disable <code>BOLD</code> and <code>DIM</code> attributes. <i>Special aspects... It's impossible to reliably disable them on a separate basis.</i></td>
  </tr>
  <tr>
    <td align=center>23</td>
    <td><code>ITALIC_OFF</code></td>
    <td><code>italic_off</code></td>
    <td>Disable italic</td>
  </tr>
  <tr>
    <td align=center>24</td>
    <td><code>UNDERLINED_OFF</code></td>
    <td><code>underlined_off</code></td>
    <td>Disable underlining</td>
  </tr>
  <tr>
    <td align=center>25</td>
    <td><code>BLINK_OFF</code></td>
    <td><code>blink_off</code></td>
    <td>Disable blinking</td>
  </tr>
  <tr>
    <td align=center>27</td>
    <td><code>INVERSED_OFF</code></td>
    <td><code>inversed_off</code></td>
    <td>Disable inversing</td>
  </tr>
  <tr>
    <td align=center>28</td>
    <td><code>HIDDEN_OFF</code></td>
    <td><code>hidden_off</code></td>
    <td>Disable conecaling</td>
  </tr>
  <tr>
    <td align=center>29</td>
    <td><code>CROSSLINED_OFF</code></td>
    <td><code>crosslined_off</code></td>
    <td>Disable strikethrough</td>
  </tr>
  <tr>
    <td align=center>39</td>
    <td><code>COLOR_OFF</code></td>
    <td><code>color_off</code></td>
    <td>Reset foreground color</td>
  </tr>
  <tr>
    <td align=center>49</td>
    <td><code>BG_COLOR_OFF</code></td>
    <td><code>bg_color_off</code></td>
    <td>Reset bg color</td>
  </tr>
  <tr>
    <td align=center>55</td>
    <td><code>OVERLINED_OFF</code></td>
    <td><code>overlined_off</code></td>
    <td>Disable overlining</td>
  </tr>

  <tr><td colspan="4"><br><b>[foreground] colors</b></td></tr>
  <tr>
    <td align=center>30</td>
    <td><code>BLACK</code></td>
    <td><code>black</code></td>
    <td>Set foreground color to black</td>
  </tr>
  <tr>
    <td align=center>31</td>
    <td><code>RED</code></td>
    <td><code>red</code></td>
    <td>Set foreground color to red</td>
  </tr>
  <tr>
    <td align=center>32</td>
    <td><code>GREEN</code></td>
    <td><code>green</code></td>
    <td>Set foreground color to green</td>
  </tr>
  <tr>
    <td align=center>33</td>
    <td><code>YELLOW</code></td>
    <td><code>yellow</code></td>
    <td>Set foreground color to yellow</td>
  </tr>
  <tr>
    <td align=center>34</td>
    <td><code>BLUE</code></td>
    <td><code>blue</code></td>
    <td>Set foreground color to blue</td>
  </tr>
  <tr>
    <td align=center>35</td>
    <td><code>MAGENTA</code></td>
    <td><code>magenta</code></td>
    <td>Set foreground color to magneta</td>
  </tr>
  <tr>
    <td align=center>36</td>
    <td><code>CYAN</code></td>
    <td><code>cyan</code></td>
    <td>Set foreground color to cyan</td>
  </tr>
  <tr>
    <td align=center>37</td>
    <td><code>WHITE</code></td>
    <td><code>white</code></td>
    <td>Set foreground color to white</td>
  </tr>
  <tr>
    <td align=center><s>38;5</s></td>
    <td colspan="2" align="center">
        Use <code>color_c256()</code> instead
    </td>
    <td>Set foreground color [256 mode]</td>
  </tr>
  <tr>
    <td align=center><s>38;2</s></td>
    <td colspan="2" align="center">
        Use <code>color_rgb()</code> instead
    </td>
    <td>Set foreground color [16M mode]</td>
  </tr>

  <tr><td colspan="4"><br><b>background colors</b></td></tr>
  <tr>
    <td align=center>40</td>
    <td><code>BG_BLACK</code></td>
    <td><code>bg_black</code></td>
    <td>Set background color to black</td>
  </tr>
  <tr>
    <td align=center>41</td>
    <td><code>BG_RED</code></td>
    <td><code>bg_red</code></td>
    <td>Set background color to red</td>
  </tr>
  <tr>
    <td align=center>42</td>
    <td><code>BG_GREEN</code></td>
    <td><code>bg_green</code></td>
    <td>Set background color to green</td>
  </tr>
  <tr>
    <td align=center>43</td>
    <td><code>BG_YELLOW</code></td>
    <td><code>bg_yellow</code></td>
    <td>Set background color to yellow</td>
  </tr>
  <tr>
    <td align=center>44</td>
    <td><code>BG_BLUE</code></td>
    <td><code>bg_blue</code></td>
    <td>Set background color to blue</td>
  </tr>
  <tr>
    <td align=center>45</td>
    <td><code>BG_MAGENTA</code></td>
    <td><code>bg_magenta</code></td>
    <td>Set background color to magenta</td>
  </tr>
  <tr>
    <td align=center>46</td>
    <td><code>BG_CYAN</code></td>
    <td><code>bg_cyan</code></td>
    <td>Set background color to cyan</td>
  </tr>
  <tr>
    <td align=center>47</td>
    <td><code>BG_WHITE</code></td>
    <td><code>bg_white</code></td>
    <td>Set background color to white</td>
  </tr>
  <tr>
    <td align=center><s>48;5</s></td>
    <td colspan="2" align="center">
        Use <code>color_c256()</code> instead
    </td>
    <td>Set background color [256 mode]</td>
  </tr>
  <tr>
    <td align=center><s>48;2</s></td>
    <td colspan="2" align="center">
        Use <code>color_rgb()</code> instead
    </td>
    <td>Set background color [16M mode]</td>
  </tr>

  <tr><td colspan="4"><br><b>high-intensity [foreground] colors</b></td></tr>
  <tr>
    <td align=center>90</td>
    <td><code>GRAY</code></td>
    <td><code>gray</code></td>
    <td>Set foreground color to bright black/gray</td>
  </tr>
  <tr>
    <td align=center>91</td>
    <td><code>HI_RED</code></td>
    <td><code>hi_red</code></td>
    <td>Set foreground color to bright red</td>
  </tr>
  <tr>
    <td align=center>92</td>
    <td><code>HI_GREEN</code></td>
    <td><code>hi_green</code></td>
    <td>Set foreground color to bright green</td>
  </tr>
  <tr>
    <td align=center>93</td>
    <td><code>HI_YELLOW</code></td>
    <td><code>hi_yellow</code></td>
    <td>Set foreground color to bright yellow</td>
  </tr>
  <tr>
    <td align=center>94</td>
    <td><code>HI_BLUE</code></td>
    <td><code>hi_blue</code></td>
    <td>Set foreground color to bright blue</td>
  </tr>
  <tr>
    <td align=center>95</td>
    <td><code>HI_MAGENTA</code></td>
    <td><code>hi_magenta</code></td>
    <td>Set foreground color to bright magenta</td>
  </tr>
  <tr>
    <td align=center>96</td>
    <td><code>HI_CYAN</code></td>
    <td><code>hi_cyan</code></td>
    <td>Set foreground color to bright cyan</td>
  </tr>
  <tr>
    <td align=center>97</td>
    <td><code>HI_WHITE</code></td>
    <td><code>hi_white</code></td>
    <td>Set foreground color to bright white</td>
  </tr>

  <tr><td colspan="4"><br><b>high-intensity background colors</b></td></tr>
  <tr>
    <td align=center>100</td>
    <td><code>BG_GRAY</code></td>
    <td><code>bg_gray</code></td>
    <td>Set background color to bright black/gray</td>
  </tr>
  <tr>
    <td align=center>101</td>
    <td><code>BG_HI_RED</code></td>
    <td><code>bg_hi_red</code></td>
    <td>Set background color to bright red</td>
  </tr>
  <tr>
    <td align=center>102</td>
    <td><code>BG_HI_GREEN</code></td>
    <td><code>bg_hi_green</code></td>
    <td>Set background color to bright green</td>
  </tr>
  <tr>
    <td align=center>103</td>
    <td><code>BG_HI_YELLOW</code></td>
    <td><code>bg_hi_yellow</code></td>
    <td>Set background color to bright yellow</td>
  </tr>
  <tr>
    <td align=center>104</td>
    <td><code>BG_HI_BLUE</code></td>
    <td><code>bg_hi_blue</code></td>
    <td>Set background color to bright blue</td>
  </tr>
  <tr>
    <td align=center>105</td>
    <td><code>BG_HI_MAGENTA</code></td>
    <td><code>bg_hi_magenta</code></td>
    <td>Set background color to bright magenta</td>
  </tr>
  <tr>
    <td align=center>106</td>
    <td><code>BG_HI_CYAN</code></td>
    <td><code>bg_hi_cyan</code></td>
    <td>Set background color to bright cyan</td>
  </tr>
  <tr>
    <td align=center>107</td>
    <td><code>BG_HI_WHITE</code></td>
    <td><code>bg_hi_white</code></td>
    <td>Set background color to bright white</td>
  </tr>
</table>

</details>

<details>
<summary><b>Formats</b> <i>(click)</i></summary>

- **name** &mdash; variable name; usage: `from pytermor.fmt import bold`
- **opening seq**, **closing seq** &mdash; corresponding <i>SGR</i>s

As a rule of a thumb, **name** equals to **opening seq** in lower case.

<table>
  <tr>
    <th>name</th>
    <th>opening seq</th>
    <th>closing seq</th>
  </tr>
  <tr><td colspan="3"><br><b>attributes</b></td></tr>
  <tr>
    <td><code>bold</code></td>
    <td><code>BOLD</code></td>
    <td><code>BOLD_DIM_OFF</code></td>
  </tr>
  <tr>
    <td><code>dim</code></td>
    <td><code>DIM</code></td>
    <td><code>BOLD_DIM_OFF</code></td>
  </tr>
  <tr>
    <td><code>italic</code></td>
    <td><code>ITALIC</code></td>
    <td><code>ITALIC_OFF</code></td>
  </tr>
  <tr>
    <td><code>underlined</code></td>
    <td><code>UNDERLINED</code></td>
    <td><code>UNDERLINED_OFF</code></td>
  </tr>
  <tr>
    <td><code>inversed</code></td>
    <td><code>INVERSED</code></td>
    <td><code>INVERSED_OFF</code></td>
  </tr>
  <tr>
    <td><code>overlined</code></td>
    <td><code>OVERLINED</code></td>
    <td><code>OVERLINED_OFF</code></td>
  </tr>

  <tr><td colspan="3"><br><b>[foreground] colors</b></td></tr>
  <tr>
    <td><code>red</code></td>
    <td><code>RED</code></td>
    <td><code>COLOR_OFF</code></td>
  </tr>
  <tr>
    <td><code>green</code></td>
    <td><code>GREEN</code></td>
    <td><code>COLOR_OFF</code></td>
  </tr>
  <tr>
    <td><code>yellow</code></td>
    <td><code>YELLOW</code></td>
    <td><code>COLOR_OFF</code></td>
  </tr>
  <tr>
    <td><code>blue</code></td>
    <td><code>BLUE</code></td>
    <td><code>COLOR_OFF</code></td>
  </tr>
  <tr>
    <td><code>magenta</code></td>
    <td><code>MAGENTA</code></td>
    <td><code>COLOR_OFF</code></td>
  </tr>
  <tr>
    <td><code>cyan</code></td>
    <td><code>CYAN</code></td>
    <td><code>COLOR_OFF</code></td>
  </tr>
  <tr>
    <td><code>gray</code></td>
    <td><code>GRAY</code></td>
    <td><code>COLOR_OFF</code></td>
  </tr>

  <tr><td colspan="3"><br><b>background colors</b></td></tr>
  <tr>
    <td><code>bg_red</code></td>
    <td><code>BG_RED</code></td>
    <td><code>BG_COLOR_OFF</code></td>
  </tr>
  <tr>
    <td><code>bg_green</code></td>
    <td><code>BG_GREEN</code></td>
    <td><code>BG_COLOR_OFF</code></td>
  </tr>
  <tr>
    <td><code>bg_yellow</code></td>
    <td><code>BG_YELLOW</code></td>
    <td><code>BG_COLOR_OFF</code></td>
  </tr>
  <tr>
    <td><code>bg_blue</code></td>
    <td><code>BG_BLUE</code></td>
    <td><code>BG_COLOR_OFF</code></td>
  </tr>
  <tr>
    <td><code>bg_magenta</code></td>
    <td><code>BG_MAGENTA</code></td>
    <td><code>BG_COLOR_OFF</code></td>
  </tr>
  <tr>
    <td><code>bg_cyan</code></td>
    <td><code>BG_CYAN</code></td>
    <td><code>BG_COLOR_OFF</code></td>
  </tr>
  <tr>
    <td><code>bg_gray</code></td>
    <td><code>BG_GRAY</code></td>
    <td><code>BG_COLOR_OFF</code></td>
  </tr>
</table>

</details>

You can of course create your own sequences and formats, but with one limitation &mdash; autoformatting will not work with custom defined sequences; unless you add the corresponding rule to `pytermor.registry.sgr_parity_registry`.

## Changelog

### v1.7.1

- Print reset sequence as `\e[m` instead of `\e[0m`.

### v1.7.0

- `Format()` constructor can be called without arguments.
- Added SGR code lists.

### v1.6.2

- Excluded `tests` dir from distribution package.

### v1.6.1

- Ridded of _EmptyFormat_ and _AbstractFormat_ classes.
- Renamed `code` module to `sgr` because of conflicts in PyCharm debugger (`pydevd_console_integration.py`).

### v1.5.0

- Removed excessive _EmptySequenceSGR_ &mdash; default _SGR_ class without params was specifically implemented to print out as empty string instead of `\e[m`.

### v1.4.0

- `Format.wrap()` now accepts any type of argument, not only _str_.
- Rebuilt _Sequence_ inheritance tree.
- Added equality methods for _Sequence_ and _Format_ classes/subclasses.
- Added some tests for `fmt.*` and `seq.*` classes.

### v1.3.2

- Added `gray` and `bg_gray` format presets. 

### v1.3.1

- Interface revisioning.

### v1.2.1

- `opening_seq` and `closing_seq` properties for _Format_ class.

### v1.2.0

- _EmptySequenceSGR_ and _EmptyFormat_ classes.

### v1.1.0

- Autoformat feature.

### v1.0.0

- First public version.

## References

- https://en.wikipedia.org/wiki/ANSI_escape_code
- [ANSI Escape Sequences](https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797)
