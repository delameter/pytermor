# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import math
import time
import typing as t
import pytermor as pt
from pytermor import Styles as BaseStyles
from .ioproxy import  get_stdout
from .tstatectl import TerminalStateController


class _DummyProgressBar:
    def __init__(self, *args, **kwargs):
        ...

    def setup(self, *args, **kwargs):
        ...

    @property
    def enabled(self) -> bool:
        return False

    def next_threshold(self, *args, **kwargs):
        ...

    def set(self, *args, **kwargs):
        ...

    def redraw(self, *args, **kwargs):
        ...

    def close(self, *args, **kwargs):
        ...


class _Styles(BaseStyles):
    _THEME_COLOR = pt.cv.BLUE
    _THEME_BRIGHT_COLOR = pt.cv.HI_BLUE

    DEFAULT = pt.Style(bg=pt.cv.GRAY_0, frozen=True)

    ICON = pt.Style(DEFAULT, fg=_THEME_BRIGHT_COLOR, frozen=True)
    TASK_NUM_CUR = pt.Style(ICON, bold=True, frozen=True)
    TASK_NUM_MAX = DEFAULT
    TASK_DELIM = pt.Style(DEFAULT, dim=True, frozen=True)
    TASK_LABEL = DEFAULT

    RATIO_DIGITS = pt.Style(bold=True, frozen=True)
    RATIO_PERC_SIGN = pt.Style(dim=True, frozen=True)
    BAR_BORDER = pt.Style(DEFAULT, fg=pt.cv.GRAY_19, frozen=True)
    BAR_FILLED = pt.Style(fg=pt.cv.GRAY_0, bg=_THEME_COLOR, frozen=True)
    BAR_EMPTY = pt.Style(fg=_THEME_COLOR, bg=pt.cv.GRAY_0, frozen=True)


