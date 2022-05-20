### v2.0.0

- Complete library reorganization.
- `numf.*` formatters rewrite.
- pytest and coverage integration.
- Unit tests for formatters.
- pydoc, sphinx and readthedocs integraton.

### v1.8.0

- `format_prefixed_unit` extended for working with decimal and binary metric prefixes.
- `format_time_delta` extended with new settings.
- Value rounding transferred from  `format_auto_float` to `format_prefixed_unit`.
- Utility classes reorganization.
- Unit tests output formatting.
- `noop` SGR sequence and `noop` format.
- Max decimal points for `auto_float` extended from (2) to (max-2).

### v1.7.4

- Added 3 formatters: `fmt_prefixed_unit`, `fmt_time_delta`, `fmt_auto_float`.

### v1.7.3

- Added `bg_black` format.

### v1.7.2

- Added `ljust_aware`, `rjust_aware`, `center_aware` util functions to align strings with SGRs correctly.

### v1.7.1

- Print reset sequence as `\e[m` instead of `\e[0m`.

### v1.7.0

- `Format()` constructor can be called without arguments.
- Added SGR code lists.

### v1.6.2

- Excluded `tests` dir from distribution package.

### v1.6.1

- Ridded of _EmptyFormat_ and _AbstractFormat_ classes.
- Renamed `code` module to `sgr` because of conflicts in PyCharm debugger (`pydevd_console_integration.py`).

### v1.5.0

- Removed excessive _EmptySequenceSGR_ &mdash; default _SGR_ class without params was specifically implemented to print out as empty string instead of `\e[m`.

### v1.4.0

- `Format.wrap()` now accepts any type of argument, not only _str_.
- Rebuilt _Sequence_ inheritance tree.
- Added equality methods for _Sequence_ and _Format_ classes/subclasses.
- Added some tests for `fmt.*` and `seq.*` classes.

### v1.3.2

- Added `gray` and `bg_gray` format presets.

### v1.3.1

- Interface revisioning.

### v1.2.1

- `opening_seq` and `closing_seq` properties for _Format_ class.

### v1.2.0

- _EmptySequenceSGR_ and _EmptyFormat_ classes.

### v1.1.0

- Autoformat feature.

### v1.0.0

- First public version.
