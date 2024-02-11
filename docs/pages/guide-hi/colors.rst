.. _guide.colors:

########################
Colors
########################

Primary method for getting a color by name is `resolve_color()`. Suggested usage
is to feed it the input in a free form and hope for the best. First argument is
`CDT` and can be specified as

    1) *str* with color name in any form distinguishable by the color resolver,
       e.g. 'red', 'navy blue', etc. (all preset color names are listed in
       `guide.ansi-presets` and `guide.es7s-colors`);

    2) *str* in full hexadecimal form: ":hex:`#RRGGBB`" or  ":hex:`0xRRGGBB`" or
       ":hex:`RRGGBB`";

    3) *str* in RGB short form: ":hex:`#RGB`", which is a special case; e.g.
       ":hex:`#3c9`" will be interpreted as :colorbox:`#3c9`;

    4) *int* in [:hex:`0x000000`; :hex:`0xFFFFFF`] range.

The method operates in three different modes depending on argument types:
resolving by name, resolving by value and instantiating; all of three
corresponding methods can be invoked independently, which makes
`resolve_color()` more like of a facade.


.. _guide.color-resolving:

====================
Resolving by name
====================

If first argument of `resolve_color()` does not represent a hexadecimal number,
case-insensitive search through the registry of ``color_type`` colors is
performed. The main method is `Color256.find_by_name()` and his siblings in
other color classes, so everything in this section can be applied to them as well.

The algorithm looks for the instance which has all the words from ``subject`` as
parts of its name (the order must be the same). Color names are stored in
registries as sets of tokens, which allows to use any form of input and get the
correct result regardless. The only requirement is to separate the words in any
matter (see the example below), so that they could be split to tokens which will
be matched with the registry keys.

