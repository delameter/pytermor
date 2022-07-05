.. _guide.color-palette:

.. default-role:: any

============================
Color palette
============================

Actual colors of ``default`` palette depend on user's terminal settings, i.e.
the result color of ``ColorDefault`` is not guaranteed to exactly match the
corresponding color in the list below.

However, usually that's not an issue, because users expect their terminal
theme to work (almost) everythere and will be surprised when the application
forcefully override default colors with custom ones (in any case, that can be
accomplished by using `ColorRGB` or ``ColorIndexed``; their color values are
hard to customize without special configurations; but it's recommended not to
use them for regular output).

Note that ``default`` palette is actually a part of *indexed* one (the first 16
colors of 256-color table).

.. only:: html

   .. raw:: html
      :file: ../_include/xterm-colors-256-p.html

.. only:: latex

   .. figure:: ../_include/xterm-colors-256-p.png
      :align: center

      *Indexed* mode palette


-----

.. rubric:: Sources

1. https://www.tweaking4all.com/software/linux-software/xterm-color-cheat-sheet/
