
.. _index:

.. title:: pytermor

:hide-toc:

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

No dependencies required, only Python Standard Library :comment:`(although there
are some for testing and docs building).`

The library is extendable and supports a variety of formatters (called
`renderers<guide.renderers>`), which determine the output syntax:

- `SgrRenderer`, global default; formats the text with ANSI escape sequences for
  terminal emulators;
- `TmuxRenderer`, suitable for integration with tmux (terminal multiplexer);
- `HtmlRenderer`, which makes a HTML page with all the formatting composed by
  CSS styles;
- `SgrDebugger`, same as ``SgrRenderer``, but control bytes are replaced with a
  regular letter, therefore all the sequences are no longer sequences and can be
  seen as a text, for SGR debugging;
- etc.

.. only:: html

   .. grid:: 3
      :gutter: 1
      :class-container: intro

      .. grid-item-card::
         :link-type: ref
         :link:      install

         `install`

      .. grid-item-card::

         :ref:`features`

      .. grid-item-card::

         :ref:`examples`


      .. grid-item-card::

         :ref:`guide.core-api-1`

         *high abstraction level*

      .. grid-item-card::

         :ref:`guide.core-api-2`

         *low abstraction level*

      .. grid-item-card::

         :ref:`API docs <apidoc>`

         *complete API reference*

      .. grid-item-card::

         :ref:`Package tree <package_graph>`

         *internal imports graph*

      .. grid-item-card::

         :ref:`changes`

         *release history*

      .. grid-item-card::

         :ref:`genindex`

         *all functions, classes, terms*

   .. rubric:: Contents

.. toctree::
   :caption: Introduction

   install
   features
   examples/index

.. toctree::
   :caption: Documentation
   :maxdepth: 2

   guide-hi/index
   guide-lo/index
   apidoc
   config
   appendix/index

.. toctree::
   :caption: Development
   :maxdepth: 2

   changes
   license
   docs-guidelines
