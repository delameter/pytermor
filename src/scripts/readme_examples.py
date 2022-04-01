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
from pytermor.preset import fmt_yellow, fmt_green, fmt_bg_blue

print(fmt_yellow('Basic'),
      fmt_bg_blue('text'),
      fmt_green('coloring'))

# -----------------------------------------------------------------------------
from pytermor.preset import fmt_green, fmt_inverse, fmt_underline

msg = fmt_green('Nes' + fmt_inverse('te' + fmt_underline('d fo') + 'rm') + 'ats')
print(msg)

# -----------------------------------------------------------------------------
from pytermor import build_c256, build
from pytermor.preset import COLOR_OFF

txt = '256 colors support'
msg = f'{build("bold")}'
start_color = 41
for idx, c in enumerate(range(start_color, start_color+(36*6), 36)):
    msg += f'{build_c256(c)}'
    msg += f'{txt[idx*3:(idx+1)*3]}{COLOR_OFF}'
print(msg)

# -----------------------------------------------------------------------------
from pytermor import build
from pytermor.preset import RESET, UNDERLINED
# create your own reusable sequences with pytermor.build():

seq1 = build('red', 1, UNDERLINED)  # keys, integer codes or existing sequences
seq2 = build('inversed', 'YELLOW')  # keys are case-insensitive

msg = f'{seq1}Flexible{RESET} ' + \
      f'{build(seq1, 3)}sequence{RESET} ' + \
      str(seq2) + 'builder' + str(RESET)
print(msg)

# -----------------------------------------------------------------------------
from pytermor.preset import *

fmt1 = Format(HI_BLUE + BOLD, hard_reset_after=True)
fmt2 = Format(BG_BLACK + INVERSED + UNDERLINED + ITALIC,
              BG_COLOR_OFF + INVERSED_OFF + UNDERLINED_OFF + ITALIC_OFF)
msg = fmt1(f'Custom n{fmt2("establ")}e formats')
print(msg)

# -----------------------------------------------------------------------------
from pytermor.preset import *
from pytermor.sequence import SequenceSGR

msg = f'{CYAN}L{GREEN}ow-{fmt_inverse("l"+str(ITALIC)+"e")}ve{ITALIC_OFF}l ' \
      f'{BG_HI_YELLOW}fo{fmt_underline.open}rm{BG_COLOR_OFF}at ' \
      f'c{SequenceSGR(*MODE8_START.params, 214)}on{RESET}' \
      f'{SequenceSGR(*MODE8_START.params, 208)}t{fmt_underline.close}r{RESET}' \
      f'{SequenceSGR(*MODE8_START.params, 202)}ol{RESET}'
print(msg)

# -----------------------------------------------------------------------------
from pytermor.sequence import SequenceSGR

seq = str(SequenceSGR(4, 7))   # direct transform with str()
msg = f'({seq})'               # f-string var substitution
print(msg + f'{SequenceSGR(0)}',  # f-string value
      str(seq.encode()),
      seq.encode().hex(':'))

# -----------------------------------------------------------------------------
from pytermor import SequenceSGR
from pytermor.preset import RESET

mixed = SequenceSGR(1, 31) + SequenceSGR(4)
print(f'{mixed}combined{RESET}', str(mixed).encode())

# -----------------------------------------------------------------------------
from pytermor.preset import BLACK, BG_HI_GREEN, RESET

print(f'{BLACK}{BG_HI_GREEN}', 'BLACK on HI-GREEN', str(RESET))

# -----------------------------------------------------------------------------
from pytermor.format import Format
from pytermor.preset import HI_RED, COLOR_OFF, fmt_overline

fmt_error = Format(HI_RED, COLOR_OFF)
print(fmt_overline.open +
      'overline might not work ' +
      fmt_error('>') + ':(' +
      fmt_overline.close)

# -----------------------------------------------------------------------------
from pytermor.preset import *

fmt_warn = Format(
    HI_YELLOW + UNDERLINED,  # sequences can be summed up, remember?
    COLOR_OFF + UNDERLINED_OFF,  # "counteractive" sequences
    hard_reset_after=False
)
orig_text = fmt_bold(f'{BG_BLACK}this is the original string{RESET}')
updated_text = orig_text.replace('original', fmt_warn('updated'), 1)
print(orig_text, '\n', updated_text)

# -----------------------------------------------------------------------------
from pytermor.preset import fmt_red
from pytermor.string_filter import ReplaceSGR

formatted = fmt_red('this text is red')
replaced = ReplaceSGR('[LIE]').invoke(formatted)
# or directly:
# replaced = ReplaceSequenceSGRs('[LIE]')(formatted)

print(formatted, '\n', replaced)

# -----------------------------------------------------------------------------
from pytermor.string_filter import apply_filters, ReplaceNonAsciiBytes

ascii_and_binary = b'\xc0\xff\xeeQWE\xffRT\xeb\x00\xc0\xcd\xed'

# can either provide filter by type (default settings will be used):
# result = apply_filters(ascii_and_binary, ReplaceNonAsciiBytes)
# ..or instantiate and configure it:
result = apply_filters(ascii_and_binary, ReplaceNonAsciiBytes(b'.'))

print(ascii_and_binary, '\n', result)

# -----------------------------------------------------------------------------
