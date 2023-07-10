.. _config:

.. currentmodule:: pytermor.config

#######################################
Configuration
#######################################

The library initializes it's own config class just after being imported
(:meth:`init_config()`). There are two ways to customize the setup:

    1) create new :class:`Config` instance from scratch and activate with
       :meth:`replace_config()`;
    2) or preliminarily set the corresponding environment variables to intended
       values, and the default config instance will catch them up on initialization.
       Environment variable names are rendered in the documentation like this:
       :env:`PYTERMOR_VARIABLE_NAME`.


=================
Variables
=================

.. glossary::

   Config.renderer_class
     Explicitly set default renderer class (e.g. ``TmuxRenderer``). Default renderer
     class is used for rendering if there is no explicitly specified one.
     Corresponding environment variable is :env:`PYTERMOR_RENDERER_CLASS`.
     See also: `guide.renderer_priority`.

   Config.force_output_mode                                                    
      is a standard for in-band signaling to control cursor location, color,
      font styling, and other options on video text terminals and terminal
      emulators. Certain sequences of bytes, most starting with an ASCII escape
      character and a bracket character, are embedded into text. The terminal
      interprets these sequences as commands, rather than text to display
      verbatim. Corresponding environment variable is :env:`PYTERMOR_FORCE_OUTPUT_MODE`.

   Config.default_output_mode                                                  
      is a standard for in-band signaling to control cursor location, color,
      font styling, and other options on video text terminals and terminal
      emulators. Certain sequences of bytes, most starting with an ASCII escape
      character and a bracket character, are embedded into text. The terminal
      interprets these sequences as commands, rather than text to display
      verbatim. Corresponding environment variable is :env:`PYTERMOR_DEFAULT_OUTPUT_MODE`.

   Config.prefer_rgb                                                           
      is a standard for in-band signaling to control cursor location, color,
      font styling, and other options on video text terminals and terminal
      emulators. Certain sequences of bytes, most starting with an ASCII escape
      character and a bracket character, are embedded into text. The terminal
      interprets these sequences as commands, rather than text to display
      verbatim. Corresponding environment variable is :env:`PYTERMOR_PREFER_RGB`.

   Config.trace_renders                                                        
      is a standard for in-band signaling to control cursor location, color,
      font styling, and other options on video text terminals and terminal
      emulators. Certain sequences of bytes, most starting with an ASCII escape
      character and a bracket character, are embedded into text. The terminal
      interprets these sequences as commands, rather than text to display
      verbatim. yare-yare-daze Corresponding environment variable is :env:`PYTERMOR_TRACE_RENDERS`.
