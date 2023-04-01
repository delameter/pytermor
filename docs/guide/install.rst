.. _guide.install:

#####################
Getting started
#####################

================
Installation
================

Python 3.8 or later should be installed and available in ``$PATH``; that's
basically it if intended usage of the package is as a library.

.. code-block:: console
   :caption: Installing into a project

   $ python -m pip install pytermor

.. code-block:: console
   :caption: Standalone installation (for developing or experimenting)

   $ git clone git@github.com:delameter/pytermor.git .
   $ python -m venv venv
   $ PYTHONPATH=. venv/bin/python -m pytermor
   v2.41.1-dev1:Feb-23


===========
Structure
===========

.. table::
   :widths: 5 10 15 70

   +-----+----------------------+----------------------+---------------------------------------------------------------------------------+
   | A L | Module               | Class(es)            | Purpose                                                                         |
   +=====+======================+======================+=================================================================================+
   | Hi  | :mod:`.text`         | `Text`               | Container consisting of text pieces each with attached ``Style``.               |
   |     |                      |                      | Renders into specified format keeping all the formatting.                       |
   |     |                      +----------------------+---------------------------------------------------------------------------------+
   |     |                      | `Style`              | Reusable abstractions defining colors and text attributes (text                 |
   |     |                      | `Styles`             | color, bg color, *bold* attribute, *underlined* attribute etc).                 |
   |     |                      +----------------------+---------------------------------------------------------------------------------+
   |     |                      | `SgrRenderer`        | ``SgrRenderer`` transforms ``Style`` instances into ``Color``, ``Span``         |
   |     |                      | `HtmlRenderer`       | and ``SequenceSGR`` instances and assembles it all up. There are                |
   |     |                      | `TmuxRenderer` etc.  | several other implementations depending on what output                          |
   |     |                      |                      | format is required.                                                             |
   |     +----------------------+----------------------+---------------------------------------------------------------------------------+
   |     | `color`              | `Color16`            | Abstractions for color operations in different color modes                      |
   |     |                      | `Color256`           | (default 16-color, 256-color, RGB). Tools for color approximation               |
   |     |                      | `ColorRGB`           | and transformations.                                                            |
   |     |                      +----------------------+---------------------------------------------------------------------------------+
   |     |                      | `Index`              | Color registry.                                                                 |
   +-----+----------------------+----------------------+---------------------------------------------------------------------------------+
   | Lo  | `ansi`               | `Span`               | Abstraction consisting of "opening" SGR sequence defined by the                 |
   |     |                      |                      | developer (or taken from preset list) and complementary "closing"               |
   |     |                      |                      | SGR sequence that is built automatically.                                       |
   |     |                      +----------------------+---------------------------------------------------------------------------------+
   |     |                      | `Spans`              | Registry of predefined instances in case the developer doesn't need dynamic     |
   |     |                      |                      | output formatting and just wants to colorize an error message.                  |
   |     |                      +----------------------+---------------------------------------------------------------------------------+
   |     |                      | `SequenceSGR`        | Abstractions for manipulating ANSI control sequences and                        |
   |     |                      | `SeqIndex`           | classes-factories, plus a registry of preset SGRs.                              |
   |     |                      +----------------------+---------------------------------------------------------------------------------+
   |     |                      | `IntCodes`           | Registry of escape control sequence parameters.                                 |
   |     +----------------------+----------------------+---------------------------------------------------------------------------------+
   |     | `util`               | \*                   | Additional formatters and common methods for manipulating strings with          |
   |     |                      |                      | SGRs inside.                                                                    |
   +-----+----------------------+----------------------+---------------------------------------------------------------------------------+


========
Features
========

One of the core concepts of the library is `Span` class. ``Span`` is a combination of two control sequences;
it wraps specified string with pre-defined leading and trailing SGR definitions.

Example code:

.. literalinclude:: /examples/ex_0_features.py
   :linenos:

.. rubric:: Content-aware format nesting

Compose text spans with automatic content-aware span termination. Preset spans can safely overlap with each
other (as long as they require different *breaker* sequences to reset).

.. literalinclude:: /examples/ex_20_content_aware_nesting.py
   :linenos:

.. image:: /_static/ex_10.png
   :width: 50%
   :align: center
   :class: no-scaled-link


.. rubric:: Flexible sequence builder

Create your own `SGR sequences <SequenceSGR>` using default constructor, which accepts color/attribute keys,
integer codes and even existing *SGRs*, in any amount and in any order. Key resolving is case-insensitive.

.. literalinclude:: /examples/ex_30_flexible.py
   :linenos:


.. rubric:: 256 colors / True Color support

The library supports extended color modes:

- XTerm 256 colors indexed mode (see `ansi-presets`);
- True Color RGB mode (16M colors).

.. literalinclude:: /examples/ex_40_ext_colors.py
   :linenos:

.. image:: /_static/ex_40.png
   :width: 50%
   :align: center
   :class: no-scaled-link


.. rubric:: Customizable output formats


.. todo ::

   @TODOTODO


.. rubric:: String and number formatters

.. todo ::

   @TODOTODO


==========
CLI usage
==========

Commands like the ones below can be used for quick experimenting without loading the IDE:

 - One-liner for system-wide installation :comment:`(which is not recommended)`:

   .. code-block:: console
      :class: highlight-adjacent

      $ python -c "import pytermor as pt; pt.echo('RED', 'red')"

   .. raw:: html

      <div class="highlight-adjacent">
         <div class="highlight">
            <pre><span style="color: red">red text</span></pre>
         </div>
      </div>

 - One-liner for virtual environment (`venv`) with `pytermor` pre-installed (see `Installation`_)
   :comment:`(note that the library source code root folder should be used as current working directory)`:

   .. code-block:: console
      :class: highlight-adjacent

      $ PYTHONPATH=. venv/bin/python -c "import pytermor as pt; pt.echo('GREEN', 'green')"

   .. raw:: html

      <div class="highlight-adjacent">
         <div class="highlight">
            <pre><span style="color: green;">green text</span></pre>
         </div>
      </div>

 - Interactive mode for virtual environment with `pytermor` pre-installed
   :comment:`(again, current working directory should be sources root dir)`:

   .. code-block:: console
      :class: highlight-adjacent

      $ PYTHONSTARTUP=.run-startup.py PYTHONPATH=. venv/bin/python -qi

   .. code-block:: python
      :class: highlight-adjacent

      python 3.8.10
      pytermor 2.41.1-dev1
      >>> pt.echo("This is warning, be warned", pt.Styles.WARNING)

   .. raw:: html

      <div class="highlight-adjacent">
         <div class="highlight">
            <pre><span style="color: orange;">This is warning, be warned</span></pre>
         </div>
      </div>
