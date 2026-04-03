import csv

from decimal import Decimal

from decimal_utils import normalize_decimal as nd
from model.currency import CurrencyPosition

def generate_fx_report(positions: list[CurrencyPosition], output_path: str):
    data = []
    for p in positions:
        total_buy = p.amount * p.buy_price
        if p.closed:
            total_sell = p.amount * p.sell_price
            total_profit = total_sell - total_buy + p.interest - p.fees
            length_days = (p.close_date - p.open_date).days
            yearly_profit = total_profit / length_days * 365 if length_days > 0 else 0
            yearly_profit_percent = yearly_profit / total_buy if total_buy > Decimal("0") else 0
            # data.append([p.name, 'CLOSED', nd(p.amount), p.open_date.date(), nd(p.buy_price), nd(p.fees), nd(p.interest), p.close_date.date(), nd(p.sell_price)])
            data.append([p.name, 'CLOSED', nd(p.amount), p.open_date.date(), nd(p.buy_price), nd(total_buy), nd(p.fees), nd(p.interest), p.close_date.date(), nd(p.sell_price), nd(total_sell)])
        else:
            # data.append([p.name, '', nd(p.amount), p.open_date.date(), nd(p.buy_price), nd(p.fees), nd(p.interest), '', '']) # add total buy here
            data.append([p.name, '', nd(p.amount), p.open_date.date(), nd(p.buy_price), nd(total_buy), nd(p.fees), nd(p.interest), '', '', '']) # add total buy here

    data.sort(key=lambda r: r[0])
    # data.insert(0, ["Name", "Closed", "Amount", "Buy date", "Buy price", "Total fees", "Total dividents", "Sell date", "Sell price"]) # change to Total interest
    data.insert(0, ["Name", "Closed", "Amount", "Buy date", "Buy price", "Total buy", "Total fees", "Total dividents", "Sell date", "Sell price", "Total sell"]) # change to Total interest

    with open(output_path + "/fx.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)
