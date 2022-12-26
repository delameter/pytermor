import pytermor.utilnum
from pytermor import RendererManager, SgrRenderer
from pytermor.util import time_delta

seconds_list = [2, 10, 60, 2700, 32340, 273600, 4752000, 864000000]
max_len_list = [3, 6, 10]

for max_len in max_len_list:
    formatter = pytermor.utilnum.tdf_registry.find_matching(max_len)

RendererManager.set_default(SgrRenderer)
for seconds in seconds_list:
    for max_len in max_len_list:
        formatter = pytermor.utilnum.tdf_registry.get_by_max_len(max_len)
        print(formatter.format(seconds, True), end=' ')
    print()
