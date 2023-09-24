.. _structure:

#####################
Library structure
#####################

.. only:: html

   .. graphviz:: /_generated/module-dark.dot
      :class: graphviz-dark

   .. graphviz:: /_generated/module_legend-dark.dot
      :class: graphviz-dark

   .. graphviz:: /_generated/module-default.dot
      :class: graphviz-default

   .. graphviz:: /_generated/module_legend-default.dot
      :class: graphviz-default
      :caption: Module dependency graph [#]_

   .. [#] Overly common modules (``exception``, ``log``, ``config`` and ``common`` itself) are not shown, as they turn the graph into a mess. Same applies to internal modules which name starts with ``_``.


.. autosummary::

   ansi
   color
   common
   config
   cval
   exception
   filter
   log
   numfmt
   renderer
   style
   template
   term
   text


.. only:: latex

   .. graphviz:: /_generated/module-pdf.dot

   .. graphviz:: /_generated/module_legend-pdf.dot
      :caption: Module dependency graph [#]_

   .. [#] Overly common modules (``exception``, ``log``, ``config`` and ``common`` itself) are not shown, as they turn the graph into a mess. Same applies to internal modules which name starts with ``_``.
