from pytermor import span
from pytermor.util import ReplaceSGR

formatted = span.red('this text is red')
replaced = ReplaceSGR('[LIE]').apply(formatted)
# replaced = ReplaceSGR('[LIE]')(formatted)

print(formatted, '\n', replaced)
