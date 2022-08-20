from pytermor import Spans, Span, Seqs

span_error = Span(Seqs.BG_HI_RED + Seqs.UNDERLINED, Seqs.BG_COLOR_OFF + Seqs.UNDERLINED_OFF)
msg = Spans.ITALIC.wrap('italic might ' + span_error('not') + ' work')
print(msg)
