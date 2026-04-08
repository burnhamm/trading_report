from decimal import Decimal

from model.action import Action
from model.cash_flow import CashFlowEvent, CASH_FLOW_EVENT_TYPE


def build_cash_flow(actions: list[Action], base_currency) -> list[CashFlowEvent]:
    ctx = CashFlowBuilder(base_currency)

    for action in actions:
        action.apply(ctx)  
        
    return ctx.cash_flow


class CashFlowBuilder:
    def __init__(self, base_currency):
        self.base_currency = base_currency
        self.cash_flow: list[CashFlowEvent] = []

    def handle_deposit(self, action: Action):
        self.cash_flow.append(CashFlowEvent(
            date=action.date,
            type=CASH_FLOW_EVENT_TYPE.DEPOSIT,
            amount=action.amount
        ))

    def handle_withdrawal(self, action: Action):
        self.cash_flow.append(CashFlowEvent(
            date=action.date,
            type=CASH_FLOW_EVENT_TYPE.WITHDRAWAL,
            amount=-action.amount
        ))

    def handle_buy(self, action: Action):
        pass

    def handle_sell(self, action: Action):
        pass

    def handle_exchange_buy(self, action: Action):
        pass

    def handle_exchange_sell(self, action: Action):
        pass

    def handle_dividend(self, action: Action):
        pass

    def handle_lending_interest(self, action: Action):
        pass

    def handle_interest_on_cash(self, action: Action):
        pass

    def handle_spending(self, action: Action):
        self.cash_flow.append(CashFlowEvent(
            date=action.date,
            type=CASH_FLOW_EVENT_TYPE.SPENDING,
            amount=-action.result
        ))

    def handle_cashback(self, action: Action):
        self.cash_flow.append(CashFlowEvent(
            date=action.date,
            type=CASH_FLOW_EVENT_TYPE.CASHBACK,
            amount=action.result
        ))

    def handle_split(self, action: Action):
        pass
