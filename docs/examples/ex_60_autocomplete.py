from pytermor import Span, Spans, Seqs

# implicitly:
span_warn = Span(93, 4)
# or explicitly:
span_warn = Span.from_seq(
    Seqs.HI_YELLOW + Seqs.UNDERLINED,  # sequences can be summed up, remember?
    Seqs.COLOR_OFF + Seqs.UNDERLINED_OFF,  # "counteractive" sequences
    hard_reset_after=False
)

orig_text = Spans.BOLD(f'this is {Seqs.BG_GRAY}the original{Seqs.RESET} string')
updated_text = orig_text.replace('original', span_warn('updated'), 1)
print(orig_text, '\n', updated_text)
