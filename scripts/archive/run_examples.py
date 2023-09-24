# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import importlib
import re
from os import listdir
from os.path import join, splitext, abspath
import sys

sys.path.append(abspath(join('../..', 'examples')))
for file in sorted(listdir(abspath(join('../..', 'examples'))),
                   key=lambda f: int(re.search(r'.*?(\d+)|.+?', f).group(1) or 0)):
    importlib.import_module('examples.' + splitext(file)[0], package=__name__)
    print(end='\n'*2)
