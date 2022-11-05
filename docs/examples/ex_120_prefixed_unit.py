from pytermor.utilnum import PrefixedUnitFormatter

PrefixedUnitFormatter(
    max_value_len=5, truncate_frac=True,
    unit='b', unit_separator=' ',
    mcoef=1024.0,
    prefixes=[None, 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y'],
    prefix_zero_idx=0,
)
