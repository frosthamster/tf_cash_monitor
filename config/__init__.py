import ast
import logging.config
import os

from .base import *

import dotenv
dotenv.load_dotenv(PROJECT_DIR / '.env')

# Override config variables from environment
# To override config variable with given name, set environment variable to `_module_prefix` + that name
_module_prefix = 'TF_CASH_MONITOR_'
for key, value in os.environ.items():
    if not key.startswith(_module_prefix):
        continue
    pure_key = key[len(_module_prefix):]
    if pure_key not in locals():
        continue

    try:
        locals()[pure_key] = ast.literal_eval(value)
    except Exception:
        locals()[pure_key] = value

# Set loggers settings
logging.config.dictConfig(LOG_SETTINGS(locals()))


for curr_name, expected_amount in CURRENCY_FILTERS_AMOUNT_GT.items():
    assert curr_name not in ('EUR', 'USD') or expected_amount <= 5000, (
        'for EUR or USD filtering with > 5000 set filter value to 5000'
    )
