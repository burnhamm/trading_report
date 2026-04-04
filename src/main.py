import os

from cli import parse_args
from exchange.broker_fx_rates_provider import BrokerFxRatesProvider
from exchange.forex_fx_rates_provider import ForexRatesProvider
from exchange.npb_fx_rates_provider import NbpRatesProvider
from loader import load_csv
from normalization import normalize_actions
from processing.asset_builder import build_assets
from processing.position_builder import build_positions
from processing.fx_positions_builder import build_fx_positions
from exchange.broker_fx_rates_builder import build_broker_fx_rates
from views.asset_view import generate_asset_view
from views.positions_view import generate_positions_view
from views.fx_view import generate_fx_view
from reporting.summary_report import generate_summary_report

from datetime import datetime as Datetime


def main():
    # 1. CLI
    args = parse_args()

    base_currency = "PLN" # TODO: pass as parameter

    # 2. Load raw data
    raw_actions = load_csv(args.input, base_currency, args.broker)

    # 3. Normalize
    actions = normalize_actions(raw_actions, base_currency, args.broker)

    # 4. Core processing
    ex_rates = build_broker_fx_rates(actions, base_currency) # FX rates based actions data
    nbp_fx_provider = NbpRatesProvider(base_currency, "nbp") # TODO: implementation may be parameterized
    fx_rate_provider = BrokerFxRatesProvider(ex_rates, base_currency, backup_provider=nbp_fx_provider) # TODO: implementation may be parameterized

    assets = build_assets(actions, fx_rate_provider)        
    positions = build_positions(actions, fx_rate_provider) # FIFO trades
    fx_positions = build_fx_positions(actions, fx_rate_provider) # FX trades

    # 5. Output artifacts
    if not os.path.exists(args.output_path):
        os.makedirs(args.output_path)

    views_path = os.path.join(args.output_path, "views")
    if not os.path.exists(views_path):
        os.makedirs(views_path)
    generate_asset_view(assets, views_path)
    generate_positions_view(positions, fx_rate_provider, views_path)
    generate_fx_view(fx_positions, views_path)

    reports_path = os.path.join(args.output_path, "reports")
    if not os.path.exists(reports_path):
        os.makedirs(reports_path)
    generate_summary_report(actions, assets, positions, fx_positions, fx_rate_provider, reports_path)


if __name__ == "__main__":
    main()
