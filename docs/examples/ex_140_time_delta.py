from pytermor import Style, color, ColorRGB
from pytermor import renderer
from pytermor.renderer import RendererManager, SGRRenderer
from pytermor.util import time_delta

seconds_list = [2, 10, 60, 2700, 32340, 273600, 4752000, 864000000]
max_len_list = [3, 6, 10]

custom_stylesheet = time_delta.TimeDeltaStylesheet(
    default=Style(bg=0x202028),
    digit=Style(0x3333000, 'yellow'),
    unit=Style(fg='green', bg=0x202028, underlined=True),
    overflow=Style(fg=color.BLACK, bg='hi_red', bold=True),
)
for max_len in max_len_list:
    formatter = time_delta.registry.find_matching(max_len)
    formatter.stylesheet = custom_stylesheet

RendererManager.set_up(SGRRenderer)
for seconds in seconds_list:
    for max_len in max_len_list:
        formatter = time_delta.registry.get_by_max_len(max_len)
        print(formatter.format(seconds, True), end=' ')
    print()
