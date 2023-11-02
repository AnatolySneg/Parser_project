from datetime import datetime
import iso4217parse
import httpx
from src.config import PRIVATBANK_API_URL, MONOBANK_API_URL, NBU_API_URL
from src.config import NATIONAL_BANK as nbu, PRIVAT_BANK as pb, MONO_BANK as mb


class BankTransformation:
    NATIONAL_BANK = nbu
    MONO_BANK = mb
    PRIVAT_BANK = pb

    All_BANKS = (NATIONAL_BANK, MONO_BANK, PRIVAT_BANK)

    PRIVAT_CURRENCY_DEFINITION = "ccy"
    MONO_CURRENCY_DEFINITION = "currencyCodeA"
    NATIONAL_BANK_CURRENCY_DEFINITION = "r030"

    BANKS_CURRENCY_DEFINITIONS = {
        NATIONAL_BANK: NATIONAL_BANK_CURRENCY_DEFINITION,
        MONO_BANK: MONO_CURRENCY_DEFINITION,
        PRIVAT_BANK: PRIVAT_CURRENCY_DEFINITION,
    }

    PRIVAT_BASE_CURRENCY_DEFINITION = "base_ccy"
    MONO_BASE_CURRENCY_DEFINITION = "currencyCodeB"

    PRIVAT_BUY_DEFINITION = "buy"
    MONO_BUY_DEFINITION = "rateBuy"

    PRIVAT_SELL_DEFINITION = "sale"
    MONO_SELL_DEFINITION = "rateSell"

    MONO_CROSS_DEFINITION = 'rateCross'

    NATIONAL_BANK_RATE_DEFINITION = "rate"

    CURRENCY_CODE = 'currency_code'
    BASE_CURRENCY_CODE = 'base_currency_code'
    BUY_RATE = 'buy_rate'
    CROSS_RATE = 'cross_rate'
    SELL_RATE = 'sale_rate'
    ON_TIME = 'on_time'

    BANK_DEFINITIONS = {
        PRIVAT_BANK: {
            CURRENCY_CODE: PRIVAT_CURRENCY_DEFINITION,
            BASE_CURRENCY_CODE: PRIVAT_BASE_CURRENCY_DEFINITION,
            BUY_RATE: PRIVAT_BUY_DEFINITION,
            SELL_RATE: PRIVAT_SELL_DEFINITION,
        },
        MONO_BANK: {
            CURRENCY_CODE: MONO_CURRENCY_DEFINITION,
            BASE_CURRENCY_CODE: MONO_BASE_CURRENCY_DEFINITION,
            BUY_RATE: MONO_BUY_DEFINITION,
            CROSS_RATE: MONO_CROSS_DEFINITION,
            SELL_RATE: MONO_SELL_DEFINITION,
        },
        NATIONAL_BANK: {
            CURRENCY_CODE: NATIONAL_BANK_CURRENCY_DEFINITION,
            BASE_CURRENCY_CODE: NATIONAL_BANK_CURRENCY_DEFINITION,
            BUY_RATE: NATIONAL_BANK_RATE_DEFINITION,
            SELL_RATE: NATIONAL_BANK_RATE_DEFINITION,
        }
    }

    ALL_BANKS_DEFINITIONS = {
        CURRENCY_CODE: {PRIVAT_CURRENCY_DEFINITION: PRIVAT_BANK, MONO_CURRENCY_DEFINITION: MONO_BANK,
                        NATIONAL_BANK_CURRENCY_DEFINITION: NATIONAL_BANK},
        BASE_CURRENCY_CODE: {PRIVAT_BASE_CURRENCY_DEFINITION: PRIVAT_BANK,
                             MONO_BASE_CURRENCY_DEFINITION: MONO_BANK, },
        BUY_RATE: {PRIVAT_BUY_DEFINITION: PRIVAT_BANK, MONO_BUY_DEFINITION: MONO_BANK, },
        CROSS_RATE: {MONO_CROSS_DEFINITION: MONO_BANK},
        SELL_RATE: {PRIVAT_SELL_DEFINITION: PRIVAT_BANK, MONO_SELL_DEFINITION: MONO_BANK, },
        ON_TIME: {NATIONAL_BANK_RATE_DEFINITION: NATIONAL_BANK},
    }

    GET_CURRENCY_NAME = {
        NATIONAL_BANK: iso4217parse.by_code_num,
        PRIVAT_BANK: iso4217parse.by_alpha3,
        MONO_BANK: iso4217parse.by_code_num,
    }

    def _get_bank_definitions(self, bank: str) -> dict:  # takes a bank name from method below
        bank_definitions = self.BANK_DEFINITIONS[bank]  # returns dict with bank definitions to method below
        return bank_definitions

    def _get_transformed_data(self):
        valid_all_banks_data = {}
        for current_bank in self.bank_data:
            bank_definitions = self._get_bank_definitions(current_bank)
            current_bank_data = {current_bank: {}}
            valid_all_banks_data.update(current_bank_data)
            for currency_data in self.bank_data[current_bank]:
                currency = self.GET_CURRENCY_NAME[current_bank](currency_data[bank_definitions[self.CURRENCY_CODE]])
                base_currency = self.GET_CURRENCY_NAME[current_bank](
                    currency_data[bank_definitions[self.BASE_CURRENCY_CODE]])
                if currency == base_currency and current_bank != self.MONO_BANK:
                    base_currency = iso4217parse.by_alpha3("UAH")

                currency_alpha_code = currency.alpha3
                base_currency_alpha_code = base_currency.alpha3
                buy_rate = currency_data.get(bank_definitions[self.BUY_RATE])
                try:
                    cross_rate = currency_data.get(bank_definitions[self.CROSS_RATE])
                except KeyError:
                    cross_rate = 0.00
                sell_rate = currency_data.get(bank_definitions[self.SELL_RATE])
                on_time = str(datetime.today().strftime("%d.%m.%Y %H:%M"))
                valid_currency_data = {currency_alpha_code:
                    {
                        self.CURRENCY_CODE: currency_alpha_code,
                        self.BASE_CURRENCY_CODE: base_currency_alpha_code,
                        self.BUY_RATE: float(buy_rate),
                        self.CROSS_RATE: float(cross_rate),
                        self.SELL_RATE: float(sell_rate),
                        self.ON_TIME: on_time,
                    }
                }
                valid_all_banks_data[current_bank].update(valid_currency_data)
        return valid_all_banks_data

    def __init__(self, bank_data):
        self.bank_data = bank_data
        self.valid_result_data = self._get_transformed_data()


