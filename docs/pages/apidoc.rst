.. _apidoc:

###################
API reference
###################

Almost all public classes are imported into the first package level
on its initialization, which makes kind of a contract on library's API.
The exceptions include some abstract superclasses or metaclasses, which
generally should not be used outside of the library, but still can be
imported directly using a full module path.

.. _package_graph:

.. only:: html

   .. graphviz:: /_generated/package-tree-dark.dot
      :class: graphviz-dark

   .. graphviz:: /_generated/package-tree-default.dot
      :class: graphviz-default
      :caption: Package internal imports graph [#]_

   .. [#] Overly common modules (``exception``, ``log``, ``config`` and ``common`` itself) are not shown, as they turn the graph into a mess. Same applies to internal modules which name starts with ``_``. ``border`` module is not shown because it does not import any other module and is not imported either.

.. only:: latex

   .. graphviz:: /_generated/package-tree-pdf.dot
      :caption: Package internal imports graph [#]_

   .. [#] Overly common modules (``exception``, ``log``, ``config`` and ``common`` itself) are not shown, as they turn the graph into a mess. Same applies to internal modules which name starts with ``_``. ``border`` module is not shown because it does not import any other module and is not imported either.

.. automodule:: pytermor

.. .. @autosummary/start

.. autosummary::
   :toctree:    apidoc

   ansi
   border
   color
   common
   config
   cval
   exception
   filter
   numfmt
   renderer
   style
   template
   term
   text

.. .. @autosummary/end
