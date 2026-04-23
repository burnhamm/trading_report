from decimal import Decimal

from model.action import Action
from model.asset import Asset


def build_assets(actions: list[Action], fx_rate_provider) -> dict[str, dict[str, Asset]]:
    ctx = AssetBuilder(fx_rate_provider)

    for action in actions:
        action.apply(ctx)  
        
    return ctx.assets


class AssetBuilder:
    def __init__(self, fx_rate_provider):
        self.fx_rate_provider = fx_rate_provider
        self.base_currency = fx_rate_provider.base_currency
        self.assets: dict[str, dict[str, Asset]] = {}

    def handle_deposit(self, action: Action):
        pass

    def handle_withdrawal(self, action: Action):
        pass

    def handle_buy(self, action: Action):
        asset = self._get_asset(action.symbol, action.currency)
        asset.quantity += action.quantity
        ex_rate = self.fx_rate_provider.get_rate(action.tax_currency, action.date) # TODO: amount + currency = separate type
        asset.taxes += action.tax * ex_rate

    def handle_sell(self, action: Action):
        asset = self._get_asset(action.symbol, action.currency)
        asset.quantity -= action.quantity
        asset.closed_quantity += action.quantity

    def handle_dividend(self, action: Action):
        ex_rate = self.fx_rate_provider.get_rate(action.currency, action.date)
        tax = action.tax * ex_rate
        self._assign_dividend(action.symbol, action.result, tax)

    def handle_lending_interest(self, action: Action):
        # TODO: assign evenly to all assets?
        pass

    def handle_interest_on_cash(self, action: Action):
        pass

    def handle_conversion(self, action: Action):
        pass

    def handle_spending(self, action: Action):
        pass

    def handle_cashback(self, action: Action):
        pass

    def handle_split(self, action: Action):
        for asset in self.assets[action.symbol].values():
            asset.quantity *= action.ratio

    def _get_asset(self, symbol: str, currency: str):
        if symbol not in self.assets:
            self.assets[symbol] = {}
        if currency not in self.assets[symbol]:
            self.assets[symbol][currency] = Asset(
                symbol=symbol,
                currency=currency,
                quantity=Decimal("0"),
                closed_quantity=Decimal("0"),
                dividends=Decimal("0"),
                taxes=Decimal("0"),
            )
        return self.assets[symbol][currency]

    def _assign_dividend(self, symbol: str, amount: Decimal, tax: Decimal):
        assign_to_closed = False
        total_quantity = sum(a.quantity for a in self.assets[symbol].values())
        if (total_quantity == Decimal("0")):
            assign_to_closed = True
            total_quantity = sum(a.closed_quantity for a in self.assets[symbol].values())
        for asset in self.assets[symbol].values():
            share = (asset.quantity if not assign_to_closed else asset.closed_quantity) / total_quantity
            asset.dividends += amount * share
            asset.taxes += tax * share