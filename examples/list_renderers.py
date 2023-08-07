#!/bin/env python3
# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------

from __future__ import annotations

import pytermor as pt
from pytermor import get_terminal_width, ljust_sgr


class Main:
    def __init__(self):
        ListRenderer().run()

class ListRenderer:
    STYLES = {
        "NOOP_COLOR": pt.Style(),
        "Color16:fg": pt.Style(fg=pt.cv.RED),
        "Color16:bg": pt.Style(bg=pt.cv.HI_RED),
        "Color256:fg": pt.Style(fg=pt.cv.GREEN_4),
        "Color256:bg": pt.Style(bg=pt.cv.DARK_SEA_GREEN_4),
        "ColorRGB:fg": pt.Style(fg=pt.ColorRGB(0x004585)),
        "ColorRGB:bg": pt.Style(bg=pt.ColorRGB(0x6E3DC7)),
    }
    PADDINGS_SUM = 13
    PADDINGS_TOTAL = PADDINGS_SUM + 2
    MAX_REL_WIDTH = 0.90

    def run(self):
        width = self.PADDINGS_SUM + sum(self._get_renderers(pt.OutputMode.AUTO).values())

        for om_idx, om in enumerate(reversed(pt.OutputMode)):
            if om == pt.OutputMode.AUTO:
                continue
            pt.echo(f' ┌{("─"+om.value+"─").replace("_", "─").upper()!s:─<{width+1}s}┐')
            self._render_results(None, pt.NOOP_STYLE, pt.OutputMode.NO_ANSI, " ")
            self._render_results(
                "─", pt.NOOP_STYLE, pt.OutputMode.NO_ANSI, "─", header=True
            )

            for style_name, style in self.STYLES.items():
                self._render_results(style_name, pt.Style(style), om)
            pt.echo(f' └{"":─<{width}s}{om_idx}┘')

        pt.echo(
            [
                "",
                "List of the output of each renderer per each output mode." "",
                "Table " "width is dynamic and depends on the terminal size.",
            ],
            wrap=True,
            indent_first=2,
        )

    def _render_results(self, text, style, om, fillchar=" ", header=False):
        align = lambda s, ml, fc=fillchar: ljust_sgr(s[:ml], ml, fc)
        result = " │" + fillchar
        renderers = self._get_renderers(om)
        for r_idx, (renderer, max_len) in enumerate(renderers.items()):
            label = text or (renderer.__class__.__name__)
            current_renderer = renderer  # force_renderer or renderer
            if isinstance(
                current_renderer,
                (
                    pt.renderer.TmuxRenderer,
                    pt.renderer.SgrDebugger,
                    pt.renderer.HtmlRenderer,
                ),
            ):
                result += align(current_renderer.render(label, style), max_len)
            else:
                result += current_renderer.render(align(label, max_len), style)
            result += (
                (fillchar + "┼")
                if (header and r_idx < len(renderers) - 1)
                else fillchar + "│"
            )
            if r_idx < len(renderers) - 1:
                result += fillchar

        pt.echo(result)

    def _get_renderers(self, om):
        term_width = round(get_terminal_width() * self.MAX_REL_WIDTH)
        sgr_r_width = 16
        other_r_width = term_width - sgr_r_width - self.PADDINGS_TOTAL
        per_sgr_width = other_r_width * 2 // 7
        return {
            pt.renderer.SgrRenderer(om): sgr_r_width,
            pt.renderer.SgrDebugger(om): per_sgr_width,
            pt.renderer.TmuxRenderer(): per_sgr_width,
            pt.renderer.HtmlRenderer(): per_sgr_width,
            pt.renderer.NoOpRenderer(): per_sgr_width // 2,
        }


if __name__ == "__main__":
    try:
        Main()
    except Exception as e:
        pt.echo(f"[ERROR] {type(e).__qualname__}: {e}\n", fmt=pt.Styles.ERROR)
        # raise e
