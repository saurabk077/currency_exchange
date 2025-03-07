from api.models import CurrencyExchangeRate, Currency
from api.adapters.adapter_factory import AdapterFactory
from providers.models import Provider
from django.utils.timezone import now
import logging

logger = logging.getLogger("currency_app")

def get_exchange_rate_from_db(source_currency, exchanged_currency, valuation_date):
    """
    Fetch exchange rate from the local database.
    """
    logger.info(f"Fetching Exchange rate from DB for {source_currency} to {exchanged_currency} for date {valuation_date}")

    source_currency = Currency.objects.get(code=source_currency)
    exchanged_currency = Currency.objects.get(code=exchanged_currency)
    
    rate_data = CurrencyExchangeRate.objects.filter(
        source_currency=source_currency,
        exchanged_currency=exchanged_currency,
        valuation_date=valuation_date
    ).first()

    if rate_data:
        logger.info(f"Exchange Rate: {rate_data.rate_value}")
        return rate_data
    else:
        logger.warning(f"No exchange rate found in DB for {source_currency} to {exchanged_currency} on {valuation_date}")
        return None  # Explicitly return None if no data is found



def fetch_exchange_rate_from_provider(source_currency: str, exchanged_currencies: list, valuation_date):
    """
    Fetch exchange rates from the highest-priority active provider for multiple exchanged currencies.
    """
    try:
        providers = Provider.objects.filter(active=True).order_by('priority')

        for provider in providers:
            adapter = AdapterFactory.get_adapter(provider.name)
            if adapter:
                rate_data = adapter.get_exchange_rate(source_currency, exchanged_currencies, valuation_date)
                logger.info(f"Exchange rates fetched from {provider.name}: {rate_data}")

                if rate_data:
                    # Store data in the DB for future use
                    store_exchange_rate(source_currency, exchanged_currencies, valuation_date, rate_data)
                    return rate_data  # Return the fetched exchange rates

        logger.warning(f"No exchange rates found from providers for {source_currency} to {exchanged_currencies} on {valuation_date}")
        return None  # No provider returned data

    except Exception as e:
        logger.error(f"Error fetching exchange rate from providers: {e}")
        return None  # Handle errors gracefully


def store_exchange_rate(source_currency_code: str, exchanged_currency_codes: list, valuation_date, rate_data):
    """
    Store exchange rates for multiple exchanged currencies in the database.
    If an exchanged currency is not found in the database, it logs a warning and skips it.
    """
    try:
        source_currency = Currency.objects.get(code=source_currency_code)

        for exchanged_currency_code in exchanged_currency_codes:
            if exchanged_currency_code not in rate_data:
                logger.warning(f"Skipping {exchanged_currency_code}: No rate data available.")
                continue  # Skip this currency if there's no rate data

            try:
                exchanged_currency = Currency.objects.get(code=exchanged_currency_code)
                
                # Store or update the exchange rate
                CurrencyExchangeRate.objects.update_or_create(
                    source_currency=source_currency,
                    exchanged_currency=exchanged_currency,
                    valuation_date=valuation_date,
                    defaults={'rate_value': rate_data[exchanged_currency_code]}
                )
                logger.info(f"Exchange rate stored in DB for {source_currency} to {exchanged_currency}")
            except Currency.DoesNotExist:
                logger.warning(f"Skipping {exchanged_currency_code}: Currency not found in DB.")

    except Currency.DoesNotExist as e:
        logger.error(f"Error storing exchange rate: {e}")


def get_exchange_rate(source_currency: str, exchanged_currency: str, valuation_date):
    """
    Get exchange rate from DB if available, else fetch from provider.
    """
    # 1. Check if the data exists in the database
    existing_rate = get_exchange_rate_from_db(source_currency, exchanged_currency, valuation_date)
    
    if existing_rate:
        return {
            "source_currency": source_currency,
            "exchanged_currency": exchanged_currency,
            "valuation_date": valuation_date,
            "rate_value": str(existing_rate.rate_value)
        }
    else:
        logger.info(f"Exchange rate not found in DB")


    # 2. Fetch from provider if not in DB
    if isinstance(exchanged_currency, str):
        exchanged_currency = [exchanged_currency]
    rate_data = fetch_exchange_rate_from_provider(source_currency, exchanged_currency, valuation_date)
    if rate_data:
        return {
            "source_currency": source_currency,
            "exchanged_currency": exchanged_currency,
            "valuation_date": valuation_date,
            "rate_value": str(rate_data[exchanged_currency[0]])
        }

    return None  # No data found anywhere
