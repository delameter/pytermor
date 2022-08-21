v2.0.0
------

- Complete library rewrite.
- High-level abstractions `Color`, `Renderer <SGRRenderer>` and `Style`.
- Unit tests for formatters and new modules.
- ``pytest`` and ``coverage`` integration.
- ``sphinx`` and ``readthedocs`` integraton.

v1.8.0
------

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

- Added ``span.BG_BLACK`` format.

v1.7.2
------

- Added `ljust_sgr`, `rjust_sgr`, `center_sgr` util functions to align strings with SGRs correctly.

v1.7.1
------

- Print reset sequence as ``\e[m`` instead of ``\e[0m``.

v1.7.0
------

- `Span` constructor can be called without arguments.
- Added SGR code lists.

v1.6.2
------

- Excluded ``tests`` dir from distribution package.

v1.6.1
------

- Ridded of ``EmptyFormat`` and ``AbstractFormat`` classes.
- Renamed ``code`` module to ``sgr`` because of conflicts in PyCharm debugger (``pydevd_console_integration.py``).

v1.5.0
------

- Removed excessive ``EmptySequenceSGR`` -- default ``SGR`` class was specifically implemented to print out as empty string instead of ``\e[m`` if constructed without params.

v1.4.0
------

- `Span.wrap()` now accepts any type of argument, not only ``str``.
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

v1.2.0
------

- ``EmptySequenceSGR`` and ``EmptyFormat`` classes.

v1.1.0
------

- Autoformat feature.

v1.0.0
------

- First public version.


-----


This project uses Semantic Versioning -- https://semver.org *(starting from 2.0.0)*
