import os

from cli import parse_args
from exchange.broker_fx_rates_provider import BrokerFxRatesProvider
from exchange.forex_fx_rates_provider import ForexRatesProvider
from exchange.npb_fx_rates_provider import NbpRatesProvider
from loader import load_csv
from normalization import normalize_actions
from processing.cash_flow_builder import build_cash_flow
from processing.asset_builder import build_assets
from processing.currency_builder import build_currencies
from processing.position_builder import build_positions
from processing.fx_positions_builder import build_fx_positions
from processing.incomes_n_costs_builder import build_income_cost
from exchange.broker_fx_rates_builder import build_broker_fx_rates
from views.cash_flow_view import generate_cash_flow_view
from views.asset_view import generate_asset_view
from views.asset_performance_closed_view import generate_asset_performance_closed_view
from views.positions_view import generate_positions_view
from views.fx_view import generate_fx_view
from views.income_cost_view import generate_income_cost_view
from reporting.summary_report import generate_summary_report
from reporting.pit38_report import generate_pit38_report

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
    
    cash_flow = build_cash_flow(actions, base_currency)
    assets = build_assets(actions, fx_rate_provider)
    currencies = build_currencies(actions, fx_rate_provider)
    positions = build_positions(actions, fx_rate_provider) # FIFO trades
    fx_positions = build_fx_positions(actions, fx_rate_provider) # FX trades
    incosts = build_income_cost(actions, base_currency)

    # 5. Output artifacts
    if not os.path.exists(args.output_path):
        os.makedirs(args.output_path)

    views_path = os.path.join(args.output_path, "views")
    if not os.path.exists(views_path):
        os.makedirs(views_path)
    generate_cash_flow_view(cash_flow, views_path)
    generate_asset_view(assets, views_path)
    generate_asset_performance_closed_view(positions, fx_rate_provider, views_path)
    generate_positions_view(positions, fx_rate_provider, views_path)
    generate_fx_view(fx_positions, views_path)
    generate_income_cost_view(incosts, fx_rate_provider, views_path)

    reports_path = os.path.join(args.output_path, "reports")
    if not os.path.exists(reports_path):
        os.makedirs(reports_path)
    generate_summary_report(actions, currencies, positions, fx_positions, fx_rate_provider, reports_path)
    generate_pit38_report(positions, incosts, nbp_fx_provider, reports_path)


if __name__ == "__main__":
    main()
