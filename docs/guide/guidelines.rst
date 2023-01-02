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

- Argument names and string literals that include escape sequences or their fragments should be wrapped in double backticks:

   ````arg1```` |rarr| ``arg1``

   ````ESC [31m ESC [m```` |rarr| ``ESC [31m ESC [m``

  On the top of that, ESC control char should be padded with spaces for better readability. This also triggers automatic application of custom style for even more visual difference.

- Any formula should be formatted using LaTeX syntax (``:math:`` role or
  ``.. math::`` directive):

   .. math::
      d_{min} = 350*10^{-3}
