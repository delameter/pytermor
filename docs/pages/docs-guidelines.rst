.. _docs-guidelines:

##########################
Docs guidelines
##########################

.. highlight:: rst

.. rst-class:: right

   :comment:`(mostly as a reminder for myself)`

====================
Built-in text roles
====================

- Basic types and built-in values should be surrounded with asterisks:

   * ``*True*`` |rarr| *True*

   * ``*None*`` |rarr| *None*

   * ``*int*`` |rarr| *int*

- Library classes, methods, etc. should be enclosed in single backticks in order
  to become a hyperlinks:

   ```SgrRenderer.render()``` |rarr| `SgrRenderer.render()`

  If class name is ambiguous (e.g., there is a glossary term with the same
  name), the solution is to specify the type explicitly:

    ``:class:`.Style``` |rarr| :class:`.Style`

- Argument names and string literals should be wrapped in double backticks:

    ````arg1```` |rarr| ``arg1``

- Abbreviations should utilize sphinx's default role for that:

    ``:abbr:`EL (Erase in Line)``` |rarr| :abbr:`EL (Erase in Line)`

- Any formula should be formatted using LaTeX syntax (``:math:`` role or ``.. math::`` directive):

    ``:math:`d_{min} = 350*10^{-3}```

    |rarr|  :math:`d_{min} = 350*10^{-3}`

- Inlined definitions should be formatted with ``:def:`` text role:

    ``:def:`term` for 1st time... or *term* later``

    |rarr|  :def:`term` for 1st time... or *term* later

-----------
References
-----------

External page setup
    ``.. _github: //github.com``

External page
    ```github`_`` |rarr| `github`_

.. _github: //github.com

External page inlined
    ```gitlab <//gitlab.com>`_`` |rarr| `gitlab <//gitlab.com>`_

External pydoc
    ``:class:`re.Match``` |rarr| :class:`re.Match`

Internal page setup
    ``.. _guide.core-api-1:``

Internal page
    ```guide.core-api-1``` |rarr| `guide.core-api-1`

Internal page custom label
    ```CORE I <guide.core-api-1>``` |rarr| `CORE I <guide.core-api-1>`

Internal pydoc
    * ```wait_key()``` |rarr| `wait_key()`
    * ``:class:`.Style``` |rarr| :class:`.Style`

Internal anchor
    ```References`_`` |rarr| `References`_

Term in glossary
    ``:term:`rendering``` |rarr| :term:`rendering`


===================
Custom text roles
===================

- Sequences with ESC control char should be enclosed in a custom text role
  ``:ansi:`` to visually distinguish the ESC from regular chars:

    ``:ansi:`ESC[m``` |rarr| :ansi:`ESC[m`

- Config options and corresponding environment variables both have a dedicated
  custom text roles:

    * ``:option:`renderer_classname``` |rarr| :option:`renderer_classname`

    * ``:envvar:`PYTERMOR_RENDERER_CLASSNAME``` |rarr| :envvar:`PYTERMOR_RENDERER_CLASSNAME`

- Colors should be defined using special role ``:colorbox:``:

    * ``:colorbox:`0xBADA90``` |rarr| :colorbox:`0xBADA90`

    * ``:colorbox:`icathian-yellow``` |rarr| :colorbox:`icathian-yellow`

--------------------
Hexadecimals
--------------------

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


=================
Structure
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

::

   ##########################
   Docs guidelines
   ##########################
   .. part header

   =================
   Structure
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

   ::

      ...

===================
Admonitions primer
===================

 .. danger::
     <danger>

 .. error::
     <error>

 .. attention::
    Tracking of visited objects is not performed by default, i.e., circular
    references and self-references will be unpacked again and again endlessly,
    until max recursion depth limit exceeds with a ``RecursionError``.

 .. important::
     Approximator implementation is selected automatically depending on availability of
     `numpy` and `scipy` packages.

 .. caution::
     <caution>

 .. warning::
     Sending this sequence to the terminal may **block** infinitely. Consider
     using a thread or set a timeout for the main thread using a signal.

 .. todo::
     There is no actual need in this superclass, better merge it into `ResolvableColor`.

 .. tip::
     A hint with type of the change shows up when icon is hovered with the mouse pointer.

 .. hint::
     <hint>

 .. note::
     Known limitation of this approach is inability to correctly handle
     multi-cased queries which include transitions between lower case
     and upper case in the middle of the word...

 .. admonition:: Terminal-based rendering

    Terminals apply this effect to foreground (=text) color, but when
    it's used together with `inversed`, they usually make the background
    darker instead.
