from pytermor import Spans
from pytermor.filter import SgrStringReplacer

formatted = Spans.RED('this text is red')
replaced = SgrStringReplacer('[LIE]').apply(formatted)
# replaced = ReplaceSGR('[LIE]')(formatted)

print(formatted, '\n', replaced)
