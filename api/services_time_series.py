from api.models import CurrencyExchangeRate, Currency
from api.adapters.adapter_factory import TimeSeriesAdapterFactory
from providers.models import Provider
from django.utils.timezone import now
import logging
from datetime import datetime

logger = logging.getLogger("currency_app")

def fetch_time_series_data(source_currency: str, start_date: str, end_date: str) -> dict:
    """
    Fetches time series exchange rates from DB or provider and filters them based on available currencies.
    """
    existing_rates = get_time_series_from_db(source_currency, start_date, end_date)
    if existing_rates:
        return existing_rates
    
    logger.info(f"Time series not found in DB, fetching from provider...")
    rate_data = fetch_time_series_from_provider(source_currency, start_date, end_date)
    filtered_rate_data = filter_rate_data(source_currency, rate_data) if rate_data else {}
    if filtered_rate_data:
        store_time_series(source_currency, start_date, end_date, filtered_rate_data)

    return {
        "source_currency": source_currency,
        "start_date": start_date,
        "end_date": end_date,
        "rates": filtered_rate_data,
    }

def get_time_series_from_db(source_currency, start_date, end_date):
    logger.info(f"Fetching time series from DB for {source_currency} from {start_date} to {end_date}")
    source_currency_obj = Currency.objects.get(code=source_currency)
    rates = CurrencyExchangeRate.objects.filter(
        source_currency=source_currency_obj,
        valuation_date__range=[start_date, end_date]
    ).values("valuation_date", "exchanged_currency__code", "rate_value")
    
    time_series_data = {}
    for rate in rates:
        date_str = rate["valuation_date"].strftime("%Y-%m-%d")
        time_series_data.setdefault(date_str, {})[rate["exchanged_currency__code"]] = str(rate["rate_value"])
    if time_series_data:
        logger.info(f"Time Series data from DB: {time_series_data}")
        time_series_data = {
        "source_currency": source_currency,
        "start_date": start_date,
        "end_date": end_date,
        "rates": time_series_data,
        }
        return time_series_data
    
    else:
        return None

def fetch_time_series_from_provider(source_currency: str, start_date: str, end_date: str):
    try:
        for provider in Provider.objects.filter(active=True).order_by("priority"):
            adapter = TimeSeriesAdapterFactory.get_time_series_adapter(provider.name)
            if adapter:
                rate_data = adapter.get_time_series(source_currency, start_date, end_date)
                if rate_data:

                    return rate_data
    except Exception as e:
        logger.error(f"Error fetching from providers: {e}")
    return None

def filter_rate_data(source_currency: str, rate_data: dict) -> dict:
    db_currencies = set(Currency.objects.values_list("code", flat=True))
    if source_currency not in db_currencies:
        logger.warning(f"Skipping all data: source currency {source_currency} not in DB.")
        return {}

    filtered_rate_data = {
        date: {cur: rate for cur, rate in currencies.items() if cur in db_currencies}
        for date, currencies in rate_data.items()
        if any(cur in db_currencies for cur in currencies)
    }
    logger.info(f"Time Series data post filtering {filtered_rate_data}")
    
    return filtered_rate_data

def store_time_series(source_currency: str, start_date: str, end_date: str, filtered_data: dict):
    try:
        source_currency_obj = Currency.objects.get(code=source_currency)
        for date_str, currencies in filtered_data.items():
            valuation_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            for exchanged_currency_code, rate_value in currencies.items():
                exchanged_currency_obj = Currency.objects.get(code=exchanged_currency_code)
                CurrencyExchangeRate.objects.update_or_create(
                    source_currency=source_currency_obj,
                    exchanged_currency=exchanged_currency_obj,
                    valuation_date=valuation_date,
                    defaults={'rate_value': rate_value}
                )
                logger.info(f"Stored in DB {source_currency} -> {exchanged_currency_code} on {date_str}")
    except Currency.DoesNotExist as e:
        logger.error(f"Error storing time series: {e}")

