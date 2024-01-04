from datetime import datetime
import iso4217parse
from src.config import NATIONAL_BANK as nbu, PRIVAT_BANK as pb, MONO_BANK as mb
from src.config import CURRENCY_CODE as cc, BASE_CURRENCY_CODE as bcc
from src.config import BUY_RATE as br, CROSS_RATE as cr, SELL_RATE as sr, ON_TIME as on_time


class CurrencyTransformation:
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

    CURRENCY_CODE = cc
    BASE_CURRENCY_CODE = bcc
    BUY_RATE = br
    CROSS_RATE = cr
    SELL_RATE = sr
    ON_TIME = on_time

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
        for current_bank in self.data_source:
            bank_definitions = self._get_bank_definitions(current_bank)
            current_bank_data = {current_bank: {}}
            valid_all_banks_data.update(current_bank_data)
            for currency_data in self.data_source[current_bank]:
                currency = self.GET_CURRENCY_NAME[current_bank](currency_data[bank_definitions[self.CURRENCY_CODE]])
                base_currency = self.GET_CURRENCY_NAME[current_bank](
                    currency_data[bank_definitions[self.BASE_CURRENCY_CODE]])
                if currency == base_currency and current_bank != self.MONO_BANK:
                    base_currency = iso4217parse.by_alpha3("UAH")

                currency_alpha_code = currency.alpha3
                base_currency_alpha_code = base_currency.alpha3
                if base_currency_alpha_code != 'UAH' and currency_alpha_code != 'UAH':
                    continue
                if currency_alpha_code not in self.currency_list:
                    continue

                try:
                    buy_rate = currency_data[bank_definitions[self.BUY_RATE]]
                except KeyError:
                    buy_rate = 0.00
                try:
                    cross_rate = currency_data[bank_definitions[self.CROSS_RATE]]
                except KeyError:
                    cross_rate = 0.00
                try:
                    sell_rate = currency_data[bank_definitions[self.SELL_RATE]]
                except KeyError:
                    sell_rate = 0.00
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

    def _get_ordered_currency_data(self):
        ordered_data = {}
        for bank in self.unsorted_currency:
            currency_data = self.unsorted_currency.get(bank)
            alpha = {}
            try:
                usd_value = currency_data.pop('USD')
                alpha['USD'] = usd_value
            except KeyError:
                pass
            try:
                eur_value = currency_data.pop('EUR')
                alpha['EUR'] = eur_value
            except KeyError:
                pass
            alpha.update(dict(sorted(currency_data.items())))
            ordered_data.update({bank: alpha})
        return ordered_data

    def _get_requested_list(self, requested_currency):
        return [cur for cur in requested_currency if requested_currency[cur]]

    def __init__(self, data_source, requested_currency: dict[str, bool]):
        self.currency_list = self._get_requested_list(requested_currency)
        self.data_source = data_source
        self.unsorted_currency = self._get_transformed_data()
        self.currency = self._get_ordered_currency_data()
