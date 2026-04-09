import os
import csv
from datetime import date as Datetime
from decimal import Decimal
from dataclasses import dataclass

from decimal_utils import normalize_money as nm
from exchange.npb_fx_rates_provider import NbpRatesProvider
from model.position import Position
from model.incomes_n_costs import Incost, IncostType


@dataclass
class PitPosition:
    symbol: str
    quantity: Decimal
    currency: str
    open_date: Datetime
    buy_price: Decimal
    buy_rate: Decimal
    close_date: Datetime
    sell_price: Decimal
    sell_rate: Decimal


@dataclass
class AnnualPitReport:
    positions_revenue: Decimal
    positions_expenses: Decimal
    dividends: Decimal
    interest_on_cash: Decimal
    lending_interest: Decimal
    exchange_fees: Decimal
    taxes: Decimal

    positions: list[PitPosition]


def generate_pit38_report(positions: list[Position], incosts: Incost, nbp_fx_provider: NbpRatesProvider, output_path: str):
    report = Pit38ReportBuilder(nbp_fx_provider) # TODO: add detailed positions csv with nbp rates

    for pos in positions:
        report.handle_position(pos)

    for inc in incosts:
        report.handle_incost(inc)

    pit_path = os.path.join(output_path, "pit")
    if not os.path.exists(pit_path):
        os.makedirs(pit_path)

    print_annual_reports(report, pit_path)
    generate_pit38_positions(report, pit_path)


class Pit38ReportBuilder:
    def __init__(self, nbp_fx_provider: NbpRatesProvider):
        self.nbp_fx_provider = nbp_fx_provider
        self.annual_reports = {}

    def handle_position(self, position: Position):
        if position.closed:
            annual = self._get_annual_report(position.close_date.year)
            buy_rate = self.nbp_fx_provider.get_prev_day_rate(position.currency, position.open_date)
            annual.positions_expenses += position.quantity * position.buy_price * buy_rate
            sell_rate = self.nbp_fx_provider.get_prev_day_rate(position.currency, position.close_date)
            annual.positions_revenue += position.quantity * position.sell_price * sell_rate
            annual.positions.append(PitPosition(
                symbol=position.symbol,
                quantity=position.quantity,
                currency=position.currency,
                open_date=position.open_date,
                buy_price=position.buy_price,
                buy_rate=buy_rate,
                close_date=position.close_date,
                sell_price=position.sell_price,
                sell_rate=sell_rate
            ))
            

    def handle_incost(self, incost: Incost):
        annual = self._get_annual_report(incost.date.year)
        match incost.type:
            case IncostType.DIVIDEND:
                annual.dividends += incost.amount
            case IncostType.INTEREST_CASH:
                annual.interest_on_cash += incost.amount
            case IncostType.INTEREST_LENDING:
                annual.lending_interest += incost.amount
            case IncostType.CONVERSION_FEE:
                annual.exchange_fees += incost.amount
            case IncostType.TAX:
                annual.taxes += incost.amount
            

    def _get_annual_report(self, year: int) -> AnnualPitReport:
        if year not in self.annual_reports:
            self.annual_reports[year] = AnnualPitReport(
                positions_revenue=Decimal("0"),
                positions_expenses=Decimal("0"),
                dividends=Decimal("0"),
                interest_on_cash=Decimal("0"),
                lending_interest=Decimal("0"),
                exchange_fees=Decimal("0"),
                taxes=Decimal("0"),
                positions=[],
            )
        return self.annual_reports[year]
    

def print_annual_reports(report: Pit38ReportBuilder, output_path: str):
    for year, report in report.annual_reports.items():
        with open(output_path + f"/{year}.txt", "w") as file:
            file.write(f"=== Rok {year} ===\n\n")

            file.write(f"=== Przychody ===\n\n")
            file.write(f"{'Zamknięcie pozycji:':<22} {report.positions_revenue:>12.2f} PLN\n")
            file.write(f"{'Dywidendy:':<22} {report.dividends:>12.2f} PLN\n")
            file.write(f"{'Odsetki od gotówki:':<22} {report.interest_on_cash:>12.2f} PLN\n")
            file.write(f"{'Odsetki od pożyczek:':<22} {report.lending_interest:>12.2f} PLN\n")
            file.write(f"-" * 40 + "\n")
            file.write(f"{'Suma przychodów:':<22} {report.positions_revenue + report.dividends + report.interest_on_cash + report.lending_interest:>12.2f} PLN\n")

            file.write(f"\n=== Koszty ===\n\n")
            file.write(f"{'Zamknięcie pozycji:':<22} {report.positions_expenses:>12.2f} PLN\n")
            file.write(f"{'Prowizje walutowe:':<22} {report.exchange_fees:>12.2f} PLN\n")
            file.write(f"-" * 40 + "\n")
            file.write(f"{'Suma kosztów:':<22} {report.positions_expenses + report.exchange_fees:>12.2f} PLN\n")
            
            file.write(f"\n=== Podatek ===\n\n")
            file.write(f"{'Zapłacony za granicą:':<22} {report.taxes:>12.2f} PLN\n")


def generate_pit38_positions(report: Pit38ReportBuilder, output_path: str):
    for year, report in report.annual_reports.items():
        data = []
        for pos in report.positions:
            costs = pos.quantity * pos.buy_price * pos.buy_rate
            revenue = pos.quantity * pos.sell_price * pos.sell_rate
            profit = revenue - costs
            data.append([pos.symbol, pos.quantity, pos.currency, pos.open_date.date(), pos.buy_price, pos.buy_rate, pos.close_date.date(), pos.sell_price, pos.sell_rate, nm(costs), nm(revenue), nm(profit)])

        data.insert(0, 
            ["Ticker", "Amount", "Currency", "Buy date", "Buy price", "Buy npb ex. rate", "Sell date", "Sell price", "Sell nbp ex. rate", "Costs", "Revenue", "Profit"])
        
        with open(output_path + f"/{year}_positions.csv", "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)
