.. _guide.core-api-1:

##########################
Core API I
##########################

================
Glossary
================

.. glossary::

   rendering
      A process of transforming text-describing instances into specified
      output format, e.g. instance of `Fragment` class with content and
      :py:class:`.Style` class containing colors and other text formatting can be
      rendered into terminal-compatible string with `SgrRenderer`, or into
      HTML markup with `HtmlRenderer`, etc.

   style
      Class describing text format options: text color, background color,
      boldness, underlining, etc. Styles can be inherited and merged
      with each other. See :py:class:`.Style` constructor description for the details.

   color
      Three main classes describing the colors: `Color16`, `Color256` and `ColorRGB`.
      The first one corresponds to 16-color terminal mode, the second -- to
      256-color mode, and the last one represents full RGB color space and filled
      with
      rather than color index palette. The first two also contain terminal
      :term:`SGR` bindings.


================
Core methods
================

.. autosummary::

   text.render
   text.echo
   color.resolve_color
   style.make_style
   style.merge_styles
