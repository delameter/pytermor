# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from os.path import dirname, join
from subprocess import PIPE, run, CalledProcessError, DEVNULL

try:
    gitdir = dirname(__file__) + "a"
    cp = run(
        ["git", "-C", gitdir, "describe", "--tags"],
        stdout=PIPE,
        stderr=DEVNULL,
        check=True,
    )
    version = cp.stdout.strip().decode()
    cp = run(
        ["git", "-C", gitdir, "show", "-s", "--format=%cd", "--date=format:%b-%y"],
        stdout=PIPE,
        stderr=DEVNULL,
        check=True,
    )
    dt = cp.stdout.strip().decode()

except CalledProcessError as e:
    from datetime import datetime
    from os import stat
    from ._version import __version__

    version = __version__

    versionfile = join(dirname(__file__), "_version.py")
    dt = datetime.fromtimestamp(stat(versionfile).st_mtime).strftime("%b-%y")

print(f"v{version}:{dt}")
