from pytermor.utilstr import apply_filters, ReplaceNonAsciiBytes

ascii_and_binary = b'\xc0\xff\xeeQWE\xffRT\xeb\x00\xc0\xcd\xed'
result = apply_filters(ascii_and_binary, ReplaceNonAsciiBytes)
print(ascii_and_binary, '\n', result)
