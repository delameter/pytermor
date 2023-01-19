# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import typing as t

from sphinx.ext.inheritance_diagram import InheritanceGraph


def class_info_patched(fn: t.Callable):

    #  Main idea is: iterate InheritanceGraph result nodelist; keep
    #  classes, which are related (directly or not) to any top-level
    #  class from the definition, while hiding not related ones. The
    #  result consists of top-level classes with all their children
    #  found in the same (top-level class origination) module.
    #
    #  ┌─ renderers.rst ──────────────────────────────────────────┐
    #  │ .. inheritance-diagram::  pytermor.renderer              │
    #  │    :top-classes:          pytermor.renderer.IRenderer    │
    #  └──────────────────────────────────────────────────────────┘
    #    ↓           ↓            ↓           ↓             ↓
    #  ┌─ filter_not_related ─────────────────────────────────────┐
    #  │ keep because          keep because is a │  hide as       │
    #  │ is a top class     child of a top class │  irrelevant    │
    #  │ ┌───────────┐           ┌─────────────┐ │ ┌────────────┐ │
    #  │ │ IRenderer │ --------> │ SgrRenderer │ │ │ OutputMode │ │
    #  │ └───────────┘           └─────────────┘ │ └────────────┘ │
    #  └──────────────────────────────────────────────────────────┘

    def filter_not_related(
        result: t.List[t.Tuple[str, str, t.List[str], str]], top_classes: t.List[t.Any]
    ) -> t.List[t.Tuple[str, str, t.List[str], str]]:
        class_parents_map = {v[0]: v for v in result}
        filtered_result = filter(
            lambda r: recurse_has_listed_parents(r, class_parents_map, top_classes),
            result,
        )
        return list(filtered_result)

    def recurse_has_listed_parents(
        target: t.List[t.AnyStr],
        class_parents_map: t.Dict[str, t.List[t.AnyStr]],
        top_classes: t.List[t.AnyStr],
    ) -> bool:
        if target[1] in top_classes:
            return True
        for target_parent in target[2]:
            parent_resolved = class_parents_map.get(target_parent)
            if not parent_resolved:
                continue
            return recurse_has_listed_parents(
                parent_resolved, class_parents_map, top_classes
            )
        return False

    def wrapper(
        instance: InheritanceGraph,
        classes: t.List[t.Any],
        show_builtins: bool,
        private_bases: bool,
        parts: int,
        aliases: t.Dict[str, str],
        top_classes: t.List[t.Any],
        *args,
        **kwargs,
    ) -> t.List[t.Tuple[str, str, t.List[str], str]]:
        result = fn(
            instance,
            classes,
            show_builtins,
            private_bases,
            parts,
            aliases,
            top_classes,
            *args,
            **kwargs,
        )
        return filter_not_related(result, top_classes)

    return wrapper
