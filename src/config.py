from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

MANAGER_SECRET = os.environ.get("MANAGER_SECRET")

RADIS_HOST = os.environ.get("RADIS_HOST")
RADIS_PORT = os.environ.get("RADIS_PORT")

# Available Banks:
NATIONAL_BANK = "national_bank"
MONO_BANK = "mono_bank"
PRIVAT_BANK = "privat_bank"

# API URLs for currency data requests:
PRIVATBANK_API_URL = "https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11"
MONOBANK_API_URL = "https://api.monobank.ua/bank/currency"
NBU_API_URL = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"

# Output currency definitions:
CURRENCY_CODE = 'currency_code'
BASE_CURRENCY_CODE = 'base_currency_code'
BUY_RATE = 'buy_rate'
CROSS_RATE = 'cross_rate'
SELL_RATE = 'sale_rate'
ON_TIME = 'on_time'
