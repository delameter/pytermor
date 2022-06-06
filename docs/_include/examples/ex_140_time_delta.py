from pytermor import span, sequence, autospan
from pytermor.util import time_delta

seconds_list = [2, 10, 60, 2700, 32340, 273600, 4752000, 864000000]
max_len_list = [3, 6, 10]

custom_stylesheet = time_delta.TimeDeltaStylesheet(
    default=span.bg_black,
    digit=autospan(sequence.BG_BLACK + sequence.YELLOW),
    unit=autospan(sequence.BG_BLACK + sequence.GREEN),
    overflow=autospan(sequence.BG_RED + sequence.BLACK),
)
for max_len in max_len_list:
    formatter = time_delta.registry.find_matching(max_len)
    formatter.stylesheet = custom_stylesheet

for seconds in seconds_list:
    for max_len in max_len_list:
        formatter = time_delta.registry.get_by_max_len(max_len)
        print(formatter.format(seconds, True), end=' ')
    print()
