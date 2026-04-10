from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Currency:
    code: str
    amount: Decimal
    interest: Decimal
    exchange_fees: Decimal
