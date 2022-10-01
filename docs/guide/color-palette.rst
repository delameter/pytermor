.. _guide.color-palette:

.. default-role:: any

============================
Color palette
============================

Actual colors of *default* palette depend on user's terminal settings, i.e.
the result color of `ColorIndexed16` is not guaranteed to exactly match the
corresponding color listed below. What's more, note that *default* palette
is actually a part of *indexed* one (first 16 colors of 256-color table).

.. todo::

   **(Verify)** The approximation algomanrithm was explicitly made to ignore these colors because
   otherwise the results of transforming *RGB* values into *indexed* ones would be
   unpredictable, in addition to different results for different users, depending
   on their terminal emulator setup.

However, it doesn't mean that `ColorIndexed16` is useless. Just the opposite -- it's
ideal for situtations when you don't actually **have to** set exact values and
it's easier to specify estimation of desired color. I.e. setting color to ``'red'``
is usually more than enough for displaying an error message -- we don't really care
of precise hue or brightness values for it.

.. todo ::

   Approximation algorithm is as simple as iterating through all colors in the
   *lookup table* (which contains all possible ...

-----

.. only:: html

   .. raw:: html
      :file: ../_generated/color-palette/output.html

.. only:: latex

   .. figure:: /_generated/color-palette/output.png
      :align: center

      *Indexed* mode palette


-----

.. rubric:: Sources

1. https://www.tweaking4all.com/software/linux-software/xterm-color-cheat-sheet/
