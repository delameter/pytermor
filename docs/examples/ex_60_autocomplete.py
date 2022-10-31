from pytermor import Span, Spans, SeqIndex

# implicitly:
span_warn = Span(93, 4)
# or explicitly:
span_warn = Span.init_explicit(
    SeqIndex.HI_YELLOW + SeqIndex.UNDERLINED,  # sequences can be summed up, remember?
    SeqIndex.COLOR_OFF + SeqIndex.UNDERLINED_OFF,  # "counteractive" sequences
    hard_reset_after=False
)

orig_text = Spans.BOLD(f'this is {SeqIndex.BG_GRAY}the original{SeqIndex.RESET} string')
updated_text = orig_text.replace('original', span_warn('updated'), 1)
print(orig_text, '\n', updated_text)
