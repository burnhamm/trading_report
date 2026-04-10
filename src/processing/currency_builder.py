from decimal import Decimal

from model.action import Action
from model.currency import Currency


def build_currencies(actions: list[Action], fx_rate_provider) -> dict[str, Currency]:
    ctx = CurrencyBuilder(fx_rate_provider)

    for action in actions:
        action.apply(ctx)  
        
    return ctx.currencies


class CurrencyBuilder:
    def __init__(self, fx_rate_provider):
        self.fx_rate_provider = fx_rate_provider
        self.base_currency = fx_rate_provider.base_currency
        self.currencies: dict[str, Currency] = {}

    def handle_deposit(self, action: Action):
        currency = self._get_currency(self.base_currency)
        currency.amount += action.amount
        currency.exchange_fees += action.fee

    def handle_withdrawal(self, action: Action):
        currency = self._get_currency(self.base_currency)
        currency.amount -= action.amount

    def handle_buy(self, action: Action):
        currency = self._get_currency(action.currency)
        currency.amount -= action.result

    def handle_sell(self, action: Action):
        currency = self._get_currency(action.currency)
        currency.amount += action.result

    def handle_exchange_buy(self, action: Action):
        src_cur = self._get_currency(self.base_currency)
        dst_cur = self._get_currency(action.currency)
        src_cur.amount -= action.result
        dst_cur.amount += action.quantity
        ex_rate = self.fx_rate_provider.get_rate(action.fee_currency, action.date)
        dst_cur.exchange_fees += action.fee * ex_rate

    def handle_exchange_sell(self, action: Action):
        src_cur = self._get_currency(self.base_currency)
        dst_cur = self._get_currency(action.currency)
        src_cur.amount += action.result
        dst_cur.amount -= action.quantity
        ex_rate = self.fx_rate_provider.get_rate(action.fee_currency, action.date)
        src_cur.exchange_fees += action.fee * ex_rate

    def handle_dividend(self, action: Action):
        currency = self._get_currency(self.base_currency)
        currency.amount += action.result

    def handle_lending_interest(self, action: Action):
        currency = self._get_currency(self.base_currency)
        currency.amount += action.result

    def handle_interest_on_cash(self, action: Action):
        currency = self._get_currency(action.currency)
        currency.interest += action.amount
        currency.amount += action.amount

    def handle_spending(self, action: Action):
        currency = self._get_currency(self.base_currency)
        currency.amount -= action.result

    def handle_cashback(self, action: Action):
        currency = self._get_currency(self.base_currency)
        currency.amount += action.result

    def handle_split(self, action: Action):
        pass

    def _get_currency(self, code: str):
        if code not in self.currencies:
            self.currencies[code] = Currency(
                code=code,
                amount=Decimal("0"),
                interest=Decimal("0"),
                exchange_fees=Decimal("0"),
            )
        return self.currencies[code]
