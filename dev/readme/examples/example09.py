from pytermor import seq, fmt, Format

fmt_error = Format(seq.BG_HI_RED + seq.UNDERLINED, seq.BG_COLOR_OFF + seq.UNDERLINED_OFF)
msg = fmt.italic.wrap('italic might ' + fmt_error('not') + ' work')
print(msg)
