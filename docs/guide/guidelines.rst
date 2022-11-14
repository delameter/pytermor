.. _guide.guidelines:

.. default-role:: any

=======================================
Documentation guidelines
=======================================

*(mostly as a reminder for myself)*

- Use single backticks for library classes/methods/modules, i.e. anything that can be transformed into a hyperlink: 
   * ```ColorRGB.to_sgr()``` -> `ColorRGB.to_sgr()`
- Use double backticks for parameter names and string literals that include ASCII control codes: 
   * ````param1```` -> ``param1``
   * ````ESC[31m```` -> ``ESC[31m``
- Use italics for basic types and built-in values:
   * ``*True*`` -> *True*  
   * ``*None*`` -> *None*
   * ``*int*`` -> *int*
