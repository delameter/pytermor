# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
# sparse printing for easier visual separation and screenshot creation
from typing import AnyStr

_print = print

def print(*args, **kwargs):
    _print()
    _print(*args, **kwargs)

# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
from pytermor.preset import fmt_green

print(fmt_green('Success'))

# -----------------------------------------------------------------------------
from pytermor.preset import fmt_green, fmt_underline

msg = fmt_green('Build ' + fmt_underline('complete') + ' in 14.88 seconds')
print(msg)

# -----------------------------------------------------------------------------
from pytermor import build, Format, RESET
from pytermor.preset import UNDERLINED

seq_date = build('red', 1, UNDERLINED)  # mix with integer codes and other sequences
fmt_caution = Format(build('inversed', 'YELLOW'),  # case-insensitive
                     reset_after=True)

msg = f'{seq_date}06-Mar-2022:{RESET} ' + \
      fmt_caution('CAUTION') + \
      f' Servers down'
print(msg)

# -----------------------------------------------------------------------------
from pytermor.preset import *

fmt_error = Format(RED + CROSSLINED + BOLD,
                   reset_after=True)
msg = fmt_error('Error') + Format(HI_RED + INVERSED, RESET)('Panic!')
print(msg)

# -----------------------------------------------------------------------------
from pytermor.preset import fmt_inverse, fmt_underline

msg = f'{fmt_inverse.open}inversed' \
      f'{fmt_underline.open} and' \
      f'{fmt_inverse.close} underlined' \
      f'{fmt_underline.close}'
print(msg)

# -----------------------------------------------------------------------------
from pytermor.preset import *

msg = f'{GREEN}green;' \
      f'{UNDERLINED}underlined;' \
      f'{UNDERLINED_OFF}green;' \
      f'{RESET}default'
print(msg)

# -----------------------------------------------------------------------------
from pytermor import build_text256, RESET

print(''.join([
    f'{build_text256(i)}{i:>4d}{RESET}' +
    ('\n' if i % 16 == 15 else '')
    for i in range(0, 256)
]))

# -----------------------------------------------------------------------------
from pytermor.sequence import SGRSequence
from pytermor.preset import BG_GREEN, RESET

seq1 = 'A' + str(SGRSequence(1, 4)) + 'B'
seq2 = f'text{BG_GREEN}text'
print(seq1, seq2, str(RESET), '', seq1.encode())

# -----------------------------------------------------------------------------
from pytermor import SGRSequence
from pytermor.preset import RESET

new_seq = SGRSequence(1, 31) + SGRSequence(4)
print(f'{new_seq}test{RESET}', '', f'{new_seq}'.encode())

# -----------------------------------------------------------------------------
from pytermor.preset import BLACK, BG_HI_GREEN, RESET

print(f'{BLACK}{BG_HI_GREEN}', 'Example text', str(RESET))

# -----------------------------------------------------------------------------
from pytermor.format import Format
from pytermor.preset import HI_RED, fmt_overline

fmt_error = Format(HI_RED, reset_after=True)
print(fmt_error('ERROR!'))
print(fmt_overline.open +
      'overline might not work because'
      ' its not fully supported :(' +
      fmt_overline.close)

# -----------------------------------------------------------------------------
from pytermor.format import Format
from pytermor.preset import HI_RED, COLOR_OFF, OVERLINED, OVERLINED_OFF, \
    fmt_bold, fmt_underline

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

# -----------------------------------------------------------------------------
from pytermor.preset import fmt_red
from pytermor.string_filter import ReplaceSGRSequences

formatted = fmt_red('this text is red')
print(formatted)
print(ReplaceSGRSequences('[LIE]').invoke(formatted))
# or:
# ReplaceSGRSequences('[E]')(formatted)

# -----------------------------------------------------------------------------
from pytermor import apply_filters
from pytermor.string_filter import ReplaceNonAsciiBytes

ascii_and_binary = b'\xc0\xff\xeeABC\xffDEF\xeb\x00\xc0\xcd\xed\xa7\xde'

# can either provide filter by type (default settings will be used):
# result = apply_filters(ascii_and_binary, ReplaceNonAsciiBytes)
# ..or instantiate and configure it:
result = apply_filters(ascii_and_binary, ReplaceNonAsciiBytes(b'.'))

print(result)

# -----------------------------------------------------------------------------
