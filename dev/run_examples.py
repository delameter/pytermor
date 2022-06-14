# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import importlib
import os
import re
from os import listdir
from os.path import join, splitext, dirname

for file in sorted(listdir(join(dirname(__name__), 'examples')),
                   key=lambda f: int(re.search(r'.*?(\d+)|.+?', f).group(1) or 0)):
    importlib.import_module('examples.' + splitext(file)[0], package=__name__)
    print(end='\n'*2)
