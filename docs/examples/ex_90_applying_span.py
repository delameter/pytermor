from pytermor import Spans, Span, SeqIndex

span_error = Span(SeqIndex.BG_HI_RED + SeqIndex.UNDERLINED, SeqIndex.BG_COLOR_OFF + SeqIndex.UNDERLINED_OFF)
msg = Spans.ITALIC.wrap('italic might ' + span_error('not') + ' work')
print(msg)
