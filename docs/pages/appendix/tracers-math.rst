.. _appendix.tracers-math:

.. default-role:: math

########################
     Tracers math
########################

The library provides a few implementations of :any:`AbstractTracer`, each of them
having an algorithm that determines the maximum amount of data per line
depending on current output device (terminal) width. Some of these algorithms
are non-linear and for the clarity listed below.

.. _appendix.tracers-math.bytes-tracer:

====================
BytesTracer
====================

Display *str*/*bytes* as byte hex codes, grouped by 4.

.. code-block:: PtTracerDump
   :caption: Example output

     0x00 | 35 30 20 35  34 20 35 35  20 C2 B0 43  20 20 33 39  20 2B 30 20
     0x14 | 20 20 33 39  6D 73 20 31  20 52 55 20  20 E2 88 86  20 35 68 20
     0x28 | 31 38 6D 20  20 20 EE 8C  8D 20 E2 80  8E 20 2B 32  30 C2 B0 43
     0x3C | 20 20 54 68  20 30 31 20  4A 75 6E 20  20 31 36 20  32 38 20 20
     0x50 | E2 96 95 E2  9C 94 E2 96  8F 46 55 4C  4C 20

The amount of characters that will fit into one line (with taking into account
all the formatting and the fact that chars are displayed in groups of `4`)
depends on terminal width and on max address value (the latter determines the
size of the leftmost field -- current line address). Let's express output line
length `L_O` in a general way -- through `C_L` (characters per line) and
`L_{adr}` (length of maximum address value for given input):

.. math ::
   :label: cl_main

         L_O& = L_{spc} + L_{sep} + L_{adr} + L_{hex},              \\\\\
     L_{adr}& = 2 + 2 \cdot ceil(\frac{L_{Ihex}}{2}), \qquad\qquad  \\\\\
     L_{hex}& = 3C_L + floor(\frac{C_L}{4}),

where:

    - `L_{spc} = 3` is static whitespace total length,
    - `L_{sep} = 1` is separator (``"|"``) length,
    - `L_{Ihex} = len(L_I)` is *length* of (hexadecimal) *length* of input.
      Here is an example, consider input data `I` `10` bytes long:

            .. math ::
                    L_I& = len(I) = 10_{10} = A_{16},    \\\\\
               L_{Ihex}& = len(L_I) = len(A_{16}) = 1,   \\\\\
                L_{adr}& = 2 + 2 \cdot ceil(\frac{1}{2}) = 4,

      which corresponds to address formatted as :hex:`0x0A`. One more example --
      input data `1000` bytes long:

            .. math ::
                      L_I& = len(I) = 1000_{10} = 3E8_{16},    \\\\\
                 L_{Ihex}& = len(L_I) = len(3E8_{16}) = 3 ,    \\\\\
                  L_{adr}& = 2 + 2 \cdot ceil(\frac{3}{2})  = 6 ,

      which matches the length of an actual address :hex:`0x03E8`). Note that the
      expression `2 \cdot ceil(\frac{L_{Ihex}}{2})` is used for rounding `L_{adr}` up
      to next even integer to avoid printing the addresses in :hex:`0x301` form,
      and displaying them more or less aligned instead. The first constant item
      `2` in :eq:`cl_main` represents :hex:`0x` prefix.
    - `L_{hex}` represents amount of chars required to display `C_L` hexadecimal bytes.
      First item `3C_L` is trivial and corresponds to every byte's hexadecimal value
      plus a space after (giving us `2+1=3`, e.g. `34`), while the second one
      represents one extra space character per each 4-byte group.

Let's introduce `L_T` as current terminal width, then `\boxed{L_O \leqslant L_T}`, which
leads to the following inequation:

.. math ::
     L_{spc} + L_{sep} + L_{adr} + L_{hex} \leqslant L_T .

Substitute the variables:

.. math ::
    3 + 1 + 2 + 2 \cdot ceil(\frac{L_{Ihex}}{2}) + 3C_L + floor(\frac{C_L}{4}) \leqslant L_T .

Suppose we limit `C_L` values to the integer factor of `4`, then:

.. math ::
   :label: cl_limit

    3C_L + floor(\frac{C_L}{4}) = 3.25C_L \qquad \forall C_L \in [4, 8, 12..) , \qquad

which gives us:

.. math ::
    6 + 2 \cdot ceil(\frac{L_{Ihex}}{2}) + 3.25C_L \leqslant L_T  &,  \\\\\
    3.25C_L \leqslant  L_T - 2 \cdot ceil(\frac{L_{Ihex}}{2}) - 6 &,  \\\\\
    13C_L \leqslant 4L_T - 8 \cdot ceil(\frac{L_{Ihex}}{2}) - 24  &.

Therefore:

.. math ::
    C_{Lmax} = floor(\frac{4L_T - 4 \cdot ceil(\frac{L_{Ihex}}{2}) - 24}{13}) .

Last step would be to round the result (down) to the nearest integer
factor of `4` as we have agreed earlier in :eq:`cl_limit`\ .

.. _appendix.tracers-math.string-tracer:

====================
StringTracer
====================

Display *str* as byte hex codes (UTF-8), grouped by characters.

.. code-block:: PtTracerDump
   :caption: Example output

      0 |     35     30     20 35 34 20 35     35     20   c2b0 43 20 |50␣54␣55␣°C␣
     12 |     20     33     39 20 2b 30 20     20     20     33 39 6d |␣39␣+0␣␣␣39m
     24 |     73     20     31 20 52 55 20     20 e28886     20 35 68 |s␣1␣RU␣␣∆␣5h
     36 |     20     31     38 6d 20 20 20 ee8c8d     20 e2808e 20 2b |␣18m␣␣␣␣‎␣+
     48 |     32     30   c2b0 43 20 20 54     68     20     30 31 20 |20°C␣␣Th␣01␣
     60 |     4a     75     6e 20 20 31 36     20     32     38 20 20 |Jun␣␣16␣28␣␣
     72 | e29695 e29c94 e2968f 46 55 4c 4c     20                     |▕✔▏FULL␣

Calculations for this class are different, although the base
formula for output line length `L_O` is the same:

.. math ::
         L_O& = L_{spc} + L_{sep} + L_{adr} + L_{hex},   \\\\\
     L_{adr}& = len(L_I),                                \\\\\
     L_{hex}& = (2C_{Umax} + 1) \cdot C_L

where:

    - `L_{spc} = 3` is static whitespace total length,
    - `L_{sep} = 2` is separators ``"|"`` total length,
    - `L_{adr}` is length of maximum address value and is equal to *length*
      of *length* of input data without any transformations (because the
      output is decimal, in contrast with :py:class:`BytesTracer`),
    - `L_{hex}` is hex representation length (`2` chars multiplied to
      `C_{Umax}` plus `1` for space separator per each character),
    - `C_{Umax}` is maximum UTF-8 bytes amount for a single codepoint
      encountered in the input (for example, `C_{Umax}` equals to `1` for
      input string consisting of ASCII-7 characters only, like ``"ABCDE"``,
      `2` for ``"эйцукен"``, `3` for ``"硸馆邚"`` and `4` for ``"􏿿"``,
      which is :hex:`U+10FFFF`),
    - `L_{chr} = C_L` is char representation length (equals to `C_L`), and
    - `C_L` is chars per line setting.

Then the condition of fitting the data to a terminal can be written as:

.. math ::
    L_{spc} + L_{sep} + L_{adr} + L_{hex} + L_{chr} \leqslant L_T ,

where `L_T` is current terminal width. Next:

.. math ::
    3 + 2 + L_{adr} + (2C_{Umax}+1) \cdot C_L + C_L ,& \leqslant L_T \\\\\
              L_{adr} + 5 + (2C_{Umax}+2) \cdot C_L ,& \leqslant L_T

Express `C_L` through `L_T`, `L_{adr}` and `C_{Umax}`:

.. math ::
    (2C_{Umax}+2) \cdot C_L \leqslant L_T - L_{adr} - 5 ,

Therefore maximum chars per line equals to:

.. math ::
    C_{Lmax} = floor(\frac{L_T - L_{adr} - 5}{2C_{Umax}+2}).

.. rubric:: Example

Consider terminal width is `80`, input data is `64` characters long
and consists of :hex:`U+10FFFF` codepoints only (`C_{Umax}=4`). Then:

 .. math ::
     L_{adr} &= len(L_I) = len(64) = 2, \\\
     C_{Lmax} &= floor(\frac{78 - 2 - 5}{8+2}), \\\
              &= floor(7.1) = 7.

.. note ::
    Max width value used in calculations is slightly smaller than real one,
    that's why output lines are `78` characters long (instead of `80`) --
    there is a `2`-char reserve to ensure that the output will fit to the
    terminal window regardless of terminal emulator type and implementation.

The calculations always consider the maximum possible length of input
data chars, and even if it will consist of the highest order codepoints
only, it will be perfectly fine.

.. code-block:: PtTracerDump
   :caption: Example output of highest order codepoints

       0 | f4808080 f4808080 f4808080 f4808080 f4808080 f4808080 f4808080 |􀀀􀀀􀀀􀀀􀀀􀀀􀀀
       7 | f4808080 f4808080 f4808080 f4808080 f4808080 f4808080 f4808080 |􀀀􀀀􀀀􀀀􀀀􀀀􀀀
      14 | ...

.. _appendix.tracers-math.string-ucp-tracer:

=======================
StringUcpTracer
=======================

Display *str* as Unicode codepoints.

.. code-block:: PtTracerDump
   :caption: Example output

      0 |U+   20   34   36 20 34 36 20 34   36   20 B0 43 20 20 33   39 20 2B |␣46␣46␣46␣°C␣␣39␣+
     18 |U+   30   20   20 20 35 20 6D 73   20   31 20 52 55 20 20 2206 20 37 |0␣␣␣5␣ms␣1␣RU␣␣∆␣7
     36 |U+   68   20   32 33 6D 20 20 20 FA93 200E 20 2B 31 33 B0   43 20 20 |h␣23m␣␣␣望‎␣+13°C␣␣
     54 |U+   46   72   20 30 32 20 4A 75   6E   20 20 30 32 3A 34   38 20 20 |Fr␣02␣Jun␣␣02:48␣␣
     72 |U+ 2595 2714 258F 46 55 4C 4C 20                                     |▕✔▏FULL␣

Calculations for :any:`StringUcpTracer` are almost the same as for :any:`StringTracer`,
expect that sum of static parts of `L_O` equals to `7` instead
of `5` (because of "U+" prefix being displayed).

The second difference is using `C_{UCmax}` instead of
`C_{Umax}`; the former variable is the amount of "n" in
:hex:`U+nnnn` identifier of the character, while the latter is amount of
bytes required to encode the character in UTF-8. Final formula is:

.. math ::
    C_{Lmax} = floor(\frac{L_T - L_{adr} - 7}{C_{UCmax}+2}).
