v2.23-dev
------------------

- Extracted `resolve`, `approximate`, `find_closest` from `Color` class to module-level.
- As well as color transform functions.
- Add missing `hsv_to_rgb` function.
- `GenericPrniter` and `OmniMapper`.
- `StringDumper` and `StringUcpDumper`.
- `SgrRenderer` support for custom I/O streams.
- `FrozenText` class.

v2.18-dev
------------------

- `cval` autobuild.
- `ArgCountError` migrated from `es7s/core`.
- `black` code style.
- Add `OmniHexPrinter` and `chunk()` helper.
- Typehinting.
- Disabled automatic rendering of `echo()` and `render()`.

v2.14-dev
-----------------
:date:`Dec 22`

- `confirm()` helper command.
- `EscapeSequenceStringReplacer` filter.
- `examples/terminal_benchmark` script.
- `StringFilter` and `OmniFilter` classes.
- Docs design fixes.
- Minor core improvements.
- Tests for `color` module.
- RGB and variations full support.

v2.6-dev
---------------
:date:`Nov 22`

- Got rid of `Span` class.
- Rewrite of `color` module.
- Changes in `ConfigurableRenderer.force_styles` logic.
- `Text` nesting.
- `TemplateEngine` implementation.
- Package reorganizing.

v2.2-dev
---------
:date:`Oct 22`

- Named colors list.
- IRenderable` interface.
- Color config.
- `TmuxRenderer`
- `wait_key()` input helper.

v2.1-dev
--------
:date:`Aug 22`

- Color presets.
- More unit tests for formatters.

v2.0-dev
---------
:date:`Jul 22`

- Complete library rewrite.
- High-level abstractions `Color`, `Renderer <SgrRenderer>` and `Style`.
- Unit tests for formatters and new modules.
- ``pytest`` and ``coverage`` integration.
- ``sphinx`` and ``readthedocs`` integraton.


v1.8
------
:date:`Jun 22`

- ``format_prefixed_unit`` extended for working with decimal and binary metric prefixes.
- `format_time_delta` extended with new settings.
- Value rounding transferred from  `format_auto_float` to ``format_prefixed_unit``.
- Utility classes reorganization.
- Unit tests output formatting.
- ``sequence.NOOP`` SGR sequence and ``span.NOOP`` format.
- Max decimal points for `auto_float` extended from (2) to (max-2).

v1.7.4
------

- Added 3 formatters: ``format_prefixed_unit``, `format_time_delta`, `format_auto_float`.

v1.7.3
------
:date:`May 22`

- Added ``span.BG_BLACK`` format.

v1.7.2
------

- Added `ljust_sgr`, `rjust_sgr`, `center_sgr` util functions to align strings with SGRs correctly.

v1.7.1
------

- Print reset sequence as ``\e[m`` instead of ``\e[0m``.

v1.7
-------

- `Span` constructor can be called without arguments.
- Added SGR code lists.

v1.6.2
------

- Excluded ``tests`` dir from distribution package.

v1.6.1
------

- Ridded of ``EmptyFormat`` and ``AbstractFormat`` classes.
- Renamed ``code`` module to ``sgr`` because of conflicts in PyCharm debugger (``pydevd_console_integration.py``).

v1.5
------

- Removed excessive ``EmptySequenceSGR`` -- default ``SGR`` class was specifically implemented to print out as empty string instead of ``\e[m`` if constructed without params.

v1.4
--------

- `Span.wrap()` now accepts any type of argument, not only *str*.
- Rebuilt ``Sequence`` inheritance tree.
- Added equality methods for `SequenceSGR` and `Span` classes/subclasses.
- Added some tests for ``fmt.*`` and ``seq.*`` classes.

v1.3.2
------

- Added ``span.GRAY`` and ``span.BG_GRAY`` format presets.

v1.3.1
------

- Interface revisioning.

v1.2.1
------

- `opening_seq` and `closing_seq` properties for `Span` class.

v1.2
-------

- ``EmptySequenceSGR`` and ``EmptyFormat`` classes.

v1.1
------
:date:`Apr 22`

- Autoformat feature.

v1.0
-------

- First public version.


v0.90
---------------
:date:`Mar 22`

- First commit.

-----


This project uses Semantic Versioning -- https://semver.org *(starting from 2.0)*
