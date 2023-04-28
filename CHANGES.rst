..
   > make update-changelist

pending
------------------
- |UPDATE| Update coverage.yml
- |MAINTAIN| pdf documentation
- |MAINTAIN| cleanup
- |MAINTAIN| (c) update
- |FIX| `flake8`
- |NEW|  `IRenderable.raw()` method
- |NEW| `cval` atlassian colors
- |REFACTOR| made `measure` and `trace` private
- |NEW| `utilmisc` color transform methods overloaded
- |DOCS| a lot
- |FIX| `pydeps` invocation
- |FIX|  `ESCAPE_SEQ_REGEX`
- |NEW| `contains_sgr` method
- |NEW|  `Text.split_by_spaces()`, `Composite`
- |NEW| +3 base sequence classes, +26 preset sequences

.. <@pending:770a83e>
.. ^ blank line before should be kept


v2.48-dev
------------------
:date:`Apr 23`

- |DOCS| small fixes
- |DOCS| updated changelog
- |FIX|  `measure_char_width` and `get_char_width` internal logic
- |FIX|  pipelines
- |FIX| `AbstractTracer` failure on empty input
- |FIX| `StaticFormatter` padding
- |FIX| bug in `SimpleTable` renderer when row is wider than a terminal
- |FIX| debug logging
- |MAINTAIN|  coverage git ignore
- |MAINTAIN| `cli-docker` make command
- |MAINTAIN| `Dockerfile` for repeatable builds
- |MAINTAIN| `hatch` as build backend
- |MAINTAIN| copyrights update
- |MAINTAIN| host system/docker interchangable building automations
- |NEW|  `format_time`, `format_time_ms`, `format_time_ns`
- |NEW| `Hightlighter` from static methods to real class
- |NEW| `lab_to_rgb()`
- |NEW| numeric formatters fallback mechanics
- |REFACTOR| ``TDF_REGISTRY`` -> `dual_registry- ``FORMATTER_`` constants from top-level imports
- |REFACTOR| ``utilnum._TDF_REGISTRY`` -> `TDF_REGISTRY`
- |REFACTOR| edited highlighter styles
- |REFACTOR| naming:

  - ``CustomBaseUnit`` -> `DualBaseUnit`
  - ``DynamicBaseFormatter`` -> `DynamicFormatter`
  - ``StaticBaseFormatter`` -> `StaticFormatter`

- |TESTS| numeric formatters colorizing
- |UPDATE|  README
- |UPDATE| license is now Lesser GPL v3


v2.40-dev
------------------
:date:`Feb 23`

- |DOCS|  `changelog` update
- |DOCS| `utilnum` module
- |DOCS| rethinking of references style
- |FIX|  `parse` method of TemplateEngine
- |FIX| `Highlighter`
- |FIX| critical `Styles` color
- |MAINTAIN| 2023 copytight update
- |NEW|  `coveralls.io` integration
- |NEW|  `echoi`, `flatten`, `flatten1` methods;  `SimpleTable` class
- |NEW|  `StringLinearizer`, `WhitespaceRemover`
- |NEW|  `text` Fragments validation
- |NEW| `Config` class
- |NEW| `hex` rst text role
- |NEW| `utilnum.format_bytes_human()`
- |NEW| add `es7s C45/Kalm` to rgb colors list
- |NEW| methods `percentile` and `median` ; `render_benchmark` example
- |REFACTOR|  `IRenderable` rewrite
- |REFACTOR| `distribute_padded` overloads
- |REFACTOR| attempt to break cyclic dependency of `util.*` modules
- |REFACTOR| moved color transformations and type vars from `_commons`
- |TESTS| additional coverage for `utilnum`


v2.32-dev
------------------
:date:`Jan 23`

- |DOCS|  `utilnum` update
- |DOCS|  docstrings, typing
- |DOCS| `utilnum` module
- |FIX|  `format_prefixed` and `format_auto_float` inaccuracies
- |FIX| `Text.prepend` typing
- |FIX| `TmuxRenderer` RGB output
- |NEW|  `Color256` aliases "colorNN"
- |NEW|  `Highlighter` from `es7s`, colorizing options of `utilnum` helpers
- |NEW|  `IRenderable` result caching
- |NEW|  `pad`, `padv` helpers
- |NEW|  `prefix_refpoint_shift` argument of PrefixedUnitFormatter
- |NEW|  `PrefixedUnitFormatter` inheritance
- |NEW|  `String` and `FixedString` base renderables
- |NEW|  `style.merge_styles()`
- |NEW| `Renderable` __eq__ methods
- |NEW| `StyledString`
- |NEW| `utilmisc` get_char_width(),  guess_char_width(), measure_char_width()
- |NEW| style merging strategies: `merge_fallback()`, `merge_overwrite`
- |NEW| subsecond delta support for `TimeDeltaFormatter`
- |TESTS|  `utilnum` update
- |TESTS| integrated in-code doctests into pytest


v2.23-dev
------------------

- |FIX| `OmniHexPrinter` missed out newlines
- |NEW| `dump` printer caching
- |NEW| `Printers` and `Mappers`
- |NEW| `SgrRenderer` now supports non-default IO stream specifying
- |NEW| `utilstr.StringHexPrinter` and `utilstr.StringUcpPrinter`
- |NEW| add missing `hsv_to_rgb` function
- |NEW| extracted `resolve`, `approximate`, `find_closest` from `Color` class to module level, as well as color transform functions
- |NEW| split `Text` to `Text` and `FrozenText`


v2.18-dev
------------------

- |FIX| Disabled automatic rendering of `echo()` and `render()`.
- |NEW| `ArgCountError` migrated from `es7s/core`.
- |NEW| `black` code style.
- |NEW| `cval` autobuild.
- |NEW| Add `OmniHexPrinter` and `chunk()` helper.
- |NEW| Typehinting.

v2.14-dev
-----------------
:date:`Dec 22`

- |DOCS| Docs design fixes.
- |NEW| `confirm()` helper command.
- |NEW| `EscapeSequenceStringReplacer` filter.
- |NEW| `examples/terminal_benchmark` script.
- |NEW| `StringFilter` and `OmniFilter` classes.
- |NEW| Minor core improvements.
- |NEW| RGB and variations full support.
- |TESTS| Tests for `color` module.

v2.6-dev
---------------
:date:`Nov 22`

- |NEW| `TemplateEngine` implementation.
- |NEW| `Text` nesting.
- |REFACTOR| Changes in `ConfigurableRenderer.force_styles` logic.
- |REFACTOR| Got rid of `Span` class.
- |REFACTOR| Package reorganizing.
- |REFACTOR| Rewrite of `color` module.

v2.2-dev
---------
:date:`Oct 22`

- |NEW| `TmuxRenderer`
- |NEW| `wait_key()` input helper.
- |NEW| Color config.
- |NEW| IRenderable` interface.
- |NEW| Named colors list.

