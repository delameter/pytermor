.. _guide.renderers:

########################
Renderers
########################

.. _guide.renderer_setup:

===========================
Renderer setup
===========================

The library provides options to select the output format, and that option
comes in the form of :term:`renderers <rendering>` .

Selecting the renderer can be accomplished in several ways:

  a. By using general-purpose functions `render()<text.render>` and
     `echo()<text.echo()>` -- both have an argument ``renderer`` (preferrable;
     *introduced in v2.x*).
  b. Method `RendererManager.set_default()` sets the default renderer globally.
     After that calling `render()<text.render>` will automatically invoke a
     said renderer and apply the required formatting (but only if ``renderer``
     argument of ``render()`` method is left empty).
  c. Set up the config variable `Config.renderer_class` directly or
     via environment variable.
  d. Use renderer's instance method `IRenderer.render()` directly,
     but that's not recommended and possibly will be deprecated in the future.

Generally speaking, if you need to invoke a custom renderer just once, it's
convenient to use the first method for this matter, and use the second one
in all the other cases.

On the contrary, if there is a necessity to use more than one renderer
alternatingly, it's better to avoid using the global one at all, and just
instantiate and invoke both renderers independently.

.. rubric :: TL;DR

To unconditionally print formatted message to standard output, call
`force_ansi_rendering()` and then `render()<text.render>`.


.. _guide.renderer_priority:

===========================
Default renderers priority
===========================

When it comes to the rendering, `RendererManager` will use the first non-empty
renderer from the list below, skipping the undefined elements:

   1. Explicitly specified as argument ``renderer`` in methods
      `render()<text.render>`, `echo()<text.echo>`, `echoi()<text.echoi>`.
   2. Default renderer in global `RendererManager` class (see
      `RendererManager.set_default()`)
   3. Renderer class in the current loaded library config:
      `Config.renderer_class`.
   4. Value from environment variable :env:`PYTERMOR_RENDERER_CLASS`.
   5. Default library renderer `SgrRenderer`.

   Argument > RendererManager > Config > Environment > Library's default


.. _guide.output_mode_select:

===========================
Output mode auto-selection
===========================

`SgrRenderer` can be set up with automatic output mode `OutputMode.AUTO`.
In that case the renderer will return `OutputMode.NO_ANSI` for any output device
other than terminal emulator, or try to find a matching rule from this list:

.. |ANY| replace:: :aux:`<any>`

.. |CV_FORCE| replace:: :ref:`Config.force_output_mode`
.. |CV_DEFAULT| replace:: :ref:`Config.default_output_mode`

.. table:: Auto output mode parameters and results

   +--------+---------------------------+---------------+--------------------+
   | Is a   | ``TERM``                  | ``COLORTERM`` | Result             |
   | tty?   | env. var                  | env. var [#]_ | output mode        |
   +========+===========================+===============+====================+
   |                      |ANY|                         | |CV_FORCE| [#]_    |
   +--------+---------------------------+---------------+--------------------+
   | No     |                   |ANY|                   | `NO_ANSI`          |
   +--------+---------------------------+---------------+--------------------+
   |        | ``xterm-256color``        | ``24bit``,    | `TRUE_COLOR`       |
   | Yes    |                           | ``truecolor`` |                    |
   |        +---------------------------+---------------+--------------------+
   |        | ``*-256color`` [#]_       |     |ANY|     | `XTERM_256`        |
   |        +---------------------------+---------------+--------------------+
   |        | ``xterm-color``           |     |ANY|     | `XTERM_16`         |
   |        +---------------------------+---------------+--------------------+
   |        | ``xterm``                 |     |ANY|     | `NO_ANSI`          |
   |        +---------------------------+---------------+--------------------+
   |        | :aux:`<any other>`        |     |ANY|     | |CV_DEFAULT| [#]_  |
   +--------+---------------------------+---------------+--------------------+

..

   .. [#] should both env. var requirements be present, they both must be true
          as well (i.e. logical AND is applied).

   .. [#] empty by default and thus ignored

   .. [#] ``*`` represents any string; that's how e.g. *bash 5*
          determines the color support.

   .. [#] `XTERM_256` by default, but can be customized.

.. graphviz:: /_include/sgr-output-mode.dot
    :caption: Auto output mode algorithm


.. _guide.renderer_class_diagram:

========================================
:fas:`sitemap` Renderer class hierarchy
========================================

.. inheritance-diagram::  pytermor.renderer
   :parts: 1
   :top-classes:          pytermor.renderer.IRenderer
   :caption:             `IRenderer` inheritance tree
