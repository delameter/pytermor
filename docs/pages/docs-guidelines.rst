.. _docs-guidelines:

##########################
Docs guidelines
##########################

.. rst-class:: right

   :comment:`(mostly as a reminder for myself)`

=================
General
=================

- Basic types and built-in values should be surrounded with asterisks:

   ``*True*`` |rarr| *True*

   ``*None*`` |rarr| *None*

   ``*int*`` |rarr| *int*

- Library classes, methods, etc. should be enclosed in single backticks in order
  to become a hyperlinks:

   ```SgrRenderer.render()``` |rarr| `SgrRenderer.render()`

  If class name is ambiguous (e.g., there is a glossary term with the same
  name), the solution is to specify the type explicitly:

    ``:class:`.Style``` |rarr| :class:`.Style`

- Argument names and string literals should be wrapped in double backticks:

  ````arg1```` |rarr| ``arg1``

-

.. table::
   :widths: 1 10 10

   +-----------------------------------------------------------------------------------+
   |                                                                                   |
   | Abbreviations should utilize sphinx's default role for that:                      |
   |                                                                                   |
   +---+---------------------------------------+---------------------------------------+
   |   | .. code-block:: rst                   |                                       |
   |   |                                       |  :abbr:`EL (Erase in Line)`           |
   |   |    :abbr:`EL (Erase in Line)`         |                                       |
   +---+---------------------------------------+---------------------------------------+
   |                                                                                   |
   | Any formula should be formatted using LaTeX syntax (``:math:`` role or            |
   | ``.. math::`` directive):                                                         |
   |                                                                                   |
   +---+---------------------------------------+---------------------------------------+
   |   | .. code-block:: rst                   |                                       |
   |   |                                       | .. math::                             |
   |   |    .. math::                          |       d_{min} = 350*10^{-3}           |
   |   |          d_{min} = 350*10^{-3}        |                                       |
   +---+---------------------------------------+---------------------------------------+
   |                                                                                   |
   | Inlined definitions should be formatted with ``:def:`` text role:                 |
   |                                                                                   |
   +---+---------------------------------------+---------------------------------------+
   |   | .. code-block:: rst                   |                                       |
   |   |                                       | | :def:`classifier` for 1st time ...  |
   |   |    :def:`classifier` for 1st time ... | |  ... or *classifier* later          |
   |   |     ... or *classifier* later         |                                       |
   +---+---------------------------------------+---------------------------------------+

===================
Custom text roles
===================

- Sequences with ESC control char should be enclosed in a custom text role
  ``:ansi:`` to visually distinguish the ESC from regular chars:

    ``:ansi:`ESC[m``` |rarr| :ansi:`ESC[m`

