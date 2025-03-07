import requests
from datetime import date
from .base_adapter import CurrencyExchangeAdapter
from .base_adapter import TimeSeriesAdapter
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("CURRENCY_BEACON_BASE_URL")
API_KEY = os.getenv("CURRENCY_BEACON_API_KEY")


class CurrencyBeaconAdapter(CurrencyExchangeAdapter):


    def get_exchange_rate(self, source_currency: str, exchanged_currencies: str, valuation_date: date):

        symbols = ",".join(exchanged_currencies)

        response = requests.get(
            f"{BASE_URL}historical?api_key={API_KEY}&date={valuation_date}&base={source_currency}&symbols={symbols}"
            )        
        
        if response.status_code == 200:
            data = response.json()
            print('data:',data)
            return data.get("rates", {})  # Extract only the rates dictionary
        else:
            print(f"Error fetching data: {response.status_code} - {response.text}")
            return {}

class CurrencyBeaconTimeSeriesAdapter(TimeSeriesAdapter):


    def get_time_series(self, source_currency: str, start_date: str, end_date: str):
        response = requests.get(
            f"{BASE_URL}timeseries?api_key={API_KEY}&start_date={start_date}&end_date={end_date}&base={source_currency}"
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("response", {})  # Extract time series rates
        else:
            print(f"Error fetching time series data: {response.status_code} - {response.text}")
            return {}