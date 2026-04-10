from dataclasses import dataclass
from datetime import datetime as Datetime
from decimal import Decimal


@dataclass
class CurrencyPosition:
    name: str
    amount: Decimal

    open_date: Datetime # TODO: should be bouth open or buy
    buy_price: Decimal

    fees: Decimal = Decimal("0.0")
    interest: Decimal = Decimal('0.0')
    
    closed: bool = False
    close_date: Datetime | None = None
    sell_price: Decimal | None = None
    