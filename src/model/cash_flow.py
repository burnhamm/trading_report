from dataclasses import dataclass
from datetime import datetime as Datetime
from decimal import Decimal
from enum import Enum


class CASH_FLOW_EVENT_TYPE(Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    SPENDING = "spending"
    CASHBACK = "cashback" 


@dataclass
class CashFlowEvent:
    date: Datetime
    type: CASH_FLOW_EVENT_TYPE
    amount: Decimal # cash flow is always in base currency
