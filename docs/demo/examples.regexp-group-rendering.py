import re
import pytermor as pt

s = """
   fetch             Download objects and refs from another repository
   pull              Fetch from and integrate with another repository or a local branch
   push              Update remote refs along with associated objects
"""

regex = re.compile(r"^(\s+)(\S+)(.+)$")
for line in s.splitlines():
    pt.echo(
        regex.sub(
            pt.render(r"\1" + pt.Fragment(r"\2", pt.cv.GREEN) + r"\3"),
            line,
        )
    )

# [extra-1-start]
def replace_expand(m: re.Match) -> str:
    tpl = pt.render(r"\1" + pt.Fragment(r"\2", pt.cv.GREEN) + r"\3")
    return m.expand(tpl)
regex.sub(replace_expand, "...")
# [extra-1-end]

# [extra-2-start]
def replace_manual(m: re.Match) -> str:
    return pt.render(m.group(1) + pt.Fragment(m.group(2), pt.cv.GREEN) + m.group(3))
regex.sub(replace_manual, "...")
# [extra-2-end]
