# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

import math
import os.path
import re
import time
import typing as t
from dataclasses import dataclass
from random import shuffle
from time import perf_counter_ns
from timeit import timeit

import pytermor as pt
from pytermor import SgrRenderer, wait_key
from pytermor.utilmisc import confirm
from pytermor.common import UserAbort, UserCancel


# from es7s/core:
class PrefixedNumericsHighlighter:
    # fmt: off
    PREFIX_UNIT_REGEX = re.compile(
        r"(?:(?<!\x1b\[)(?<=[]()\s[-])\b|^)"
        r"(\d+)([.,]\d+)?(\s?)"
        r"([kmgtpuμµn%])?"
        r"("
        r"i?b[/ip]?t?s?|v|a|s(?:econd|ec|)s?|m(?:inute|in|onth|on|o|)s?|"
        r"h(?:our|r|)s?|d(?:ay|)s?|w(?:eek|k|)s?|y(?:ear|r|)s?|hz"
        r")?"
        r"(?=[]\s\b()[]|$)",
        flags=re.IGNORECASE,
    )
                                                                          # |_PW_|_G.MULT___G.DIV______TIME______
    STYLE_DEFAULT = pt.NOOP_STYLE                                         # |    | misc.               second
    STYLE_NUL = pt.Style(STYLE_DEFAULT, dim=True)                         # |  0 | zero
    STYLE_PRC = pt.Style(STYLE_DEFAULT, fg=pt.cval.MAGENTA, bold=True)    # |  2 |          percent
    STYLE_KIL = pt.Style(STYLE_DEFAULT, fg=pt.cval.BLUE, bold=True)       # |  3 | Kilo-    milli-     minute
    STYLE_MEG = pt.Style(STYLE_DEFAULT, fg=pt.cval.CYAN, bold=True)       # |  6 | Mega-    micro-     hour
    STYLE_GIG = pt.Style(STYLE_DEFAULT, fg=pt.cval.GREEN, bold=True)      # |  9 | Giga-    nano-      day
    STYLE_TER = pt.Style(STYLE_DEFAULT, fg=pt.cval.YELLOW, bold=True)     # | 12 | Tera-    pico-      week
    STYLE_MON = pt.Style(STYLE_DEFAULT, fg=pt.cval.HI_YELLOW, bold=True)  # |    |                     month
    STYLE_PET = pt.Style(STYLE_DEFAULT, fg=pt.cval.RED, bold=True)        # | 15 | Peta-               year

    PREFIX_MAP = {
        '%': STYLE_PRC,
        'K': STYLE_KIL, 'k': STYLE_KIL, 'm': STYLE_KIL,
        'M': STYLE_MEG, 'μ': STYLE_MEG, 'µ': STYLE_MEG,
        'G': STYLE_GIG, 'g': STYLE_GIG, 'n': STYLE_GIG,
        'T': STYLE_TER, 'p': STYLE_TER,
        'P': STYLE_PET,
    }
    UNIT_MAP = {
        's': STYLE_PRC, 'sec': STYLE_PRC, 'second': STYLE_PRC,
        'm': STYLE_KIL, 'min': STYLE_KIL, 'minute': STYLE_KIL,
        'h': STYLE_MEG,  'hr': STYLE_MEG,   'hour': STYLE_MEG,
        'd': STYLE_GIG, 'day': STYLE_GIG,
        'w': STYLE_TER,  'wk': STYLE_TER, 'week': STYLE_TER,
        'M': STYLE_MON,  'mo': STYLE_MON,  'mon': STYLE_MON, 'month': STYLE_MON,
        'y': STYLE_PET,  'yr': STYLE_PET, 'year': STYLE_PET,
    }
    # fmt: on

    @classmethod
    def format(cls, string: str, renderer: pt.AbstractRenderer) -> str:
        def replace(m: re.Match) -> str:
            return renderer.render(cls._colorize_match(m))

        return cls.PREFIX_UNIT_REGEX.sub(replace, string)

    @classmethod
    def _colorize_match(cls, m: re.Match) -> pt.Text:
        intp, floatp, sep, pref, unit = m.groups("")
        unitn = unit.rstrip("s").strip()

        style_i = cls.STYLE_DEFAULT
        if pref:
            style_i = cls.PREFIX_MAP.get(pref, cls.STYLE_DEFAULT)
        elif unitn:
            style_i = cls.UNIT_MAP.get(unitn, cls.STYLE_DEFAULT)

        digits = intp + floatp[1:]
        if digits.count("0") == len(digits):
            style_i = cls.STYLE_NUL

        style_f = pt.Style(style_i, dim=True)
        style_un = pt.Style(style_i, dim=True, bold=False)
        return (
            pt.Text(intp, style_i)
            + pt.Text(floatp, style_f)
            + sep
            + pt.Text(pref + unit, style_un)
        )


