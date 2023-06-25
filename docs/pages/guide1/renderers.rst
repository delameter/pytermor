.. _guide.renderers:

########################
Renderers
########################

.. _guide.renderer_setup:

===========================
Renderer setup
===========================

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
      :term:`Config.renderer_class`.
   4. Value from environment variable :env:`PYTERMOR_RENDERER_CLASS`.
   5. Default library renderer `SgrRenderer`.

   Argument > RendererManager > Config > Environment > Library's default


===========================
Output mode auto-select
===========================

.. graphviz ::

   digraph {
       rankdir = TB;
       nodesep = .2;
       ranksep = .33;
       splines=ortho;
       ratio=expand;
       size="8,6";

       node [
          fontname="Pragmasevka"
           fontsize=12
           margin=".125,.125"
           style="filled"
           color="#000000"
           fillcolor="#fbf8f8"
       ];
       edge [fontname = "Pragmasevka"  fontsize=10 ];

       start [shape=Mrecord label="START" style="filled,bold" fontname="ASM-Bold" fontsize=16 margin=".5,0"]
       is_config_force [shape=diamond label="<config.force>\nis set?"]
       is_a_tty [shape=diamond label="is a tty?" tailport=s]
       is_true [shape=diamond label="TERM=xterm-256color &&\n(COLORTERM=truecolor ||\nCOLORTERM=24bit) ?"]
       is_xterm [shape=diamond label="TERM=xterm ?"]
       is_256 [shape=diamond label="TERM=*-256color ?"]
       is_16 [shape=diamond label="TERM=xterm-color ?" ]

       node [margin=".25,.125" style="filled,bold" fontname="ASM-Bold" ]

       set_no_ansi [shape=Mrecord label="set\nNO_ANSI"]
       set_true_color [shape=Mrecord label="set\nTRUE_COLOR"]
       set_256 [shape=Mrecord label="set\nXTERM_256"]
       set_16 [shape=Mrecord label="set\nXTERM_16"]
       set_config_force [shape=Mrecord label="set\n\<config.force\>"]
       set_config_default [shape=Mrecord label="set\n\<config.default\>"]

       edge [labeldistance=1.5 labelangle=-45];

       start -> is_config_force []
       is_config_force -> is_a_tty [taillabel=no ]
       is_a_tty -> is_true [taillabel=yes ]
       is_true -> is_256 [taillabel=no ]
       is_256 -> is_16 [taillabel=no ]
       is_16 -> is_xterm [taillabel=no]

       edge [labeldistance=1.5 labelangle=45];

       is_xterm -> set_no_ansi [taillabel=yes minlen=1]
       is_config_force -> set_config_force [taillabel=yes minlen=6 tailport=e]
       is_a_tty -> set_no_ansi [taillabel=no]
       is_true -> set_true_color [taillabel=yes minlen=4 ]
       is_256 -> set_256 [taillabel=yes minlen=3]
       is_16 -> set_16 [taillabel=yes minlen=2 ]
       is_xterm -> set_config_default [taillabel=no]
   }


===========================
Renderer class hierarchy
===========================

.. inheritance-diagram::  pytermor.renderer
   :parts: 1
   :top-classes:          pytermor.renderer.IRenderer
   :caption:             `IRenderer` inheritance tree
