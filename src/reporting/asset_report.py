import csv

from decimal import Decimal, ROUND_HALF_UP

from decimal_utils import normalize_decimal as nd
from model.asset import Asset

def generate_asset_report(assets: dict[str, dict[str, Asset]], fx_rate_provider, output_path: str):
    data = []
    for cur_assets in assets.values():
        for asset in cur_assets.values():
            if asset.is_currency:
                # continue
                pass
            data.append([asset.symbol, asset.currency, nd(asset.quantity), nd(asset.dividends), nd(asset.taxes)]) # TODO: add mean profit 

    data.sort(key=lambda r: r[0])
    data.insert(0, ["Ticker", "Currency", "Quantity", "Total dividends", "Total taxes"])

    with open(output_path + "/assets.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)
