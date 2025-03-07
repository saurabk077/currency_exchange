import requests
from datetime import date
from .base_adapter import CurrencyExchangeAdapter, TimeSeriesAdapter
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("OTHER_PROVIDER_BASE_URL")
API_KEY = os.getenv("OTHER_PROVIDER_API_KEY")

class OtherProviderAdapter(CurrencyExchangeAdapter):

    def get_exchange_rate(self, source_currency: str, exchanged_currency: str, valuation_date: date):
        response = requests.get(f"{self.BASE_URL}?api_key={self.API_KEY}&date={valuation_date}&base_currency={source_currency}")
        if response.status_code == 200:
            data = response.json()
            return {"rate": data["exchange_rates"].get(exchanged_currency)}
        return {"rate": None}



class OtherProviderTimeSeriesAdapter(TimeSeriesAdapter):


    def get_time_series(self, source_currency: str, start_date: str, end_date: str):
        response = requests.get(
            f"{self.BASE_URL}timeseries?api_key={self.API_KEY}&start_date={start_date}&end_date={end_date}&base={source_currency}"
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("rates", {})  # Extract time series rates
        else:
            print(f"Error fetching time series data: {response.status_code} - {response.text}")
            return {}