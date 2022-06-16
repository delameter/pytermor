.. _guide.xterm-colors:

.. default-role:: any

==========================
XTerm Colors
==========================

There are two types of color palettes used in modern terminals -- first one, containing 16 colors (library references
that palette as *default*, see `ColorDefault`), and second one, containing 256 colors (referenced as *indexed*,
e.g. `ColorIndexed`).


Actual colors of *default* palette depend on user's terminal settings, i.e. the result color of ``ColorDefault``
is not guaranteed to exactly match the corresponding color in the list below. However, usually that's not an issue,
because users expect their terminal theme to work (almost) everythere and will be surprised when the application
forcefully override default colors with custom ones (in any case, that can be accomplished by using `ColorRGB` or
`ColorIndexed`; their color values are hard to customize without special configurations; but it's recommended not
to use them for regular output).

*Default* mode table
====================

.. only:: html

   .. raw:: html
      :file: ../_include/xterm-colors-16-t.html

.. only:: latex

   .. include:: ../_include/xterm-colors-16-t.rst


*Indexed* mode palette
======================

.. only:: html

   .. raw:: html
      :file: ../_include/xterm-colors-256-p.html

.. only:: latex

   .. image:: ../_include/xterm-colors-256-p.png
      :align: center

.. note::

   First 16 colors are effectively the same as colors in *default* 16-color mode and share with them the same
   color values (i.e. are also terminal-settings-dependant).


*Indexed* mode table
====================

.. only:: html

   .. raw:: html
      :file: ../_include/xterm-colors-256-t.html

.. only:: latex

   .. include:: ../_include/xterm-colors-256-t.rst


-----

.. rubric:: Sources

1. https://www.tweaking4all.com/software/linux-software/xterm-color-cheat-sheet/
2. https://www.ditig.com/256-colors-cheat-sheet
