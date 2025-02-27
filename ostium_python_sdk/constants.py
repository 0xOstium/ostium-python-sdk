
# Constants
from decimal import Decimal


MAX_PROFIT_P = Decimal('900')  # 900% * PRECISION_6
MAX_STOP_LOSS_P = Decimal('85')

PRECISION_2 = Decimal('100')
PRECISION_6 = Decimal('1000000')
PRECISION_9 = Decimal('1000000000')
PRECISION_12 = Decimal('1000000000000')
PRECISION_16 = Decimal('10000000000000000')
PRECISION_18 = Decimal('1000000000000000000')

LIQ_THRESHOLD_P = Decimal('90')  # -90% (of collateral)
