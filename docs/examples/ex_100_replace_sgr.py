from pytermor import Spans
from pytermor.utilstr import ReplaceSGR

formatted = Spans.RED('this text is red')
replaced = ReplaceSGR('[LIE]').apply(formatted)
# replaced = ReplaceSGR('[LIE]')(formatted)

print(formatted, '\n', replaced)
