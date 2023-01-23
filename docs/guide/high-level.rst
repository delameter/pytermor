.. _guide.high-level:

==========================
High-level API
==========================

Core methods
================

.. autosummary::

   text.render
   text.echo
   color.resolve_color
   style.make_style
   style.merge_styles


.. grid:: 2
   :class-container: inheritance-columns

   .. grid-item::

      .. inheritance-diagram:: pytermor.color
         :top-classes:         pytermor.color.IColor
         :caption:             `IColor` inheritance tree
         :parts: 1

   .. grid-item::

      .. inheritance-diagram:: pytermor.text
         :top-classes:         pytermor.text.IRenderable
         :caption:             `IRenderable` inheritance tree
         :parts: 1


Colors
================

Styles
================

Output format control
=====================

Color mode fallbacks
====================

.. only:: html

   .. figure:: /_generated/approx/output-bgwhite.png
      :width: 400px
      :align: center

      Color approximations for indexed modes
      :comment:`(click to enlarge)`

.. only:: latex

   .. figure:: /_generated/approx/output-bgwhite.png
      :align: center

      Color approximations for indexed modes

