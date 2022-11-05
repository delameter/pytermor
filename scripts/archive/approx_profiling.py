# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import time
import timeit
import typing as t
from math import trunc

import pytermor as pt
from pytermor.util import system, PrefixedUnitFormatter

puf = PrefixedUnitFormatter(
    4,
    True,
    prefixes=pt.util.prefixed_unit.PREFIXES_SI,
    prefix_zero_idx=pt.util.prefixed_unit.PREFIX_ZERO_SI,
)


def mem():
    for c in [pt.ColorRGB]:  # pt.Color.__subclasses__()
        out(c, len(c._map), system.total_size(c._map, verbose=False))
        out(c, len(c._map), system.total_size(c._approx_query_cache, verbose=False))
    out(
        pt.Color,
        len(pt.Color.index._name_index),
        system.total_size(
            pt.Color.index, {pt.color.Index: lambda i: i._name_index}, verbose=False
        ),
    )
    print("-" * 50)


def out(subj: t.Any, len: int, mem: int):
    print(
        "  ".join(
            (
                puf.format(len, "").rjust(5),
                pt.util.format_si_binary(mem).rjust(8),
                repr(subj).ljust(40),
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
        if (n := len(pt.ColorRGB.index._name_index)) % 2000000 == 0:
            print(n)
        return origin(*args, **kwargs)

    return fn


pt.ColorRGB.index.register = hook(pt.ColorRGB.index.register)

idx = 0

MAX = 256 * 256 * 16  # 1m
# MAX = 25600


def register_virtual():
    global idx
    pt.ColorRGB.index.register_virtual(idx := idx + 1, (str(idx) + ":" + str(idx)))


def instantiate():
    global idx
    pt.ColorRGB(idx := idx + 1, (str(idx) + ":" + str(idx)))


def instantiate_and_map():
    global idx
    pt.ColorRGB(idx := idx + 1, (str(idx) + ":" + str(idx)), add_to_map=True)


def resolve():
    idx = time.time_ns() % MAX + 1
    pt.ColorRGB.index.resolve(str(idx) + ":" + str(idx))


def approximate():
    val = time.time_ns() % 0xFFFFFF
    pt.ColorRGB.approximate(val, max_results=1)


def approximate_cached():
    val = time.time_ns() % 0xFFFFFF
    pt.ColorRGB.find_closest(val)


# p = timeit.timeit(instantiate, number=MAX, globals={'idx': 0})
p = timeit.timeit(instantiate_and_map, number=MAX, globals={"idx": 0})
print(f"#       {p:6.2f} s  init time                             #")

# ss = timeit.repeat(resolve, number=1000000, repeat=5)
# print(f'#       {min(ss):6.2f} s  1M operations (bestof5) #')
ss = timeit.repeat(approximate_cached, number=1000, repeat=2)
print(f"#       {min(ss):6.2f} s  1K operations (bestof5) #")
print(ss)

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
