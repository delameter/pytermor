.. _guide.styles:

.. currentmodule:: pytermor.style

########################
Styles
########################

One of the core concepts of the library is a :term:`style`, represented by a
:class:`.Style` class. It provides all possible parameters of the text format
and can be applied to a *str* or any *IRenderable* descendant via `several
methods <guide.renderer_setup>`.


========================
Constructing
========================

The primary method of creating a `Style` is via `make_style()`, which accepts
various argument types:

  - :class:`.Style` or *str*
      Existing style instance, which is returned as is, OR a name of the constant
      defined in `Styles`; if there are no constant with that name found in the class,
      the function assumes that the string is either a hex color value or a color name.

  - `CDT` (*str* or *int*)
      This argument type implies the creation of basic :class:`.Style`
      with the only attribute set being `fg` (i.e., text color). The color
      can be specified as hexadecimal RGB value or a color name in a free form.
      For the details on color resolving see `resolve_color()`.

  - `IColorValue` (`RGB` or `HSV` etc.)
      Color value is also accepted as `fmt` and is used as `fg` color of
      newly created style.

  - *None*
      Return `NOOP_STYLE`.


========================
Inheritance
========================

The secondary method is to use the default :class:`.Style()` class constructor.

    >>> from pytermor import Style
    >>> Style(fg='green', bold=True)
    <Style[green +BOLD]>
    >>> Style(bg=0x0000ff)
    <Style[|#0000ff]>
    >>> Style(fg='DeepSkyBlue1', bg='gray3')
    <Style[x39|x232]>

Attribute merging from ``fallback`` works this way:

  - If constructor argument is *not* empty (*True*, *False*, ``Color``
    etc.), keep it as attribute value.

  - If constructor argument is empty (*None*, ``NOOP_COLOR``), take the
    value from ``fallback``'s corresponding attribute (in case it is empty too
    -- keep it that way).

See `merge_fallback()` and `merge_overwrite()` methods and take the
differences into account. The method used in the constructor is the first one.

.. important::

  Both empty (i.e., *None*) attributes of type ``Color`` after initialization
  will be replaced with special constant `NOOP_COLOR`, which behaves like
  there was no color defined, and at the same time makes it safer to work
  with nullable color-type variables. Merge methods are aware of this and
  treat `NOOP_COLOR` as *None*.

.. attention::

  *None* and `NOOP_COLOR` are always treated as placeholders for fallback
  values, i.e., they can't be used as *resetters* -- that's what `DEFAULT_COLOR`
  is for.


.. _guide.styles.merging:

========================
Merging
========================

There is a support for joining several styles into one, implemented as
`merge_styles()` method, which works this way: first merges `fallbacks`
styles with the ``origin`` in the same order they are provided, using
`merge_fallback()` algorithm; then do the same for `overwrites` styles, but
using `merge_overwrite()` merge method.

.. note::

  The original `origin` is left untouched, as all the operations are performed on
  its clone. To make things clearer the name of the argument differs from the ones
  that are modified in-place (``base`` and ``origin``).

.. code-block::

                                   +-----+                                 +-----+
      >---->---->----->---->------->     >-------(B)-update---------------->     |
      |    |    |     |    |       |     |                                 |  R  |
      |    |    |     |    |       |  B  >=>Ø    [0]>-[1]>-[2]> .. -[n]>   |  E  |
   [0]>-[1]>-[2]>- .. >-[n]>->Ø    |  A  >=>Ø       |    |    |        |   |  S  |
      |    |    >- .. ------->Ø    |  S  >=>Ø       >---(D)-update----->--->  U  |
      |    >-----  .. ------->Ø    |  E  | (C) drop                        |  L  |
      >----------  .. ------->Ø    |     |=================(E)=keep========>  T  |
                            (A)    |     |                                 |     |
              FALLBACKS    drop    +-----+            OVERWRITES           +-----+

The key actions are marked with (**A**) to (**E**) letters. In reality the algorithm
works in slightly different order, but the exact scheme would be less illustrative.


`FALLBACK`
---------------------

