.. _guide.advanced-seq-types:

##############################
Exotic sequence types
##############################

Sequences can be divided to 4 different classes depending on their *introducer*
byte(s); class represent the general purpose of the sequence and application
domain. There is 4 of them according to `ECMA-48`_ specification -- **nF**,
**Fp**, **Fe**, **Fs**.

.. sidebar::

   :nobr:`0x20-0x2F` |nbspt| :kbd:` "#$%&'()*+,-./`

**nF** escape sequences are mostly used for ANSI/ISO code-switching
mechanisms. All **nF**-class sequences start with ``ESC`` plus ASCII byte
from the range :hex:`0x20-0x2F`. They are represented by `SequenceNf` class
without any specific implementations.

**fP**-class sequences can be used for invoking private control functions.
The characteristic property is that the first byte after ``ESC`` is always
in range :hex:`0x30-0x3F` (``0``-``9``, ``:``, ``;``, ``<``, ``=``, ``>``, ``?``).
They are represented by `SequenceFp` class, which, for example, runs the
assembly of :abbr:`DECSC <Save Cursor>` and :abbr:`Restore Cursor (DECRC)`
sequence types.

.. sidebar::

   (space, ``!``, ``"``, ``#``, ``$``, ``%``, ``&``, ``'``, ``(``, ``)``, ``*``, ``+``, ``,``, ``-``, ``.``, ``/``).


**Fe**-class sequences are the most common ones and 99% of the sequences
you will ever encounter will be of **Fe** class. `ECMA-48`_ names them
"C1 set sequences", and their *introducer* byte (the one right after
escape byte) is from :hex:`0x40` to :hex:`0x5F` range (``@``, ``[``, ``\\``,
``]``, ``_``, ``^`` and capital letters ``A``-``Z``).

These sequences are implemented in `SequenceFe` parent class, which is then
subclassed by even more specificp=-classes `SequenceST`, `SequenceOSC`,
`SequenceCSI` and *(drums)* `SequenceSGR` -- the one responsible for
setting the terminal colors and formats, or at least the j

time the developer usually sare the sequences that gonna be encountered

jAt the time of writing
(v2.73) `ansi` module contains the implementations of about 25 control sequence
types.

The main principle of `pytermor` development was the rule "if I don't see it,
it doesn't exist", which should be read as "Don't waste days and nights on
specs comprehension and implementation of the features no one ever will use".


 .. _`ECMA-48`: https://www.ecma-international.org/publications-and-standards/standards/ecma-48/
