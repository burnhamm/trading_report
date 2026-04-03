from datetime import datetime as Datetime
from decimal import Decimal


class BrokerFxRatesProvider:
    def __init__(self, rates: dict[str, dict[Datetime, Decimal]], base_currency: str, backup_provider=None):
        self.rates = rates
        self.base_currency = base_currency
        self.backup_provider = backup_provider

    def get_rate(self, currency: str, date: Datetime) -> Decimal:
        if currency == self.base_currency:
            return Decimal("1")

        if currency not in self.rates or date not in self.rates[currency]:
            # try finding rate from the same date, but different time
            if currency in self.rates:
                for dt, rate in self.rates[currency].items():
                    if dt.date() == date.date():
                        return rate
            # try backup provider
            if self.backup_provider:
                return self.backup_provider.get_rate(currency, date)

            raise ValueError(f"Missing exchange rate for {currency} on {date}")
        
        return self.rates[currency][date]