import csv

from decimal import Decimal

from decimal_utils import normalize_decimal as nd
from model.position import Position

def generate_positions_view(positions: list[Position], fx_rate_provider, output_path: str):
    data = []
    for p in positions:
        ex_rate = fx_rate_provider.get_rate(p.currency, p.close_date if p.closed else p.open_date)
        total_buy = p.quantity * p.buy_price * ex_rate
        if p.closed:
            total_sell = p.quantity * p.sell_price * ex_rate
            total_profit = total_sell - total_buy + p.dividends - p.taxes
            length_days = (p.close_date - p.open_date).days
            yearly_profit = total_profit / length_days * 365 if length_days > 0 else 0
            yearly_profit_percent = yearly_profit / total_buy if total_buy > Decimal("0") else 0
            data.append(["CLOSED", p.symbol, nd(p.quantity), p.currency,  p.open_date.date(), nd(p.buy_price), nd(total_buy), p.close_date.date(), nd(p.sell_price), nd(total_sell), nd(p.dividends), nd(p.taxes), nd(total_profit), length_days, f"{nd(yearly_profit_percent * 100)}%"])
        else:
            data.append(["", p.symbol, nd(p.quantity), p.currency,  p.open_date.date(), nd(p.buy_price), nd(total_buy), "", "", "", nd(p.dividends), nd(p.taxes), "", "", ""])

    data.sort(key=lambda r: (r[1], r[3], r[4]))
    data.sort(key=lambda r: r[0], reverse=True)
    data.insert(0, 
        ["Closed", "Ticker", "Amount", "Currency", "Buy date", "Buy price", "Total buy", "Sell date", "Sell price", "Total sell", "Dividends", "Taxes", "Net profit", "Position length (days)", "Yearly profit %"])

    with open(output_path + "/positions.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)
