from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Asset:
    symbol: str
    currency: str
    quantity: Decimal
    closed_quantity: Decimal
    dividends: Decimal # in base currency
    taxes: Decimal # in base currency