class ProgressBar:
    BAR_WIDTH = 5
    LABEL_PAD = 2

    MAX_FRAME_RATE = 8
    TERM_WIDTH_QUERY_INTERVAL_SEC = 5

    FIELD_SEP = " "
    ICON = "◆"
    NUM_DELIM = "/"
    BORDER_LEFT_CHAR = "▕"
    BORDER_RIGHT_CHAR = "▏"

    def __init__(
        self,
        tstatectl: t.Optional[TerminalStateController],
        tasks_amount=1,
        task_num=1,
        task_label="Working",
        steps_amount=0,
        step_num=0,
        step_label="...",
        print_step_num=True,
    ):
        self._enabled = True
        get_stdout().set_progress_bar_mode()

        if tstatectl:
            tstatectl.hide_cursor()
            tstatectl.disable_input()

        self._tasks_amount: int = tasks_amount
        self._task_num: int = task_num
        self._task_label: str = task_label

        self._steps_amount = steps_amount
        self._step_num = step_num
        self._step_label: str = step_label

        self._print_step_num = print_step_num

        self._last_frame_ts: t.Optional[int] = None
        self._icon_frame = 0

        self._max_label_len: t.Optional[int] = None
        self._last_term_width_query_ts: t.Optional[int] = None

    @property
    def enabled(self) -> bool:
        return self._enabled

    def init_tasks(self, tasks_amount: int = None, task_num: int = 1):
        if tasks_amount is not None:
            self._tasks_amount = tasks_amount
        if task_num is not None:
            self._task_num = task_num
            self._steps_amount = 0
            self._step_num = 0
        self._task_num = min(self._task_num, self._get_max_task_num())

    def next_task(self, task_label: str = None):
        if task_label is not None:
            self._task_label = task_label
        self.init_tasks(task_num=self._task_num + 1)

    def init_steps(self, steps_amount: int = None, step_num: int = 0):
        if steps_amount is not None:
            self._steps_amount = steps_amount
        if step_num is not None:
            self._step_num = step_num
        self._step_num = min(self._step_num, self._get_max_step_num())

    def next_step(self, step_label: str = None):
        if step_label is not None:
            self._step_label = step_label
        self.init_steps(step_num=self._step_num + 1)

    def render(self):
        if not self._enabled:
            return

        self._compute_max_label_len()
        try:
            self._ensure_next_frame()
        except _FrameAlreadyRendered:
            return

        task_ratio = self._compute_task_progress()
        field_sep = f"{_Styles.DEFAULT.bg.to_sgr(pt.ColorTarget.BG)}{self.FIELD_SEP}"
        result = get_stdout().render(
            pt.Composite(
                field_sep,
                self._format_icon(),
                field_sep,
                *self._format_task_state(),
                field_sep,
                *self._format_ratio_bar(task_ratio),
                pt.SeqIndex.BOLD_DIM_OFF.assemble(),
                field_sep,
                *self._format_labels(),
            )
        )
        get_stdout().echo_progress_bar(result)

    def close(self):
        self._task_num = self._get_max_task_num()
        self._steps_amount = 0

        if self._enabled:
            get_stdout().set_progress_bar_mode(False)
            self._enabled = False

    def _get_max_step_num(self) -> int:
        return self._steps_amount

    def _get_max_task_num(self) -> int:
        return self._tasks_amount

    def _get_max_task_num_len(self) -> int:
        return len(str(self._get_max_task_num()))

    def _compute_task_progress(self) -> float:
        if not self._get_max_step_num():
            return 0.0
        return (self._step_num - 1) / self._get_max_step_num()

    def _compute_max_label_len(self):
        now = time.time()
        if (
            self._last_term_width_query_ts
            and (now - self._last_term_width_query_ts)
            < self.TERM_WIDTH_QUERY_INTERVAL_SEC
        ):
            return

        self._last_term_width_query_ts = now

        field_seps_len = 4 * len(self.FIELD_SEP)
        icon_len = len(self.ICON)
        task_state_len = 2 * self._get_max_task_num_len() + len(self.NUM_DELIM)
        task_bar_len = self.BAR_WIDTH + len(
            self.BORDER_LEFT_CHAR + self.BORDER_RIGHT_CHAR
        )

        self._max_label_len = pt.get_terminal_width() - (
            field_seps_len + icon_len + task_bar_len + task_state_len + self.LABEL_PAD
        )

    def _ensure_next_frame(self):
        now = time.time()
        if self._last_frame_ts and (
            now - self._last_frame_ts < (1 / self.MAX_FRAME_RATE)
        ):
            raise _FrameAlreadyRendered
        self._last_frame_ts = now
        self._icon_frame += 1

    def _format_ratio_bar(self, ratio: float) -> t.Iterable[t.Union[str, pt.Fragment]]:
        filled_length = math.floor(ratio * self.BAR_WIDTH)
        ratio_label = list(f"{100*ratio:>3.0f}%")
        ratio_label_len = 4  # "100%"
        ratio_label_left_pos = (self.BAR_WIDTH - ratio_label_len) // 2
        ratio_label_perc_pos = ratio_label_left_pos + 3

        ren = get_stdout().renderer
        bar_styles = [
            ren.render("\x00", _Styles.BAR_FILLED).split("\x00", 1)[0],
            pt.SeqIndex.INVERSED.assemble(),
        ]
        label_styles = [
            pt.SeqIndex.BOLD.assemble(),
            pt.SeqIndex.DIM.assemble(),
        ]

        cursor = 0
        yield pt.Fragment(self.BORDER_LEFT_CHAR, _Styles.BAR_BORDER)
        yield bar_styles.pop(0)

        while cursor < self.BAR_WIDTH:
            if cursor >= filled_length and bar_styles:
                yield bar_styles.pop()
            if cursor >= ratio_label_left_pos:
                if len(label_styles) == 2:
                    yield label_styles.pop(0)
                if cursor >= ratio_label_perc_pos and label_styles:
                    yield label_styles.pop()
                if len(ratio_label):
                    cursor += 1
                    yield ratio_label.pop(0)
                    continue
            cursor += 1
            yield " "

        if bar_styles:
            yield bar_styles.pop()
        yield pt.SeqIndex.INVERSED_OFF.assemble()
        yield pt.Fragment(self.BORDER_RIGHT_CHAR, _Styles.BAR_BORDER)

    def _format_icon(self) -> pt.Fragment:
        icon = (self.ICON, " ")[self._icon_frame % 2]
        return pt.Fragment(icon, _Styles.ICON)

    def _format_task_state(self) -> t.Iterable[pt.Fragment]:
        task_num_cur = f"{self._task_num:>{self._get_max_task_num_len()}d}"
        task_num_max = f"{self._get_max_task_num():<d}"

        yield pt.Fragment(task_num_cur, _Styles.TASK_NUM_CUR)
        yield pt.Fragment(self.NUM_DELIM, _Styles.TASK_DELIM)
        yield pt.Fragment(task_num_max, _Styles.TASK_NUM_MAX)

    def _format_labels(self) -> t.Iterable[pt.Fragment]:
        task_label = self._task_label
        step_label = self._step_label
        step_num = ""
        if self._print_step_num:
            step_num = f"[{self._step_num}/{self._steps_amount}] "

        # expand right label to max minus (initial) left
        label_right_text = pt.fit(
            step_label,
            self._max_label_len - self.LABEL_PAD * 2 - len(task_label) - len(step_num),
            "<",
        )
        yield pt.Fragment(f"{pt.SeqIndex.DIM}{step_num}")
        yield pt.Fragment(
            f"{pt.SeqIndex.BOLD_DIM_OFF}{task_label}{pt.pad(self.LABEL_PAD)}"
        )
        yield pt.Fragment(f"{pt.SeqIndex.DIM}{label_right_text}")


