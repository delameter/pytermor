# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

import timeit
from os.path import abspath, join, dirname
import re
import typing as t
import yaml

import pytermor as pt

# logger = logging.getLogger('pytermor')
# handler = logging.StreamHandler(sys.stderr)
# logging.Formatter('[%(levelname)5.5s][%(name)s][%(module)s] %(message)s')
# handler.setFormatter(formatter)
# logger.addHandler(handler)
# logger.setLevel('DEBUG')


def error(string: str | pt.Renderable):
    print(pt.render("[ERROR] ", pt.Styles.ERROR_LABEL) + string)
    exit(1)


class RgbPreprocessor:
    # fmt: off
    NAME_ALLOWED_CHARS = "[a-z0-9 -]+"
    NAME_ALLOWED_REGEX = re.compile(NAME_ALLOWED_CHARS, flags=re.ASCII)
    TRANSLATION_MAP = {
        0xe9: 'e',  # é
    }
    # fmt: on

    PROJECT_ROOT = abspath(join(dirname(__file__), ".."))
    CONFIG_PATH = join(PROJECT_ROOT, "config")
    INPUT_CONFIG_FILENAME = "rgb.source.yml"
    OUTPUT_CONFIG_FILENAME = "rgb.yml"

    def run(self) -> t.List[t.Dict]:
        with open(join(self.CONFIG_PATH, self.INPUT_CONFIG_FILENAME), "rt") as f:
            color_defs = yaml.safe_load(f)
            filesize = pt.util.format_si_binary(f.tell())
            print(f"Read  {filesize:8s} <-- '{self.INPUT_CONFIG_FILENAME}'")

        ids = set()  # tuple(name, lvl1var, lvl2var...)
        colors = []

        for color_def in color_defs:
            parts = []
            for raw_part in re.split(r"\s*[()#]\s*", color_def["name"].strip()):
                part = re.sub(r"[^\w]+", "-", raw_part.strip().lower().replace("'", ""))
                part = re.sub("-color(ed)?$", "", part.strip("-"))
                if part:
                    parts.append(part)

            for idx in range(0, len(parts)):
                possible_id = tuple(parts[: idx + 1])
                if possible_id in ids:
                    if idx == len(parts) - 1:
                        error(
                            "Unresolvable conflict in "
                            + pt.render("-".join(parts), pt.Styles.WARNING)
                        )
                    continue
                else:
                    ids.add(possible_id)
                    name = parts[0].replace("-", " ")
                    name = name.translate(self.TRANSLATION_MAP)

                    prohibited_chars = self.NAME_ALLOWED_REGEX.sub("", name)
                    if len(prohibited_chars) > 0:
                        prohibited_chars = ",".join(
                            pt.render(c, pt.Styles.ERROR_ACCENT)
                            for c in prohibited_chars
                        )
                        error(
                            f"Prohibited characters: [{prohibited_chars}] in "
                            + pt.render(name, pt.Styles.WARNING)
                        )
                    color = {
                        "value": color_def["value"],
                        "name": name,
                        "original_name": color_def["name"],
                    }
                    if (v := ("-".join(parts[1 : idx + 1]))) != "":
                        color["variation"] = v
                    colors.append(color)

                    break

        config = {
            "class": pt.ColorRGB.__qualname__,
            "colors": list(sorted(colors, key=lambda c: c["value"])),
        }

        yaml.add_representer(
            int, lambda dumper, data: dumper.represent_int(f"0x{data:06x}")
        )
        with open(join(self.CONFIG_PATH, self.OUTPUT_CONFIG_FILENAME), "wt") as f:
            yaml.dump(
                config,
                f,
                allow_unicode=True,
                indent=2,
                encoding="utf8",
            )
            filesize = pt.util.format_si_binary(f.tell())
            print(f"Wrote {filesize:8s} --> '{self.OUTPUT_CONFIG_FILENAME}'")

        return colors


def __main():
    color_defs = RgbPreprocessor().run()
    print(f"Preprocessed {len(color_defs)} definitions", end='')


if __name__ == "__main__":
    elapsed = timeit.Timer(__main).timeit(1)
    if elapsed > 10:
        print(f" in {pt.util.format_time_delta(elapsed)}")
    else:
        print(f" in {pt.util.format_si_metric(elapsed, 's')}")
