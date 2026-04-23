from datetime import datetime as Datetime
from decimal import Decimal

from model.action import Action

def build_broker_fx_rates(actions: list[Action], base_currency: str) -> dict[str, dict[Datetime, Decimal]]:
    ctx = BrokerFxRatesBuilder(base_currency)

    for action in actions:
        action.apply(ctx)

    return ctx.rates


class BrokerFxRatesBuilder:
    def __init__(self, base_currency: str):
        self.base_currency = base_currency
        self.rates: dict[str, dict[Datetime, Decimal]] = {}

    def handle_deposit(self, action: Action):
        pass

    def handle_withdrawal(self, action: Action):
        pass

    def handle_buy(self, action: Action):
        if action.ex_rate:
            self._add_rate(action.currency, action.date, action.ex_rate)

    def handle_sell(self, action: Action):
        if action.ex_rate:
            self._add_rate(action.currency, action.date, action.ex_rate)

    def handle_dividend(self, action: Action):
        pass

    def handle_lending_interest(self, action: Action):
        pass

    def handle_interest_on_cash(self, action: Action):
        pass

    def handle_conversion(self, action: Action):
        if action.from_currency == self.base_currency:
            self._add_rate(action.to_currency, action.date, action.from_amount / action.to_amount)
        elif action.to_currency == self.base_currency:
            breakpoint()
            self._add_rate(action.from_currency, action.date, action.to_amount / action.from_amount)

    def handle_spending(self, action: Action):
        pass

    def handle_cashback(self, action: Action):
        pass

    def handle_split(self, action: Action):
        pass

    def _add_rate(self, currency: str, date: Datetime, rate: Decimal):
        if currency not in self.rates:
            self.rates[currency] = {}
        
        self.rates[currency][date] = rate