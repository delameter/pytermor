# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
import logging

LOGGING_TRACE = 5
logger = logging.getLogger(__package__)

logging.addLevelName(LOGGING_TRACE, "TRACE")
logger.addHandler(logging.NullHandler())  # discards logs by default

# - 8< - - - - - - - - - in your project: - - - - - - - - - - - - - -
#   logger = logging.getLogger('pytermor')
#   handler = logging.StreamHandler()
#   fmt = '[%(levelname)5.5s][%(name)s.%(module)s] %(message)s'
#   handler.setFormatter(logging.Formatter(fmt))
#   logger.addHandler(handler)
#   logger.setLevel(logging.DEBUG)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - >8-


def get_qname(obj) -> str:
    """
    Convenient method for getting a class name for class instances
    as well as for the classes themselves.

    >>> get_qname("aaa")
    'str'
    >>> get_qname(logging.Logger)
    '<Logger>'

    """
    if isinstance(obj, type):
        return "<" + obj.__name__ + ">"
    if isinstance(obj, object):
        return obj.__class__.__qualname__
    return str(obj)
