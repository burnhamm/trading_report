import csv

from decimal import Decimal

from decimal_utils import normalize_decimal as nd
from model.position import Position

def generate_positions_report(positions: list[Position], fx_rate_provider, output_path: str):
    data = []
    for p in positions:
        if p.is_currency:
            continue

        ex_rate = fx_rate_provider.get_rate(p.currency, p.close_date if p.closed else p.open_date)
        total_buy = p.quantity * p.buy_price * ex_rate
        if p.closed:
            total_sell = p.quantity * p.sell_price * ex_rate
            total_profit = total_sell - total_buy + p.dividents - p.fees
            length_days = (p.close_date - p.open_date).days
            yearly_profit = total_profit / length_days * 365 if length_days > 0 else 0
            yearly_profit_percent = yearly_profit / total_buy if total_buy > Decimal("0") else 0
            #data.append([p.symbol, 'CLOSED', p.currency, nd(p.quantity), p.open_date.date(), nd(p.buy_price), nd(p.fees), nd(p.dividents), p.close_date.date(), nd(p.sell_price)])
            data.append([p.symbol, 'CLOSED', p.currency, nd(p.quantity), p.open_date.date(), nd(p.buy_price), nd(total_buy), nd(p.fees), nd(p.dividents), p.close_date.date(), nd(p.sell_price), nd(total_sell)])
        else:
            # data.append([p.symbol, '', p.currency, nd(p.quantity), p.open_date.date(), nd(p.buy_price), nd(p.fees), nd(p.dividents), '', '']) # add total buy here
            data.append([p.symbol, '', p.currency, nd(p.quantity), p.open_date.date(), nd(p.buy_price), nd(total_buy), nd(p.fees), nd(p.dividents), '', '', ''])

    # sort by closed first, then by symbol, then by currency, then by quantity
    # data.sort(key=lambda r: (r[0]))
    data.sort(key=lambda r: (r[0], r[2], r[4]))
    data.sort(key=lambda r: r[1], reverse=True)
    # data.insert(0, ["Ticker", "Closed", "Currency", "Amount", "Buy date", "Buy price", "Total fees", "Total dividents", "Sell date", "Sell price"])
    data.insert(0, ["Ticker", "Closed", "Currency", "Amount", "Buy date", "Buy price", "Total buy", "Total fees", "Total dividents", "Sell date", "Sell price", "Total sell"])

    with open(output_path + "/positions.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)
