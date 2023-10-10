# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
import datetime
import os
import sys

import yaml
from docs.conf_extras import read_x, latex_elements

# -- Path setup ---------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

# sys.path.insert(0, os.path.abspath("/usr/bin/python3.8"))
sys.path.insert(0, os.path.abspath(".."))
root_doc = "pages/index"

# -- Project information ------------------------------------------------------

project = "pytermor"
copyright = f"2022-{datetime.date.today().year}, A. Shavykin"
author = "Alexandr Shavykin"
show_authors = True
# language = "ru"

github_repository = "pytermor"
github_branch = "master"

from pytermor import __version__

version = __version__
release = version

# -- General configuration ----------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.todo",
    "sphinx.ext.autosummary",
    "sphinx.ext.extlinks",
    "sphinx.ext.viewcode",
    "sphinx.ext.inheritance_diagram",
    "sphinx.ext.graphviz",
    "sphinx.ext.doctest",  # replaced with sybil
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx_design",  # <<<MAKE_DOCS_MAN<<<
    "sphinx.ext.imgmath",
    #"sphinx_toolbox.more_autodoc.regex",
    #"sphinx_toolbox.more_autodoc.overloads",
    # "sphinx_toolbox.more_autodoc.generic_bases",
    #"sphinx_toolbox.more_autodoc.typehints",
    #"sphinx_toolbox.more_autodoc.typevars",
    #"sphinxext-opengraph", # @TODO
]
# sphinx-design breaks building docs in man format, so `make` comments that
# line before building it and uncomments it afterwards (yeah I know it's ugly)

rst_prolog = read_x('_prolog.rsti')
default_role = 'any'

templates_path = ["_templates"]
exclude_patterns = [
    "_build",
    "_static",
    ".static.sources",
    "examples",
    "_generated",
    "demo",
    "_include",
]

# smartquotes = False  # breaks at custom directive "textcolor"

# -- HTML ---------------------------------------------------------------------

# html_theme = 'alabaster'  # alibabaster f[f[f[
html_theme = "furo"
html_title = ("<br>" if len(version) > 5 else "").join([project, version])
#html_baseurl = "https://pwk.local/pt"
html_copy_source = False
html_last_updated_fmt = '%d %b %Y'

html_static_path = ["_static"]
html_css_files = [
    "color.css",
    "custom.css",
    "custom-furo.css",
    "hint.css",
    "fork-awesome-1.2.0.min.css",
]
html_js_files = ["custom.js"]
html_favicon = "_static/logo-96.svg"
html_logo = "_static/logo-96.svg"

html_theme_options = yaml.safe_load(read_x('html_theme_options.yml'))

pygments_style = "tango"
pygments_dark_style = "github-dark"

from docs.conf_extras import tracer_dump_lexer


copybutton_prompt_text = ">>> "

imgmath_image_format = "png"
imgmath_font_size = 14
imgmath_add_tooltips = False
imgmath_embed = True
imgmath_use_preview = True

# -- LaTeX / PDF --------------------------------------------------------------

latex_logo = "_static/logo-96.png"
#latex_show_urls = "footnote"

# noinspection SpellCheckingInspection
latex_elements = latex_elements.get()

image_converter_args=["-density", "80"]

# -- autodoc ------------------------------------------------------------------

# from sphinx.application import Sphinx  # noqa E402
#
# def setup(app: Sphinx):
#     app.connect('autodoc-skip-member', autodoc_skip_member)
#
# def autodoc_skip_member(app, what, name, obj, skip, options):
#     if what == 'class' and name.startswith('__'):
#         print(what, name, obj, skip, options)

autodoc_typehints_format = 'short'
autodoc_default_options = {
    "members": True,
    # 'undoc-members': True,
    "inherited-members": True,
    # 'private-members': True,
    "show-inheritance": True,
    # "special-members": "__call__",
    "member-order": "bysource",
    # 'member-order': 'groupwise',
}

# class pytermor.Colors.Color(hex_value.. -> class Color(..
# add_module_names = False

# include signature in the class desc or document __init__ separately
autodoc_class_signature = "mixed"  # 'separated'

autoclass_content = "both"  # "class" "init"

# doctest_test_doctest_blocks = 'True'

# static set_up(force_styles: bool | None = False, compatibility_indexed: bool.. ->
# static set_up(force_styles=False, compatibility_indexed=False, compatibility_default..
#
# but "assemble() → str" becomes:
# assemble()
#   Build up actual byte sequence and return as an ASCII-assembled string.
#     RETURN TYPE:
#       str
# autodoc_typehints = 'both'
# autodoc_typehints = 'signature'
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented_params"
# autodoc_typehints_description_target = "all"
# autodoc_inherit_docstrings =

autodoc_type_aliases = {
    # "CT": "pytermor.color.CT",
    # "RT": "pytermor.text.RT",
    # "FT": "pytermor.style.FT",
    # "IT": "pytermor.utilstr.IT",
    # "OT": "pytermor.utilstr.OT",
}

keep_warnings = True

nitpicky = True
nitpick_ignore = []

for line in read_x('nitpick-exceptions').splitlines():
    if (line := line.strip()) == "" or line.startswith("#"):
        continue
    dtype, target = line.split(None, 1)
    target = target.strip()
    nitpick_ignore.append((dtype, target))

# -- autosummary ------------------------------------------------------------------

autosummary_generate = True

# -- doctest ------------------------------------------------------------------
# disabled due to clashing with pytest/sybil

# doctest_path = [os.path.abspath("..")]
# doctest_global_setup = """
# import pytermor
# pytermor.RendererManager.set_default_format_always()
# """

# -- intersphinx  -------------------------------------------------------------

intersphinx_mapping = {"python": ("https://docs.python.org/3.8", None)}
intersphinx_disabled_reftypes = ["*"]  # 'py:*'

# -- graphviz -----------------------------------------------------------------

# graphviz_output_format = "svg"
graphviz_output_format = "png"

graphviz_dot_args = ["-Gbgcolor=transparent"] # "-Nfontname=ASM-Bold"

# -- Inheritance graph --------------------------------------------------------

inheritance_graph_attrs = dict(
    rankdir="LR",
    size='"8,5"',
    fontsize=12,
    ratio="compress",
    splines="line",
)
inheritance_node_attrs = dict(fontname='"Pragmasevka"')
inheritance_edge_attrs = dict(
    arrowsize=0.5,
    style='"setlinewidth(0.5)"',
    fillcolor="white",
    headport="w",
)

# limit members with specified module and list of allowed ascendants
from sphinx.ext.inheritance_diagram import InheritanceGraph
from docs.conf_extras.inheritance_limit import class_info_patched

# noinspection PyProtectedMember
# ikr
InheritanceGraph._class_info = class_info_patched(InheritanceGraph._class_info)

# -- Misc ---------------------------------------------------------------------

# modindex_common_prefix = ['pytermor']

todo_include_todos = True
# todo_emit_warnings = True
# .. todolist:: ## todo_link_only = True/FALSE


# -- Hide "bases: object" elements --------------------------------------------

from sphinx.ext.autodoc import ClassDocumenter
from docs.conf_extras.hide_object_base import add_directive_header_no_object_base

ClassDocumenter.add_directive_header = add_directive_header_no_object_base

# ---------------------------------------------------------------------------------------


def setup(app):
    # mark index docfile as always outdated, forces static files (e.g. CSS) update:
    app.connect("env-get-outdated", lambda *args: ["index"])
