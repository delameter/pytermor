.. _config:

.. currentmodule:: pytermor.config

#######################################
Configuration
#######################################

The library initializes it's own config class right before first read
attempt via `ConfigManager.get()`. There are 3 ways to customize the setup:

    a) create new :class:`Config` instance from scratch and make it current with
       `ConfigManager.set()`:

       >>> from pytermor import ConfigManager, Config
       >>> ConfigManager.set(Config(force_output_mode='auto'))

    b) modify attribute(s) of exising :class:`Config` instance returned by
       `ConfigManager.get()`, e.g.:

       >>> ConfigManager.get().prefer_rgb = False

    c) preliminarily set the corresponding :envvar:`\ ` environment variable(s) to required
       values, and config manager will catch them up upon initialization (upon
       first read access, to be preciese). This method is suitable for the
       development or debugging.

       .. admonition:: Docs formatting

          This is how env. var names are rendered in docs: :envvar:`ENVVAR_NAME`

          And these are configuration option names: :option:`option_name`


.. _options:

=================
Options
=================

.. option:: renderer_classname

    :envvar:`PYTERMOR_RENDERER_CLASSNAME`

    Sets default renderer class (e.g. ``TmuxRenderer``). Default renderer
    class is used for rendering if there is no explicitly specified one. Corresponding
    environment variable is . See also: `guide.renderer_priority`.

.. option::  force_output_mode

   :envvar:`PYTERMOR_FORCE_OUTPUT_MODE`

   is a standard for in-band signaling to control cursor location, color,
   font styling, and other options on video text terminals and terminal
   emulators. Certain sequences of bytes, most starting with an ASCII escape
   character and a bracket character, are embedded into text. The terminal
   interprets these sequences as commands, rather than text to display
   verbatim.


.. option:: default_output_mode

   :envvar:`PYTERMOR_DEFAULT_OUTPUT_MODE`

   is a standard for in-band signaling to control cursor location, color,
   font styling, and other options on video text terminals and terminal
   emulators. Certain sequences of bytes, most starting with an ASCII escape
   character and a bracket character, are embedded into text. The terminal
   interprets these sequences as commands, rather than text to display
   verbatim.

.. option:: prefer_rgb

  :envvar:`PYTERMOR_PREFER_RGB`

  is a standard for in-band signaling to control cursor location, color,
  font styling, and other options on video text terminals and terminal
  emulators. Certain sequences of bytes, most starting with an ASCII escape
  character and a bracket character, are embedded into text. The terminal
  interprets these sequences as commands, rather than text to display
  verbatim.

.. option:: trace_renders

  :envvar:`PYTERMOR_TRACE_RENDERS`

  is a standard for in-band signaling to control cursor location, color,
  font styling, and other options on video text terminals and terminal
  emulators. Certain sequences of bytes, most starting with an ASCII escape
  character and a bracket character, are embedded into text. The terminal
  interprets these sequences as commands, rather than text to display
  verbatim. yare-yare-daze
