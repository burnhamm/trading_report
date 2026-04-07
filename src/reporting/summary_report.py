from decimal import Decimal

from model.asset import Asset
from model.action import Action
from model.position import Position
from model.currency import CurrencyPosition


def generate_summary_report(actions: list[Action], assets: dict[str, dict[str, Asset]], positions: list[Position], currencies: list[CurrencyPosition], fx_rate_provider, output_path: str):
    ctx = SummaryReport(fx_rate_provider)

    min_date = actions[0].date.date()
    max_date = actions[-1].date.date()

    for action in actions:
        action.apply(ctx)

    for cur_asset in assets.values():
        for asset in cur_asset.values():
            ctx.handle_asset(asset)

    for position in positions:
        ctx.handle_position(position)

    for currency in currencies:
        ctx.handle_currency(currency)

    with open(output_path + "/summary.txt", "w") as file:
        print_period(file, min_date, max_date)
        print_cash_flow(ctx, file)
        file.write("\n\n")
        print_realized(ctx, file)
        file.write("\n\n")
        print_open(ctx, file)


# TODO: SummaryReport belongs to processing module
class SummaryReport:
    def __init__(self, fx_rate_provider):
        self.fx_rate_provider = fx_rate_provider
        self.base_currency = fx_rate_provider.base_currency

        self.deposits = Decimal("0")
        self.withdrawals = Decimal("0")
        self.spending = Decimal("0")
        self.cashback = Decimal("0")

        self.open_position_total = Decimal("0")
        self.open_position_currency = {}

        self.closed_position_revenue = Decimal("0")
        self.closed_position_expenses = Decimal("0")
        self.dividends = Decimal("0")
        self.interest_on_lending = Decimal("0")
        self.taxes = Decimal("0")

        self.currency_revenue = Decimal("0")
        self.currency_expenses = Decimal("0")
        self.interest_on_cash = Decimal("0")        
        self.deposit_fees = Decimal("0")
        self.exchange_fees = Decimal("0")

        self.cash_balance = {}

    def handle_deposit(self, action: Action):
        self.deposits += action.amount
        self.deposit_fees += action.fee

    def handle_withdrawal(self, action: Action):
        self.withdrawals += action.amount

    def handle_buy(self, action: Action):
        ex_rate = self.fx_rate_provider.get_rate(action.tax_currency, action.date)
        self.taxes += action.tax * ex_rate

    def handle_sell(self, action: Action):
        pass

    def handle_exchange_buy(self, action: Action):
        self.exchange_fees += action.fee

    def handle_exchange_sell(self, action: Action):
        self.exchange_fees += action.fee

    def handle_dividend(self, action: Action):
        self.dividends += action.result
        ex_rate = self.fx_rate_provider.get_rate(action.tax_currency, action.date)
        self.taxes += action.tax * ex_rate

    def handle_lending_interest(self, action: Action):
        self.interest_on_lending += action.result

    def handle_interest_on_cash(self, action: Action):
        ex_rate = self.fx_rate_provider.get_rate(action.currency, action.date)
        self.interest_on_cash += action.amount * ex_rate

    def handle_spending(self, action: Action):
        self.spending += action.result

    def handle_cashback(self, action: Action):
        self.cashback += action.result

    def handle_split(self, action: Action):
        pass

    def handle_asset(self, asset: Asset):
        if asset.is_currency:
            self.cash_balance[asset.currency] = asset.quantity

    def handle_position(self, position: Position):
        ex_rate = self.fx_rate_provider.get_rate(position.currency, position.close_date if position.closed else position.open_date)
        if not position.closed:
            self.open_position_currency[position.currency] = self.open_position_currency.get(position.currency, Decimal("0")) + position.quantity * position.buy_price
            self.open_position_total += position.quantity * position.buy_price * ex_rate
        else:
            self.closed_position_revenue += position.quantity * position.sell_price * ex_rate
            self.closed_position_expenses += position.quantity * position.buy_price * ex_rate

    def handle_currency(self, currency: CurrencyPosition):
        if currency.closed:
            self.currency_revenue += currency.amount * currency.sell_price
            self.currency_expenses += currency.amount * currency.buy_price


