from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum


class IncostType(Enum):
    DEPOSIT_FEE = "deposit_fee"
    INTEREST_CASH = "interest_cash"
    CONVERSION_FEE = "conversion_fee"
    DIVIDEND = "dividend"
    INTEREST_LENDING = "interest_lending"
    TAX = "tax"


@dataclass
class Incost: # represents income (amount positive) or cost (amount negative)
    date: datetime
    type: IncostType
    amount: Decimal
    currency: str
    symbol: str | None = None
