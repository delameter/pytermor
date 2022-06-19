from pytermor import span

print('... ' +
      span.BLUE(span.UNDERLINED('nested') +
                span.BOLD(' styles')) + ' in...')

c1 = color.ColorRGB(0x000001)
c2 = color.ColorRGB.find_closest(0x000001)
print(c1 == c2)
print(c1 is c2)
