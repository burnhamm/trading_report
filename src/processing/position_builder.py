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
        pass

    def handle_withdrawal(self, action: Action):
        pass

    def handle_buy(self, action: Action):
        ex_rate = self.fx_rate_provider.get_rate(action.tax_currency, action.date)
        tax = action.tax * ex_rate
        self._open(action.symbol, action.currency, action.quantity, action.date, action.price, tax)

    def handle_sell(self, action: Action):
        self._close(action.symbol, action.currency, action.quantity, action.date, action.price, Decimal("0"))

    def handle_exchange_buy(self, action: Action):
        pass

    def handle_exchange_sell(self, action: Action):
        pass

    def handle_dividend(self, action: Action):
        ex_rate = self.fx_rate_provider.get_rate(action.tax_currency, action.date)
        tax = action.tax * ex_rate
        self._assign_income(action.symbol, action.result, action.tax, action.no_of_shares, action.reversed_assignment)

    def handle_lending_interest(self, action: Action):
        pass # TODO: consider spreading it to all open positions

    def handle_interest_on_cash(self, action: Action):
        pass

    def handle_spending(self, action: Action):
        pass

    def handle_cashback(self, action: Action):
        pass

    def handle_split(self, action: Action):
        for pos in self.positions:
            if pos.symbol == action.symbol and not pos.closed:
                pos.quantity *= action.ratio
                pos.buy_price /= action.ratio

    def _open(self, symbol: str, currency: str, quantity: Decimal, date: Datetime, price: Decimal, tax: Decimal):
        self.positions.append(Position(
            symbol=symbol,
            currency=currency,
            quantity=quantity,
            open_date=date,
            buy_price=price,
            taxes=tax,
            dividends=Decimal("0"),
        ))

    def _close(self, symbol: str, currency: str, quantity: Decimal, date: Datetime, price: Decimal, tax: Decimal):
        if quantity == 0:
            raise ValueError(f"zero quantity on sell: close_date: {date}, quantity: {quantity}")
        
        asset_quantity = sum(p.quantity for p in self.positions if not p.closed and p.symbol == symbol and p.currency == currency)
        if asset_quantity < quantity:
            raise ValueError(f"negative asset {symbol} balance on sell: close_date: {date}, quantity: {quantity}, asset_amount: {asset_quantity}")
        
        quantity_left = quantity
        for i, pos in enumerate(self.positions):
            if not pos.closed and pos.symbol == symbol and pos.currency == currency:
                if pos.quantity > quantity_left:
                    self._split_position(i, quantity_left)
                pos.closed = True
                pos.close_date = date
                pos.sell_price = price
                pos.taxes += tax * pos.quantity / quantity
                quantity_left -= pos.quantity
                if quantity_left == 0:
                    break

    def _split_position(self, index: int, quantity: Decimal):
        pos = self.positions[index]
        new_quantity = pos.quantity - quantity
        new_pos = Position(
            symbol=pos.symbol,
            currency=pos.currency,        
            quantity=new_quantity,
            open_date=pos.open_date,
            buy_price=pos.buy_price,
            taxes=pos.taxes * new_quantity / pos.quantity,
            dividends=pos.dividends * new_quantity / pos.quantity,
        )
        pos.quantity -= new_quantity
        pos.taxes -= new_pos.taxes
        pos.dividends -= new_pos.dividends
        self.positions.insert(index + 1, new_pos)

    def _assign_income(self, symbol: str, amount: Decimal, tax: Decimal, no_of_shares: Decimal, reversed_assignment: bool):
        if no_of_shares == 0:
            no_of_shares = sum(p.quantity for p in self.positions if p.symbol == symbol and not p.closed)

        amount_left = amount
        positions = reversed(self.positions) if reversed_assignment else self.positions
        for pos in positions:
            if pos.symbol == symbol and not pos.closed:
                pos_amount = min(amount * pos.quantity / no_of_shares, amount_left)
                pos.dividends += pos_amount
                pos.taxes += tax * pos_amount / amount
                amount_left -= pos_amount
                if amount_left == 0:
                    break

        if amount_left > Decimal('0.000001'):
            for pos in reversed(self.positions):
                if pos.symbol == symbol and pos.closed:
                    pos_amount = min(amount * pos.quantity / no_of_shares, amount_left)
                    pos.dividends += pos_amount
                    pos.taxes += tax * pos_amount / amount
                    amount_left -= pos_amount
                    if amount_left == 0:
                        break

        if abs(amount_left) > Decimal('0.000001'): # TODO: compatibilty backward, in clean version pos_amount should be rouneded and this shouldn't happen
            raise ValueError(f"wrong left over from dividends for {symbol}: {amount_left}; total: {amount}")
