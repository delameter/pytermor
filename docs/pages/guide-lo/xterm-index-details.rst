.. _guide.xterm-index-details:

#####################################
:term:`xterm` indexed colors
#####################################

.. _guide.color16-256-equiv:

---------------------------------
Color16 and Color256 equivalents
---------------------------------

:class:`~color.Color16` palette consists of 16 base colors which are listed
below. At the same time, they are part of :class:`~color.Color256` palette
(the first 16 ones). Actual colors of `Color16` palette depend on user's
terminal settings, i.e. the result color of `Color16` is not guaranteed to
exactly match the corresponding color. That's why using this color type is
discouraged, if you want to be sure that the result will match the expectations.

However, it doesn't mean that ``Color16`` is useless. Just the opposite -- it's
ideal for situations when you don't actually **need** to set exact values and
it's easier to specify estimation of desired color. I.e. setting color to ``'red'``
is usually more than enough for displaying an error message -- we don't really care
about precise values of hue or brightness that will be used to display it.

The instances of ``Color256`` with an exact ``Color16`` counterpart have a private
property ``_color16_equiv``, which is used to determine the result of comparison
between two colors -- i.e., ``==`` opeartor will return *True* for pairs of
equivalent colors:

    >>> col1, col2 = pt.Color256.get_by_code(1), pt.Color16.get_by_code(31)
    (<Color256[x1(#800000? maroon)]>, <Color16[c31(#800000? red)]>)
    >>> col1 == col2
    True

At the same time, colors which share the color value, but behave differently due
to equivalence mechanics are considered different:

    >>> col1, col2 = pt.Color256.get_by_code(9), pt.Color256.get_by_code(196)
    (<Color256[x9(#ff0000? red)]>, <Color256[x196(#ff0000 red-1)]>)
    >>> col1 == col2
    False

.. _guide.approximation:

---------------------------------
Approximation algorithm
---------------------------------

The approximation algorithm was explicitly made to ignore these colors because
otherwise the results of transforming `RGB` values into e.g. ``Color256``, would
be unpredictable, in addition to different results for different users, depending
on their terminal emulator setup.

.. todo ::

   Approximation algorithm is as simple as iterating through all colors in the
   *lookup table* (which contains all possible ...

.. _guide.xterm-256-palette:

---------------------------------
:term:`xterm-256` palette
---------------------------------

.. only:: html

   .. raw:: html
      :file: ../../_generated/color-palette/output.html

.. only:: latex

   .. figure:: /_generated/color-palette/output.png
      :align: center

      `Color256` mode palette

-----

.. rubric:: Sources

1. https://www.tweaking4all.com/software/linux-software/xterm-color-cheat-sheet/
