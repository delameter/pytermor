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
