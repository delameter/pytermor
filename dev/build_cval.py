# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
# BUILD AUTOMATION SCRIPT. Fell free to look around if you'd like, though.
# Makes library source file from color preset configs.
# 'config/*.yml' -> 'pytermor/cval.py'

from __future__ import annotations

import datetime
import re
import typing as t
from os.path import join, dirname, abspath
import yaml


class IndexBuilder:
    PROJECT_ROOT = abspath(join(dirname(__file__), ".."))
    CONFIG_PATH = join(PROJECT_ROOT, "config")
    OUTPUT_TPL_PATH = join(PROJECT_ROOT, "pytermor", "cval.py.tpl")
    OUTPUT_DEST_PATH = join(PROJECT_ROOT, "pytermor", "cval.py")

    def __init__(self):
        self.names = set()

    def run(self):
        result = ""
        for mode in ["xterm_16", "xterm_256", "rgb"]:
            result += "\n".join(self._run_mode(mode)) + "\n\n"
        result = result.rstrip()

        now = datetime.datetime.now().isoformat()
        with open(self.OUTPUT_TPL_PATH, "rt") as inp:
            with open(self.OUTPUT_DEST_PATH, "wt") as out:
                out.write(inp.read().replace("%s", result).replace("%t", now))

    def _run_mode(self, mode: str):
        with open(join(self.CONFIG_PATH, mode + ".yml")) as f:
            config = yaml.safe_load(f)
        color_class = config.get("class")

        for color in config.get("colors"):
            color["var_name"] = color.get("name").upper().replace("-", "_")
            self._validate_names(color)
        longest_name_len = 1 + max(
            len(color.get("var_name")) for color in config.get("colors")
        )

        for color in config.get("colors"):
            var_name = color.get("var_name")
            code = str(color.get("code"))
            color16_equiv = None
            if mode == "xterm_256" and (color16_equiv := color.get("color16_equiv")):
                color16_equiv = color.get("color16_equiv")

            col_var_name = None
            if mode != "rgb" and not color16_equiv:
                col_var_name = f"{var_name}".ljust(longest_name_len) + "= "

            col_value = "0x{:06x}, ".format(color.get("value"))

            col_name = f'"{color.get("name")}", '
            col_name = col_name.ljust(longest_name_len + 4)

            cols_code = []
            col_color16_eq = None
            if mode == "xterm_16":
                cols_code = [
                    "IntCode." + (code + ",").ljust(longest_name_len + 2),
                    "IntCode.BG_" + (code + ",").ljust(longest_name_len + 2),
                ]
            if mode == "xterm_256":
                cols_code = [(code + ",").ljust(5)]
                if color16_equiv:
                    col_color16_eq = f"color16_equiv={color16_equiv},"

            col_aliases = None
            if aliases := color.get("aliases"):
                col_aliases = f"aliases={aliases},"

            col_variations = ""
            if variations := color.get("variations"):
                variation_map = self._map_variations(variations)
                col_variations = f"variation_map={{\n{variation_map} }},"

            columns = [
                col_var_name,
                f"{color_class}(",
                col_value,
                *cols_code,
                col_name,
                'register=True, ',
                'index=True, ',
                col_color16_eq,
                col_aliases,
                col_variations,
            ]
            yield "".join(filter(None, columns)).rstrip(", ") + ")"

    def _extract_names(self, color: t.Dict) -> t.List[str]:
        return [
            color.get("name"),
            *color.get("aliases", []),
            *[v.get("name") for v in color.get("variations", [])],
        ]

    def _validate_names(self, color: t.Dict):
        for name in self._extract_names(color):
            if not re.fullmatch("[a-z0-9-]+", name):
                raise ValueError(f"Invalid name '{name}' for color def {color}")

    def _map_variations(self, variations: t.List[t.Dict]) -> str:
        return ", \n".join(
            f"         0x{v.get('value'):06x}:   \"{v.get('name')}\"" for v in variations
        )


if __name__ == "__main__":
    IndexBuilder().run()