- *(deprecated)* Another approach is to just pad the ESC with spaces
  and include in literal text span. This triggers automatic application
  of custom style, but only for HTML, and is useless for e.g. PDF:

   ````ESC [31m ESC [m```` |rarr| ``ESC [31m ESC [m``

- Config options and corresponding environment variables both have a dedicated
  custom text roles:

    ``:option:`renderer_classname``` |rarr| :option:`renderer_classname`

    ``:envvar:`PYTERMOR_RENDERER_CLASSNAME``` |rarr| :envvar:`PYTERMOR_RENDERER_CLASSNAME`

- Colors should be defined using special role ``:colorbox:``:

    - ``:colorbox:`0xBADA90``` |rarr| :colorbox:`0xBADA90`

    - ``:colorbox:`icathian-yellow``` |rarr| :colorbox:`icathian-yellow`

=================
Hexadecimals
=================

Hexadecimal numbers should be displayed using ``:hex:`` role (applies to all
examples below except the last one). In general, when the characters are
supposed to be typed manually, or when the result length is 6+ chars, it's
better to use lower case; when the numbers are distinct or "U+" notation is
used, the upper case is acceptable:

separate bytes
   :hex:`0x1B 0x23 0x88`

Unicode codepoints
   :hex:`U+21BC` ; :hex:`U+F0909`

hex dump
   :hex:`"0x 00 AF 00 BB  11 BD AA B5"`

UTF-8
   :hex:`e0a489 efbfbe efbfaf f0af8cb3`

RGB colors (*int*/*str* forms)
   :hex:`0xeb0c0c` ; :hex:`#ff00ff`

escaped strings
    ::

        import re
        "\u21bc", "\U000f0909", re.compile(R"\x1b\[[0-9;]*m")


==================
References
==================

+------------------+---------------------------------------+---------------------------------------+
|                  | .. code-block:: rst                   | `github`_ and                         |
| External         |                                       | `gitlab <//gitlab.com>`_              |
| pages            |    `github`_ and                      |                                       |
|                  |    `gitlab <//gitlab.com>`_           | .. _github: //github.com              |
|                  |                                       |                                       |
|                  |    .. _github: //github.com           |                                       |
+------------------+---------------------------------------+---------------------------------------+
|                  | .. code-block:: rst                   |                                       |
| External pydoc   |                                       | :class:`re.Match`                     |
|                  |    :class:`re.Match`                  |                                       |
+------------------+---------------------------------------+---------------------------------------+
|                  | .. code-block:: rst                   |                                       |
| Internal page    |                                       | `guide-lo` or                         |
|                  |    `guide-lo` or                      | `high-level <guide-hi>`               |
|                  |    `high-level <guide-hi>`            |                                       |
+------------------+---------------------------------------+---------------------------------------+
|                  | .. code-block:: rst                                                           |
| Internal page    |    :linenos:                                                                  |
| setup            |                                                                               |
|                  |    .. _guide.core-api-1:                                                      |
+------------------+---------------------------------------+---------------------------------------+
|                  | .. code-block:: rst                   |                                       |
| Internal pydoc   |                                       | `wait_key()`,                         |
|                  |    `wait_key()`,                      | :class:`.Style`                       |
|                  |    :class:`.Style`                    |                                       |
+------------------+---------------------------------------+---------------------------------------+
|                  | .. code-block:: rst                   |                                       |
| Internal anchor  |                                       | `References`_                         |
|                  |    `References`_                      |                                       |
+------------------+---------------------------------------+---------------------------------------+
|                  | .. code-block:: rst                   |                                       |
| Term in glossary |                                       | :term:`rendering`                     |
|                  |    :term:`rendering`                  |                                       |
+------------------+---------------------------------------+---------------------------------------+


=================
Headers
=================
.. chapter header

----------------
Section header
----------------

Subsection header
-------------------

Paragraph header
""""""""""""""""""

.. rubric:: Rubric

.. code-block:: rst

   ##########################
   Docs guidelines
   ##########################
   .. part header

   =================
   Headers
   =================
   .. chapter header

   ----------------
   Section header
   ----------------

   Subsection header
   -------------------

   Paragraph header
   """"""""""""""""""

   .. rubric:: Rubric

   .. code-block:: rst

      ...

===================
Admonitions Primer
===================


.. grid:: 3
  :gutter: 2

  .. grid-item-card::

     .. danger::
         For injecting the library into an existing project. A coloured icon: :octicon:`report;1em;sd-text-info`, some more text.


  .. grid-item-card::

     .. error::
         Downloading source code for running some predefined examples.

  .. grid-item-card::

     .. attention::
        Tracking of visited objects is not performed by default.

  .. grid-item-card::

     .. important::
         Template tags and non-closing `Fragments <Fragment>` allow to build complex formats.

  .. grid-item-card::

     .. caution::
         Python 3.8 or later should be installed and available in ``$PATH``.

  .. grid-item-card::

     .. warning::
         Registry containing more than 2400 named colors, in addition to
         default 256 from ``xterm`` palette.

  .. grid-item-card::

     .. todo::
         This is how `SgrRenderer` output can be seen in a terminal emulator.

  .. grid-item-card::

     .. tip::
         A color defined in any of these can be transparently translated into any other.

  .. grid-item-card::

     .. hint::
         `guide.fargs` allows to compose formatted text parts much faster.

  .. grid-item-card::

     .. note::
         The library supports XTerm 256 colors indexed mode and True Color RGB mode.

  .. grid-item-card::

     .. admonition:: Custom title

         `Renderers <guide.renderers>` are classes responsible for creating
         formatted strings from `IRenderable` instances.
