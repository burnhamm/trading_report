import csv

from collections import defaultdict
from datetime import date as Date
from decimal import Decimal
from pyxirr import xirr

from decimal_utils import normalize_money as nm
from model.position import Position

def generate_asset_performance_closed_view(positions: list[Position], fx_rate_provider, output_path: str):
    asset_names = list({ (pos.symbol, pos.currency) for pos in positions })
    
    data = []
    for symbol, currency in asset_names:
        asset_positions = [pos for pos in positions if pos.symbol == symbol and pos.currency == currency and pos.closed]
        if len(asset_positions) == 0: 
            continue

        quantity = Decimal("0")
        cost = Decimal("0")
        cost_ccy = Decimal("0")
        proceeds = Decimal("0")        
        proceeds_ccy = Decimal("0")
        taxes = Decimal("0")
        dividends = Decimal("0")
        asset_weight = Decimal("0")
        annualized = Decimal("0")

        for pos in asset_positions:
            quantity += pos.quantity

            open_ex_rate = fx_rate_provider.get_rate(pos.currency, pos.open_date)
            close_ex_rate = fx_rate_provider.get_rate(pos.currency, pos.close_date)

            pos_cost_ccy = pos.quantity * pos.buy_price
            pos_cost = pos_cost_ccy * open_ex_rate
            pos_proceeds_ccy = pos.quantity * pos.sell_price
            pos_proceeds = pos_proceeds_ccy * close_ex_rate

            cost += pos_cost
            cost_ccy += pos_cost_ccy
            proceeds += pos_proceeds
            proceeds_ccy += pos_proceeds_ccy

            taxes += sum(tax.amount for tax in pos.taxes)
            pos_dividends = sum(div.amount for div in pos.dividends)
            dividends += pos_dividends

            pos_profit = pos_proceeds - pos_cost + pos_dividends
            pos_duration = Decimal(max(1, (pos.close_date - pos.open_date).days) / 365.24)
            pos_annualized = pos_profit / pos_duration / pos_cost

            pos_weight = pos_cost * pos_duration
            asset_weight += pos_weight

            annualized += pos_weight * pos_annualized

        profit = proceeds - cost + dividends
        profit_ccy = proceeds_ccy - cost_ccy

        annualized /= asset_weight
        data.append([symbol, currency, nm(asset_weight), quantity, nm(cost_ccy), nm(proceeds_ccy), nm(cost), nm(proceeds), 
                     nm(dividends), nm(taxes), nm(profit_ccy), nm(profit), nm(annualized)])

    data.sort(key=lambda r: (r[2]), reverse=True)
    #TODO: add FX impact
    #TODO: add exchange fee
    data.insert(0, ["Ticker", "Currency", f"Capital Exposure ({fx_rate_provider.base_currency} * years)", "Total Quantity Traded",
                    f"Cost Basis (CURRENCY)", f"Proceeds (CURRENCY)",
                    f"Cost Basis ({fx_rate_provider.base_currency})", f"Proceeds ({fx_rate_provider.base_currency})",
                    f"Dividends ({fx_rate_provider.base_currency})", f"Taxes ({fx_rate_provider.base_currency})",
                    f"Net Profit/Loss (CURRENCY)", f"Net Profit/Loss ({fx_rate_provider.base_currency})", "Annualized Return"])
    
    with open(output_path + "/asset_performance_closed.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)
