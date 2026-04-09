import csv
from datetime import datetime as Datetime, date as Date, timedelta
from decimal import Decimal


class NbpRatesProvider:
    def __init__(self, base_currency: str, csv_path: str):
        if base_currency != "PLN":
            raise ValueError("NBP rates provider only supports PLN as base currency")

        self.base_currency = base_currency
        self.csv_path = csv_path
        self.rates: dict[str, dict[int, dict[Date, Decimal]]] = {}

    def get_rate(self, currency: str, date: Datetime) -> Decimal:
        rate = None
        date = date.date()
        while rate is None:
            rate = self._get_rate_for_date(currency, date)
            if rate is None: # must by holiday, try previous day
                date = date - timedelta(days=1)
        return rate
    
    def get_prev_day_rate(self, currency: str, date: Datetime) -> Decimal:
        return self.get_rate(currency, date - timedelta(days=1))

    def _get_rate_for_date(self, currency: str, date: Date) -> Decimal:
        if currency not in self.rates or date.year not in self.rates[currency]:
            self._load_rates_for_year(currency, date.year)

        return self.rates[currency][date.year].get(date, None)
    
    def _load_rates_for_year(self, currency: str, year: int):
        if currency not in self.rates:
            self.rates[currency] = {}

        def _parse_rate(rate_str: str) -> Decimal:
            return Decimal(rate_str.replace(",", "."))

        self.rates[currency][year] = {}

        column_name = f"1{currency}" # TODO: it may be 100{currency} for some currencies, but those are rare

        with open(f"{self.csv_path}/{year}.csv", mode="r", newline='', encoding="ascii", errors="replace") as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                # data is not empty and contains only digits (some rows may contain "data" value like "20200101A", which is invalid)
                if not row['data'] or not row['data'].isdigit():
                    continue
                date = Datetime.strptime(row['data'], "%Y%m%d").date()
                rate = _parse_rate(row[column_name])
                self.rates[currency][year][date] = rate

    
    

                
