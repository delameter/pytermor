##########################
Core API
##########################


So, what's happening under the hood?

================
Glossary
================

.. glossary::

   ANSI escape sequence
      is a standard for in-band signaling to control cursor location, color,
      font styling, and other options on video text terminals and terminal
      emulators. Certain sequences of bytes, most starting with an ASCII escape
      character and a bracket character, are embedded into text. The terminal
      interprets these sequences as commands, rather than text to display
      verbatim. [#]_

   SGR
      :term:`ANSI escape sequence` with varying amount of parameters. SGR sequences
      allow to change the color of text or/and terminal background (in 3 different
      color spaces) as well as decorate text with italic style, underlining,
      overlining, cross-lining, making it bold or blinking etc. Represented by
      `SequenceSGR` class.


.. [#] https://en.wikipedia.org/wiki/ANSI_escape_code


================
Core methods
================

.. autosummary::

   ansi.SequenceSGR
   term.make_color_256
   term.make_color_rgb
   color.Color256.to_sgr



.. rubric:: Sources

1. `XTerm Control Sequences <https://invisible-island.net/xterm/ctlseqs/ctlseqs.html>`_
2. `ECMA-48 specification <https://www.ecma-international.org/publications-and-standards/standards/ecma-48/>`_
