.. _features:

#################
    Features
#################

==================================
Flexible input formats
==================================

`guide.fargs` allows to compose formatted text parts much faster and keeps the code
compact:

.. literalinclude:: /demo/features.fargs.py
   :linenos:

.. only:: html

   .. raw:: html
       :file: ../demo/features.fargs.html

.. only:: latex

   .. figure:: /demo/features.fargs.svg
      :align: center

==================================
Content-aware format nesting
==================================
r
Template tags and non-closing `Fragments <Fragment>` allow to build complex formats.

.. literalinclude:: /demo/features.templates.py
   :linenos:

.. only:: html

   .. raw:: html
       :file: ../demo/features.templates.html

.. only:: latex

   .. figure:: /demo/features.templates.svg
      :align: center


==================================
256 colors / True Color support
==================================

The library supports extended color modes:

- XTerm 256 colors indexed mode
- True Color RGB mode (16M colors)


.. literalinclude:: /demo/features.color-modes.py
   :linenos:

.. only:: html

   .. raw:: html
       :file: ../demo/features.color-modes.html

.. only:: latex

   .. figure:: /demo/features.color-modes.svg
      :align: center

==================================
Different color spaces
==================================

Currently supported spaces: `RGB`, `HSV`, `XYZ`, `LAB`. Any of these
can be transparently translated to any other.

.. literalinclude:: /demo/features.color-spaces.py
   :linenos:

.. only:: html

   .. raw:: html
       :file: ../demo/features.color-spaces.html

.. only:: latex

   .. figure:: /demo/features.color-spaces.svg
      :align: center


==================================
Named colors collection
==================================

Registry containing more than 2400 named colors, in addition to
default 256 from ``xterm`` palette.

.. only:: html

   .. raw:: html
       :file: ../demo/features.named-colors.html

.. only:: latex

   .. figure:: /demo/features.named-colors.svg
      :align: center


==================================
Extendable renderers
==================================

`Renderers <guide.renderers>` is a family of classes responsible for creating
formatted strings from `IRenderable` instances, which, in general, consist of
a text piece and a :term:`Style` -- a set of formatting rules. Concrete implementation
of the renderer determines the target format and/or platform.


This is how `SgrRenderer`, `HtmlRenderer`, `TmuxRenderer`, `SgrDebugger` (from top
to bottom) output can be seen in a terminal emulator:

.. only:: html

   .. raw:: html
       :file: ../demo/features.renderers.html

.. only:: latex

   .. figure:: /demo/features.renderers.svg
      :align: center


==================================
Number formatters
==================================

Set of highly customizable helpers, see `numfmt`.

`format_si()` output sample:

.. only:: html

   .. raw:: html
      :file: ../demo/features.formatters.si.html

.. only:: latex

   .. figure:: /demo/features.formatters.si.svg
      :align: center

`format_time_ns()` output samples:

.. only:: html

   .. raw:: html
      :file: ../demo/features.formatters.time_ns.html

.. only:: latex

   .. figure:: /demo/features.formatters.time_ns.svg
      :align: center

`format_time_delta()` output sample:

.. only:: html

   .. raw:: html
      :file: ../demo/features.formatters.time_delta.html

.. only:: latex

   .. figure:: /demo/features.formatters.time_delta.svg
      :align: center

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