def print_period(file, min_date, max_date):
    file.write(f"=== PERIOD: {min_date} - {max_date} ===\n\n")


def print_cash_flow(report: SummaryReport, file):
    def fmt(x: Decimal) -> str: #TODO: move to utils
        return f"{x:.2f}"
    
    file.write("=== CASH FLOW ===\n\n")

    file.write(f"{'category':<22} {'amount':>12}\n")
    file.write("-" * 36 + "\n")

    file.write(f"{'deposits':<22} {fmt(report.deposits):>12}\n")
    file.write(f"{'withdrawals':<22} {fmt(report.withdrawals):>12}\n")
    file.write(f"{'spending':<22} {fmt(report.spending):>12}\n")
    file.write(f"{'cashback':<22} {fmt(report.cashback):>12}\n")

    file.write("-" * 36 + "\n")

    net_flow = report.deposits - report.withdrawals - report.spending
    file.write(f"{'NET CASH FLOW':<22} {fmt(net_flow):>12}\n")


def print_realized(report: SummaryReport, file):
    def fmt(x: Decimal) -> str: #TODO: move to utils
        return f"{x:.2f}"

    def row(name, expenses, revenue):
        result = revenue - expenses
        return f"{name:<22} {fmt(expenses):>12} {fmt(revenue):>12} {fmt(result):>12}\n"
    
    file.write("=== REALIZED PnL ===\n\n")

    file.write("--- Assets ---\n")
    file.write(f"{'category':<22} {'expenses':>12} {'revenue':>12} {'result':>12}\n")
    file.write("-" * 62 + "\n")

    file.write(row("closed positions", report.closed_position_expenses, report.closed_position_revenue))
    file.write(row("dividends", Decimal("0"), report.dividends))
    file.write(row("interest", Decimal("0"), report.interest_on_lending))
    file.write(row("taxes", report.taxes, Decimal("0")))

    total_exp = report.closed_position_expenses + report.taxes
    total_rev = report.closed_position_revenue + report.dividends + report.interest_on_lending
    file.write("-" * 62 + "\n")
    file.write(row("TOTAL (net)", total_exp, total_rev))

    file.write("\n--- Currencies ---\n")
    file.write(f"{'category':<22} {'expenses':>12} {'revenue':>12} {'result':>12}\n")
    file.write("-" * 62 + "\n")

    file.write(row("currency trading", report.currency_expenses, report.currency_revenue))
    file.write(row("interest on cash", Decimal("0"), report.interest_on_cash))
    file.write(row("deposit fees", report.deposit_fees, Decimal("0")))
    file.write(row("exchange fees", report.exchange_fees, Decimal("0")))

    total_exp = report.currency_expenses + report.deposit_fees + report.exchange_fees
    total_rev = report.currency_revenue + report.interest_on_cash
    file.write("-" * 62 + "\n")
    file.write(row("TOTAL (net)", total_exp, total_rev))


def print_open(report: SummaryReport, file):
    def fmt(x: Decimal) -> str: #TODO: move to utils
        return f"{x:.2f}"
    
    file.write("=== OPEN POSITIONS ===\n\n")
    file.write("--- Assets ---\n")
    for currency, amount in report.open_position_currency.items():
        file.write(f"{currency:<28}: {fmt(amount):>8}\n")
    file.write("-" * 36 + "\n")
    file.write(f"total capital invested ({report.base_currency}): {fmt(report.open_position_total):>8}\n")

    file.write("\n--- Cash ---\n")
    for currency, amount in report.cash_balance.items():
        file.write(f"{currency:<28}: {fmt(amount):>8}\n")
    