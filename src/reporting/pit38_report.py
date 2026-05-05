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
    positions_revenue: dict[str, Decimal]
    positions_expenses: dict[str, Decimal]
    dividends: Decimal
    interest_on_cash: Decimal
    lending_interest: Decimal
    exchange_fees: Decimal
    dividend_taxes: Decimal
    transaction_taxes: dict[str, Decimal]

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


def get_country_code(ticker: str):
    country_codes = {
        "AMZN": "US",
        "CSPX": "GB",
        "VJPN": "DE",
        "EGLN": "GB",
        "VEUR": "GB",
        "VNRT": "DE",
        "VDPA": "GB",
        "VAPX": "GB",
        "VWRP": "GB",
        "VHVG": "GB",
        "VAGU": "GB",
        "VFEG": "GB",
        "QDVE": "DE",
        "RHM": "DE",
        "RR": "GB",
        "HO": "FR",
        "HAG": "DE",
        "CSX5": "GB",
        "SAF": "FR",
        "ICSU": "GB",
        "FINMY": "US",
        "QQ": "GB",
        "SGLN": "GB",
        "SXR8": "DE",
        "RRU": "DE",
        "AIR": "FR",
        "SDV1": "DE",
        "BA" : "GB",
        "BAB": "GB",
        "AM": "FR",
        "IGLN": "GB",
        "IBGS": "NL",
        "UNH": "US",
        "KOZ1": "DE",
        "WCBR": "IT",
        "MTX": "DE",
        "SSLN": "GB",
        "COFF": "GB",
        "WREE": "GB",
        "NCLP": "GB",
        "SBRT": "IT",
        "EVOK": "GB",
        "UBSFY": "US",
        "META": "US",
        "2B7D": "DE",
        "ABEC": "DE",
        "SNV3": "GB",
        "BSP": "DE",
        "BRNT": "IT",
        "NFLX": "US",
        "CSP1": "GB",
    }

    if not ticker in country_codes:
        raise ValueError(f"Unknown ticker: {ticker}")

    return country_codes[ticker]


class Pit38ReportBuilder:
    def __init__(self, nbp_fx_provider: NbpRatesProvider):
        self.nbp_fx_provider = nbp_fx_provider
        self.annual_reports = {}

    def handle_position(self, position: Position):
        if position.closed:
            annual = self._get_annual_report(position.close_date.year)
            country = get_country_code(position.symbol)
            buy_rate = self.nbp_fx_provider.get_prev_day_rate(position.currency, position.open_date)
            annual.positions_expenses[country] = annual.positions_expenses.get(country, Decimal("0")) + position.quantity * position.buy_price * buy_rate
            sell_rate = self.nbp_fx_provider.get_prev_day_rate(position.currency, position.close_date)
            annual.positions_revenue[country] = annual.positions_revenue.get(country, Decimal("0")) + position.quantity * position.sell_price * sell_rate
            annual.transaction_taxes[country] = annual.transaction_taxes.get(country, Decimal("0")) + sum(tax.amount for tax in position.taxes)
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
            case IncostType.DEPOSIT_FEE:
                pass # deposit fees are not tax deductible in Poland
            case IncostType.DIVIDEND:
                annual.dividends += incost.amount
            case IncostType.INTEREST_CASH:
                annual.interest_on_cash += incost.amount
            case IncostType.INTEREST_LENDING:
                annual.lending_interest += incost.amount
            case IncostType.CONVERSION_FEE:
                annual.exchange_fees += incost.amount
            case IncostType.DIVIDEND_TAX:
                annual.dividend_taxes += incost.amount
            case IncostType.TRANSACTION_TAX:
                pass # transaction taxes are accounted for in position expenses
            

    def _get_annual_report(self, year: int) -> AnnualPitReport:
        if year not in self.annual_reports:
            self.annual_reports[year] = AnnualPitReport(
                positions_revenue={},
                positions_expenses={},
                dividends=Decimal("0"),
                interest_on_cash=Decimal("0"),
                lending_interest=Decimal("0"),
                exchange_fees=Decimal("0"),
                dividend_taxes=Decimal("0"),
                transaction_taxes={},
                positions=[],
            )
        return self.annual_reports[year]
    

def print_annual_reports(report: Pit38ReportBuilder, output_path: str):
    for year, report in report.annual_reports.items():
        with open(output_path + f"/{year}.txt", "w") as file:
            file.write(f"=== Rok {year} ===\n\n")

            revenue = sum(report.positions_revenue.values())
            expenses = sum(report.positions_expenses.values())
            taxes = sum(report.transaction_taxes.values()) + report.dividend_taxes
            file.write(f"=== Przychody ===\n\n")
            file.write(f"{'Zamknięcie pozycji:':<22} {revenue:>12.2f} PLN\n")
            file.write(f"{'Dywidendy:':<22} {report.dividends:>12.2f} PLN\n")
            file.write(f"{'Odsetki od gotówki:':<22} {report.interest_on_cash:>12.2f} PLN\n")
            file.write(f"{'Odsetki od pożyczek:':<22} {report.lending_interest:>12.2f} PLN\n")
            file.write(f"-" * 40 + "\n")
            file.write(f"{'Suma przychodów:':<22} {revenue + report.dividends + report.interest_on_cash + report.lending_interest:>12.2f} PLN\n")

            file.write(f"\n=== Koszty ===\n\n")
            file.write(f"{'Otwarcie pozycji:':<22} {expenses:>12.2f} PLN\n")
            file.write(f"{'Prowizje walutowe:':<22} {report.exchange_fees:>12.2f} PLN\n")
            file.write(f"-" * 40 + "\n")
            file.write(f"{'Suma kosztów:':<22} {expenses + report.exchange_fees:>12.2f} PLN\n")

            file.write(f"\n=== Dochód ===\n\n")
            for country, rev in report.positions_revenue.items():
                exp = report.positions_expenses.get(country, Decimal("0"))
                profit = rev - exp
                file.write(f"{country + ':':<22} {profit:>12.2f} PLN\n")
            file.write("-" * 40 + "\n")
            file.write(f"{'Suma dochodu:':<22} {revenue - expenses:>12.2f} PLN\n")
            
            file.write(f"\n=== Podatki zapłacone za granicą ===\n\n")
            for country, tax in report.transaction_taxes.items():
                if tax > Decimal("0"):
                    file.write(f"{country + ':':<22} {tax:>12.2f} PLN\n")
            file.write(f"{'Podatek od dywidend:':<22} {report.dividend_taxes:>12.2f} PLN\n")
            file.write("-" * 40 + "\n")
            file.write(f"{'Suma podatków:':<22} {taxes:>12.2f} PLN\n")

            pit_tax = (Decimal(0.19) * (revenue - expenses)).quantize(Decimal("0.01"))
            file.write(f"\n=== Podsumowanie ===\n\n")
            file.write(f"{'Dochód przed opodatkowaniem:':<30} {revenue - expenses:>12.2f} PLN\n")
            file.write(f"{'Podatek należny (19%):':<30} {pit_tax:>12.2f} PLN\n")
            file.write(f"{'Podatek zapłacony za granicą:':<30} {taxes:>12.2f} PLN\n")
            file.write(f"{'Podatek do zapłaty:':<30} {max(Decimal(0), pit_tax - taxes):>12.2f} PLN\n")


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
