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
        self.assets: dict[str, Asset] = {}

    def handle_deposit(self, action: Action):
        asset = self._get_asset(self.base_currency, self.base_currency, True)
        asset.quantity += action.amount
        asset.fees += action.fee

    def handle_withdrawal(self, action: Action):
        asset = self._get_asset(self.base_currency, self.base_currency, True)
        asset.quantity -= action.amount

    def handle_buy(self, action: Action):
        cur_asset = self._get_asset(action.currency, action.currency, True)
        asset = self._get_asset(action.symbol, action.currency)
        cur_asset.quantity -= action.result
        asset.quantity += action.quantity
        ex_rate = self.fx_rate_provider.get_rate(action.tax_currency, action.date) # TODO: amount + currency = separate type
        asset.taxes += action.tax * ex_rate

    def handle_sell(self, action: Action):
        asset = self._get_asset(action.symbol, action.currency)
        cur_asset = self._get_asset(action.currency, action.currency, True)
        asset.quantity -= action.quantity
        asset.closed_quantity += action.quantity
        cur_asset.quantity += action.result

    def handle_exchange_buy(self, action: Action):
        src_cur = self._get_asset(self.base_currency, self.base_currency, True)
        dst_cur = self._get_asset(action.currency, action.currency, True)
        src_cur.quantity -= action.result
        dst_cur.quantity += action.quantity
        ex_rate = self.fx_rate_provider.get_rate(action.fee_currency, action.date)
        dst_cur.fees += action.fee * ex_rate

    def handle_exchange_sell(self, action: Action):
        src_cur = self._get_asset(self.base_currency, self.base_currency, True)
        dst_cur = self._get_asset(action.currency, action.currency, True)
        src_cur.quantity += action.result
        dst_cur.quantity -= action.quantity
        ex_rate = self.fx_rate_provider.get_rate(action.fee_currency, action.date)
        src_cur.fees += action.fee * ex_rate

    def handle_dividend(self, action: Action):
        cur_asset = self._get_asset(self.base_currency, self.base_currency, True)
        cur_asset.quantity += action.result
        ex_rate = self.fx_rate_provider.get_rate(action.currency, action.date)
        tax = action.tax * ex_rate
        self._assign_dividend(action.symbol, action.result, tax)

    def handle_lending_interest(self, action: Action):
        asset = self._get_asset(self.base_currency, self.base_currency, True)
        asset.quantity += action.result

    def handle_interest_on_cash(self, action: Action):
        asset = self._get_asset(action.currency, action.currency, True)
        asset.dividents += action.amount
        asset.quantity += action.amount

    # TODO: same as withdrawal?
    def handle_spending(self, action: Action):
        asset = self._get_asset(self.base_currency, self.base_currency, True)
        asset.quantity -= action.result

    def handle_cashback(self, action: Action):
        asset = self._get_asset(self.base_currency, self.base_currency, True)
        asset.quantity += action.result

    def handle_split(self, action: Action):
        for asset in self.assets[action.symbol].values():
            asset.quantity *= action.ratio

    def _get_asset(self, symbol: str, currency: str, is_currency=False):
        if symbol not in self.assets:
            self.assets[symbol] = {}
        if currency not in self.assets[symbol]:
            self.assets[symbol][currency] = Asset(
                symbol=symbol,
                currency=currency,
                quantity=Decimal("0"),
                dividents=Decimal("0"),
                taxes=Decimal("0"),
                fees=Decimal("0"),
                is_currency=is_currency,
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
            asset.dividents += amount * share
            asset.taxes += tax * share