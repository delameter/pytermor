# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
# BUILD AUTOMATION SCRIPT. Fell free to look around if you'd like, though.
# Transforms arbitrary named color config into standardized library format.
# 'config/sources/rgb.source.yml' -> 'config/rgb.yml'

from __future__ import annotations

import re
import typing as t
import unicodedata
from os.path import join

import yaml

import pytermor as pt
from common import CONFIG_PATH, error, TaskRunner


# logger = logging.getLogger('pytermor')
# handler = logging.StreamHandler(sys.stderr)
# formatter = logging.Formatter('[%(levelname)5.5s][%(name)s][%(module)s] %(message)s')
# handler.setFormatter(formatter)
# logger.addHandler(handler)
# logger.setLevel('DEBUG')


class RgbPreprocessor(TaskRunner):
    NAME_ALLOWED_CHARS = "[a-z0-9 -]+"
    NAME_ALLOWED_REGEX = re.compile(NAME_ALLOWED_CHARS, flags=re.ASCII)

    INPUT_CONFIG_FILENAME = "sources/rgb.source.yml"
    OUTPUT_CONFIG_FILENAME = "rgb.yml"

    def __init__(self):
        config_path = join(CONFIG_PATH, self.INPUT_CONFIG_FILENAME)
        with open(config_path, "rt") as f:
            self._color_defs = yaml.safe_load(f)
            self._print_fin_result(f, config_path)

        # tuple(name, variation_part_1, variation_part_2...)
        self._ids: t.Set[t.Tuple[str, ...]] = set()
        self._colors: t.Dict[str, t.Dict] = {}
        self._variations: t.Dict[str, t.Dict[str, t.Dict]] = {}

    def _run(self) -> t.List[t.Dict]:
        for color_def in self._color_defs:
            self._process_color_def(color_def)
        config = self._assemble_config()
        self._dump_config(config)
        return config.get("colors")

    def _run_callback(self, result: t.List[t.Dict]):
        print(f"Definitions preprocessed: {len(result)}")

    def _process_color_def(self, color_def: t.Dict):
        color_def_name = color_def.get("name")
        parts = list(self._split_name(color_def_name))
        name, variation = self._pick_unique_id(parts)
        value = color_def.get("value")
        color = self._create_color(name, variation, value, color_def_name)

        if aliases_raw := color_def.get("aliases", []):
            aliases = []
            for alias_raw in aliases_raw:
                parts = list(self._split_name(alias_raw))
                alias, _ = self._pick_unique_id(parts)
                aliases.append(alias)
            color.update({"aliases": aliases})

    def _split_name(self, color_def_name: str) -> t.List[str]:
        color_def_name = color_def_name.replace("'", "").strip()
        for raw_part in re.split(r"\s*[()#]\s*", color_def_name):
            part = re.sub(r"([a-z])([A-Z0-9])|[^\w]+", r"\1-\2", raw_part.strip("-"))
            part = re.sub("-color(ed)?$", "", part.lower().strip("-"))
            part = "".join(
                filter(  # é->e, ō->o, ū->u etc
                    lambda c: unicodedata.category(c) != "Mn",
                    unicodedata.normalize("NFD", part),
                )
            )
            if part:
                prohibited_chars = self.NAME_ALLOWED_REGEX.sub("", part)
                if len(prohibited_chars) > 0:
                    prohibited_chars = ",".join(
                        pt.render(c, pt.Styles.ERROR_ACCENT) for c in prohibited_chars
                    )
                    parts_str = pt.render(part, pt.Styles.WARNING)
                    error(f"Prohibited characters: [{prohibited_chars}] in " + parts_str)
                yield part

    def _pick_unique_id(self, parts: t.List[str]) -> t.Tuple[str, str]:
        for part_idx in range(0, len(parts)):
            possible_id = tuple(parts[: part_idx + 1])
            if possible_id in self._ids:
                if part_idx < len(parts) - 1:
                    continue
                parts_str = pt.render(" ".join(parts), pt.Styles.WARNING)
                error("Unresolvable conflict: " + parts_str + " already exists")
            else:
                self._ids.add(possible_id)
                return parts[0], "-".join(parts[1 : part_idx + 1])

    def _create_color(
        self, name: str, variation: str, value: int, original_name: str
    ) -> t.Dict:
        color: t.Dict[str, t.Any] = {
            "name": variation if variation else name,
            "value": value,
            "original_name": original_name,
        }
        if variation:
            if name not in self._variations.keys():
                self._variations[name] = {}
            self._variations[name][variation] = color
        else:
            self._colors[name] = color
        return color

    def _assemble_config(self):
        color_defs = []
        for color in sorted(self._colors.values(), key=lambda c: c.get("name")):
            color_name = color.get("name")
            if color_variations := self._variations.get(color_name):
                sorted_variations = sorted(
                    color_variations.values(), key=lambda v: v["name"]
                )
                color.update({"variations": list(sorted_variations)})
            color_defs.append(color)
        return {"class": pt.ColorRGB.__qualname__, "colors": color_defs}

    def _dump_config(self, config: t.Dict):
        class IndentedDumper(yaml.Dumper):
            def __init__(self, *args, **kwargs) -> None:
                super().__init__(*args, **kwargs)

                self.add_representer(
                    int, lambda dumper, data: dumper.represent_int(f"0x{data:06x}")
                )

            def increase_indent(self, flow=False, indentless=False):
                return super(IndentedDumper, self).increase_indent(flow, False)

        output_path = join(CONFIG_PATH, self.OUTPUT_CONFIG_FILENAME)
        with open(output_path, "wt") as fout:
            yaml.dump(
                config,
                fout,
                allow_unicode=True,
                indent=2,
                encoding="utf8",
                Dumper=IndentedDumper,
            )
            self._print_fout_result(fout, output_path)


if __name__ == "__main__":
    RgbPreprocessor().run()
