.. vN.NN
.. -------------------
.. :date:`MMM 23`
..
.. git log hhhhhh~1..dev --reverse --pretty='%B' | \
   sed -Ee '/^\s*$/d; s/^(\s*)/- /; ' | \
   less

pending (v2.38-dev)
------------------

- |REFACTOR| `distribute_padded` overloads
- |DOCS| `utilnum` module
- |DOCS|  `changelog` update
- |FIX| critical `Styles` color
- |NEW|  `echoi`, `flatten`, `flatten1` methods;  `SimpleTable` class
- |MAINTAIN| 2023 copytight update
- |NEW| methods `percentile` and `median` ; `render_benchmark` example
- |REFACTOR|  `IRenderable` rewrite
- |FIX| `NumHighlighter`
- |REFACTOR| moved color transformations and type vars from `_commons`
- |NEW| `Config` class
- |NEW| add `es7s C45/Kalm` to rgb colors list
- |REFACTOR| attempt to break cyclic dependency of `util.*` modules
- |TESTS| additional coverage for `utilnum`


v2.32-dev
------------------
:date:`Jan 23`

- |FIX| `TmuxRenderer` RGB output
- |NEW|  `PrefixedUnitFormatter` inheritance
- |NEW| `StyledString`
- |NEW|  `pad`, `padv` helpers
- |NEW|  `String` and `FixedString` base renderables
- |TESTS| integrated in-code doctests into pytest
- |NEW|  `IRenderable` result caching
- |NEW| `Renderable` __eq__ methods
- |FIX|  `format_prefixed` and `format_auto_float` inaccuracies
- |DOCS|  `utilnum` update
- |TESTS|  `utilnum` update
- |NEW| subsecond delta support for `TimeDeltaFormatter`
- |NEW| `utilmisc` get_char_width(),  guess_char_width(), measure_char_width()
- |NEW|  `Color256` aliases "colorNN"
- |NEW|  `prefix_refpoint_shift` argument of PrefixedUnitFormatter
- |NEW|  `NumHighlighter` from `es7s`, colorizing options of `utilnum` helpers
- |FIX| `Text.prepend` typing
- |DOCS|  docstrings, typing
- |NEW|  `style.merge_styles()`
- |NEW| style merging strategies: `merge_fallback()`, `merge_overwrite`
- |DOCS| `utilnum` module


v2.23-dev
------------------

- |FIX| `OmniHexPrinter` missed out newlines
- |NEW| split `Text` to `Text` and `FrozenText`
- |NEW| `SgrRenderer` now supports non-default IO stream specifying
- |NEW| `utilstr.StringHexPrinter` and `utilstr.StringUcpPrinter`
- |NEW| `Printers` and `Mappers`
- |NEW| `dump` printer caching
- |NEW| extracted `resolve`, `approximate`, `find_closest` from `Color` class to
  module level, as well as color transform functions
- |NEW| add missing `hsv_to_rgb` function


v2.18-dev
------------------

- |NEW| `cval` autobuild.
- |NEW| `ArgCountError` migrated from `es7s/core`.
- |NEW| `black` code style.
- |NEW| Add `OmniHexPrinter` and `chunk()` helper.
- |NEW| Typehinting.
- |FIX| Disabled automatic rendering of `echo()` and `render()`.

v2.14-dev
-----------------
:date:`Dec 22`

- |NEW| `confirm()` helper command.
- |NEW| `EscapeSequenceStringReplacer` filter.
- |NEW| `examples/terminal_benchmark` script.
- |NEW| `StringFilter` and `OmniFilter` classes.
- |DOCS| Docs design fixes.
- |NEW| Minor core improvements.
- |TESTS| Tests for `color` module.
- |NEW| RGB and variations full support.

v2.6-dev
---------------
:date:`Nov 22`

- |REFACTOR| Got rid of `Span` class.
- |REFACTOR| Rewrite of `color` module.
- |REFACTOR| Changes in `ConfigurableRenderer.force_styles` logic.
- |NEW| `Text` nesting.
- |NEW| `TemplateEngine` implementation.
- |REFACTOR| Package reorganizing.

v2.2-dev
---------
:date:`Oct 22`

- |NEW| Named colors list.
- |NEW| IRenderable` interface.
- |NEW| Color config.
- |NEW| `TmuxRenderer`
- |NEW| `wait_key()` input helper.

v2.1-dev
--------
:date:`Aug 22`

- |NEW| Color presets.
- |TESTS| More unit tests for formatters.

v2.0-dev
---------
:date:`Jul 22`

- |[]| Complete library rewrite.
- |NEW| High-level abstractions `Color`, `Renderer <SgrRenderer>` and `Style`.
- |TESTS| Unit tests for formatters and new modules.
- |TESTS| ``pytest`` and ``coverage`` integration.
- |DOCS| ``sphinx`` and ``readthedocs`` integraton.


v1.8
------
:date:`Jun 22`

- |NEW| Added 3 formatters: ``format_prefixed_unit``, `format_time_delta`, `format_auto_float`.
- |NEW| ``format_prefixed_unit`` extended for working with decimal and binary metric prefixes.
- |NEW| `format_time_delta` extended with new settings.
- |REFACTOR| Value rounding transferred from  `format_auto_float` to ``format_prefixed_unit``.
- |REFACTOR| Utility classes reorganization.
- |TESTS| Unit tests output formatting.
- |NEW| ``sequence.NOOP`` SGR sequence and ``span.NOOP`` format.
- |NEW| Max decimal points for `auto_float` extended from (2) to (max-2).

v1.7
-------
:date:`May 22`

- |NEW| `Span` constructor can be called without arguments.
- |NEW| Added SGR code lists.
- |FIX| Print reset sequence as ``\e[m`` instead of ``\e[0m``.
- |NEW| Added `ljust_sgr`, `rjust_sgr`, `center_sgr` util functions to align strings with SGRs correctly.
- |NEW| Added ``span.BG_BLACK`` format.

v1.6
------

- |REFACTOR| Ridded of ``EmptyFormat`` and ``AbstractFormat`` classes.
- |REFACTOR| Renamed ``code`` module to ``sgr`` because of conflicts in PyCharm debugger (``pydevd_console_integration.py``).
- |TESTS| Excluded ``tests`` dir from distribution package.

v1.5
------

- |REFACTOR| Removed excessive ``EmptySequenceSGR`` -- default ``SGR`` class was specifically implemented to print out as empty string instead of ``\e[m`` if constructed without params.

v1.4
--------

- |NEW| `Span.wrap()` now accepts any type of argument, not only *str*.
- |REFACTOR| Rebuilt ``Sequence`` inheritance tree.
- |NEW| Added equality methods for `SequenceSGR` and `Span` classes/subclasses.
- |TESTS| Added some tests for ``fmt.*`` and ``seq.*`` classes.

v1.3
------

- |REFACTOR| Interface revisioning.
- |NEW| Added ``span.GRAY`` and ``span.BG_GRAY`` format presets.


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
