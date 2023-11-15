.. _guide.colors:

########################
Colors
########################



====================
Color mode fallbacks
====================

.. only:: html

   .. figure::  /_generated/approx/output-rgb.png
      :width: 400px
      :align: center

      Color approximations for indexed modes
      :comment:`(click to enlarge)`

.. only:: latex

   .. figure::  /_generated/approx/output-rgb.png
      :align: center

      Color approximations for indexed modes


.. _guide.color_class_diagram:

========================================
:fas:`sitemap` Color class hierarchy
========================================


.. grid:: 1
   :class-container: inheritance-columns

   .. grid-item::

      .. inheritance-diagram:: pytermor.color
         :parts: 1
         :top-classes:         pytermor.color.IColorValue,
                               pytermor.color.NamedColor,
                               pytermor.color.IndexedColor,
                               pytermor.color.RenderColor,
                               pytermor.color.ResolvableColor
         :caption:             ``Color`` inheritance diagram