If ``color_type`` is omitted, the registries are accessed in this order:
`Color16`, `Color256`, `ColorRGB`. Should any registry find a full match, the
resolving is stopped and the result is returned.

    >>> from pytermor import resolve_color
    >>> resolve_color('deep-sky-blue-7')
    <Color256[x23(#005f5f deep-sky-blue-7)]>

    >>> resolve_color('DEEP SKY BLUE 7')
    <Color256[x23(#005f5f deep-sky-blue-7)]>

    >>> resolve_color('DeepSkyBlue7')
    <Color256[x23(#005f5f deep-sky-blue-7)]>

    >>> resolve_color('deepskyblue7')
    Traceback (most recent call last):
    LookupError: Color 'deepskyblue7' was not found in any registry


========================
Registry implementation
========================

When new color is created, it gets registered under it's exact original name,
as well as under split and *normalized* set of tokens made from that name.
Searching is performed first by exact query match, and then by exact
match of split and *normalized* set of tokens made from the query.

Splitting string into tokens is performed by transitions between (lower
cased letter OR underscore OR non-letter character) AND (upper-cased
letter OR a digit). This rule in a form of a regular expression:

:regexp:`[\W_]+|(?<=[a-z])(?=[A-Z0-9])`

It covers all popular methods of writing an enumerated name. It is implied
that queries to the registry will look like one of the cases below:

+---------------+---------------------+-----------------------------+-----------------------------+
|     Case      |     Example query   |         Split query         |     Normalized token set    |
+===============+=====================+=============================+=============================+
|snake_case     |``atomic_tangerine`` |``('atomic', 'tangerine')``  |``('atomic', 'tangerine')``  |
+---------------+---------------------+-----------------------------+                             |
|camelCase      |``atomicTangerine``  |``('atomic', 'Tangerine')``  |                             |
+---------------+---------------------+-----------------------------+-----------------------------+
|kebab-case     |``icathian-yellow``  |``('icathian', 'yellow')``   |``('icathian', 'yellow')``   |
+---------------+---------------------+-----------------------------+                             |
|SCREAMING_CASE |``ICATHIAN_YELLOW``  |``('ICATHIAN', 'YELLOW')``   |                             |
+---------------+---------------------+-----------------------------+-----------------------------+
|PascalCase     |``AirForceBlue``     |``('Air', 'Force', 'Blue')`` |``('air', 'force', 'blue')`` |
+---------------+---------------------+-----------------------------+                             |
|*(mixed)*      |``AIR force-blue``   |``('AIR', 'force', 'blue')`` |                             |
+---------------+---------------------+-----------------------------+-----------------------------+

Normalization consists of two operations: discarding all characters
except latin letters, digits, underscore and hyphen, and translating
all upper-cased letters to lower case.

.. note::

    Known limitation of this approach is inability to correctly handle
    multi-cased queries which include transitions between lower case
    and upper case in the middle of the word (=token), e.g.
    "AtoMicTangErine" will end up being split into four tokens ('ato',
    'mic', 'tang', 'erine'), and such query will fail with zero results.
    Pre-normalization instead of post-normalization can help here, but
    that will break all valid camel case and pascal case queries.

    The aforementioned query is more like an artificial example than a real
    case anyway, but if it's essential, then one way to fix it is to
    perform two searches instead of just one, i.e. first to see if split
    token set exists in a registry, and if it does not -- normalize it
    and try again.


.. _guide.finding_closest_color:

=====================================
Finding closest colors
=====================================

When first argument of `resolve_color()` represents a hexadecimal number
and ``color_type`` is **present**\ , the result will be the best ``subject``
approximation to corresponding color index. Note that this value is expected
to differ from the requested one (and sometimes differs a lot), unless the
exact color requested is present in the index (e.g. :colorbox:`#0000FF` can be
found in all three color palettes).

Omit the second parameter to create an exact color: if ``color_type`` is
**missing**, no searching is performed; instead a new nameless `ColorRGB` is
instantiated and returned.

Integer values over the maximum of :hex:`0xFFFFFF` will be set to match the limit.

::

    >>> from pytermor import resolve_color, Color256
    >>> resolve_color("#333")
    <ColorRGB[#333333]>

    >>> resolve_color(0xfafef0)
    <ColorRGB[#fafef0]>

    >>> resolve_color(0x333333, Color256)
    <Color256[x236(#303030 gray-19)]>


.. important::

    The instance created this way is an "unbound" color, i.e. it does
    not end up in a registry or an index bound to its type, thus the resolver
    and approximation algorithms are unaware of its existence. The rationale
    for this is to keep the registries clean and immutable to ensure that
    the same input always resolves to the same output. If you absolutely
    want your new color to be accessible from a registry and color index,
    create it manually using a class constructor::

        Color256(0x123456, code=257, register=True, index=True)

    Although this will not work properly for xterm-indexed colors, because code
    257 does not exist, and not a single terminal emulator does know anything
    about it, this can be used to extend `ColorRGB` color set, as it translates
    to SGRs explicitly (by color value).



Also there are two top-level methods that provide a capability to search for
the colors closest to specified one in an indexed palette: `find_closest()`
and `approximate()`.

These methods are useful for finding applicable color alternatives if user's
terminal is incapable of operating in more advanced mode. Usually it is
done by the library automatically and transparently for both the developer
and the end-user.

Both methods take ``value`` parameter which is a target color value, e.g.
:hex:`0x404030`, and ``color_type`` which determines the type of the result.
If `color_type` is omitted, the searching is performed in `Color256` index.

`find_closest()` caches the results, i.e., the same search query will from
then onward result in the same return value without the necessity of
iterating through the color index. If that's not applicable, use
`approximate()`, which is unaware of caching mechanism altogether.

The main difference between the methods is that `find_closest()` always returns
the color with lowest color difference with the target, while `approximate()`
takes third parameter ``max_results``, which can be used to control how many
colors we want to receive.  Also note that the latter method response is not
just the color instances, but a data class containing the color and numeric
distance to the target.

    >>> from pytermor import approximate
    >>> print(*approximate(0x123456, Color256, 3), sep='\n')
    ApxResult(color=<Color256[x24(#005f87 deep-sky-blue-6)]>, distance=19.69124894424491)
    ApxResult(color=<Color256[x60(#5f5f87 medium-purple-7)]>, distance=22.56723105940626)
    ApxResult(color=<Color256[x236(#303030 gray-19)]>, distance=24.151294783796793)

.. _guide.approximators:

============================
Approximator implementations
============================

There are two approximator implementations in the library -- the first one does
not require any dependencies, but is slow, as it has to iterate all the colors
in the index and calculate color distance to each of those, and the second one,
which requires ``scipy`` package to be installed along with the library, which
results in approximating about **10.06** times faster than the first one thanks to
using optimized data structure\ [#]_. In order to utilize the second one the library
must be installed as ``pytermor[fast]`` , which installs extra dependencies automatically.

.. important::
    Approximator implementation is selected automatically on library initialization
    depending on availability of `numpy` and `scipy` packages.

Distance between two colors is calculated using CIE76 ΔE\* color
difference formula in LAB color space\ [#]_. This method is considered to be
an acceptable tradeoff between sRGB euclidean distance, which doesn't
account for differences in human color perception, and CIE94/CIEDE2000,
which are more complex and in general excessive for this task.


.. figure::  /_static/approx-spaces.png
  :align: center

  Approximation of red colors using different color spaces for color distance
  computation

More details: :ref:`appendix.approx-diff`

There is also a demo script which can illustrate the difference between approximated
colors using different color distance formulas. For the details see `Examples —
Demo — approximate.py <examples.demo.approximate>`.

.. [#] https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.KDTree.html

.. [#] http://www.brucelindbloom.com/index.html?Eqn_DeltaE_CIE76.html


.. _guide.color_class_diagram:

========================================
:fas:`sitemap` Color class hierarchy
========================================


.. grid:: 1
   :class-container: inheritance-columns

   .. grid-item::

      .. inheritance-diagram:: pytermor.color
         :parts: 1
         :private-bases:
         :top-classes:         pytermor.color.IColorValue,
                               pytermor.color.RenderColor,
                               pytermor.color.ResolvableColor
         :caption:             ``Color`` inheritance diagram
