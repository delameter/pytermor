# -----------------------------------------------------------------------------
# es7s/pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import importlib

for i in range(0, 11):
    importlib.import_module(f'examples.example{i:02d}', package=__name__)
    print(end='\n'*2)
