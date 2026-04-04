from dataclasses import dataclass
from datetime import datetime as Datetime
from decimal import Decimal


@dataclass
class Position:
    symbol: str
    currency: str
    quantity: Decimal

    open_date: Datetime
    buy_price: Decimal

    taxes: Decimal = Decimal("0")
    dividents: Decimal = Decimal("0")
    
    closed: bool = False
    close_date: Datetime | None = None
    sell_price: Decimal | None = None
    