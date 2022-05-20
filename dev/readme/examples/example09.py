from pytermor import sequence, span, Span

span_error = Span(sequence.BG_HI_RED + sequence.UNDERLINED, sequence.BG_COLOR_OFF + sequence.UNDERLINED_OFF)
msg = span.italic.wrap('italic might ' + span_error('not') + ' work')
print(msg)
