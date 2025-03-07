from .currencybeacon import CurrencyBeaconAdapter, CurrencyBeaconTimeSeriesAdapter
from .other_provider import OtherProviderAdapter, OtherProviderTimeSeriesAdapter

class AdapterFactory:
    @staticmethod
    def get_adapter(provider: str):
        if provider == "CurrencyBeacon":
            return CurrencyBeaconAdapter()
        elif provider == "OtherProvider":
            return OtherProviderAdapter()
        else:
            raise ValueError("Unknown provider")

class TimeSeriesAdapterFactory:
    @staticmethod
    def get_time_series_adapter(provider: str):
        if provider == "CurrencyBeacon":
            return CurrencyBeaconTimeSeriesAdapter()
        elif provider == "OtherProvider":
            return OtherProviderTimeSeriesAdapter()
        else:
            raise ValueError("Unknown provider")
