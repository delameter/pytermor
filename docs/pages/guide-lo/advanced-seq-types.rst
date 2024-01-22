.. _guide.advanced-seq-types:

##############################
ANSI sequences review
##############################

=====================
Sequence classes
=====================

Sequences can be divided to 4 different classes depending on their :def:`classifier`
byte(s); a class indicates the application domain the purpose of the sequence
in general. According to `ECMA-48`_ specification the classes are: **nF**,
**Fp**, **Fe**, **Fs**.

.. |u2x| replace:: ``!"#$%&'()*+\-./`` and space
.. |u3x| replace:: ``0123456789:;<=>?``
.. |u45x| replace:: ``@[\\]_^ABCDEFGHIJKLMNOPQRSTUVWXYZ``

- **nF** escape sequences are mostly used for ANSI/ISO code-switching
  mechanisms. All **nF**-class sequences start with :ansi:`ESC` plus ASCII byte
  from the range :hex:`0x20-0x2F`: ( |u2x| ).

  They are represented by :any:`SequenceNf` class without any specific implementations.

- **fP**-class sequences can be used for invoking private control functions.
  The characteristic property is that the first byte after :ansi:`ESC` is always
  in range :hex:`0x30-0x3F` (|u3x|).

  They are represented by :any:`SequenceFp` class, which, for example,
  assembles :abbr:`DECSC (Save Cursor)` and :abbr:`DECRC(Restore Cursor)`
  sequence types.

- **Fe**-class sequences are the most common ones and 99% of the sequences
  you will ever encounter will be of **Fe** class. ECMA-48 names them
  "C1 set sequences", and their *classifier* byte (the one right after
  escape byte) is from :hex:`0x40` to :hex:`0x5F` range (|u45x|).

  These sequences are implemented in `SequenceFe` parent class, which is then
  subclassed by even more specific classes `SequenceST`, `SequenceOSC`,
  `SequenceCSI` and *(drums)* `SequenceSGR` -- the one responsible for
  setting the terminal colors and formats (or at least the majority of them),
  and also the one that's going to be encountered most of the time. The examples
  include :abbr:`CUP (Cursor Position)`, :abbr:`ED (Erase in Display)`,
  aforementioned :abbr:`SGR (Set Graphic Rendition)` and much more.

- **Fs**-class sequences ...

   .. todo :: This

=========================
Sequence types
=========================

`ECMA-48`_ introduces a list of terminal control functions and contains the
implementation details and formats. Each of these usually has a 3+ letters
abbreviation (SGR, CSI, EL, etc.) which determines the action that will be
performed after the terminal receives control sequence of this function.
Let's identify these abbreviations as :def:`sequence types`.

At the time of writing (v2.75) `ansi` module contains the implementations of
about 25 control sequence types (that should be read as "has seperated classes
and/or factory methods and is also documented). However, ECMA-48 standard
mentions about 160 sequence types.

The main principle of `pytermor` development was the rule *"if I don't see it,
it doesn't exist"*, which should be read as "Don't waste days and nights on
specs comprehension and implementation of the features no one ever will use".

That's why the only types of sequences implemented are the ones that I personally
encountered in the modern environment (and having a practical application, of
course).

However, the library was designed to provide an easy way to extend the control
sequences class hierarchy; what's more, this includes not only the extendability
of the library itself (i.e., improvements in the context of library source code),
but also the extra logic in the client code referencing the library classes. In
case something important is missed -- there is an `Issues`_ page on the GitHub,
you are welcome to make a feature request.

 .. _`ECMA-48`: https://www.ecma-international.org/publications-and-standards/standards/ecma-48/
 .. _`Issues`: https://github.com/delameter/pytermor/issues