@dataclass
class TestSet:
    mode_read: bool
    mode_binary: bool
    limit: int
    buf_size: int
    name: tuple[int, int]
    last_data_sample: t.AnyStr = ""
    results_ns: t.List[int] = None
    result_avg: float = 0.0
    result_min: float = 0.0
    result_max: float = 0.0
    result_d: float = 0.0
    result_drel: float = 0.0
    speed_avg: float = 0.0

    def __post_init__(self):
        self.results_ns = []

    def compute_stats(self):
        self.result_avg = sum(self.results_ns) / len(self.results_ns)
        self.result_min = min(self.results_ns)
        self.result_max = max(self.results_ns)
        self.result_d = (self.result_max - self.result_min) / 2
        self.result_drel = self.result_d / self.result_avg
        self.speed_avg = self.limit / (self.result_avg * 1e-9)

    def read(self, fr: t.TextIO | t.BinaryIO):
        self.last_data_sample = b"" if self.mode_binary else ""
        while len(self.last_data_sample) < self.limit:
            self.last_data_sample += fr.read(self.buf_size)

    def write(self, fw: t.TextIO | t.BinaryIO):
        total = 0
        while total < self.limit:
            fw.write(self.last_data_sample)
            total += self.buf_size

    def init_random_data(self, frand: t.TextIO | t.BinaryIO):
        self.last_data_sample = frand.read(self.buf_size)

    @property
    def key(self) -> t.Tuple[int, int]:
        return self.limit, self.buf_size

    def __hash__(self):
        return hash(self.key)


class TestRunner:
    REPEATS = 10000
    RUNS = 3

    LIMITS = (4000, 9000, 16000)
    BUF_SIZES = (40, 200, 400, 900, 2000, 4000)

    def __init__(self, mode_read: bool, mode_binary: bool):
        self.mode_read = mode_read
        self.mode_binary = mode_binary
        self.dev = get_test_device(self.mode_read)
        self.test_sets: t.List[TestSet] = [
            TestSet(mode_read, mode_binary, l, b, (l, b))
            for l in self.LIMITS
            for b in self.BUF_SIZES
            if b <= l and (l / b <= 100)
        ]

    def run(self):
        filemode = ("r" if self.mode_read else "w") + ("b" if self.mode_binary else "t")
        args = {}
        if not self.mode_binary:
            args.update({"errors": "replace"})
        frand = open("/dev/random", "r" + filemode[1], **args)

        total_data = 0
        total_cycles = 0
        for run in range(1, self.RUNS + 1):
            fd = open(self.dev, filemode, **args)
            if run == 1:
                printer.print_header(fd)

            shuffle(self.test_sets)
            test_sets_amount = len(self.test_sets)
            for ts_idx, test_set in enumerate(self.test_sets):
                if self.mode_read:
                    fn = test_set.read
                else:
                    fn = test_set.write
                    test_set.init_random_data(frand)

                result = timeit(lambda f=fd: fn(f), "", perf_counter_ns, self.REPEATS)
                test_set.results_ns.append(int(result))
                test_set.compute_stats()
                total_data += test_set.limit * self.REPEATS
                total_cycles += self.REPEATS

                progress = ts_idx / (test_sets_amount - 1 if test_sets_amount > 1 else 1)
                printer.update_status(test_set, run, total_cycles, progress, total_data)

            if runner.RUNS < 30 or run % 100 == 0:
                printer.print_nl()

            fd.close()

        if runner.RUNS >= 30:
            printer.print_nl()


