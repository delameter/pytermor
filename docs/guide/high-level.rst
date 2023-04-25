.. _guide.high-level:

##########################
High-level core API
##########################

.. rubric:: Glossary
.. glossary::

   rendering
      A process of transforming text-describing instances into specified
      output format, e.g. instance of `Fragment` class with content and
      :py:class:`.Style` class containing colors and other text formatting can be
      rendered into terminal-compatible string with `SgrRenderer`, or into
      HTML markup with `HtmlRenderer`, etc.

   style
      Class describing text format options: text color, background color,
      boldness, underlining, etc. Styles can be inherited and merged
      with each other. See :py:class:`.Style` constructor description for the details.

   color
      Three different classes describing the color options: `Color16`, `Color256`
      and `ColorRGB`. The first one corresponds to 16-color terminal mode, the
      second -- to 256-color mode, and the last one represents full RGB color
      space rather than color index palette. The first two also contain terminal
      :term:`SGR` bindings.


================
Core methods
================

.. autosummary::

   text.render
   text.echo
   color.resolve_color
   style.make_style
   style.merge_styles



================
Colors
================

================
Styles
================

=====================
Output format control
=====================

====================
Color mode fallbacks
====================

.. only:: html

   .. figure::   /generated/approx/output-bgwhite.png
      :width: 400px
      :align: center

      Color approximations for indexed modes
      :comment:`(click to enlarge)`

.. only:: latex

   .. figure::   /generated/approx/output-bgwhite.png
      :align: center

      Color approximations for indexed modes


==================
Class hierarchy
==================

.. grid:: 2
   :class-container: inheritance-columns

   .. grid-item::

      .. inheritance-diagram:: pytermor.color
         :top-classes:         pytermor.color.IColor
         :caption:             ``IColor`` inheritance diagram
         :parts: 1

   .. grid-item::

      .. inheritance-diagram:: pytermor.text
         :top-classes:         pytermor.text.IRenderable
         :caption:             `IRenderable` inheritance diagram
         :parts: 1
