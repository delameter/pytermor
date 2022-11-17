.. _guide.guidelines:

=======================================
Documentation guidelines
=======================================

.. rst-class:: right

*(mostly as a reminder for myself)*


- Basic types and built-in values should be surrounded with asterisks:

   ``*True*`` |rarr| *True*

   ``*None*`` |rarr| *None*

   ``*int*`` |rarr| *int*

- Library classes, methods, etc. should be enclosed in single backticks in order to become a hyperlinks:

   ```SgrRenderer.render()``` |rarr| `SgrRenderer.render()`

- Parameter names and string literals that include escape sequences or their fragments should be wrapped in double backticks:

   ````param1```` |rarr| ``param1``

   ````[31m```` |rarr| ``[31m``

  On the top of that ASCII control chars should be written within ``:kbd:`` for better readability:

  ``ESC]8;;http://localhostESC\\TextESC]8;;ESC\\``

  |e|\ ``]8;;http://localhost``\ |e|\ ``\\Text``\ |e|\ ``]8;;``\ |e|\ ``\\``

  ::

   |e|\ ``]8;;http://localhost``\ |e|\ ``\\Text``\ |e|\ ``]8;;``\ |e|\ ``\\``

  ``|e|`` is a globally registered replacer of ``:kbd:`ESC```.
