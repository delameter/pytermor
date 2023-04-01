.. _index:

.. title:: pytermor

#####################
pytermor
#####################

:comment:`(yet another)` Python library initially designed for formatting terminal output using ANSI escape codes.

Provides `high-level <guide.high-level>` methods for working with text sections, colors, formats, alignment and wrapping, as well as `low-level <guide.low-level>` `ansi` module which allows operating with :abbr:`SGR (Select Graphic Rendition)` `sequences<SequenceSGR>` and also implements automatic "soft" format termination. Depending on the context and technical requirements either approach can be used. Also includes a set of additional number/string/date formatters for pretty output.

Key feature of this library is extendability and a variety of formatters (called `renderers<guide.renderers>`), which determine the output syntax:

- `SgrRenderer` (global default)
- `TmuxRenderer`
- `HtmlRenderer`
- `SgrDebugger` (mostly for development)
- etc.

No dependencies required, only Python Standard Library :comment:`(there are some for testing and docs building, though).`


.. only:: html

   .. grid:: 3
      :gutter: 1
      :class-container: intro

      .. grid-item-card::

         :ref:`guide.install`

         *installation, in-depth review*

      .. grid-item-card::

         :ref:`API docs <apidoc>`

         *complete API reference*

      .. grid-item-card::

         :ref:`license`

         *license*

      .. grid-item-card::

         :ref:`Presets <guide.presets>`

         *color and attribute preset list*

      .. grid-item-card::

         :ref:`changes`

         *release history*

      .. grid-item-card::

         :ref:`genindex`

         *all functions, classes, terms*


.. todo ::

   This is how you **should** format examples:

.. figure:: /_static/ex_ex.png

   https://chrisyeh96.github.io/2020/03/28/terminal-colors.html#color-schemes


.. toctree::
   :hidden:

   guide/index
   apidoc
   changes
   license
