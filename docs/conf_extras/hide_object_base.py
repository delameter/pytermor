# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------

# ClassDocumenter.add_directive_header uses ClassDocumenter.add_line to write the class documentation.
# We'll monkeypatch the add_line method and intercept lines that begin with "Bases:".
# In order to minimize the risk of accidentally intercepting a wrong line, we'll apply this patch inside of the
# add_directive_header method.
# https://stackoverflow.com/a/46284013/5834973

from sphinx.ext.autodoc import ClassDocumenter, _

add_line = ClassDocumenter.add_line
line_to_delete = _("Bases: %s") % ":py:class:`object`"


def add_line_no_object_base(self, text, *args, **kwargs):
    if text.strip() == line_to_delete:
        return
    add_line(self, text, *args, **kwargs)


def add_directive_header_no_object_base(self, *args, **kwargs):
    self.add_line = add_line_no_object_base.__get__(self)
    result = add_directive_header_origin(self, *args, **kwargs)  # noqa
    del self.add_line
    return result


add_directive_header_origin = ClassDocumenter.add_directive_header