# thresholds: 6
# ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
# pre1      post1 pre2      post2 pre3        post3 pre4      post4 pre5       post5 pre6         post6
# |>-----(1)-----||>-----(2)-----||>-----(3)-------||>----(4)------||>-----(5)------||>-----(6)-------|
# |______________|_______________|_________________|_______________|________________|_________________|
# ╹0 ''╵''''╹10 '╵''''╹20 '╵''''╹30 '╵''''╹40 '╵''''╹50 '╵''''╹60 '╵''''╹70 '╵''''╹80 '╵''''╹90 '╵''''╹100
#
#                  LABEl      IDX     RATIO
#        pre-1    prepare     0/6| == | 0%           0
#      start-1    task 1      1/6| != | 0%           1
# post-1 pre-2    task 1      1/6| == |16%           1
# post-2 pre-3    task 2      2/6      33%           2
# post-3 pre-4    task 3      3/6      50%           3
# post-4 pre-5    task 4      4/6      66%           4
# post-5 pre-6    task 5      5/6      83%           5
# post-6          task 6      6/6     100%           6
#
# ------------------------------------------------------------------------------------------------------
# FEATURE: tasks with non-linear step thresholds   @TODO @MAYBE
#
#     def _get_ratio_at(self, idx: int):
#         idx = max(0, min(len(self._thresholds) - 1, idx))
#         return self._thresholds[idx]
#
#     def _get_ratio(self):
#         left = self._get_ratio_global()
#         right = self._get_next_ratio_global()
#         return left + self._ratio_local * (right - left)


def get_partial_hblock(val: float) -> str:
    if val >= 7 / 8:
        return "▉"
    elif val >= 6 / 8:
        return "▊"
    elif val >= 5 / 8:
        return "▋"
    elif val >= 4 / 8:
        return "▌"
    elif val >= 3 / 8:
        return "▍"
    elif val >= 2 / 8:
        return "▎"
    elif val >= 1 / 8:
        return "▏"
    return ""


class _FrameAlreadyRendered(Exception):
    pass
