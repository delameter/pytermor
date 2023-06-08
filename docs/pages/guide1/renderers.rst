.. _guide.renderers:

########################
Renderers
########################

.. _guide.renderer_setup:

---------------------------
Renderer setup
---------------------------

The library provides options to select the output format, and that option
comes in the form of :term:`renderers <rendering>`.

Selecting the renderer can be accomplished in several ways:

  a. By using general-purpose functions `render()<text.render>` and
     `echo()<text.echo()>` -- both have an argument ``renderer`` (preferrable;
     *introduced in v2.x*).
  b. Method `RendererManager.set_default()` sets the default renderer globally.
     After that calling `render()<text.render>` will automatically invoke a
     said renderer and apply the required formatting (but only if ``renderer``
     argument of ``render()`` method is left empty).
  c. Set up the config variable :term:`Config.renderer_class` directly or
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

---------------------------
Default renderers priority
---------------------------

When it comes to the rendering, `RendererManager` will use the first non-empty
renderer from the list below, skipping the undefined elements:

   1. Explicitly specified as argument ``renderer`` in methods
      `render()<text.render>`, `echo()<text.echo>`, `echoi()<text.echoi>`.
   2. Default renderer in global `RendererManager` class (see
      `RendererManager.set_default()`)
   3. Renderer class in the current loaded library config:
      :term:`Config.renderer_class`.
   4. Value from environment variable :env:`PYTERMOR_RENDERER_CLASS`.
   5. Default library renderer `SgrRenderer`.

   Argument > RendererManager > Config > Environment > Library's default


----------------
Class hierarchy
----------------

.. inheritance-diagram::  pytermor.renderer
   :parts: 1
   :top-classes:          pytermor.renderer.IRenderer
   :caption:             `IRenderer` inheritance tree

.. todo ::

   Win32Renderer ?
