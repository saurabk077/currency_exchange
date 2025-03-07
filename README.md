# Currency Exchange API

This is a Django-based API for currency exchange rate calculations.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/saurabk077/currency_exchange.git
   cd currency_exchange
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\\Scripts\\activate
   pip install -r requirements.txt
   ```

3. Run database migrations:
   ```bash
   python manage.py migrate
   ```

4. Start the server:
   ```bash
   python manage.py runserver
   ```

## API Endpoints
- `GET /api/time_series_exchange_rate/` – Fetch historical exchange rates.
- `GET /api/convert_amount/` – Convert currency amounts.
- `GET /api/currencies/` - Currency CURD operation
