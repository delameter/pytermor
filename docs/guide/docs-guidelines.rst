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
.. code-block:: rst

   ----------------
   Section header
   ----------------

Subsection header
-------------------
.. code-block:: rst

   Subsection header
   -------------------

Paragraph header
""""""""""""""""""
.. code-block:: rst

   Paragraph header
   """"""""""""""""""


.. rubric:: Rubric
.. code-block:: rst

   .. rubric:: Rubric
