# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------

def get_terminal_width():
    try:
        import shutil as _shutil
        return _shutil.get_terminal_size().columns - 2
    except ImportError:
        return 80
