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
     `echo()<text.echo()>` -- both have an argument ``renderer`` (preferable;
     *introduced in v2.x*).
  b. Method `RendererManager.override()` sets the default renderer globally.
     After that calling `render()<text.render>` will automatically invoke
     specified renderer and apply the required formatting (but only if ``renderer``
     argument of ``render()`` method is left empty).
  c. Set up the config variable :option:`renderer_classname` directly or
     preliminary via :envvar:`environment variable`.
  d. Use renderer's instance method `IRenderer.render()` directly,
     but that's not recommended and possibly will be deprecated in the future.

Generally speaking, if you need to invoke a custom renderer just once or twice, it's
convenient to use the first method for this matter, and use the second one
in all the other cases.

On the contrary, if there is a necessity to use more than one renderer
alternatingly, it's better to avoid using the global one at all, and just
instantiate and invoke both renderers independently.

.. rubric :: TL;DR

To unconditionally print formatted message to standard output, call
`force_ansi_rendering()` and then `render()<text.render>`.

See `Examples — Rendering <examples.rendering>` for practical applications.


.. _guide.renderer_priority:

===========================
Default renderers priority
===========================

When it comes to the rendering, `RendererManager` will use the **first non-empty**
renderer from the list below:

   1. Explicitly specified as argument ``renderer`` in methods
      `render()<text.render>`, `echo()<text.echo>`, `echoi()<text.echoi>`.
   2. Default renderer in global `RendererManager` class (see
      `RendererManager.override()`)
   3. Renderer class in the current loaded config:
      :ref:`config.renderer_classname`.
   4. Default library renderer `SgrRenderer`.

   .. important::

      Argument > `Global override<RendererManager.override>` > Current config > Library fallback

Also note that the approach of setting up a renderer with a config in one place
and overriding the global one in another can cause hard-to-catch bugs when the
attempts to change renderer mode with config value will seem to fail, whereas in
fact they work, but with no effect, as the renderer defined in config always gets
shadowed by a global override.

.. _guide.output_mode_select:

===========================
Output mode auto-selection
===========================

`SgrRenderer` can be set up with automatic output mode `AUTO`.
In that case the renderer will return `NO_ANSI` for any output device
other than terminal emulator, or try to find a matching rule from this list:
                                                            
.. |ANY| replace:: :aux:`<any>`

.. table:: Auto output mode parameters and results

   +-----------+---------------------+--------------------------+-------------------------------------+
   | Is a tty? | :envvar:`TERM`      | :envvar:`COLORTERM` [#]_ | Result output mode                  |
   +===========+=====================+==========================+=====================================+
   | |ANY|                                                      | :option:`force_output_mode` [#]_    |
   +-----------+---------------------+--------------------------+-------------------------------------+
   | No        | |ANY|                                          | `NO_ANSI`                           |
   +-----------+---------------------+--------------------------+-------------------------------------+
   | Yes       | ``xterm-256color``  | ``24bit``, ``truecolor`` | `TRUE_COLOR`                        |
   |           +---------------------+--------------------------+-------------------------------------+
   |           | ``*-256color`` [#]_ |          |ANY|           | `XTERM_256`                         |
   |           +---------------------+--------------------------+-------------------------------------+
   |           | ``xterm-color``     |          |ANY|           | `XTERM_16`                          |
   |           +---------------------+--------------------------+-------------------------------------+
   |           | ``xterm``           |          |ANY|           | `NO_ANSI`                           |
   |           +---------------------+--------------------------+-------------------------------------+
   |           | :aux:`<any other>`  |          |ANY|           | :option:`default_output_mode` [#]_  |
   +-----------+---------------------+--------------------------+-------------------------------------+

..

   .. [#] should both env. var requirements be present, they both must be true
          as well (i.e. logical AND is applied).

   .. [#] empty by default and thus ignored

   .. [#] ``*`` represents any string; that's how e.g. *bash 5*
          determines the color support.

   .. [#] `XTERM_256` by default, but can be customized.

.. graphviz:: /_include/sgr-output-mode.dot
    :caption: Auto output mode algorithm


====================
Color mode fallbacks
====================

There is a couple of approximation algorithms implemented in the library, the main purpose of which
is to provide a nearest color supported by a user's terminal emulator when the original color is defined
in a higher-order palette. For example, if user's terminal is only capable of displaying 256 colors, all
`ColorRGB` instances will be automatically approximated to the nearest color available in the palette.
Details described in :ref:`guide.finding_closest_color` section.


.. _guide.renderer_class_diagram:

========================================
:fas:`sitemap` Renderer class hierarchy
========================================

.. inheritance-diagram::  pytermor.renderer
   :parts: 1
   :top-classes:          pytermor.renderer.IRenderer
   :caption:             `IRenderer` inheritance tree
