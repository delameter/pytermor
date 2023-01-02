from pytermor.utilnum import StaticBaseFormatter

StaticBaseFormatter(
    max_value_len=6, allow_fractional=False,
    unit='m', unit_separator='',
    mcoef=1000.0,
    prefixes=['y', 'z', 'a', 'f', 'p', 'n', 'μ', 'm', None],
    prefix_zero_idx=8,
)
