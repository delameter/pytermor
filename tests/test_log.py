# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import re
from collections import deque
from time import sleep

from pytermor import measure, log


class TestMeasure:
    _original_logger = None

    class _LoggerMock:
        def __init__(self):
            self.queue = deque[str]()

        def log(self, msg: str, *_, **__) -> None:
            self.queue.append(msg)

        info = log
        debug = log
        exception = log

    @classmethod
    def setup_class(cls):
        cls._original_logger = log._logger
        log._logger = cls._LoggerMock()

    @classmethod
    def teardown_class(cls):
        log._logger = cls._original_logger

    def test_measure_with_callable(self):
        self._decorated_with_callable()
        assert re.match(r'result: 5\dms', log._logger.queue.pop().strip())

    def test_measure_without_fmter(self):
        self._decorated_without_fmter()
        assert len(log._logger.queue) == 0

    @classmethod
    def _decorated(cls):
        sleep(0.05)
        log._logger.queue.clear()

    @classmethod
    @measure(formatter=lambda s, *_: [f"result: {s}"])
    def _decorated_with_callable(cls, *_, **__):
        cls._decorated()

    @classmethod
    @measure(formatter=lambda *_: None)
    def _decorated_without_fmter(cls, *_, **__):
        cls._decorated()
