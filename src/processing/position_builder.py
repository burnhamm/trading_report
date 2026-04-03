from datetime import datetime as Datetime
from decimal import Decimal, ROUND_HALF_UP

from model.action import Action
from model.position import Position


def build_positions(actions: list[Action], fx_rate_provider) -> list[Position]:
    ctx = PositionBuilder(fx_rate_provider)

    for action in actions:
        action.apply(ctx)

    return ctx.positions


class PositionBuilder:
    def __init__(self, fx_rate_provider):
        self.fx_rate_provider = fx_rate_provider
        self.base_currency = fx_rate_provider.base_currency
        self.positions = []

    def handle_deposit(self, action: Action):
        # self._open(self.base_currency, True, self.base_currency, action.quantity, action.date, Decimal("0"), action.fee)
        self._open(self.base_currency, True, self.base_currency, action.amount, action.date, Decimal("0"), Decimal("0"))

    def handle_withdrawal(self, action: Action):
        self._close(self.base_currency, True, self.base_currency, action.amount, action.date, Decimal("0"), Decimal("0"))

    def handle_buy(self, action: Action):
        self._close(action.currency, True, self.base_currency, action.result, action.date, Decimal("0"), Decimal("0"))
        ex_rate = self.fx_rate_provider.get_rate(action.tax_currency, action.date)
        tax = action.tax * ex_rate
        self._open(action.symbol, False, action.currency, action.quantity, action.date, action.price, tax) # TODO: separate from fee field for tax?

    def handle_sell(self, action: Action):
        self._close(action.symbol, False, action.currency, action.quantity, action.date, action.price, Decimal("0"))
        self._open(action.currency, True, self.base_currency, action.result, action.date, Decimal("0"), Decimal("0"))

    def handle_exchange_buy(self, action: Action):
        # fees are ignored for position builder. Instead those are accounted for in exchange rate gain builder
        self._close(self.base_currency, True, self.base_currency, action.result, action.date, Decimal("0"), Decimal("0"))
        self._open(action.currency, True, self.base_currency, action.quantity, action.date, Decimal("0"), Decimal("0"))

    def handle_exchange_sell(self, action: Action):
        # Currency positions are closed with price 0, to not pollute positions with exchange rate changes.
        #+There is a separate builder for exchange rate gains
        self._close(action.currency, True, self.base_currency, action.quantity, action.date, Decimal("0"), Decimal("0"))
        self._open(self.base_currency, True, self.base_currency, action.result, action.date, Decimal("0"), Decimal("0"))

    def handle_dividend(self, action: Action):
        self._assign_income(action.symbol, action.result, action.no_of_shares, action.reversed_assignment)
        ex_rate = self.fx_rate_provider.get_rate(action.tax_currency, action.date)
        tax = action.tax * ex_rate
        # self._open(action.currency, True, self.base_currency, action.result, action.date, Decimal("0"), tax)
        self._open(action.currency, True, self.base_currency, action.result, action.date, Decimal("0"), Decimal("0"))

    def handle_lending_interest(self, action: Action):
        self._open(self.base_currency, True, self.base_currency, action.result, action.date, Decimal("0"), Decimal("0"))

    def handle_interest_on_cash(self, action: Action):
        # don't assign interest on cash here, it is done in fx position builders
        self._open(action.currency, True, self.base_currency, action.amount, action.date, Decimal("0"), Decimal("0"))

    def handle_currency_conversion(self, action: Action):
        self._close(action.from_currency, True, self.base_currency, action.from_amount, action.date, Decimal("0"), Decimal("0"))
        self._open(action.to_currency, True, self.base_currency, action.to_amount, action.date, Decimal("0"), Decimal("0"))

    def handle_spending(self, action: Action):
        self._close(self.base_currency, True, self.base_currency, action.result, action.date, Decimal("0"), Decimal("0"))

    def handle_cashback(self, action: Action):
        self._open(self.base_currency, True, self.base_currency, action.result, action.date, Decimal("0"), Decimal("0"))

    def handle_split(self, action: Action):
        for pos in self.positions:
            if pos.symbol == action.symbol and not pos.closed:
                pos.quantity *= action.ratio
                pos.buy_price /= action.ratio

    def _open(self, symbol: str, is_currency: bool, currency: str, quantity: Decimal, date: Datetime, price: Decimal, fee: Decimal):
        self.positions.append(Position(
            symbol=symbol,
            currency=currency,
            is_currency=is_currency,
            quantity=quantity,
            open_date=date,
            buy_price=price,
            fees=fee,
            dividents=Decimal("0"),
            closed=False,
        ))

    def _close(self, symbol: str, is_currency: bool, currency: str, quantity: Decimal, date: Datetime, price: Decimal, fee: Decimal):
        # too small to account for
        if is_currency and quantity < Decimal('0.01'):
            return
        
        if quantity == 0:
            raise ValueError(f"zero quantity on sell: open_date: {date}, quantity: {quantity}")
        
        asset_quantity = sum(p.quantity for p in self.positions if p.symbol == symbol and not p.closed)
        if asset_quantity < quantity:
            raise ValueError(f"negative asset {symbol} balance on sell: open_date: {date}, quantity: {quantity}, asset_amount: {asset_quantity}")
        
        quantity_left = quantity
        for i, pos in enumerate(self.positions):
            if pos.symbol == symbol and not pos.closed:
                if pos.quantity > quantity_left:
                    self._split_position(i, quantity_left)

                pos.closed = True
                pos.close_date = date
                pos.sell_price = price
                pos.fees += fee * pos.quantity / quantity
                quantity_left -= pos.quantity
                if quantity_left == 0:
                    break

    def _split_position(self, index: int, quantity: Decimal):
        pos = self.positions[index]
        new_quantity = pos.quantity - quantity
        new_pos = Position(
            symbol=pos.symbol,
            is_currency=pos.is_currency,
            currency=pos.currency,        
            quantity=new_quantity,
            open_date=pos.open_date,
            buy_price=pos.buy_price,
            fees=(pos.fees * new_quantity / pos.quantity).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP),
            dividents=(pos.dividents * new_quantity / pos.quantity).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP),
            closed=False,
        )
        pos.quantity -= new_quantity
        pos.fees -= new_pos.fees
        pos.dividents -= new_pos.dividents
        self.positions.insert(index + 1, new_pos)

    def _assign_income(self, symbol: str, amount: Decimal, no_of_shares: Decimal, reversed_assignment: bool):
        amount_left = amount
        positions = reversed(self.positions) if reversed_assignment else self.positions
        for pos in positions:
            if pos.symbol == symbol and not pos.closed:
                pos_amount = min(amount * pos.quantity / no_of_shares, amount_left)
                pos.dividents += pos_amount
                amount_left -= pos_amount
                if amount_left == 0:
                    break

        if amount_left > Decimal('0.000001'):
            for pos in reversed(self.positions):
                if pos.symbol == symbol and pos.closed:
                    pos_amount = min(amount * pos.quantity / no_of_shares, amount_left)
                    pos.dividents += pos_amount
                    amount_left -= pos_amount
                    if amount_left == 0:
                        break

        if abs(amount_left) > Decimal('0.000001'): # TODO: compatibilty backward, in clean version pos_amount should be rouneded and this shouldn't happen
            print(f"wrong left over from dividents for {symbol}: {amount_left}; total: {amount}")
            breakpoint()