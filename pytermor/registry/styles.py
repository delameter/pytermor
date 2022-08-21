# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from .colors import Colors
from ..common import Registry
from ..render import Style


class Styles(Registry[Style]):
    """
    Some ready-to-use styles. Can be used as examples.

    This registry has unique keys in comparsion with other ones (`Seqs` / `Spans` / `IntCodes`),
    Therefore there is no risk of key/value duplication and all presets can be listed
    in the initial place -- at API docs page directly.
    """

    ERROR = Style(fg=Colors.RED)
    ERROR_LABEL = Style(ERROR, bold=True)
    ERROR_ACCENT = Style(fg=Colors.HI_RED)
