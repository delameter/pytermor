#!/bin/sh
#------------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]                           -
# (c) 2023. A. Shavykin <0.delameter@gmail.com>                               -
# Licensed under GNU Lesser General Public License v3.0                       -
#------------------------------------------------------------------------------

PYTHONSTARTUP=.run-startup.py PYTHONPATH=. venv/bin/python -q "$@"
