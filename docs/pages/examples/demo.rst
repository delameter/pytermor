.. _examples.demo:

#################
     Demo
#################

.. highlight:: bash

There are several predefined examples made specifically for the demonstration
of library's features located in ``examples`` directory. Use `second installation
method <install.demo>` to obtain them along with the library source code.
Command for running any example looks like this: :code:`./run-cli examples/<FILENAME>`


.. _examples.demo.approximate:

-----------------------------------
approximate.py
-----------------------------------

Script for finding the closest color to the specified one, in three color palettes:
xterm-16, xterm-256, named colors. The library is using CIE76 ΔE\* formula in
LAB color space as a default color difference computation algorithm.

:Usage:
    .. code-block::

        ./run-cli examples/approximate.py [-e[e…]] [-R|-H] [COLOR...]

:Arguments:

    Any amount of **COLOR**\ (s) can be specified as arguments, and they will be
    approximated instead of the default (random) one. Required format is a string
    1-6 characters long representing an integer(s) in a hexadecimal form: :hex:`FFFFFF`
    (case insensitive), or a name of the color in any format.

:Options:

   -e    Increase results amount (can be used multiple times).
   -R    Compute color difference using RGB euclidean distance formula.
   -H    Compute color difference using HSV euclidean distance formula.

:Examples:

    .. code-block::

        ./run-cli examples/approximate.py 3AEBA1 0bceeb 666
        ./run-cli examples/approximate.py red DARK_RED icathian-yellow

    .. container:: fullwidthimage

        .. image:: /_generated/term-output/example001.png
           :width: 100%
           :align: center
           :class: no-scaled-link

.. _examples.demo.autopick_fg:

-----------------------------------
autopick_fg.py
-----------------------------------

Script demonstrating auto selection of foreground color depending on a specified
background color defined as :meth:`.Style.autopick_fg()`. No arguments of options.

The details on color selection algorithm can be found at `guide.styles.autopick_fg`.

:Usage:
    .. code-block::

        ./run-cli examples/autopick_fg.py

:Examples:
    .. container:: fullwidthimage

        .. image:: /_generated/term-output/example008.png
          :width: 100%
          :align: center
          :class: no-scaled-link

-----------------------------------
list_named_rgb.py
-----------------------------------

Example script printing all colors in named colors collection (`ColorRGB`
registry), as a list or as a grid. Each cell in grid mode contains different
set of data depending on its size: color number, color hex value, color name,
all of these together (if big enough) or none at all (for very small ones).

The colors in either of modes are sorted using multi-level criteria in HSV color
space, which can be described in a simpler way as follows:

    - make 18 big groups of colors with more or less similar hue, and also
      one extra group for colors without a hue (i.e. colors with zero saturation);
    - in each "hue group" make 5 more groups of colors separated by
      saturation value (19*5=95 groups total);
    - in each "saturation group" sort colors by value (or, roughly speaking,
      brightness) forming 19*5*20=1900 groups total; these actually can hardly
      be named as "groups", as almost every one contains only one color;
    - in each smallest group sort the colors by exact hue value; if they match,
      compare the exact saturation value; if they match, compare the exact value
      value (...);
    - the colors should be deterministically sorted by now, as there are no
      colors with exactly the same H, S an V values (these would be the
      duplicates, which is prohibited by `Color` registries).

"Saturation groups" are clearly visible if the cells are small enough to allow
the script to fit all the colors in a terminal window at once (here size of each
cell is exactly 1x1 character, while the terminal width is set to 160 characters):

.. container:: fullwidthimage

    .. image:: /_generated/term-output/example007.png
      :width: 100%
      :align: center
      :class: no-scaled-link

:Usage:
    .. code-block::

        ./run-cli examples/list_named_rgb.py [MODE [CELL_SIZE [CELL_HEIGHT]]]

:Arguments:

    :MODE:          Either "list" or "grid".
    :CELL_SIZE:     (grid only) Cell width, in characters. Also determines cell
                    height if ``CELL_HEIGHT`` is not provided: the result height
                    will be equal to cell width divided by 2, rounded down.
    :CELL_HEIGHT:   (grid only) Cell height, in characters.

:Examples:
    .. code-block::

        list_named_rgb list
        list_named_rgb grid 2
        list_named_rgb grid 6 3
        list_named_rgb grid 16 6

    .. container:: fullwidthimage

        .. image:: /_generated/term-output/example002.png
          :width: 100%
          :align: center
          :class: no-scaled-link

    .. container:: fullwidthimage

        .. image:: /_generated/term-output/example003.png
          :width: 100%
          :align: center
          :class: no-scaled-link


-----------------------------------
list_renderers.py
-----------------------------------

Print example output of combinations of all the renderers defined in the
library and all possible output modes. No arguments or options. Table width
adjusts for terminal size.

:Usage:
    .. code-block::

        ./run-cli examples/list_renderers.py

-----------------------------------
render_benchmark.py
-----------------------------------

Kind of profiling tool made for measuring how long does it take to render a
colored text using different `IRenderable` implementations. No arguments or
options.

:Usage:
    .. code-block::

        ./run-cli examples/render_benchmark.py

:Examples:
    .. container:: fullwidthimage

        .. image:: /_generated/term-output/example004.png
          :width: 100%
          :align: center
          :class: no-scaled-link

-----------------------------------
terminal_color_mode.py
-----------------------------------

Script made for manual testing of terminal color mode capabilities. No arguments
of options. Run and follow the instructions.

:Usage:
    .. code-block::

        ./run-cli examples/terminal_color_mode.py

:Examples:
    .. container:: fullwidthimage

        .. image:: /_generated/term-output/example005.png
          :width: 100%
          :align: center
          :class: no-scaled-link

-----------------------------------
tone_neighbours.py
-----------------------------------

Script that prints the specified colors along with full spectre of closest
colors with the same hue and value, but different saturation, and with the same
hue and saturation, but different value (≈brightness). The original color and
its RGB derivatives are placed in the middle column, the same colors
approximated to xterm-256 palette are listed in the left column, the same colors
approximated to named colors registry are listed in the right column.

:Usage:
    .. code-block::

        ./run-cli examples/tone_neighbours.py [COLOR...]

:Arguments:

    Any amount of **COLOR**\ (s) can be specified as arguments, and they will be
    approximated instead of the default (random) one. Required format is a string
    1-6 characters long representing an integer(s) in a hexadecimal form:
    :hex:`FFFFFF` (case insensitive). Color names are not supported because the
    main purpose of this script is to find neighbours for the colors that are
    not in the index, not for the indexed ones.

:Examples:

    .. code-block::

        ./run-cli examples/tone_neighbours.py 3AEBA1 0bceeb 666

    .. container:: fullwidthimage

        .. image:: /_generated/term-output/example006.png
           :width: 100%
           :align: center
           :class: no-scaled-link
