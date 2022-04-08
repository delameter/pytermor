# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import os

_print = print
def print(*args):
    with open(_outpath, 'at') as f:
        _print('\n\n', end=' ', file=f)
        _print(*args, file=f)


_outpath = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..', '..', 'readme.tmp'
)
with open(_outpath, 'wt'): pass  # recreate


# -----------------------------------------------------------------------------
# -------------------------- EXAMPLES START -----------------------------------
# -----------------------------------------------------------------------------
from pytermor import fmt

print(fmt.blue(fmt.underlined('Nested') + fmt.bold(' formats')))

# -----------------------------------------------------------------------------
from pytermor import autof

fmt1 = autof('hi_cyan', 'bold')
fmt2 = autof('bg_black', 'inversed', 'underlined', 'italic')

msg = fmt1(f'Content{fmt2("-aware format")} nesting')
print(msg)

# -----------------------------------------------------------------------------
from pytermor import seq, build

seq1 = build('red', 1)  # keys or integer codes
seq2 = build(seq1, seq.ITALIC)  # existing SGRs as part of a new one
seq3 = build('underlined', 'YELLOW')  # case-insensitive

msg = f'{seq1}Flexible{seq.RESET} ' + \
      f'{seq2}sequence{seq.RESET} ' + \
      str(seq3) + 'builder' + str(seq.RESET)
print(msg)

# -----------------------------------------------------------------------------
from pytermor import build, build_c256
from pytermor import seq

txt = '256 colors support'
msg = f'{build("bold")}'
start_color = 41
for idx, c in enumerate(range(start_color, start_color+(36*6), 36)):
    msg += f'{build_c256(c)}'
    msg += f'{txt[idx*3:(idx+1)*3]}{seq.COLOR_OFF}'
print(msg)

# -----------------------------------------------------------------------------
from pytermor import build, build_rgb
from pytermor import seq

txt = 'True color support'
msg = f'{build("bold")}'
for idx, c in enumerate(range(0, 256, 256//18)):
    msg += f'{build_rgb(max(0, 255-c), max(0, min(255, 127-(c*2))), c)}'
    msg += f'{txt[idx:(idx+1)]}{seq.COLOR_OFF}'
print(msg)

# -----------------------------------------------------------------------------
from pytermor import seq, fmt
from pytermor.fmt import Format

# automatically:
fmt_warn = autof(seq.HI_YELLOW + seq.UNDERLINED)
# or manually:
fmt_warn = Format(
    seq.HI_YELLOW + seq.UNDERLINED,  # sequences can be summed up, remember?
    seq.COLOR_OFF + seq.UNDERLINED_OFF,  # "counteractive" sequences
    hard_reset_after=False
)

orig_text = fmt.bold(f'{seq.BG_BLACK}this is the original string{seq.RESET}')
updated_text = orig_text.replace('original', fmt_warn('updated'), 1)
print(orig_text, '\n', updated_text)

# -----------------------------------------------------------------------------
from pytermor.seq import SequenceSGR

seq = SequenceSGR(4, 7)
msg = f'({seq})'
print(msg + f'{SequenceSGR(0).print()}', str(msg.encode()), msg.encode().hex(':'))

# -----------------------------------------------------------------------------
from pytermor.seq import SequenceSGR
from pytermor import seq

combined = SequenceSGR(1, 31) + SequenceSGR(4)
print(f'{combined}combined{seq.RESET}', str(combined).encode())

# -----------------------------------------------------------------------------
from pytermor.fmt import Format
from pytermor import seq, fmt

fmt_error = Format(seq.BG_HI_RED + seq.UNDERLINED, seq.BG_COLOR_OFF + seq.UNDERLINED_OFF)
msg = fmt.italic.wrap('italic might ' + fmt_error('not') + ' work')
print(msg)

# -----------------------------------------------------------------------------
from pytermor.util import ReplaceSGR
from pytermor import fmt

formatted = fmt.red('this text is red')
replaced = ReplaceSGR('[LIE]').apply(formatted)
# replaced = ReplaceSequenceSGRs('[LIE]')(formatted)

print(formatted, '\n', replaced)

# -----------------------------------------------------------------------------
from pytermor.util import apply_filters, ReplaceNonAsciiBytes

ascii_and_binary = b'\xc0\xff\xeeQWE\xffRT\xeb\x00\xc0\xcd\xed'
result = apply_filters(ascii_and_binary, ReplaceNonAsciiBytes)
print(ascii_and_binary, '\n', result)

# -----------------------------------------------------------------------------
