.. _features:

#####################
Features
#####################

One of the core concepts of the library is `Span` class. ``Span`` is a combination of two control sequences;
it wraps specified string with pre-defined leading and trailing SGR definitions.

Example code:

.. ..literalinclude:: /examples/ex_0_features.py
   :linenos:

==================================
Content-aware format nesting
==================================

Compose text spans with automatic content-aware span termination. Preset spans can safely overlap with each
other (as long as they require different *breaker* sequences to reset).

.. ..literalinclude:: /examples/ex_20_content_aware_nesting.py
   :linenos:

.. image:: /_static/ex_10.png
   :width: 50%
   :align: center
   :class: no-scaled-link


==================================
Flexible sequence builder
==================================

Create your own `SGR sequences <SequenceSGR>` using default constructor, which accepts color/attribute keys,
integer codes and even existing *SGRs*, in any amount and in any order. Key resolving is case-insensitive.

.. ..literalinclude:: /examples/ex_30_flexible.py
   :linenos:


==================================
256 colors / True Color support
==================================

The library supports extended color modes:

- XTerm 256 colors indexed mode (see `ansi-presets`);
- True Color RGB mode (16M colors).

.. ..literalinclude:: /examples/ex_40_ext_colors.py
   :linenos:

.. image:: /_static/ex_40.png
   :width: 50%
   :align: center
   :class: no-scaled-link


==================================
Customizable output formats
==================================


.. todo ::

   @TODOTODO


==================================
String and number formatters
==================================

.. todo ::

   @TODOTODO
