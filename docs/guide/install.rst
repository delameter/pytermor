.. _guide.install:

.. default-role:: any

Getting started
===============================


-------------------
Installation
-------------------

.. code-block:: shell

   pip install pytermor


-------------------
Features
-------------------

One of the core concepts of the library is `Span` class. ``Span`` is a combination of two control sequences; it wraps specified string with pre-defined leading and trailing SGR definitions.

Example code:

.. literalinclude:: /_include/examples/ex_0_features.py
   :linenos:

.. rubric:: Content-aware format nesting

Compose text spans with automatic content-aware span termination. Preset spans can safely overlap with each other (as long as they require different *breaker* sequences to reset).

.. literalinclude:: /_include/examples/ex_20_content_aware_nesting.py
   :linenos:

.. image:: /_static/ex_10.png
   :width: 50%
   :align: center
   :class: no-scaled-link


.. rubric:: Flexible sequence builder

Create your own `SGR sequences <SequenceSGR>` with `build()` method, which accepts color/attribute keys, integer codes and even existing *SGRs*, in any amount and in any order. Key resolving is case-insensitive.

.. literalinclude:: /_include/examples/ex_30_flexible.py
   :linenos:


.. rubric:: 256 colors / True Color support

The library supports extended color modes:

- XTerm 256 colors indexed mode (see `xterm-colors`);
- True Color RGB mode (16M colors).

.. literalinclude:: /_include/examples/ex_40_ext_colors.py
   :linenos:

.. image:: /_static/ex_40.png
   :width: 50%
   :align: center
   :class: no-scaled-link


.. rubric:: Customizable output formats

@TODO


.. rubric:: String and number formatters

@TODO
