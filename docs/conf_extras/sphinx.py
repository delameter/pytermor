# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2024. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import re
from typing import Tuple, List

from docutils import nodes
from docutils.nodes import Node, system_message
from docutils.parsers.rst import Directive
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxRole

from sphinx.domains.std import OptionXRefRole, EnvVarXRefRole, Cmdoption, EnvVar
import pytermor as pt

def depart_node_noop(self, node):
    pass

def visit_node_unsupported(self, node):
    self.builder.warn(f"unsupported output format (node skipped)")
    raise nodes.SkipNode

# -------------------------------------------------------------------------

class AnsiRole(SphinxRole):
    def run(self) -> Tuple[List[Node], List[system_message]]:
        node_list = []

        for span in re.split(r'\s*(ESC)\s*', self.text):
            if 'ESC' in span:
                node = nodes.inline(rawtext=span, classes=[self.name])
            else:
                node = nodes.literal(rawtext=span, role='literal', classes=[self.name])
            node += nodes.Text(span)
            node_list.append(node)

        return node_list, []

# -------------------------------------------------------------------------

class CBoxRole(SphinxRole):
    def run(self) -> Tuple[List[Node], List[system_message]]:
        col: pt.ColorRGB = pt.resolve_color(self.text)
        box = CBoxNode(value=col)
        return [box], []

class ColorBoxRole(SphinxRole):
    def run(self) -> Tuple[List[Node], List[system_message]]:
        col: pt.ColorRGB = pt.resolve_color(self.text)
        box = ColorBoxNode(value=col)
        return [box], []

class LabeledColorBoxRole(ColorBoxRole):
    def run(self) -> Tuple[List[Node], List[system_message]]:
        col: pt.ColorRGB = pt.resolve_color(self.text)
        box = LabeledColorBoxNode(value=col, label=col.name)
        return [box], []

class CBoxNode(nodes.General, nodes.Element):
    def hexval(self, prefix):
        return self["value"].format_value(prefix)

    @staticmethod
    def visit_node_html(self, node: ColorBoxNode):
        hexval = node.hexval("#")
        self.body.append(f'<span class="colorbox" style="background-color: {hexval}">&nbsp;</span>')

    @staticmethod
    def visit_node_latex(self, node):
        hexval = node.hexval("")
        self.body.append("\\definecolor{HEX%s}{HTML}{%s}" % (hexval, hexval))
        self.body.append("\\begin{ptcolorbox}[colback=HEX%s,colupper=HEX%s]{@}\\end{ptcolorbox}" % (hexval, hexval))

    @staticmethod
    def visit_node_plain(self, node):
        self.body.append(node.hexval("#"))

    @classmethod
    def get_visitors(cls):
        return {
            "html": (cls.visit_node_html, depart_node_noop),
            "latex": (cls.visit_node_latex, depart_node_noop),
            "man": (cls.visit_node_plain, depart_node_noop),
            "texinfo": (visit_node_unsupported, None),
            "text": (cls.visit_node_plain, depart_node_noop),
        }


class ColorBoxNode(CBoxNode):
    @staticmethod
    def visit_node_html(self, node):
        CBoxNode.visit_node_html(self, node)
        self.body.append(f'<code class="colorboxvalue hex literal">{node.hexval("#")}</code>')

    @staticmethod
    def visit_node_latex(self, node):
        CBoxNode.visit_node_latex(self, node)
        self.body.append("\\begin{ptinlbox}[]{\\#%s}\\end{ptinlbox}" % (node.hexval("#")))


class LabeledColorBoxNode(ColorBoxNode):
    def label(self) -> str:
        return self["label"]

    @staticmethod
    def visit_node_html(self, node):
        if label := node.label():
            self.body.append(f'<span class="colorboxlabel literal">{label}</span> ')
        ColorBoxNode.visit_node_html(self, node)

    @staticmethod
    def visit_node_latex(self, node):
        if label := node.label():
            self.body.append("\\emph{%s}\\space" % label)
        ColorBoxNode.visit_node_latex(self, node)


# -------------------------------------------------------------------------

class IconNode(nodes.General, nodes.Element):
    icon_name = None
    plain_icon = ""

    @staticmethod
    def visit_node_html(self, node):
        # self.body.insert(-3, f'<i class="fa fa-{node.icon_name}"></i>')
        self.body.append(f'<i class="fa fa-{node.icon_name}"></i>&nbsp;')

    @staticmethod
    def visit_node_latex(self, node):
        self.body.append(f"\\faicon{{{node.icon_name}}}\\space")

    @staticmethod
    def visit_node_plain(self, node):
        self.body.append(node.plain_icon)

    @classmethod
    def get_visitors(cls):
        return {
            "html": (cls.visit_node_html, depart_node_noop),
            "latex": (cls.visit_node_latex, depart_node_noop),
            "man": (cls.visit_node_plain, depart_node_noop),
            "texinfo": (visit_node_unsupported, None),
            "text": (cls.visit_node_plain, depart_node_noop),
        }


class OptionIconNode(IconNode):
    icon_name = "gears"
    plain_icon = "@"

class EnvVarIconNode(IconNode):
    icon_name = "wrench"
    plain_icon = "$"

ICON_NODES = [
    OptionIconNode,
    EnvVarIconNode,
]


def _patch_add_icon(node_cls: type[IconNode], elem_classes: tuple[type[SphinxRole | Directive], ...]):
    def result_nodes_patched(origin: callable):
        def result_nodes(*args, **kwargs) -> list[Node] | tuple[list[Node], list]:
            result = origin(*args, **kwargs)
            nodes = result[0]

            try:
                format = args[1].app.builder.format
            except:
                format = None

            if format == 'html':
                nodes.append(node_cls())
            else:
                nodes.insert(0, node_cls())
            return result
        return result_nodes

    for cls in elem_classes:
        if hasattr(cls, 'result_nodes'):
            cls.result_nodes = result_nodes_patched(cls.result_nodes)

# -------------------------------------------------------------------------

def setup(app: Sphinx):
    app.add_role('ansi', AnsiRole(), override=True)

    app.add_role('cbox', CBoxRole())
    app.add_role('colorbox', ColorBoxRole())
    app.add_role('lcolorbox', LabeledColorBoxRole())
    app.add_node(CBoxNode, **CBoxNode.get_visitors())
    app.add_node(ColorBoxNode, **ColorBoxNode.get_visitors())
    app.add_node(LabeledColorBoxNode, **LabeledColorBoxNode.get_visitors())

    for icon_node_cls in ICON_NODES:
        app.add_node(icon_node_cls, **icon_node_cls.get_visitors())
    _patch_add_icon(OptionIconNode, (OptionXRefRole, Cmdoption))
    _patch_add_icon(EnvVarIconNode, (EnvVarXRefRole, EnvVar))
