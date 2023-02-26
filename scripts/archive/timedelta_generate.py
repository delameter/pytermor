from functools import partial

from test_utilnum import TestDualFormatter

import pytermor.utilnum

f6 = partial(pytermor.utilnum.format_time_delta, max_len=6)
f6 = pytermor.utilnum.DualFormatter(pytermor.utilnum.TDF_REGISTRY.get_by_max_len(6), allow_negative=True)

for td in TestDualFormatter.TIMEDELTA_TEST_SET:
    print(f6.format(td[0].total_seconds()))