class CurrencyTransformation(BankTransformation):

    def _source_identify(self):
        defined_data = {}
        for data in self.data_list:
            if type(data) is dict:
                valid_data = data["currency"]
            else:
                valid_data = data
            for definition in self.ALL_BANKS_DEFINITIONS[self.CURRENCY_CODE]:
                if definition in valid_data[0]:
                    bank_name = self.ALL_BANKS_DEFINITIONS[self.CURRENCY_CODE][definition]
                    defined_data[bank_name] = valid_data
                    break
        return defined_data

    def _requested_banks(self) -> list:
        source_to_get_currency = [bank for bank in self.source_check if self.source_check[bank]]
        return source_to_get_currency

    def _source_to_parce(self):
        source_to_get_currency: list = self._requested_banks()

    def __init__(self, data_source):
        # self.source_check: dict = banks.get_banks_currency_data()
        # self.banks_to_parse = self._requested_banks()

        # self.banks = banks
        #
        # self.data_list: list = args
        self.data_source = data_source
        self.currency = BankTransformation(self.data_source).valid_result_data


if __name__ == "__main__":
    privat_data = [{"ccy": "EUR", "base_ccy": "UAH", "buy": "39.90000", "sale": "40.90000"},
                   {"ccy": "USD", "base_ccy": "UAH", "buy": "37.15000", "sale": "37.75000"}]

    mono_data = {
        "currency": [
            {
                "currencyCodeA": 840,
                "currencyCodeB": 980,
                "date": 1695934873,
                "rateBuy": 36.65,
                "rateCross": 0,
                "rateSell": 37.4406
            },
            {
                "currencyCodeA": 978,
                "currencyCodeB": 980,
                "date": 1695995773,
                "rateBuy": 38.8,
                "rateCross": 0,
                "rateSell": 40.0994
            },
            {
                "currencyCodeA": 978,
                "currencyCodeB": 840,
                "date": 1695995773,
                "rateBuy": 1.048,
                "rateCross": 0,
                "rateSell": 1.063
            }
        ]
    }

    nbu_data = {
        "currency": [
            {
                "r030": 840,
                "txt": "Долар США",
                "rate": 36.5686,
                "cc": "USD",
                "exchangedate": "02.10.2023"
            },
            {
                "r030": 978,
                "txt": "Євро",
                "rate": 38.7408,
                "cc": "EUR",
                "exchangedate": "02.10.2023"
            }
        ]
    }

    instance = CurrencyTransformation(banks='test banks', args=[privat_data, mono_data, nbu_data])

    # print(instance.data_source)
