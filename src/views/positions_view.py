import csv

from decimal import Decimal
from pyxirr import xirr

from decimal_utils import normalize_money as nm
from model.position import Position

def generate_positions_view(positions: list[Position], fx_rate_provider, output_path: str):
    data = []
    for pos in positions:
        buy_ex_rate = pos.buy_ex_rate or fx_rate_provider.get_rate(pos.currency, pos.open_date)
        cost = pos.quantity * pos.buy_price * buy_ex_rate
        dividends = sum(i.amount for i in pos.dividends)
        taxes = sum(i.amount for i in pos.taxes)
        fees = sum(i.amount for i in pos.exchange_fees)
        if pos.closed:
            sell_ex_rate = pos.sell_ex_rate or fx_rate_provider.get_rate(pos.currency, pos.close_date)
            proceeds = pos.quantity * pos.sell_price * sell_ex_rate
            profit = pos.quantity * buy_ex_rate * (pos.sell_price - pos.buy_price)
            fx_impact = proceeds - cost - profit
            total_profit = proceeds - cost + dividends - fees
            duration_days = max(1, (pos.close_date - pos.open_date).days)
            duration = Decimal(duration_days / 365.24)
            annualized = profit / duration / cost
            exposure = duration * cost
            data.append(["CLOSED", pos.symbol, pos.currency, pos.quantity, nm(exposure),
                         pos.open_date.date(), pos.buy_price, nm(cost), 
                         pos.close_date.date(), pos.sell_price, nm(proceeds),
                         nm(dividends), nm(fees), nm(taxes), nm(profit), duration_days,
                         nm(annualized)])
        else:
            data.append(["", pos.symbol, pos.currency, "",
                         pos.quantity, pos.open_date.date(), pos.buy_price, nm(cost), 
                         "", "", "",
                         nm(dividends), nm(fees), nm(taxes), "", "",
                         ""])

    data.sort(key=lambda r: (r[1], r[2], r[5]))
    data.sort(key=lambda r: r[0], reverse=True)
    data.insert(0, 
        ["Closed", "Ticker", "Currency", "Quantity", f"Capital Exposure ({fx_rate_provider.base_currency} * years)", 
         "Open date", f"Entry price ({fx_rate_provider.base_currency})", f"Cost Basis ({fx_rate_provider.base_currency})", 
         "Close date", f"Exit price ({fx_rate_provider.base_currency})", f"Proceeds ({fx_rate_provider.base_currency})",
         f"Dividends ({fx_rate_provider.base_currency})", f"Exchange fees ({fx_rate_provider.base_currency})", f"Taxes ({fx_rate_provider.base_currency})",
         f"Profit/Loss ({fx_rate_provider.base_currency})", "Holding period (days)",
         "Annual Return"])

    with open(output_path + "/positions.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)
