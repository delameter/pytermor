from pytermor import Style, color, ColorRGB
from pytermor import renderer
from pytermor.util import time_delta

seconds_list = [2, 10, 60, 2700, 32340, 273600, 4752000, 864000000]
max_len_list = [3, 6, 10]

custom_stylesheet = time_delta.TimeDeltaStylesheet(
    default=Style(bg_color=0x202028),
    digit=Style(0x3333000, 'yellow'),
    unit=Style(fg_color='green', bg_color=0x202028, underlined=True),
    overflow=Style(fg_color=color.BLACK, bg_color='hi_red', bold=True),
)
for max_len in max_len_list:
    formatter = time_delta.registry.find_matching(max_len)
    formatter.stylesheet = custom_stylesheet

renderer.SGRRenderer.set_as_default()
for seconds in seconds_list:
    for max_len in max_len_list:
        formatter = time_delta.registry.get_by_max_len(max_len)
        print(formatter.format(seconds, True), end=' ')
    print()
