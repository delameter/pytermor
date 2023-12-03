# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
# ### ### ### ### ### ### ### ###   WARNING   ### ### ### ### ### ### ### ### #
#                                                                             #
#   This is an archived script kept for historical purposes. It can contain   #
#   bugs or even not work all because it was made for old pytermor version.   #
#                                                                             #
#               P R O C E E D   A T   Y O U R   O W N   R I S K               #
#                                                                             #
# ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### #

from __future__ import annotations

import re
from os.path import join, dirname

from PIL import Image
import yaml
from yaml import SafeLoader

SIZE = 64
# @todo update
with open(join(dirname(__name__), 'indexed.yml'), 'r') as f:
    cfg_indexed = yaml.load(f, SafeLoader)

for c in cfg_indexed:
    im = Image.new('RGB', (SIZE, SIZE), f'#{c["value"]:06x}')
    p = join(dirname(__name__), '../..', 'docs', '_generated', 'preset-samples', f'color{c["id"]}.png')
    print(p)
    im.save(p)
