.. _guide.low-level:

.. default-role:: any

Low-level abstractions
==========================

So, what's happening under the hood?


--------------------
Format soft reset
--------------------

There are two ways to manage color and attribute termination:

- hard reset (SGR 0 | :kbd:`\e[0m`)
- soft reset (SGR 22, 23, 24 etc.)

The main difference between them is that *hard* reset disables all formatting after itself, while *soft* reset disables only actually necessary attributes (i.e. used as opening sequence in `Span` instance's context) and keeps the other.

That's what ``Span`` class and `autospan()` method are designed for: to simplify creation of soft-resetting text spans, so that developer doesn't have to restore all previously applied formats after every closing sequence.

.. rubric:: Example

We are given a text span which is initially *bold* and *underlined*. We want to recolor a few words inside of this span. By default this will result in losing all the formatting to the right of updated text span (because `RESET <sequence.RESET>`, or :kbd:`\e[0m`, clears all text attributes).

However, there is an option to specify what attributes should be disabled or let the library do that for you:

.. literalinclude:: /_include/examples/ex_60_autocomplete.py
   :linenos:

.. image:: /_static/ex_60.png
   :width: 50%
   :align: center
   :class: no-scaled-link

As you can see, the update went well -- we kept all the previously applied formatting. Of course, this method cannot be 100% applicable; for example, imagine that original text was colored blue. After the update "string" word won't be blue anymore, as we used `COLOR_OFF <sequence.COLOR_OFF>` escape sequence to neutralize our own yellow color. But it still can be helpful for a majority of cases (especially when text is generated and formatted by the same program and in one go).


--------------------------------
Working with *Spans*
--------------------------------

Use `autospan()` to create new `Span` with specified control sequence(s) as a opening/starter sequence and **automatically composed** closing sequence that will terminate attributes defined in opening sequence while keeping the others (soft reset).

Resulting sequence params' order is the same as argument's order.

Each sequence param can be specified as:

- string key (see `presets`);
- integer param value;
- existing `SequenceSGR` instance (params will be extracted).


----------------------------
Creating and applying *SGRs*
----------------------------

You can use any of predefined sequences from `sequence` or create your own via standard constructor. Valid argument values as well as preset constants are described in `presets` page.

There is also a set of methods for dynamic ``SequenceSGR`` creation:

- `build()` for non-specific sequences;

  .. important::
     ``SequenceSGR`` with zero params was specifically implemented to translate into an empty string and not into :kbd:`\e[m`, which would make sense, but also could be very entangling, as terminal emulators interpret that sequence as :kbd:`\e[0m`, which is *hard* reset sequence.

- `color_indexed()` for complex color selection sequences operating in 256-colors mode (for a complete list see `xterm-colors`);
- `color_rgb()` for setting the colors in True Color 16M mode (however, some terminal emulators doesn't support it).

To get the resulting sequence chars use `print()` method or cast instance to *str*.

.. literalinclude:: /_include/examples/ex_70_sgr_structure.py
   :linenos:

.. image:: /_static/ex_70.png
   :width: 50%
   :align: center
   :class: no-scaled-link

- First line is "applied" escape sequence;
- Second line shows up a sequence in raw mode, as if it was ignored by the terminal;
- Third line is hexademical sequence byte values.


-----------------------
SGR sequence structure
-----------------------

1. :kbd:`\x1b` is ESC *control character*, which opens a control sequence.

2. :kbd:`[` is sequence *introducer*, it determines the type of control sequence (in this case it's :abbr:`CSI (Control Sequence Introducer)`).

3. :kbd:`4` and :kbd:`7` are *parameters* of the escape sequence; they mean "underlined" and "inversed" attributes respectively. Those parameters must be separated by :kbd:`;`.

4. :kbd:`m` is sequence *terminator*; it also determines the sub-type of sequence, in our case :abbr:`SGR (Select Graphic Rendition)`. Sequences of this kind are most commonly encountered.


-----------------------
Combining *SGRs*
-----------------------

One instance of `SequenceSGR` can be added to another. This will result in a new ``SequenceSGR`` with combined params.

.. literalinclude:: /_include/examples/ex_80_combined.py
   :linenos:


------------------
Core API
------------------

.. table::
   :class: core-api-refs

   ============= =================== ================
   `build()`     `color_indexed()`   `color_rgb()`
   `autospan()`  `SequenceSGR` class `Span` class
   ============= =================== ================
