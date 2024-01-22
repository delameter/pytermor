# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
# ### ### ### ### ### ### ### ###   WARNING   ### ### ### ### ### ### ### ### #
#                                                                             #
#   This is an archived script kept for historical purposes. It can contain   #
#   bugs or even not work all because it was made for old pytermor version.   #
#                                                                             #
#               P R O C E E D   A T   Y O U R   O W N   R I S K               #
#                                                                             #
# ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### #

import time
import timeit
import typing as t
from math import trunc

from _totalsize import total_size

import pytermor as pt

puf = pt.StaticFormatter(
    max_value_len=4,
    prefixes=pt.PREFIXES_SI_DEC,
)


def mem():
    for c in [pt.ColorRGB]:  # pt.Color.__subclasses__()
        out(c, 'registry', len(c._registry), total_size(c._registry._map, verbose=False))
        out(c, 'index', len(c._index), total_size(c._index._map, verbose=False))
        out(c, 'approx_cache', len(c._approximator._cache), total_size(c._approximator._cache, verbose=False))
    print("-" * 50)


def out(subj: t.Any, desc:str, len: int, mem: int):
    print(
        "  ".join(
            (
                puf.format(len, "").rjust(6),
                pt.format_si_binary(mem).rjust(10),
                (pt.get_qname(subj)+desc).ljust(40),
            )
        )
    )


# for v in range(0, 256*256*256):
#     pt.Color.index.register_virtual(v, (str(v)+'::')*6)
#     if v % 4000000 == 0:
#         measure()

# for v in range(0, 256*256*256):
#     pt.ColorRGB(v, (str(v)+'::')*6)
#     if v % 4000000 == 0:
#         measure()


def hook(origin):
    def fn(*args, **kwargs):
        if (n := len(pt.ColorRGB._index._map)) % 2000000 == 0:
            print(n)
        return origin(*args, **kwargs)

    return fn


pt.ColorRGB._index.add = hook(pt.ColorRGB._index.add)

idx = 0

#MAX = 256 * 256 * 16  # 1m
MAX = 256
#MAX = 25600


def register_virtual():
    global idx
    pt.ColorRGB.index.register_virtual(idx := idx + 1, (str(idx) + ":" + str(idx)))


def instantiate():
    global idx
    pt.ColorRGB(idx := idx + 1, (str(idx) + ":" + str(idx)), approx=True)


def instantiate_and_map():
    global idx
    pt.ColorRGB(idx := idx + 1, (str(idx) + ":" + str(idx)), register=True, approx=True)


def resolve():
    idx = time.time_ns() % MAX + 1
    pt.ColorRGB._registry.find_by_name(str(idx) + ":" + str(idx))


def approximate():
    val = time.time_ns() % 0xFFFFFF
    pt.ColorRGB.approximate(val, max_results=1)

def approximate_cache_misses():
    val = time.time_ns() % 0xFFFFFF
    print(f'{100*len(pt.ColorRGB._approximator._cache)/MAX:.2f}%', end='\r')
    pt.ColorRGB.find_closest(val)

def approximate_cache_hits():
    pt.ColorRGB.find_closest(0x808080)


# p = timeit.timeit(instantiate, number=MAX, globals={'idx': 0})
p = timeit.timeit(instantiate_and_map, number=MAX, globals={"idx": 0})
print(f"#       {p:6.2f} s  making {MAX} instances              #")

ss = timeit.repeat(approximate_cache_misses, number=500, repeat=5)
print(f"#       {pt.format_time(sum(ss)/(500*5))}  approximation (cache miss, 2.5Kavg) #")

ss = timeit.repeat(approximate_cache_hits, number=20000, repeat=50)
print(f"#       {pt.format_time(sum(ss)/(20000*50))}  approximation (cache hit, 1Mavg) #")

ss = timeit.repeat(resolve, number=1000000, repeat=5)
print(f'#       {min(ss):6.2f} s  1M operations (bestof5) #')

mem()

