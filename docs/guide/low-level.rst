.. _guide.low-level:

.. default-role:: any

==========================
Low-level abstractions
==========================

So, what's happening under the hood?


Format soft reset
=================

There are two ways to manage color and attribute termination:

- hard reset (SGR-0 or :kbd:`\e[0m`)
- soft reset (SGR-22, 23, 24 etc.)

The main difference between them is that *hard* reset disables all formatting after itself, while *soft*
reset disables only actually necessary attributes (i.e. used as opening sequence in `Span` instance's context)
and keeps the other.

That's what ``Span`` class is designed for: to simplify creation of soft-resetting text spans, so that developer
doesn't have to restore all previously applied formats after every closing sequence.

.. rubric:: Example

We are given a text span which is initially *bold* and *underlined*. We want to recolor a few words inside of this
span. By default this will result in losing all the formatting to the right of updated text span (because
`RESET <Seqs.RESET>`, or :kbd:`\e[0m`, clears all text attributes).

However, there is an option to specify what attributes should be disabled or let the library do that for you:

.. literalinclude:: /examples/ex_60_autocomplete.py
   :linenos:

.. image:: /_static/ex_60.png
   :width: 50%
   :align: center
   :class: no-scaled-link

As you can see, the update went well -- we kept all the previously applied formatting. Of course, this method
cannot be 100% applicable; for example, imagine that original text was colored blue. After the update "string"
word won't be blue anymore, as we used ``Seqs.COLOR_OFF`` escape sequence to neutralize our own yellow color.
But it still can be helpful for a majority of cases (especially when text is generated and formatted by the same
program and in one go).


Working with :mono:`Spans`
=============================

Use `Span` constructor to create new instance with specified control sequence(s) as a opening/starter sequence
and **automatically composed** closing sequence that will terminate attributes defined in opening sequence while
keeping the others (soft reset).

Resulting sequence params' order is the same as argument's order.

Each sequence param can be specified as:

- string key (see `presets`);
- integer param value;
- existing `SequenceSGR` instance (params will be extracted).

It's also possible to avoid auto-composing mechanism and create `Span` with
explicitly set parameters using `Span.init_explicit()`.


Creating and applying :mono:`SGRs`
==================================

You can use any of predefined sequences from `Seqs` registry or create your own via standard constructor. Valid
argument values as well as preset constants are described in `presets` page.

.. important::
  ``SequenceSGR`` with zero params was specifically implemented to translate into an empty string and not
  into :kbd:`\e[m`, which would make sense, but also could be very entangling, as terminal emulators interpret
  that sequence as :kbd:`\e[0m`, which is *hard* reset sequence.

There is also a set of methods for dynamic ``SequenceSGR`` creation:

- `init_color_indexed()` will produce sequence operating in 256-colors mode (for a complete list
  see `presets`);
- `init_color_rgb()` will create a sequence capable of setting the colors in True Color 16M mode (however, some terminal emulators doesn't
  support it).

To get the resulting sequence chars use `assemble() <SequenceSGR.assemble()>` method or cast instance to *str*.

.. literalinclude:: /examples/ex_70_sgr_structure.py
   :linenos:

.. image:: /_static/ex_70.png
   :width: 50%
   :align: center
   :class: no-scaled-link

- First line is the string with encoded escape sequence;
- Second line shows up the string in raw mode, as if sequences were ignored by the terminal;
- Third line is hexademical string representation.


:mono:`SGR` sequence structure
================================

1. :kbd:`\\x1b` is ESC *control character*, which opens a control sequence.

2. :kbd:`[` is sequence *introducer*; it determines the type of control sequence (in this case
   it's :abbr:`CSI (Control Sequence Introducer)`).

3. :kbd:`4` and :kbd:`7` are *parameters* of the escape sequence; they mean "underlined" and "inversed"
   attributes respectively. Those parameters must be separated by :kbd:`;`.

4. :kbd:`m` is sequence *terminator*; it also determines the sub-type of sequence, in our
   case :abbr:`SGR (Select Graphic Rendition)`. Sequences of this kind are most commonly encountered.


Combining :mono:`SGRs`
=========================

One instance of `SequenceSGR` can be added to another. This will result in a new ``SequenceSGR`` with combined params.

.. literalinclude:: /examples/ex_80_combined.py
   :linenos:


Core API
========

.. only :: html

   .. table::
      :class: core-api-refs

      =================================== ======================
      `SequenceSGR` constructor           `Span` constructor
      `SequenceSGR.init_color_indexed()`  `Span.init_explicit()`
      `SequenceSGR.init_color_rgb()`
      =================================== ======================

.. only :: latex

   * @TODO
   * `SequenceSGR` constructor
   * `SequenceSGR.init_color_indexed()`
   * `SequenceSGR.init_color_rgb()`
   * `Span` constructor
   * `Span.init_explicit()`