:(A),(B):
  Iterate ``fallback`` styles one by one; discard all the attributes of a
  current ``fallback`` style, that are already set in ``origin`` style
  (i.e., that are not *Nones*). Update all ``origin`` style empty attributes
  with corresponding ``fallback`` values, if they exist and are not empty.
  Repeat these steps for the next ``fallback`` in the list, until the list
  is empty.

  .. latex:samepage::

    .. code-block::

               FALLBACK   BASE(SELF)   RESULT
               +-------+   +------+   +------+
      ATTR-1   | False --Ø | True ===>| True |  BASE is in priority
      ATTR-2   | True -----| None |-->| True |  no BASE, taking FALLBACK
      ATTR-3   | None  |   | True ===>| True |  BASE is in priority
      ATTR-4   | None  |   | None |   | None |  no value, keeping unset
               +-------+   +------+   +------+

    >>> from pytermor import merge_styles
    >>> origin = Style(fg='red')
    >>> fallbacks = [Style(fg='blue'), Style(bold=True), Style(bold=False)]
    >>> merge_styles(origin, fallbacks=fallbacks)
    <Style[red +BOLD]>

  In the example above:

      - the first fallback will be ignored, as `fg` is already set;
      - the second fallback will be applied (``origin`` style will now have `bold`
        set to *True*;
      - which will make the handler ignore third fallback completely; if third
        fallback was encountered earlier than the 2nd one, ``origin`` `bold` attribute
        would have been set to *False*, but alas.

  See also: `examples.style-merging`


`OVERWRITE`
-----------------

:(C),(D),(E):
  Iterate ``overwrite`` styles one by one; discard all the attributes of a ``origin``
  style that have a non-empty counterpart in ``overwrite`` style, and put
  corresponding ``overwrite`` attribute values instead of them. Keep ``origin``
  attribute values that have no counterpart in current ``overwrite`` style (i.e.,
  if attribute value is *None*). Then pick next ``overwrite`` style from the input
  list and repeat all these steps.

  .. code-block::

            BASE(SELF)  OVERWRITE    RESULT
             +------+   +-------+   +-------+
    ATTR-1   | True ==Ø | False --->| False |  OVERWRITE is in priority
    ATTR-2   | None |   | True ---->| True  |  OVERWRITE is in priority
    ATTR-3   | True ====| None  |==>| True  |  no OVERWRITE, keeping BASE
    ATTR-4   | None |   | None  |   | None  |  no value, keeping unset
             +------+   +-------+   +-------+

  >>> origin = Style(fg='red')
  >>> overwrites = [Style(fg='blue'), Style(bold=True), Style(bold=False)]
  >>> merge_styles(origin, overwrites=overwrites)
  <Style[blue -BOLD]>

  In the example above all the ``overwrites`` will be applied in order they were
  put into *list*, and the result attribute values are equal to the last
  encountered non-empty values in ``overwrites`` list.

`REPLACE`
------------

For the sake of completeness, the diagram for third merging method looks like this:

  .. code-block::

            BASE(SELF)   REPLACE     RESULT
             +------+   +-------+  +-------+
    ATTR-1   | False =Ø | True --->| True  |  REPLACE is in priority
    ATTR-2   | True ==Ø | False -->| False |  REPLACE is in priority
    ATTR-3   | None |   | False -->| False |  REPLACE is in priority
    ATTR-4   | True ==Ø | None --->| None  |  ..even when it's unset
             +------+   +-------+  +-------+


.. _guide.styles.autopick_fg:

========================
Text color auto select
========================

.. default-role:: math

The class provides method :meth:`.Style.autopick_fg()` which can be used after
assigning background color to a style. The result of invoking the method is that
the style in question now will have a foreground color set to complement a
background color, i.e. no matter what background color is set, the text will
always be readable.

The foreground color is selected from two opposite colors :colorbox:`GRAY_0`
and :colorbox:`GRAY_100`. The formula is adjusted to ensure that any pair of
(bg, fg) colors has a contrast ratio at least `3:1`, which is a requirement of
WCAG 2.0 level AA standard. [#]_ In fact, the contrast ratio in the current
implementation never goes below `4.5:1` for any background color.

.. math::
   :nowrap:

    \begin{equation*}
    L_f =
      \begin{cases}
        \begin{aligned}
         & L_{0},    & L_b & > 0.178           \\
         & L_{100},  & L_b & \leqslant 0.178
        \end{aligned}
      \end{cases},
    \end{equation*}

where `L_f` is a relative luminance of foreground color, `L_b` is a relative luminance of
background color, and `L_{0}`, `L_{100}` are relative luminances of *gray-0* and *gray-100*
colors, respectively. Relative luminance equals to `Y` component of the color in :class:`.XYZ`
space by the definition, which gives us `L_{0} = 0\%` and `L_{100} = 100\%`.

The formula can be interpreted like follows: if background color is brighter than `17.8\%`, use *gray-0*
color as a foreground; if backkground color is darker than `17.8\%`, use *gray-100* instead. The number
which determines the edge for the algorithm was calculated using numerical methods and this value
has the highest minimum contrast ratio across the whole RGB color space (i.e., it can be worse,
but it cannot be better with any other value, increasing it to compensate the bright colors makes
dark colors less readable, and vice versa).

Contrast ratio is calculated as: `C_{fb} = \dfrac{max(L_b, L_f) + 0.05}{min(L_b, L_f) + 0.05}`.

`V_{b}` is :class:`.HSV` *value* of the background color listed for the contrast to `L_b`.

   +----------------------+---------+-----------+-------------------+----------+--+---------------------+---------+----------+-----------------+----------+
   | bg color             | `V_b`   | `L_b`     | fg                | `C_{fb}` |  | bg color            | `V_b`   | `L_b`    | fg              | `C_{fb}` |
   +======================+=========+===========+===================+==========+==+=====================+=========+==========+=================+==========+
   | :colorbox:`#333333`  | `20\%`  | `3.3\%`   | :cbox:`gray100`   | `12.6`   |  | :colorbox:`#003300` | `20\%`  | `2.4\%`  | :cbox:`gray100` | `14.2`   |
   +----------------------+---------+-----------+-------------------+----------+  +---------------------+---------+----------+-----------------+----------+
   | :colorbox:`#666666`  | `40\%`  | `13.3\%`  | :cbox:`gray100`   | `5.7`    |  | :colorbox:`#006600` | `40\%`  | `9.5\%`  | :cbox:`gray100` | `7.3`    |
   +----------------------+---------+-----------+-------------------+----------+  +---------------------+---------+----------+-----------------+----------+
   | :colorbox:`#999999`  | `60\%`  | `31.9\%`  | :cbox:`gray0`     |  `7.4`   |  | :colorbox:`#009900` | `60\%`  | `22.8\%` | :cbox:`gray0`   | `5.5`    |
   +----------------------+---------+-----------+-------------------+----------+  +---------------------+---------+----------+-----------------+----------+
   | :colorbox:`#cccccc`  | `80\%`  | `60.4\%`  | :cbox:`gray0`     | `13.1`   |  | :colorbox:`#00cc00` | `80\%`  | `43.2\%` | :cbox:`gray0`   | `9.6`    |
   +----------------------+---------+-----------+-------------------+----------+  +---------------------+---------+----------+-----------------+----------+
   | :colorbox:`#ffffff`  | `100\%` | `100\%`   | :cbox:`gray0`     | `21.0`   |  | :colorbox:`#00ff00` | `100\%` | `71.5\%` | :cbox:`gray0`   | `15.3`   |
   +----------------------+---------+-----------+-------------------+----------+  +---------------------+---------+----------+-----------------+----------+
   | \                                                                         |  | \                                                                     |
   +----------------------+---------+-----------+-------------------+----------+  +---------------------+---------+----------+-----------------+----------+
   | :colorbox:`#330000`  | `20\%`  | `0.7\%`   | :cbox:`gray100`   | `18.4`   |  | :colorbox:`#000033` | `20\%`  | `0.2\%`  | :cbox:`gray100` | `20.0`   |
   +----------------------+---------+-----------+-------------------+----------+  +---------------------+---------+----------+-----------------+----------+
   | :colorbox:`#660000`  | `40\%`  | `2.8\%`   | :cbox:`gray100`   | `13.4`   |  | :colorbox:`#000066` | `40\%`  | `1.0\%`  | :cbox:`gray100` | `17.6`   |
   +----------------------+---------+-----------+-------------------+----------+  +---------------------+---------+----------+-----------------+----------+
   | :colorbox:`#990000`  | `60\%`  | `6.8\%`   | :cbox:`gray100`   | `8.9`    |  | :colorbox:`#000099` | `60\%`  | `2.3\%`  | :cbox:`gray100` | `14.4`   |
   +----------------------+---------+-----------+-------------------+----------+  +---------------------+---------+----------+-----------------+----------+
   | :colorbox:`#cc0000`  | `80\%`  | `12.8\%`  | :cbox:`gray100`   | `5.9`    |  | :colorbox:`#0000cc` | `80\%`  | `4.4\%`  | :cbox:`gray100` | `11.2`   |
   +----------------------+---------+-----------+-------------------+----------+  +---------------------+---------+----------+-----------------+----------+
   | :colorbox:`#ff0000`  | `100\%` | `21.3\%`  | :cbox:`gray0`     | `5.3`    |  | :colorbox:`#0000ff` | `100\%` | `7.2\%`  | :cbox:`gray100` | `8.6`    |
   +----------------------+---------+-----------+-------------------+----------+--+---------------------+---------+----------+-----------------+----------+

Note how the resulting foreground color sets differ for each series of 5 colors
with the same hue: there are only two white colors in green group, but five of
them are sitting in a blue group, despite the fact that the corresponding colors
has the **same** HSV *values*. That's what *uniform* color spaces (e.g. LAB, XYZ)
were created to begin with -- to compensate non-linearity of human color perception
(e.g. first one of these *looks* much brighter than the second: :cbox:`#00ff00`
:cbox:`#0000ff`, especially when you're trying to read black text on a colored
background -- and that is taken into account).

.. default-role:: any

See the demo script `demo.autopick_fg`.

.. [#] https://www.w3.org/TR/2008/REC-WCAG20-20081211 , section 1.4.3
