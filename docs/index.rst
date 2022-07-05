.. _index:

.. default-role:: any

.. role:: underline
    :class: underline

.. title:: pytermor

=====================
pytermor
=====================

*(yet another)* Python library designed for formatting terminal output using ANSI escape codes. Implements automatic `"soft" <guide.low-level>` format termination. Provides a registry of low-level :abbr:`SGR (Select Graphic Rendition)` `sequences<SequenceSGR>` and formatting `spans <Span>` (or combined sequences). Also includes a set of formatters for pretty output.

Key feature of this library is providing necessary abstractions for building complex text sections with lots of formatting, while keeping the application code clear and readable.

No dependencies besides Python Standard Library are required (there are some for testing and docs building, though).


.. only :: html

   .. table::
      :class: intro
      :widths: 50 50

      +-----------------------------------+----------------------------------+
      | :ref:`guide.index`                | :ref:`apidoc.index`              |
      |                                   |                                  |
      | *in-depth review with examples*   | *complete API reference*         |
      +-----------------------------------+----------------------------------+
      | :ref:`changes`                    | :ref:`genindex`                  |
      |                                   |                                  |
      | *release history*                 | *all functions, classes, terms*  |
      +-----------------------------------+----------------------------------+


``@TODO`` This is how you **should** format examples:

.. figure:: /_static/ex_ex.png

   https://chrisyeh96.github.io/2020/03/28/terminal-colors.html#color-schemes



.. toctree::
   :maxdepth: 3
   :hidden:

   guide/index
   apidoc/index
   changes
   license
