#!/bin/sh
#-------------------------------------------------------------------------------
# es7s/core
# (c) 2023 A. Shavykin <0.delameter@gmail.com>
#-------------------------------------------------------------------------------

PYTHONSTARTUP=.run-startup.py PYTHONPATH=. venv/bin/python -q "$@"
