import re
import pytermor as pt

pt.echo(''.join(
    pt.render([
        *pt.apply_style_selective(
            re.compile(R'([A-Z]+)([^A-Z]+|$)'),
            "A few CAPITALs",
            pt.Style(fg='red'),
        )
    ], renderer=pt.SgrRenderer(pt.OutputMode.XTERM_16))
))
