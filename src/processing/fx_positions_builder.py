from datetime import date as Date
from decimal import Decimal, ROUND_HALF_UP

from model.action import Action
from model.currency_position import CurrencyPosition


# Currency view is not working properly right now
#+when asset is bought and then sold, certain amount of currency gets "created" or "destroyed"
#+it's not accounted for right now
#+for this to work, I should count shares and "create" or "destroy" currency positions when shares are sold
#+for this to be possible, I should merge back together buy and exchange_buy


def build_fx_positions(actions: list[Action], fx_rate_provider) -> list[CurrencyPosition]:
    ctx = CurrencyBuilder(fx_rate_provider)

    for action in actions:
        action.apply(ctx)

    return ctx.positions


class CurrencyBuilder:
    def __init__(self, fx_rate_provider):
        self.fx_rate_provider = fx_rate_provider
        self.base_currency = fx_rate_provider.base_currency
        self.positions = []

    def handle_deposit(self, action: Action):
        pass

    def handle_withdrawal(self, action: Action):
        pass

    def handle_buy(self, action: Action):
        if action.ex_rate:
            self._open(action.currency, action.quantity * action.price, action.date, action.ex_rate, action.exchange_fee, self.base_currency)

    def handle_sell(self, action: Action):
        if action.ex_rate:
            self._close(action.currency, action.quantity * action.price, action.date, action.ex_rate, action.exchange_fee, self.base_currency)

    def handle_dividend(self, action: Action):
        pass

    def handle_lending_interest(self, action: Action):
        pass

    def handle_interest_on_cash(self, action: Action):
        if action.currency != self.base_currency:
            ex_rate = self.fx_rate_provider.get_rate(action.currency, action.date)
            self._open(action.currency, action.amount, action.date, ex_rate, Decimal("0"), self.base_currency)

    def handle_conversion(self, action: Action):
        fee = action.fee * self.fx_rate_provider.get_rate(action.fee_currency, action.date)
        if action.to_currency == self.base_currency:
            ex_rate = self.fx_rate_provider.get_rate(action.to_currency, action.date)
            self._open(action.to_currency, action.to_amount, action.date, ex_rate, fee, self.base_currency)
            fee = 0

        if action.from_currency != self.base_currency:
            ex_rate = self.fx_rate_provider.get_rate(action.from_currency, action.date)
            self._close(action.from_currency, action.from_amount, action.date, ex_rate, fee, self.base_currency)

    def handle_spending(self, action: Action):
        pass

    def handle_cashback(self, action: Action):
        pass

    def handle_split(self, action: Action):
        pass

    def _open(self, name: str, amount: Decimal, date: Date, price: Decimal, fee: Decimal, fee_currency: str):
        if fee_currency != self.base_currency:
            fee *= price

        self.positions.append(CurrencyPosition(
            name=name,
            amount=amount,
            open_date=date,
            buy_price=price,
            fees=fee,
            interest=Decimal("0"),
            closed=False,
        ))

    def _close(self, name: str, amount: Decimal, date: Date, price: Decimal, fee: Decimal, fee_currency: str):
        # too small to account for
        if amount < Decimal('0.01'):
            return

        total_amount = sum(p.amount for p in self.positions if p.name == name and not p.closed)
        if total_amount < amount:
            raise ValueError(f"negative {name} balance on sell: open_date: {date}, amount: {amount}, total_amount: {total_amount}")
        
        if fee_currency != self.base_currency:
            breakpoint()
            fee *= price
        
        amount_left = amount
        for i, pos in enumerate(self.positions):
            if pos.name == name and not pos.closed:
                if pos.amount > amount_left:
                    self._split_position(i, amount_left)

                pos.closed = True
                pos.close_date = date
                pos.sell_price = price
                pos.fees += fee * pos.amount / amount
                amount_left -= pos.amount
                if amount_left == 0:
                    break

    def _split_position(self, index: int, quantity: Decimal):
        pos = self.positions[index]
        new_amount = pos.amount - quantity
        new_pos = CurrencyPosition(
            name=pos.name,
            amount=new_amount,
            open_date=pos.open_date,
            buy_price=pos.buy_price,
            fees=(pos.fees * new_amount / pos.amount).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP),
            interest=(pos.interest * new_amount / pos.amount).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP),
            closed=False,
        )
        pos.amount -= new_amount
        pos.fees -= new_pos.fees
        pos.interest -= new_pos.interest
        self.positions.insert(index + 1, new_pos)
