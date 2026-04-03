from dataclasses import dataclass
from datetime import datetime as Datetime
from decimal import Decimal


@dataclass
class Action: # add validation for all fields in constructors
    date: Datetime

    def apply(self, ctx):
        raise NotImplementedError


@dataclass
class DepositAction(Action):
    amount: Decimal
    fee: Decimal

    def apply(self, ctx):
        ctx.handle_deposit(self)


@dataclass
class WithdrawalAction(Action):
    amount: Decimal

    def apply(self, ctx):
        ctx.handle_withdrawal(self)


@dataclass
class AssetAction(Action):
    symbol: str
    currency: str

    quantity: Decimal
    price: Decimal

    result: Decimal


@dataclass
class BuyAction(AssetAction):
    tax: Decimal
    tax_currency: str

    def apply(self, ctx):
        ctx.handle_buy(self)


@dataclass
class SellAction(AssetAction):
    def apply(self, ctx):
        ctx.handle_sell(self)


@dataclass
class ExchangeAction(Action):
    currency: str # destination currency for exchange, the source is always base currency
    quantity: Decimal
    exchange_rate: Decimal

    fee: Decimal
    fee_currency: str # TODO: ensure it is used correclty in all reports and builders

    result: Decimal


@dataclass
class ExchangeBuyAction(ExchangeAction):
    def apply(self, ctx):
        ctx.handle_exchange_buy(self)


@dataclass
class ExchangeSellAction(ExchangeAction):
    def apply(self, ctx):
        ctx.handle_exchange_sell(self)


@dataclass
class DividendAction(Action):
    symbol: str
    currency: str # TODO: determine if this can be not base currency
    no_of_shares: Decimal
    amount_per_share: Decimal # TODO: currently not used anywhere
    reversed_assignment: bool
    tax: Decimal
    tax_currency: str
    result: Decimal

    def apply(self, ctx):
        ctx.handle_dividend(self)


@dataclass
class LendingInterestAction(Action):
    result: Decimal

    def apply(self, ctx):
        ctx.handle_lending_interest(self)


@dataclass
class InterestOnCashAction(Action):
    currency: str
    amount: Decimal

    def apply(self, ctx):
        ctx.handle_interest_on_cash(self)


@dataclass
class SpendingAction(Action):
    result: Decimal

    def apply(self, ctx):
        ctx.handle_spending(self)


@dataclass
class CashbackAction(Action):
    result: Decimal

    def apply(self, ctx):
        ctx.handle_cashback(self)


@dataclass
class SplitAction(Action):
    symbol: str
    ratio: Decimal

    def apply(self, ctx):
        ctx.handle_split(self)