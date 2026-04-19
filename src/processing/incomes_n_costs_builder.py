from datetime import date as Date
from decimal import Decimal, ROUND_HALF_UP

from model.action import Action
from model.currency_position import CurrencyPosition
from model.incomes_n_costs import Incost, IncostType

def build_income_cost(actions: list[Action], base_currency: str) -> list[Incost]:
    ctx = IncomeCostBuilder(base_currency)

    for action in actions:
        action.apply(ctx)

    return ctx.incomes_n_costs


class IncomeCostBuilder:
    def __init__(self, base_currency: str):
        self.base_currency = base_currency
        self.incomes_n_costs = []

    def handle_deposit(self, action: Action):
        if action.fee > Decimal(0):
            self.incomes_n_costs.append(Incost(
                date=action.date,
                type=IncostType.DEPOSIT_FEE,
                amount=action.fee,
                currency=self.base_currency
            ))

    def handle_withdrawal(self, action: Action):
        pass

    def handle_buy(self, action: Action):
        if action.exchange_fee > Decimal(0):
            self.incomes_n_costs.append(Incost(
                date=action.date,
                type=IncostType.CONVERSION_FEE,
                amount=action.exchange_fee,
                currency=self.base_currency,
            ))
        if action.tax > Decimal(0):
            self.incomes_n_costs.append(Incost(
                date=action.date,
                type=IncostType.TAX,
                amount=action.tax,
                currency=action.tax_currency,
                symbol=action.symbol
            ))

    def handle_sell(self, action: Action):
        if action.exchange_fee > Decimal(0):
            self.incomes_n_costs.append(Incost(
                date=action.date,
                type=IncostType.CONVERSION_FEE,
                amount=action.exchange_fee,
                currency=self.base_currency,
            ))

    def handle_exchange_buy(self, action: Action):
        if action.fee > Decimal(0):
            self.incomes_n_costs.append(Incost(
                date=action.date,
                type=IncostType.CONVERSION_FEE,
                amount=action.fee,
                currency=action.fee_currency,
            ))

    def handle_exchange_sell(self, action: Action):
        if action.fee > Decimal(0):
            self.incomes_n_costs.append(Incost(
                date=action.date,
                type=IncostType.CONVERSION_FEE,
                amount=action.fee,
                currency=action.fee_currency,
            ))

    def handle_dividend(self, action: Action):
        self.incomes_n_costs.append(Incost(
            date=action.date,
            type=IncostType.DIVIDEND,
            amount=action.result,
            currency=action.currency,
            symbol=action.symbol
        ))
        if action.tax > Decimal(0):
            self.incomes_n_costs.append(Incost(
                date=action.date,
                type=IncostType.TAX,
                amount=action.tax,
                currency=action.tax_currency,
                symbol=action.symbol
            ))

    def handle_lending_interest(self, action: Action):
        self.incomes_n_costs.append(Incost(
            date=action.date,
            type=IncostType.INTEREST_LENDING,
            amount=action.result,
            currency=self.base_currency
        ))

    def handle_interest_on_cash(self, action: Action):
        self.incomes_n_costs.append(Incost(
            date=action.date,
            type=IncostType.INTEREST_CASH,
            amount=action.amount,
            currency=action.currency
        ))

    def handle_spending(self, action: Action):
        pass

    def handle_cashback(self, action: Action):
        pass

    def handle_split(self, action: Action):
        pass