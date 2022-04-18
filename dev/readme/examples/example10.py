from pytermor import fmt, ReplaceSGR

formatted = fmt.red('this text is red')
replaced = ReplaceSGR('[LIE]').apply(formatted)
# replaced = ReplaceSequenceSGRs('[LIE]')(formatted)

print(formatted, '\n', replaced)