class Printer:
    FPS_MAX = 12
    PREFIXES_SI_UPPER_WUNIT = list(
        map(lambda s: s.upper() if s else "b", pt.utilnum.PREFIXES_SI)
    )
    PREFIXES_SI_UPPER = list(
        map(lambda s: s.upper() if s else None, pt.utilnum.PREFIXES_SI)
    )
    PROGBAR_WIDTH = 15
    TABLE_WIDTH = 100

    size_formatter = pt.utilnum.PrefixedUnitFormatter(  # @TODO implement inheritance
        max_value_len=4,
        truncate_frac=True,
        mcoef=1024.0,
        prefixes=PREFIXES_SI_UPPER_WUNIT,
        prefix_zero_idx=pt.utilnum.PREFIX_ZERO_SI,
    )
    total_size_formatter = pt.utilnum.PrefixedUnitFormatter(
        max_value_len=4,
        truncate_frac=False,
        unit="b",
        unit_separator=" ",
        mcoef=1024.0,
        prefixes=PREFIXES_SI_UPPER,
        prefix_zero_idx=pt.utilnum.PREFIX_ZERO_SI,
    )
    speed_formatter = pt.utilnum.PrefixedUnitFormatter(
        max_value_len=5,
        unit="b/s",
        unit_separator=" ",
        mcoef=1024.0,
        prefixes=PREFIXES_SI_UPPER,
        prefix_zero_idx=pt.utilnum.PREFIX_ZERO_SI,
    )
    int_formatter = pt.utilnum.PrefixedUnitFormatter(
        max_value_len=3,
        truncate_frac=True,
        prefixes=[None, "K", "M", "G"],
        prefix_zero_idx=0,
    )

    def __init__(self):
        self.renderer = SgrRenderer()
        self.prev_update_time = 0

    def render(self, *args, **kwargs) -> str:
        return self.renderer.render(*args, **kwargs)

    @staticmethod
    def print_hr(num: int = 1, fill: str = "─"):
        print((fill * Printer.TABLE_WIDTH + "\n") * num, flush=True, end="")

    @staticmethod
    def print_nl():
        print(flush=True)

    def print_header(self, fd: t.IO):
        self.print_hr()
        header = [
            f" " f"" f"RUNS: {runner.RUNS}",
            f"CYCLES: {runner.REPEATS}",
            f"BUFFER SIZES: {len(runner.test_sets)}",
            f"{'BINARY' if runner.mode_binary else 'TEXT'}"
            + f" {'READ from' if runner.mode_read else 'WRITE to'}"
            + f" {runner.dev or 'FD ' + str(fd.name):>.32s} ",
        ]
        print(pt.distribute_padded(header, self.TABLE_WIDTH), flush=True)
        self.print_hr()

    def format_data_sample(self, test_set: TestSet, max_size: int = 4) -> str:
        sample = (test_set.last_data_sample or "")[: math.trunc(max_size * 2.33)]
        if isinstance(sample, bytes):
            sample = sample[:max_size].hex(" ", -2).upper()
        else:
            sample = re.sub("[^\x20-\x7e]", ".", sample)
        return self.render(f"{sample + '..':<s} ", pt.Style(fg=pt.cval.GRAY_35))

    def update_status(
        self,
        test_set: TestSet,
        run: int,
        total_cycles: int,
        progress: float,
        total_data: int,
    ):
        if (
            self.prev_update_time
            and time.time_ns() - self.prev_update_time < 1e9 / self.FPS_MAX
            and progress < 1.00
        ):
            return
        self.prev_update_time = time.time_ns()

        status = "\r" + pt.ansi.make_erase_in_line().assemble()
        status += f" RUN "
        status += f"{self.int_formatter.format(run):<3s}" + " ["
        status += (
            f"{'|'*math.floor(self.PROGBAR_WIDTH * progress):<{self.PROGBAR_WIDTH}s}"
        )
        status += "] "
        status += (
            f"{pt.format_auto_float(100 * progress, 3)+'%':>4s}"
            if progress < 1
            else self.render("DONE", pt.Style(fg=pt.cval.HI_MAGENTA))
        )

        status += f"   I/O total:"
        status += f"{Printer.total_size_formatter.format(total_data):>4s}".rjust(8)
        status += f"   Cycle avg: "
        status += (
            Printer.format_time_ns(test_set.result_avg, True)
            if test_set.result_avg
            else "--"
        ).rjust(7)
        status += f"  {self.speed_formatter.format(test_set.speed_avg):>9s}"
        status += f" │ {self.format_data_sample(test_set, 4)} "
        status += " "

        status = PrefixedNumericsHighlighter().format(status, self.renderer)
        print(status, end="", flush=True)

    def print_results(self, test_sets: t.List[TestSet]):
        self.print_nl()
        self.print_hr(fill="═")

        header = f" RUNSx     DATA     I/O    BUF. │  AVERAGE TOTAL      "
        header += "TIME   │ AVG I/O    AVG DATA    │ DATA  \n"
        header += f"  CYCLESx   LIMIT    OPSx  CAP. │     RUN DURATION"
        header += "        δ  │  OP. DUR.   COM. SPEED │    SAMPLES"
        print(header)

        prev_limit = None
        for test_set in sorted(test_sets, key=lambda ts: ts.key):
            if prev_limit != test_set.limit:
                self.print_hr()
                prev_limit = test_set.limit
            limit_str = ""
            limit_str += f"{self.int_formatter.format(TestRunner.RUNS):>3s}x "
            limit_str += f"{self.int_formatter.format(TestRunner.REPEATS):>3s}x "
            limit_str += "["
            limit_str += self.size_formatter.format(test_set.limit).rjust(4)
            limit_str += "]"
            limit_str += " <─ " if runner.mode_read else " ─> "
            limit_str = limit_str.ljust(20)

            result_avg_ns = 0
            result_total = "--".center(18)
            result_drel_str = "±> ∞".center(9)
            if TestRunner.RUNS * TestRunner.REPEATS > 0:
                result_avg_ns = sum(test_set.results_ns) / (
                    TestRunner.RUNS * TestRunner.REPEATS
                )
                result_drel = 100 * test_set.result_d / test_set.result_avg
                result_avg_str = self.format_time_ns(test_set.result_avg, True)
                result_d_str = self.format_time_ns(test_set.result_d, True)
                result_total = f"{result_avg_str:>8s} ± {result_d_str:<7s}"

                result_drel_str = (
                    f"±> {pt.format_auto_float(result_drel, 4, True)}%".rjust(9)
                )
                result_drel_st = pt.Style(fg="gray")
                if result_drel > 50:
                    result_drel_st = pt.Styles.ERROR
                elif result_drel > 10:
                    result_drel_st = pt.Styles.WARNING
                result_drel_str = pt.render(result_drel_str, result_drel_st)

            op_num = math.ceil(test_set.limit / test_set.buf_size)
            s = PrefixedNumericsHighlighter.format(
                limit_str
                + f"[{self.int_formatter.format(op_num):>3s}x"
                + f"{self.size_formatter.format(test_set.buf_size):>5s}]"
                + f" │ {result_total} {result_drel_str}"
                + f" │{self.format_time_ns(result_avg_ns, False):>11s}"
                + f" {self.speed_formatter.format(test_set.speed_avg):>11s}"
                + f" │ {self.format_data_sample(test_set)}",
                self.renderer,
            ).replace("±> ", "±")

            print(s, flush=True)
        self.print_hr()

    @staticmethod
    def format_time_ns(value_ns: float, trunc: bool) -> str:
        return Printer.format_time(value_ns, -9, trunc)

    @staticmethod
    def format_time(value: float, pow_shift: float = 0.00, trunc: bool = False) -> str:
        def fmt(p: float, v: float, l: str) -> str:
            if p >= 2 or trunc:
                return "{:>d} {:s}".format(math.trunc(v), l)
            return "{:>.1f} {:s}".format(v, l)

        thresholds = [
            (math.log10(60 * 60 * 24 * 365), "yr"),
            (math.log10(60 * 60 * 24 * 30), "mon"),
            (math.log10(60 * 60 * 24 * 7), "w"),
            (math.log10(60 * 60 * 24), "d"),
            (math.log10(60 * 60), "hr"),
            (math.log10(60), "min"),
            (0, "sec"),
            (-3, "ms"),
            (-6, "μs"),
            (-9, "ns"),
            (-12, "ps"),
            (-15, "fs"),
            (-18, "as"),
        ]
        min_pow, min_label = thresholds[-1]
        value = max(value, math.pow(10, min_pow))
        value_pow = math.log10(value) + pow_shift

        while len(thresholds):
            thr_pow, label = thresholds.pop(0)
            if value_pow >= thr_pow:
                coef = math.pow(10, thr_pow - pow_shift)
                return fmt(value_pow, value / coef, label)
        return "--"


