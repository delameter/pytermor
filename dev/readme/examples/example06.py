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
