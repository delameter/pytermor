.. _guide.docs-guidelines:

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

- Library classes, methods, etc. should be enclosed in single backticks in order to become a hyperlinks:

   ```SgrRenderer.render()``` |rarr| `SgrRenderer.render()`

- Argument names and string literals that include escape sequences or their fragments should be wrapped in double backticks:

   ````arg1```` |rarr| ``arg1``

   ````ESC [31m ESC [m```` |rarr| ``ESC [31m ESC [m``

  On the top of that, ESC control char should be padded with spaces for better readability. This also triggers automatic application of custom style for even more visual difference.

- Any formula should be formatted using LaTeX syntax (``:math:`` role or
  ``.. math::`` directive):

   .. math::
      d_{min} = 350*10^{-3}

- Hexadecimal numbers should be displayed using ``:hex:`` role (applies to all
  examples below except the last one). In general, when the characters are
  supposed to be typed manually, or when the result length is 6+ chars, it's
  better to use lower case; when the numbers are distinct or "U+" notation is
  used, the upper case is acceptable:

   separate bytes
      :hex:`0x1B 0x23 0x88`

   Unicode codepoints
      :hex:`U+21BC` ; :hex:`U+F0909`

   hex dump
      :hex:`"0x 00AF 00BB 96CA"` ; :hex:`"0x 80 80 11 BD AA B5"`

   memory address or size
      :hex:`0000:9cf0`

   RGB colors (*int*/*str* forms)
      :hex:`0xeb0c0c` ; :hex:`#ff00ff`

   escaped strings

      .. code-block:: python

         "\u21bc", "\U000f0909", re.compile(R"\x1b\[[0-9;]*m")


==================
References
==================

+------------------+-------------------------------------------+-------------------------------------+
| Type             | Code                                      |  Example                            |
+==================+===========================================+=====================================+
|                  | .. code-block:: rst                       |                                     |
| Internal pydoc   |                                           | use `SgrRenderer.render()`          |
|                  |    use `SgrRenderer.render()`             |                                     |
+------------------+-------------------------------------------+-------------------------------------+
|                  | .. code-block:: rst                       |                                     |
| Internal page    |                                           | called `renderers<guide.renderers>` |
|                  |    called `renderers<guide.renderers>`    |                                     |
+------------------+-------------------------------------------+-------------------------------------+
|                  | .. code-block:: rst                       |                                     |
| Internal anchor  |                                           | `References`_                       |
|                  |    `References`_                          |                                     |
+------------------+-------------------------------------------+-------------------------------------+
|                  | .. code-block:: rst                       |                                     |
| External pydoc   |                                           | see :class:`logging.NullHandler`    |
|                  |    see `:class:`logging.NullHandler``     |                                     |
+------------------+-------------------------------------------+-------------------------------------+
|                  | .. code-block:: rst                       |                                     |
| External page    |                                           | https://github.com                  |
|                  |    `https://github.com`                   |                                     |
+------------------+-------------------------------------------+-------------------------------------+


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
