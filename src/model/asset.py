from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Asset:
    symbol: str
    currency: str
    quantity: Decimal = Decimal("0")
    closed_quantity: Decimal = Decimal("0")
    dividends: Decimal = Decimal("0") # in base currency
    taxes: Decimal = Decimal("0") # in base currency
    fees: Decimal = Decimal("0")
    is_currency: bool = False
