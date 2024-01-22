.. _features:

#################
    Features
#################

.. highlight:: python

==================================
Flexible input formats
==================================

`guide.fargs` allows to compose formatted text parts much faster and to keep the
code compact::

    import pytermor as pt

    ex_st = pt.Style(bg='#ffff00', fg='black')
    text = pt.FrozenText(
        'This is red ', pt.cv.RED,
        "This is white ",
        "This is black on yellow", ex_st,
    )
    pt.echo(text)

.. container:: highlight highlight-manual highlight-adjacent output

    :red:`This is red`\ |nbsp| This is white\ |nbsp| :blackonyellow:`This is black on yellow`

==================================
Content-aware format nesting
==================================

Template tags and non-closing `Fragments <Fragment>` allow to build complex formats::

   import pytermor as pt

   s = ":[fg=red]fg :[bg=blue]and bg :[fg=black]formatting with:[-] overlap:[-] support"
   pt.echo(pt.TemplateEngine().substitute(s))

.. container:: highlight highlight-manual highlight-adjacent output

    :red:`fg` :redonblue:`and bg\ \ `\ :blackonblue:`formatting with\ \ `\ :redonblue:`overlap` :red:`support`


==================================
256 colors / True Color support
==================================

The library supports extended color modes:

- XTerm 256 colors indexed mode
- True Color RGB mode (16M colors)

::

    import pytermor as pt

    for outm in ['true_color', 'xterm_256', 'xterm_16']:
        for c in range((W:=80) + 1):
            b = pt.RGB.from_ratios(1 - (p := c / W), 2 * min(p, 1 - p), p).int
            f = pt.Fragment("▁", pt.Style(fg=pt.cv.GRAY_0, bg=b, bold=True))
            print(f.render(pt.SgrRenderer(outm)), end=["", "\n"][c >= W], flush=True)


.. container:: highlight highlight-manual highlight-adjacent output fullwidthimage

    .. image:: /_generated/features/xterm-truecolor.png
      :width: 100%
      :align: center
      :class: no-scaled-link

==================================
Different color spaces
==================================

Currently supported spaces: `RGB`, `HSV`, `XYZ`, `LAB`. A color defined
in any of these can be transparently translated into any other::

    import pytermor as pt

    col = pt.cvr.SUPERUSER
    pt.echo(repr(col.rgb) + ", " + repr(col.hsv), col)


.. container:: highlight highlight-manual highlight-adjacent output

    | :superuser:`RGB[#F8B889][R=248 G=184 B=137]`
    | :superuser:`HSV[H=25° S=45% V=97%]`

==================================
Named colors collection
==================================

Registry containing more than 2400 named colors, in addition to
default 256 from ``xterm`` palette. See `guide.es7s-colors`.

.. code-block:: console

    $ /run-cli examples/list_named_rgb.py

.. container:: highlight highlight-manual highlight-adjacent output fullwidthimage

    .. image:: /_generated/features/named-colors.png
       :width: 100%
       :align: center
       :class: no-scaled-link


==================================
Extendable renderers
==================================

`Renderers <guide.renderers>` is a family of classes responsible for creating
formatted strings from `IRenderable` instances, which, in general, consist of
a text piece and a :term:`Style` -- a set of formatting rules. Concrete implementation
of the renderer determines the target format and/or platform.

This is how `SgrRenderer`, `HtmlRenderer`, `TmuxRenderer`, `SgrDebugger` (from top
to bottom) output can be seen in a terminal emulator:

.. container:: highlight highlight-manual outputstandalone output

    | :red:`This is red`\ |nbsp| This is white\ |nbsp| :blackonyellow:`This is black on yellow`
    |
    | <span style="color: #800000">This is red </span><span style="">This is white </span><span style="background-color: #ffff00; color: #000000">This is black on yellow</span>
    |
    | #[fg=red]This is red #[fg=default]This is white #[fg=black bg=#ffff00]This is black on yellow#[fg=default bg=default]
    |
    | (·[31m)This is red (·[39m)This is white (·[30;48;5;11m)This is black on yellow(·[39;49m)


==================================
Number formatters
==================================

Set of highly customizable helpers, see `numfmt`.

.. container:: code-block-caption outputcaption

    `format_si()` output sample

.. container:: highlight highlight-manual highlight-adjacent output fullwidthimage

    .. image:: /_generated/features/formatter-si.png
      :width: 100%
      :align: center
      :class: no-scaled-link


.. container:: code-block-caption outputcaption

    `format_time_ns()` output samples

.. container:: highlight highlight-manual highlight-adjacent output fullwidthimage

    .. image:: /_generated/features/formatter-time-ns.png
      :width: 100%
      :align: center
      :class: no-scaled-link


.. container:: code-block-caption outputcaption

    `format_time_delta()` output sample

.. container:: highlight highlight-manual highlight-adjacent output fullwidthimage

    .. image:: /_generated/features/formatter-time-delta.png
      :width: 100%
      :align: center
      :class: no-scaled-link


==================================
Data dumps
==================================

Special formatters for raw binary/string data.

These examples were composed for a terminal 80-chars wide; tracers
dynamically change the amount of elements per line at each `dump()`
call.

Input data for all examples below was the same.

.. literalinclude:: /demo/features.dump.bytes.txt
    :caption: Decomposition into separate bytes by `BytesTracer`. Note the hexadecimal offset format.
    :language: PtTracerDump

.. literalinclude:: /demo/features.dump.strings.txt
    :caption: Decomposition into UTF-8 sequences by `StringTracer`
    :language: PtTracerDump

.. literalinclude:: /demo/features.dump.string-ucps.txt
    :caption: Decomposition into Unicode codepoints by  `StringUcpTracer`
    :language: PtTracerDump
