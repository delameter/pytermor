#!/bin/env python3
# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------

from __future__ import annotations

import os

import pytermor as pt


class Main:
    STYLES_1 = {
        "A": pt.Style(fg=pt.ColorRGB(0x943CE0), bg=pt.ColorRGB(0x553592), bold=True),
        "B": pt.Style(fg=pt.ColorRGB(0x8D408C), bg=pt.ColorRGB(0x6E3DC7), bold=True),
        "C": pt.Style(fg=pt.ColorRGB(0x6F3E98), bg=pt.ColorRGB(0x9838A3), bold=True),
    }
    STYLES_2 = {
        "A": pt.Style(fg=pt.ColorRGB(0x006F00), bg=pt.ColorRGB(0x005000), bold=True),
        "B": pt.Style(fg=pt.ColorRGB(0x003500), bg=pt.ColorRGB(0x005000), bold=True),
        "C": pt.Style(fg=pt.ColorRGB(0x6F0000), bg=pt.ColorRGB(0x500000), bold=True),
        "D": pt.Style(fg=pt.ColorRGB(0x350000), bg=pt.ColorRGB(0x500000), bold=True),
    }
    WIDTH = 52

    def run(self):
        pt.echo(
            ["", "Look at the rectangle below. In normal conditions you:"],
            wrap=True,
            indent_first=2,
        )
        pt.echo(
            [
                "1) should see that it's a purple rectangle with some purple letters inside;",
                "2) should be able to read the full word (although it can be challenging);",
                "3) can distinguish 3 sections of the rectangle with different brightness.",
            ],
            wrap=True,
            indent_first=2,
            indent_subseq=5,
        )

        pt.echo()
        pt.echo(pt.pad(8), nl=False)
        wparts = ["insp", "irat", "ion★"]
        for style in reversed(self.STYLES_1.values()):
            wpart = (lambda s: s.center(len(s) + 2))(" ".join(wparts.pop(0).upper()))
            pt.echo(wpart, style, pt.SgrRenderer(), nl=False)
            if len(wparts) == 0:
                break

        pt.echo()
        pt.echo()
        pt.echo(
            [
                "",
                "If ALL these conditions are met, your terminal is working in either "
                "256 color mode or True Color mode. If ANY of these is false -- the "
                "terminal doesn't support neither 256-colors nor True Color mode and "
                "is operating in legacy 16-colors or even monochrome mode. It means "
                "that your terminal does not support advanced SGR formatting (or, which "
                "is more likely, these capabilities are disabled). Your environment "
                "variables are set as follows: ",
                "",
                f"  TERM={os.environ.get('TERM', '')}",
                f"  COLORTERM={os.environ.get('COLORTERM', '')}",
                "",
                "-----",
                "",
                "Previous test cannot tell with enough confidence, which mode exactly "
                "you are running -- the difference between advanced modes would be "
                "insignificant. However, the next test was specially designed to "
                "distinguish between True Color mode and 256 colors mode:",
            ],
            wrap=True,
            indent_first=2,
        )

        pt.echo()
        pt.echo(pt.pad(8), nl=False)
        wparts = ["man", "ife", "sta", "tion"]
        for style in self.STYLES_2.values():
            wpart = (lambda s: s.center(len(s) + 2))(" ".join(wparts.pop(0).upper()))
            style.inversed = not style.inversed
            pt.echo(wpart, style, pt.SgrRenderer(), nl=False)
            if len(wparts) == 0:
                break

        pt.echo()
        pt.echo()
        pt.echo()
        pt.echo(
            ["Same as before, there are three conditions. You:"],
            wrap=True,
            indent_first=2,
        )
        pt.echo(
            [
                "1) should see that the left part is a green rectangle with some "
                "green letters inside, and the right part is similar, except the "
                "color is red;",
                "2) should be able to read the full word;",
                "3) can recognize 4 sections of the target with different brightness -- "
                "the green sections (4 total).",
            ],
            wrap=True,
            indent_first=2,
            indent_subseq=5,
        )
        pt.echo(
            [
                "If all these are met -- your terminal is in True Color mode and "
                "can display full variety of RGB color space (16M colors). Otherwise "
                "the mode is indexed xterm-256."
            ],
            wrap=True,
            indent_first=2,
        )


if __name__ == "__main__":
    Main().run()
