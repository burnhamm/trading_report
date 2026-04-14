import csv

from decimal import Decimal
from pyxirr import xirr

from decimal_utils import normalize_money as nm
from model.position import Position

def generate_positions_view(positions: list[Position], fx_rate_provider, output_path: str):
    data = []
    for pos in positions:
        ex_rate = fx_rate_provider.get_rate(pos.currency, pos.close_date if pos.closed else pos.open_date)
        cost = pos.quantity * pos.buy_price * ex_rate
        dividends = sum(i.amount for i in pos.dividends)
        taxes = sum(i.amount for i in pos.taxes)
        if pos.closed:
            proceeds = pos.quantity * pos.sell_price * ex_rate
            profit = proceeds - cost + dividends
            length_days = max(1, (pos.close_date - pos.open_date).days)
            duration = Decimal(length_days / 365.24)
            annualized = profit / duration / cost
            xirr_result = calculate_xirr(pos, ex_rate)
            data.append(["CLOSED", pos.symbol, pos.quantity, pos.currency,  pos.open_date.date(), pos.buy_price, nm(cost), 
                         pos.close_date.date(), pos.sell_price, nm(proceeds), nm(dividends), nm(taxes), nm(profit), length_days, 
                         nm(annualized), nm(xirr_result)])
        else:
            data.append(["", pos.symbol, pos.quantity, pos.currency, pos.open_date.date(), pos.buy_price, nm(cost), "", "", "", 
                         nm(dividends), nm(taxes), "", "", "", ""])

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
