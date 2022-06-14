from pytermor import sequence, span, Span

# automatically:
span_warn = Span(sequence.HI_YELLOW + sequence.UNDERLINED)
# or explicitly:
span_warn = Span.new(
    sequence.HI_YELLOW + sequence.UNDERLINED,  # sequences can be summed up, remember?
    sequence.COLOR_OFF + sequence.UNDERLINED_OFF,  # "counteractive" sequences
    hard_reset_after=False
)

orig_text = span.BOLD(f'this is {sequence.BG_GRAY}the original{sequence.RESET} string')
updated_text = orig_text.replace('original', span_warn('updated'), 1)
print(orig_text, '\n', updated_text)
