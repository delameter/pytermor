.. _index:

.. default-role:: any

.. title:: pytermor

=====================
pytermor
=====================

*(yet another)* Python library designed for formatting terminal output using ANSI escape codes. Implements automatic `"soft" <guide.low-level>` format termination. Provides a registry of low-level :abbr:`SGR (Select Graphic Rendition)` `sequences<SequenceSGR>` and formatting `spans <Span>` (or combined sequences). Also includes a set of formatters for pretty output.

Key feature of this library is providing necessary abstractions for building complex text sections with lots of formatting, while keeping the application code clear and readable.

.. only :: html

   .. grid:: 2
      :gutter: 1
      :class-container: intro

      .. grid-item-card::

         :ref:`guide.index`

         .. line-block::

            in-depth review with examples

      .. grid-item-card::

         :ref:`apidoc.index`

         *complete API reference*

      .. grid-item-card::

         :ref:`changes`

         *release history*

      .. grid-item-card::

         :ref:`genindex`

         *all functions, classes, terms*


.. toctree::
   :maxdepth: 3
   :hidden:

   guide/index
   apidoc/index
   changes
   license