# fmt: off ############################################################################################################
#######################################################################################################################
#|    | instantiate_and_map_eco | approximate          |#|    | register_virtual    | resolve                  |# noqa!
#| 1A +-------------------------+----------------------|#| 2A +---------------------+--------------------------|# noqa!
#|    | map: <intval> -> <ColorRGB>                    |#|    | memory stores <name> => <intvalue> mappings    |# noqa!
#|----+------------------------------------------------|#|----+------------------------------------------------|# noqa!
#|          0.09 s  25K inserts                        |#|          1.12 s  1M inserts                         |# noqa!
#|         29.89 s  1K operations (bestof5)            |#|          3.23 s  1M searches (bestof5)              |# noqa!
#| 25.6k  3.106 Mb  <class 'pytermor.color.ColorRGB'>  |#|     0     232 b  <class 'pytermor.color.ColorRGB'>  |# noqa!
#| 25.9k  1.459 Mb  <class 'pytermor.color.Color'>     |#| 1.05M  61.90 Mb  <class 'pytermor.color.Color'>     |# noqa!
#|_____________________________________________________|#|_____________________________________________________|# noqa!
#|    | instantiate_and_map | approximate              |#|    | instantiate         | resolve                  |# noqa!
#| 1B +---------------------+--------------------------|#| 2B +---------------------+--------------------------|# noqa!
#|    | map: <intval> -> <ColorRGB, int, int, int>     |#|    | memory stores <name> => <ColorRGB> mappings    |# noqa!
#|----+------------------------------------------------|#|----+------------------------------------------------|# noqa!
#|          0.09 s  25K inserts                        |#|          2.75 s  1M inserts                         |# noqa!
#|         22.51 s  1K operations (bestof5)            |#|          1.56 s  1M searches (bestof5)              |# noqa!
#| 25.6k  4.863 Mb  <class 'pytermor.color.ColorRGB'>  |#|     0     232 b  <class 'pytermor.color.ColorRGB'>  |# noqa!
#| 25.9k  1.459 Mb  <class 'pytermor.color.Color'>     |#| 1.05M  61.90 Mb  <class 'pytermor.color.Color'>     |# noqa!
#|_____________________________________________________|#|_____________________________________________________|# noqa!
#|    | instantiate_and_map | approximate_cached       |#|                                                     |# noqa!
#| 1C +---------------------+--------------------------|#|                       SUMMARY                       |# noqa!
#|    | map: <intval> -> <ColorRGB, int, int, int>     |#|                                                     |# noqa!
#|    | cache: <intval> -> <ColorRGB>                  |#|  1. QUERY CACHE IS ALMOST USELESS -- REMOVE IT.     |# noqa!
#|----+------------------------------------------------|#|                                                     |# noqa!
#|          0.09 s  25K inserts                        |#|  2. COLOR INSTANCES TAKE UP THE SAME AMOUNT OF ME-  |# noqa!
#|         21.62 s  1K operations (bestof5)            |#|     MORY AS RAW INTEGER VALUES -- THERE IS NO NEED  |# noqa!
#| 25.6k  4.863 Mb  <class 'pytermor.color.ColorRGB'>  |#|     IN VIRTUAL REGISTRATION MECHANISM.              |# noqa!
#| 25.6k  172.2 kb  <class 'pytermor.color.ColorRGB'>  |#|                                                     |# noqa!
#| 25.9k  1.459 Mb  <class 'pytermor.color.Color'>     |#|  3. SEPARATED CHANNELS IN COLOR MAP INCREASE MEMO-  |# noqa!
#|_____________________________________________________|#|     RY CONSUMPTION UP TO +50%, BUT ACTUAL VALUE IS  |# noqa!
#########################################################|     AROUND 200 KB, WHICH MAKES IT IRRELEVANT.       |# noqa!
#########################################################|                                                     |# noqa!
#########################################################|  4. AFOREMENTIONED SEPARATION SPEEDS UP APPROXIMA-  |# noqa!
#########################################################|     TING, BUT THE ALGORITHM IS STILL RIDICULOUSLY   |# noqa!
#########################################################|     SLOW AND INEFFECTIVE.                           |# noqa!
#########################################################|                                                     |# noqa!
#########################################################|_____________________________________________________|# noqa!
# fmt: on #############################################################################################################
