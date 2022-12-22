.. _guide.high-level:

==========================
High-level abstractions
==========================

:mono:`ColorIndex` and :mono:`Styles`
=======================================

Output format control
=====================

Color mode fallbacks
====================

.. only:: html

   .. figure:: /_generated/approx/output-bgwhite.png
      :width: 400px
      :align: center

      Color approximations for indexed modes
      *(click to enlarge)*

.. only:: latex

   .. figure:: /_generated/approx/output-bgwhite.png
      :align: center

      Color approximations for indexed modes


Class hierarchy
=================

.. inheritance-diagram::
                  pytermor.color.Color16
                  pytermor.color.Color256
                  pytermor.color.ColorRGB
   :top-classes:  pytermor.color.Color
   :parts: 2

.. inheritance-diagram::
                  pytermor.text.Text
                  pytermor.text.FixedString
   :top-classes:  pytermor.text.Renderable
   :caption:      High-level components inheritance
   :parts: 2



Core API
=============

