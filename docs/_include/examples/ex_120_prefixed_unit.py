from pytermor.util import PrefixedUnitPreset

PrefixedUnitPreset(
    max_value_len=5, integer_input=True,
    unit='b', unit_separator=' ',
    mcoef=1024.0,
    prefixes=[None, 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y'],
    prefix_zero_idx=0,
)
