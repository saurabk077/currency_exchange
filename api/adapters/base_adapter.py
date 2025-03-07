from abc import ABC, abstractmethod
from datetime import date
from typing import Dict

class CurrencyExchangeAdapter(ABC):
    @abstractmethod
    def get_exchange_rate(self, source_currency: str, exchanged_currency: str, valuation_date: date) -> Dict:
        pass


class TimeSeriesAdapter(ABC):
    """
    Abstract class for exchange rate adapters.
    """

    @abstractmethod
    def get_time_series(self, source_currency, start_date, end_date):
        """
        Fetch exchange rate time series from provider.
        """
        pass