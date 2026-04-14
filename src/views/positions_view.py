import csv

from decimal import Decimal
from pyxirr import xirr

from decimal_utils import normalize_money as nm
from model.position import Position

def generate_positions_view(positions: list[Position], fx_rate_provider, output_path: str):
    data = []
    for p in positions:
        ex_rate = fx_rate_provider.get_rate(p.currency, p.close_date if p.closed else p.open_date)
        total_buy = p.quantity * p.buy_price * ex_rate
        dividends = sum(i.amount for i in p.dividends)
        taxes = sum(i.amount for i in p.taxes)
        if p.closed:
            total_sell = p.quantity * p.sell_price * ex_rate
            total_profit = total_sell - total_buy + dividends
            length_days = (p.close_date - p.open_date).days
            yearly_profit = total_profit / length_days * 365 if length_days > 0 else 0
            yearly_profit_percent = yearly_profit / total_buy if total_buy > Decimal("0") else 0
            xirr_result = calculate_xirr(p, ex_rate)
            data.append(["CLOSED", p.symbol, p.quantity, p.currency,  p.open_date.date(), p.buy_price, nm(total_buy), p.close_date.date(), p.sell_price, nm(total_sell), nm(dividends), nm(taxes), nm(total_profit), length_days, nm(yearly_profit_percent), nm(xirr_result)])
        else:
            data.append(["", p.symbol, p.quantity, p.currency,  p.open_date.date(), p.buy_price, nm(total_buy), "", "", "", nm(dividends), nm(taxes), "", "", "", ""])

    data.sort(key=lambda r: (r[1], r[3], r[4]))
    data.sort(key=lambda r: r[0], reverse=True)
    data.insert(0, 
        ["Closed", "Ticker", "Amount", "Currency", "Buy date", "Buy price", "Total buy", "Sell date", "Sell price", "Total sell", "Dividends", "Taxes", "Net profit", "Position length (days)", "Annual profit", "XIRR"])

    with open(output_path + "/positions.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)


def calculate_xirr(position: Position, ex_rate: Decimal) -> Decimal:
    flows = []
    flows.append((position.open_date, -position.quantity * position.buy_price * ex_rate))
    flows.append((position.close_date, position.quantity * position.sell_price * ex_rate))
    for tax in position.taxes:
        if tax.amount > Decimal("0"):
            flows.append((tax.date, -tax.amount))
    for dividend in position.dividends:
        flows.append((dividend.date, dividend.amount))
    result = xirr(flows)
    if result is None:
        breakpoint()
    return Decimal(xirr(flows))
