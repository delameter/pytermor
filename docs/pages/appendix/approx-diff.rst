.. _appendix.approx-diff:

#####################################
     Approximation differences
#####################################

.. |origin| replace:: Full RGB color cube and its' slice.
.. |color16| replace:: Cube approximation to `Color16` palette.
.. |color256| replace:: Cube approximation to `Color256` palette.
.. |colorrgb| replace:: Cube approximation to `ColorRGB` list.


.. only:: html

    .. sidebar::

        .. figure::  /_static/approx-origin.png
          :align: center
          :scale: 75%
          :width: 800px

          |origin|


.. only:: latex

    .. figure::  /_static/approx-origin-pdf.png
      :align: center
      :scale: 75%

      |origin|


To demonstrate the difference between various approximation formulas we will
use a RGB color cube sliced by R and B axes for better observability. There
is a few color spaces implemented in the library, namely `RGB`, `HSV`, `LAB`
and `XYZ`. Each of these also provides `diff()` class method which takes two
`IColorValue` instances and returns a "distance" between them, i.e. the number
representing how close is first color to the second. Zero distance means that
colors are identical.

.. note::

    Color distances can be compared only in a context of single color space,
    i.e. distance 100 in `HSV` space is not the same as distance
    100 in `LAB` space. Probably they should be named *relative*
    distances, but that would assume that some normalizing is done, and
    thus one may except that unit of measurement would be a ratio, whereas
    that's not the case.

.. only:: html

    .. figure::  /_static/approx-color16.png
      :align: center
      :scale: 75%
      :width: 800px

      |color16|


.. only:: latex

    .. figure::  /_static/approx-color16-pdf.png
      :align: center
      :scale: 75%

      |color16|

First let's examine the results of approximation RGB cube to `Color16` palette.
Because the palette is very limited, the results look robust and, in fact, they
are. There is just not much choice for the algorithm.

Notice that there is no green color at the leftmost picture above; the reason for
that is the fact that `RGB.diff()` thinks that e.g. :colorbox:`#80ff80`
is closer to :colorbox:`white`  color than to :colorbox:`green` color:

 .. math:: \Delta_r = \sqrt{ (R_2 - R_1)^2 + (G_2 - G_1)^2 + (B_2 - B_1)^2 },

where :math:`\Delta_r` is RGB distance, which gives:

 .. math::

    \Delta_{rW} = \sqrt{ (128-192)^2 + (255-192)^2 + (128-192)^2 } = \sqrt{ 64^2 + 63^2 + 64^2 } = 110.28,

    \Delta_{rG} = \sqrt{ (128-0)^2 + (255-128)^2 + (128-0)^2 } = \sqrt{ 128^2 + 127^2 + 128^2 } = 221.13,

which explains the absense of the former in the cube slice approximation. Let's prove our calculations:

    >>> from pytermor import RGB
    >>> RGB.diff(RGB(0x80ff80), RGB(0xc0c0c0))
    110.27692415006868
    >>> RGB.diff(RGB(0x80ff80), RGB(0x008000))
    221.12666053644458


.. only:: html

    .. figure::  /_static/approx-color256.png
      :align: center
      :scale: 75%
      :width: 800px

      |color256|


.. only:: latex

    .. figure::  /_static/approx-color256-pdf.png
      :align: center
      :scale: 75%

      |color256|



.. only:: html

    .. figure::  /_static/approx-colorrgb.png
      :align: center
      :scale: 75%
      :width: 800px

      |colorrgb|



.. only:: latex

    .. figure::  /_static/approx-colorrgb-pdf.png
      :align: center
      :scale: 75%

      |colorrgb|
