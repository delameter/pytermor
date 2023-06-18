.. _structure:

#####################
Library structure
#####################

.. only:: latex

   .. graphviz:: /_generated/module.dot
      :caption: Module dependency graph [#]_

   .. [#] Overly common modules (``exception``, ``log``, ``config`` and ``common`` itself) are not shown, as they turn the graph into a mess. Same applies to internal modules which name starts with ``_``.


.. only:: html

   .. graphviz:: /_generated/module.dot
      :caption: Module dependency graph [#]_


   .. [#] Overly common modules (``exception``, ``log``, ``config`` and ``common`` itself) are not shown, as they turn the graph into a mess. Same applies to internal modules which name starts with ``_``.


.. autosummary::

   ansi
   color
   common
   config
   conv
   cval
   exception
   filter
   log
   numfmt
   parser
   renderer
   style
   template
   term
   text
