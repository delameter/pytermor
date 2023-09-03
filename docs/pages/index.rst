
.. _index:

.. title:: pytermor

#####################
pytermor
#####################

:comment:`(yet another)` Python library initially designed for formatting
terminal output using ANSI escape codes.

Provides `high-level <guide-hi>` methods for working with text sections, colors,
formats, alignment and wrapping, as well as `low-level <guide-lo>` modules which
allow to operate with :term:`ANSI` sequences directly and also implement
automatic format termination. Depending on the context and technical
requirements either approach can be used. Also includes a set of additional
number/string/time formatters for pretty output, filters, templating engine,
escape sequence parser and provides support for several color spaces, which is
also used for fluent color approximation if terminal capabilities do not
allow to work in True Color mode. See `features` page for the details.

Key feature of the library is extendability and a variety of formatters (called
`renderers<guide.renderers>`), which determine the output syntax:

- `SgrRenderer` (global default)
- `TmuxRenderer`
- `HtmlRenderer`
- `SgrDebugger` (mostly for development)
- etc.

No dependencies required, only Python Standard Library :comment:`(although there
are some for testing and docs building).`


.. only:: html

   .. grid:: 3
      :gutter: 1
      :class-container: intro

      .. grid-item-card::

         :ref:`install`

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


.. toctree::
   :caption: Introduction

   install
   features
   structure

.. toctree::
   :caption: Documentation
   :maxdepth: 2

   guide-hi
   guide-lo
   apidoc
   config
   cli

.. toctree::
   :caption: Development
   :maxdepth: 2

   changes
   license
   docs-guidelines
