.. _guide.styles:

########################
Styles
########################

One of the core concepts of the library is a :term:`style`, represented by a
:class:`.Style` class. It provides all possible parameters of the text format and can be
applied to a *str* or any *IRenderable* descendant via `several methods
<guide.renderer_setup>`.

========================
Constructing
========================

...

========================
Inheritance
========================

...

========================
Merging
========================

...

.. _guide.styles.autopick_fg:

========================
Text color auto select
========================

.. default-role:: math

The class provides method :meth:`.Style.autopick_fg()` which can be used after
assigning background color to a style. The result of invoking the method is that
the style in question now will have a foreground color set to complement a
background color, i.e. no matter what bg color is set, the text will always be
readable.

The foreground color is selected from two opposite colors :lcolorbox:`GRAY_0`
and :lcolorbox:`GRAY_100`. The formula is adjusted to ensure that any pair of
(bg, fg) colors has a contrast ratio at least `3:1`, which is a requirement of
WCAG 2.0 level AA standard. [#]_ In fact, the contrast ratio in the current
implementation never goes below `4.5:1` for any bg color.


.. math::
   :nowrap:

    \begin{equation*}
    L_f =
      \begin{cases}
        \begin{aligned}
         & L_{G0},    & L_b & > 0.178           \\
         & L_{G100},  & L_b & \leqslant 0.178
        \end{aligned}
      \end{cases}
    \end{equation*}

where `L_f` is a relative luminance of foreground color, `L_b` is a relative luminance of
background color, and `L_{G0}`, `L_{G100}` are relative luminances of *gray-0* and *gray-100*
colors, respectively. Relative luminance equals to `Y` component of the color in :class:`.XYZ`
space by the definition.

The formula can be interpreted like follows: if bg color is brighter that `17.8\%`, use *gray-0*
color as a foreground; if bg color is darker than `17.8\%`, use *gray-100* instead. The number
which determines the edge for the algorithm was calculated with numerical methods and this value
has the highest minimum contrast ratio across the whole RGB color space (i.e., it can be worse,
but it cannot be better with any other value, increasing it to compensate the bright colors makes
dark colors unreadable, and vice versa).

Contrast ratio `C_{fb}` is calculated as:
`C_{fb} = \dfrac{max(L_b, L_f) + 0.05}{min(L_b, L_f) + 0.05}`, whereas `V_{b}` is :class:`.HSV`
`value` of the bg color listed for the contrast to `L_b`.

   +----------------------+---------+-----------+-------------------+----------+--+---------------------+---------+----------+-----------------+----------+
   | bg color             | `V_b`   | `L_b`     | fg                | `C_{fb}` |  | bg color            | `V_b`   | `L_b`    | fg              | `C_{fb}` |
   +======================+=========+===========+===================+==========+==+=====================+=========+==========+=================+==========+
   | :colorbox:`#333333`  | `20\%`  | `3.3\%`   | :cbox:`gray0`     | `12.6`   |  | :colorbox:`#333300` | `20\%`  | `3.1\%`  | :cbox:`gray0`   | `13.0`   |
   +----------------------+---------+-----------+-------------------+----------+  +---------------------+---------+----------+-----------------+----------+
   | :colorbox:`#666666`  | `40\%`  | `13.3\%`  | :cbox:`gray0`     | `5.7`    |  | :colorbox:`#666600` | `40\%`  | `12.3\%` | :cbox:`gray0`   | `6.1`    |
   +----------------------+---------+-----------+-------------------+----------+  +---------------------+---------+----------+-----------------+----------+
   | :colorbox:`#999999`  | `60\%`  | `31.9\%`  | :cbox:`gray100`   |  `7.4`   |  | :colorbox:`#999900` | `60\%`  | `29.6\%` | :cbox:`gray100` | `6.9`    |
   +----------------------+---------+-----------+-------------------+----------+  +---------------------+---------+----------+-----------------+----------+
   | :colorbox:`#cccccc`  | `80\%`  | `60.4\%`  | :cbox:`gray100`   | `13.1`   |  | :colorbox:`#cccc00` | `80\%`  | `56.0\%` | :cbox:`gray100` | `12.2`   |
   +----------------------+---------+-----------+-------------------+----------+  +---------------------+---------+----------+-----------------+----------+
   | :colorbox:`#ffffff`  | `100\%` | `100\%`   | :cbox:`gray100`   | `21.0`   |  | :colorbox:`#ffff00` | `100\%` | `92.8\%` | :cbox:`gray100` | `19.6`   |
   +----------------------+---------+-----------+-------------------+----------+  +---------------------+---------+----------+-----------------+----------+
   | \                                                                         |  | \                                                                     |
   +----------------------+---------+-----------+-------------------+----------+  +---------------------+---------+----------+-----------------+----------+
   | :colorbox:`#330000`  | `20\%`  | `0.7\%`   | :cbox:`gray0`     | `18.4`   |  | :colorbox:`#000033` | `20\%`  | `0.2\%`  | :cbox:`gray0`   | `20.0`   |
   +----------------------+---------+-----------+-------------------+----------+  +---------------------+---------+----------+-----------------+----------+
   | :colorbox:`#660000`  | `40\%`  | `2.8\%`   | :cbox:`gray0`     | `13.4`   |  | :colorbox:`#000066` | `40\%`  | `1.0\%`  | :cbox:`gray0`   | `17.6`   |
   +----------------------+---------+-----------+-------------------+----------+  +---------------------+---------+----------+-----------------+----------+
   | :colorbox:`#990000`  | `60\%`  | `6.8\%`   | :cbox:`gray0`     | `8.9`    |  | :colorbox:`#000099` | `60\%`  | `2.3\%`  | :cbox:`gray0`   | `14.4`   |
   +----------------------+---------+-----------+-------------------+----------+  +---------------------+---------+----------+-----------------+----------+
   | :colorbox:`#cc0000`  | `80\%`  | `12.8\%`  | :cbox:`gray0`     | `5.9`    |  | :colorbox:`#0000cc` | `80\%`  | `4.4\%`  | :cbox:`gray0`   | `11.2`   |
   +----------------------+---------+-----------+-------------------+----------+  +---------------------+---------+----------+-----------------+----------+
   | :colorbox:`#ff0000`  | `100\%` | `21.3\%`  | :cbox:`gray100`   | `5.3`    |  | :colorbox:`#0000ff` | `100\%` | `7.2\%`  | :cbox:`gray0`   | `8.6`    |
   +----------------------+---------+-----------+-------------------+----------+--+---------------------+---------+----------+-----------------+----------+

Note how the resulting fg color sets differ for each series of 5 colors
with the same hue: there are only two black colors in yellow group, but five of
them are sitting in a blue group, despite the fact that the colors has the same
HSV values. That's what *uniform* color spaces (e.g. LAB, XYZ) were created to
begin with -- to compensate non-linearity of human color perception.

.. default-role:: any

See the demo script `Examples — Demo — autopick_fg.py <examples.demo.autopick_fg>`.

.. [#] https://www.w3.org/TR/2008/REC-WCAG20-20081211 , section 1.4.3
