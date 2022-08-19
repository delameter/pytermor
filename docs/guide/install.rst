.. _guide.install:

.. default-role:: any

===============================
Getting started
===============================

Installation
============

.. code-block:: shell

   pip install pytermor


Structure
===========

.. table::
   :widths: 5 10 15 70

   +-----+----------------------+----------------------+---------------------------------------------------------------------------------+
   | Lvl | Module               | Classes              | Purpose                                                                         |
   +=====+======================+======================+=================================================================================+
   | Hi  | `render`             | `Text`               | Container consisting of text pieces each with attached `Style`.                 |
   |     |                      |                      | Renders into specified format keeping all the formatting.                       |
   |     |                      +----------------------+---------------------------------------------------------------------------------+
   |     |                      | `Style`              | Reusable abstractions defining colors and text attributes (text                 |
   |     |                      |                      | color, bg color, `bold` attribute, `underlined` attribute etc).                 |
   |     |                      +----------------------+---------------------------------------------------------------------------------+
   |     |                      | `*Renderer`          | `SGRRenderer` transforms `Style` instances into `Color`, `Span`                 |
   |     |                      |                      | and `SequenceSGR` instances and assembles it all up. There are                  |
   |     |                      |                      | several other implementations depenging on required output                      |
   |     |                      |                      | format: `HtmlRenderer`, `TmuxRenderer` etc.                                     |
   |     +----------------------+----------------------+---------------------------------------------------------------------------------+
   |     | `color`              | `Color*`             | Abstractions for color operations in different color modes                      |
   |     |                      |                      | (default 16-color, 256-color, RGB). Tools for color approximation               |
   |     |                      |                      | and transformations.                                                            |
   +-----+----------------------+----------------------+---------------------------------------------------------------------------------+
   | Lo  | `ansi`               | `Span`               | Abstraction consisting of "opening" SGR sequence defined by the                 |
   |     |                      |                      | developer (or taken from preset list) and complementary "closing"               |
   |     |                      |                      | SGR sequence that is built automatically.                                       |
   |     |                      +----------------------+---------------------------------------------------------------------------------+
   |     |                      | `SequenceSGR`        | Abstractions for manipulating ANSI control sequences and                        |
   |     |                      |                      | classes-factories.                                                              |
   |     +----------------------+----------------------+---------------------------------------------------------------------------------+
   |     | `intcode`            | \*                   | Registry of escape control sequence parameters.                                 |
   |     +----------------------+----------------------+---------------------------------------------------------------------------------+
   |     | `util`               | \*                   | Additional formatters and common methods for manipulating strings with          |
   |     |                      |                      | SGRs inside.                                                                    |
   +-----+----------------------+----------------------+---------------------------------------------------------------------------------+


Features
========

One of the core concepts of the library is `Span` class. ``Span`` is a combination of two control sequences;
it wraps specified string with pre-defined leading and trailing SGR definitions.

Example code:

.. literalinclude:: /examples/ex_0_features.py
   :linenos:

.. rubric:: Content-aware format nesting

Compose text spans with automatic content-aware span termination. Preset spans can safely overlap with each
other (as long as they require different *breaker* sequences to reset).

.. literalinclude:: /examples/ex_20_content_aware_nesting.py
   :linenos:

.. image:: /_static/ex_10.png
   :width: 50%
   :align: center
   :class: no-scaled-link


.. rubric:: Flexible sequence builder

Create your own `SGR sequences <SequenceSGR>` with `build()` method, which accepts color/attribute keys,
integer codes and even existing *SGRs*, in any amount and in any order. Key resolving is case-insensitive.

.. literalinclude:: /examples/ex_30_flexible.py
   :linenos:


.. rubric:: 256 colors / True Color support

The library supports extended color modes:

- XTerm 256 colors indexed mode (see `presets`);
- True Color RGB mode (16M colors).

.. literalinclude:: /examples/ex_40_ext_colors.py
   :linenos:

.. image:: /_static/ex_40.png
   :width: 50%
   :align: center
   :class: no-scaled-link


.. rubric:: Customizable output formats

@TODO


.. rubric:: String and number formatters

@TODO