def get_mode_read() -> bool:
    mode_read = True

    prompt = (
        "Press R to test terminal reading speed (this is "
        "a default) or W for writing (r/w)"
    )
    print(prompt, end=": ", flush=True)

    if wait_key() in ("w", "W"):
        mode_read = False
    print("(read)" if mode_read else "(write)")
    return mode_read


def get_mode_binary() -> bool:
    mode_binary = True

    prompt = "Binary mode (default) or text mode? (b/t)"
    print(prompt, end=": ", flush=True)

    if wait_key() in ("t", "T"):
        mode_binary = False
    print("(bin)" if mode_binary else "(text)")
    return mode_binary


def get_test_device(mode_read) -> str:
    dev = "/dev/urandom"  # if mode_read else None
    default = f'use "{dev}"'
    # default = f'use "{dev}"' if mode_read else "automatically allocate a pseudo-terminal"

    prompt = f"Enter name of test file/device or leave empty to {default}: "
    try:
        devstr = input(prompt)
        if not devstr:
            return dev

        if not mode_read and not devstr.startswith('/dev'):
            pt.echo(f"NOTICE: The application will write around 4.15 Gb of data in order to "
                    f"measure speed using various buffer sizes. After the measurements the "
                    f"file then will be truncated to zero size.", pt.Styles.WARNING, wrap=True)
            confirm(required=True)

        if not mode_read and os.path.isfile(devstr):
            if not os.getenv("FORCE_OVERWRITE", None):
                pt.echo(
                    f"NOTICE: For security reasons writing to existing regular files is "
                    f"disabled. If you are OK with the fact that all the data from specified "
                    f'file "{devstr}" will be lost forever and REALLY know what you are '
                    f"doing, set the environment variable FORCE_OVERWRITE to a non-empty "
                    f"string and restart the application. For now writing will be performed "
                    f'into "/dev/null" instead.',
                    pt.Styles.WARNING,
                    wrap=True,
                )
                devstr = "/dev/null"
                confirm(required=True)
        return devstr

    except (EOFError, KeyboardInterrupt, UserAbort, UserCancel):
        print("\nTerminating")
        raise SystemExit(126)


if __name__ == "__main__":
    runner = TestRunner(get_mode_read(), get_mode_binary())
    printer = Printer()
    runner.run()
    printer.print_results(runner.test_sets)
