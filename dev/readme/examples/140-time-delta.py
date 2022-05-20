from pytermor.formatters import TimeDeltaFormatter, TimeUnit

TimeDeltaFormatter([
    TimeUnit('sec', 60),
    TimeUnit('min', 60, custom_short='min'),
    TimeUnit('hour', 24, collapsible_after=24),
    TimeUnit('day', 30, collapsible_after=10),
    TimeUnit('month', 12),
    TimeUnit('year', overflow_afer=999),
], allow_negative=True,
    unit_separator=' ',
    plural_suffix='s',
    overflow_msg='OVERFLOW',
)
