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
from os.path import join

import yaml

from common import PROJECT_ROOT, CONFIG_PATH, TaskRunner


class IndexBuilder(TaskRunner):
    OUTPUT_TPL_PATH = join(PROJECT_ROOT, "pytermor", "cval.py.tpl")
    OUTPUT_DEST_PATH = join(PROJECT_ROOT, "pytermor", "cval.py")
    INDENT = " " * 4

    MODE_TO_SORTER_MAP: t.Dict[str, t.Callable] = {
        "xterm_16": lambda _: 0,
        "xterm_256": lambda col: (
            "_" + str(col.get("code")).zfill(2)
            if col.get("color16_equiv")
            else col.get("name")
        ),
        "rgb": lambda col: col.get("name"),
    }

    def __init__(self):
        self._names = set()
        self._colors_count = 0

    def _run(self) -> int:
        result = ""
        for mode, sorter in self.MODE_TO_SORTER_MAP.items():
            result += "\n".join(self._run_mode(mode, sorter)) + "\n\n"
        result = result.rstrip()

        now = datetime.datetime.now().isoformat()
        with open(self.OUTPUT_TPL_PATH, "rt") as fin:
            with open(self.OUTPUT_DEST_PATH, "wt") as fout:
                fout.write(fin.read().replace("%s", result).replace("%t", now))
                self._print_fout_result(fout, self.OUTPUT_DEST_PATH)
        return self._colors_count

    def _run_callback(self, colors_count: int):
        print(f"Colors processed: {colors_count}")

    def _run_mode(self, mode: str, sorter: t.Callable):
        config_path = join(CONFIG_PATH, mode + ".yml")
        with open(config_path, "rt") as f:
            config = yaml.safe_load(f)
            self._print_fin_result(f, config_path)
        color_class = config.get("class")

        colors = sorted(config.get("colors"), key=sorter)
        for color in colors:
            color["var_name"] = color.get("name").upper().replace("-", "_")
            self._validate_names(color)

        longest_name_len = 1 + max(
            len(color.get("var_name")) for color in config.get("colors")
        )

        for color in colors:
            self._colors_count += 1

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
                "register=True, ",
                "index=True, ",
                col_color16_eq,
                col_aliases,
                col_variations,
            ]
            yield self.INDENT + "".join(filter(None, columns)).rstrip(", ") + ")"

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
            f"{self.INDENT}{'':9s}0x{v.get('value'):06x}:{'':3s}\"{v.get('name')}\""
            for v in variations
        )


if __name__ == "__main__":
    IndexBuilder().run()