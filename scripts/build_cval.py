# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
# BUILD AUTOMATION SCRIPT. Fell free to look around if you'd like, though.
# Makes library source file from color preset configs.
# 'config/*.yml' -> 'pytermor/cval.py'

from __future__ import annotations

import datetime
import re
import sys
import typing as t
from os.path import join
from string import Template

import yaml

from common import PROJECT_ROOT, CONFIG_PATH, TaskRunner
from pytermor import pad


class IndexBuilder(TaskRunner):
    OUTPUT_TPL_PATH = join(PROJECT_ROOT, "pytermor", "cval.py.tpl")
    OUTPUT_DEST_PATH = join(PROJECT_ROOT, "pytermor", "cval.py")
    INDENT = pad(4)

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
        result = {k: "" for k in self.MODE_TO_SORTER_MAP.keys()}
        counts = ""
        for mode, sorter in self.MODE_TO_SORTER_MAP.items():
            self._colors_mode_class = ""
            self._colors_mode_count = 0
            self._colors_mode_unique = 0
            mode_results = [*self._run_mode(mode, sorter)]
            result[mode] += ("\n".join(mode_results) + "\n\n").rstrip()
            counts += f"\n - {self._colors_mode_count:4d}x " \
                      f"`{self._colors_mode_class}` " \
                      f"({self._colors_mode_unique} unique)"

        now = datetime.datetime.now().isoformat()
        with open(self.OUTPUT_TPL_PATH, "rt") as fin:
            with open(self.OUTPUT_DEST_PATH, "wt") as fout:
                fout.write(Template(fin.read()).safe_substitute({
                    'created_at': now,
                    'counts': counts,
                    **{f"defs_{k}": v for k, v in result.items()}
                }))
                self._print_fout_result(fout, self.OUTPUT_DEST_PATH)
        return self._colors_count

    def _run_callback(self, colors_count: int):
        print(f"Colors processed: {colors_count}", file=sys.stdout)

    def _run_mode(self, mode: str, sorter: t.Callable):
        config_path = join(CONFIG_PATH, mode + ".yml")
        with open(config_path, "rt") as f:
            config = yaml.safe_load(f)
            self._print_fin_result(f, config_path)
        self._colors_mode_class = config.get("class")

        colors = sorted(config.get("colors"), key=sorter)
        for color in colors:
            color["var_name"] = color.get("name").upper().replace("-", "_")
            self._validate_names(color)

        longest_name_len = 2 + max(
            len(color.get("var_name")) for color in config.get("colors")
        )

        color_values = set()
        for color in colors:
            self._colors_count += 1
            self._colors_mode_count += 1

            var_name = color.get("var_name")
            code = str(color.get("code"))
            color16_equiv = None
            if mode == "xterm_256" and (color16_equiv := color.get("color16_equiv")):
                color16_equiv = color.get("color16_equiv")

            if color16_equiv:
                col_var_name = f"__256A_16_{color16_equiv}".ljust(longest_name_len) + "= "
            else:
                col_var_name = f"{var_name}".ljust(longest_name_len) + "= "

            col_value = "0x{:06x}, ".format(color.get("value"))
            color_values.add(color.get("value"))

            col_name = f'"{color.get("name")}", '
            col_name = col_name.ljust(longest_name_len + 4)

            cols_code = []
            col_color16_eq = None
            if mode == "xterm_16":
                cols_code = [
                    "IntCode." + (code + ",").ljust(longest_name_len + 1),
                    "IntCode.BG_" + (code + ",").ljust(longest_name_len + 1),
                ]
            if mode == "xterm_256":
                cols_code = [(code + ",").ljust(5)]
                if color16_equiv:
                    col_color16_eq = f"color16_equiv={color16_equiv}, "

            col_aliases = None
            if aliases := color.get("aliases"):
                col_aliases = f"aliases={aliases}, "

            col_variations = ""
            if variations := color.get("variations"):
                variation_map = self._map_variations(variations)
                col_variations = f"variation_map={{\n{variation_map} }}, "

            columns = [
                col_var_name,
                f"{self._colors_mode_class}(",
                col_value,
                *cols_code,
                col_name,
                "register=True, ",
                "index=True, ",
                col_aliases,
                col_color16_eq,
                col_variations,
            ]
            yield self.INDENT + "".join(filter(None, columns)).rstrip(", ") + ")"

        self._colors_mode_unique = len(color_values)

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
            f"{self.INDENT}{pad(9)}0x{v.get('value'):06x}:{pad(3)}\"{v.get('name')}\""
            for v in variations
        )


if __name__ == "__main__":
    IndexBuilder().run()
