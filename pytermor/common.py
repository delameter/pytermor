# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import enum


class ExtendedEnum(enum.Enum):
    """
    Standard `Enum` with a few additional methods on top.


    """

    @classmethod
    def list(cls):
        """
        Return all enum values as list.

        :example:    [1, 10]
        """
        return list(map(lambda c: c.value, cls))

    @classmethod
    def dict(cls):
        """
        Return mapping of all enum keys to corresponding enum values.

        :example:   {<ExampleEnum.VAL1: 1>: 1, <ExampleEnum.VAL2: 10>: 10}
        """
        return dict(map(lambda c: (c, c.value), cls))

