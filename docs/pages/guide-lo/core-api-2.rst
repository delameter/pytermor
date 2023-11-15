.. _guide.core-api-2:

##########################
Core API II
##########################


So, what's happening under the hood?

================
Glossary
================

.. glossary::

   ASCII
      Basic charset developed back in 1960s, consisting of 128 code points.
      Nevertheless it is still used nowadays as a part of Unicode character
      set.

   ANSI
      ..escape sequence is a standard for in-band signaling to control cursor
      location, color, font styling, and other options on video text terminals
      and terminal emulators. Certain sequences of bytes, most starting with an
      :term:`ASCII` escape character (``ESC`` :hex:`0x1B`) and a bracket
      character (``[`` :hex:`0x5B`), are embedded into text. The terminal
      interprets these sequences as commands, rather than text to display
      verbatim. [#]_

   SGR
      ..sequence is a subtype of :term:`ANSI` escape sequences with a varying
      amount of parameters. SGR sequences used for changing the color of text or/and
      terminal background (in 3 different color modes), as well as for
      decorating text with italic font, underline, overline, cross-line, making
      it bold or blinking etc. Represented by `SequenceSGR` class.


.. [#] https://en.wikipedia.org/wiki/ANSI_escape_code


================
Core methods
================

.. autosummary::

   ansi.SequenceSGR
   term.make_color_256
   term.make_color_rgb
   color.Color256.to_sgr
   color.find_closest



.. rubric:: Sources

1. `XTerm Control Sequences <https://invisible-island.net/xterm/ctlseqs/ctlseqs.html>`_
2. `ECMA-48 specification <https://www.ecma-international.org/publications-and-standards/standards/ecma-48/>`_
