import re
import pytermor as pt

s = """
   reset             Reset current HEAD to the specified state
   switch            Switch branches
   tag               Create, list, delete or verify a tag object signed with GPG
"""

class SgrNamedGroupsRefilter(pt.AbstractNamedGroupsRefilter):
    def _render(self, v: pt.IT, st: pt.FT) -> str:
        return pt.render(v, st, pt.SgrRenderer)

f = SgrNamedGroupsRefilter(
    re.compile(r"(\s+)(?P<cmd>\S+)(.+)"),
    {"cmd": pt.cv.GREEN},
)

pt.echo(pt.apply_filters(s, f))
