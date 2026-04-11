from dataclasses import dataclass
from datetime import datetime as Datetime
from decimal import Decimal


@dataclass
class DatedAmount:
    date: Datetime
    amount: Decimal


@dataclass
class Position:
    symbol: str
    currency: str
    quantity: Decimal

    open_date: Datetime
    buy_price: Decimal

    taxes: list[DatedAmount]
    dividends: list[DatedAmount]
    
    closed: bool = False
    close_date: Datetime | None = None
    sell_price: Decimal | None = None
    