v2.1-dev
--------
:date:`Aug 22`

- |NEW| Color presets.
- |TESTS| More unit tests for formatters.

v2.0-dev
---------
:date:`Jul 22`

- |REWORK| Complete library rewrite.
- |DOCS| ``sphinx`` and ``readthedocs`` integraton.
- |NEW| High-level abstractions `Color`, `Renderer <SgrRenderer>` and `Style`.
- |TESTS| ``pytest`` and ``coverage`` integration.
- |TESTS| Unit tests for formatters and new modules.


v1.8
------
:date:`Jun 22`

- |NEW| ``format_prefixed_unit`` extended for working with decimal and binary metric prefixes.
- |NEW| ``sequence.NOOP`` SGR sequence and ``span.NOOP`` format.
- |NEW| `format_time_delta` extended with new settings.
- |NEW| Added 3 formatters: ``format_prefixed_unit``, `format_time_delta`, `format_auto_float`.
- |NEW| Max decimal points for `auto_float` extended from (2) to (max-2).
- |REFACTOR| Utility classes reorganization.
- |REFACTOR| Value rounding transferred from  `format_auto_float` to ``format_prefixed_unit``.
- |TESTS| Unit tests output formatting.

v1.7
-------
:date:`May 22`

- |FIX| Print reset sequence as ``\e[m`` instead of ``\e[0m``.
- |NEW| `Span` constructor can be called without arguments.
- |NEW| Added ``span.BG_BLACK`` format.
- |NEW| Added `ljust_sgr`, `rjust_sgr`, `center_sgr` util functions to align strings with SGRs correctly.
- |NEW| Added SGR code lists.

v1.6
------

- |REFACTOR| Renamed ``code`` module to ``sgr`` because of conflicts in PyCharm debugger (``pydevd_console_integration.py``).
- |REFACTOR| Ridded of ``EmptyFormat`` and ``AbstractFormat`` classes.
- |TESTS| Excluded ``tests`` dir from distribution package.

v1.5
------

- |REFACTOR| Removed excessive ``EmptySequenceSGR`` -- default ``SGR`` class was specifically implemented to print out as empty string instead of ``\e[m`` if constructed without params.

v1.4
--------

- |NEW| `Span.wrap()` now accepts any type of argument, not only *str*.
- |NEW| Added equality methods for `SequenceSGR` and `Span` classes/subclasses.
- |REFACTOR| Rebuilt ``Sequence`` inheritance tree.
- |TESTS| Added some tests for ``fmt.*`` and ``seq.*`` classes.

v1.3
------

- |NEW| Added ``span.GRAY`` and ``span.BG_GRAY`` format presets.
- |REFACTOR| Interface revisioning.


v1.2
-------

- |NEW| ``EmptySequenceSGR`` and ``EmptyFormat`` classes.
- |NEW| `opening_seq` and `closing_seq` properties for `Span` class.

v1.1
------
:date:`Apr 22`

- |NEW| Autoformat feature.

v1.0
-------

- |[]| First public version.

v0.90
---------------
:date:`Mar 22`

- |[]| First commit.
