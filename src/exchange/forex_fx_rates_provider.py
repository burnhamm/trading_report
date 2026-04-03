from datetime import datetime as Datetime
from decimal import Decimal
from forex_python.converter import CurrencyRates


class ForexRatesProvider:
    def __init__(self, base_currency: str):
        self.base_currency = base_currency
        self.rates = CurrencyRates()

    def get_rate(self, currency: str, date: Datetime) -> Decimal:
        return self.rates.get_rate(currency, self.base_currency, date.date())