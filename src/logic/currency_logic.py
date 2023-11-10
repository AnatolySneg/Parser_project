from datetime import datetime
import iso4217parse
import httpx
from src.config import PRIVATBANK_API_URL, MONOBANK_API_URL, NBU_API_URL
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

    def _get_requested_list(self):
        return [cur for cur in self.requested_currency if self.requested_currency[cur]]

    def __init__(self, data_source, requested_currency: dict[str, bool]):
        self.requested_currency = requested_currency
        self.currency_list = self._get_requested_list()
        self.data_source = data_source
        self.unsorted_currency = self._get_transformed_data()
        self.currency = self._get_ordered_currency_data()


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

    # print(instance.data_source)

    income_data = {
        'national_bank': [
            {'r030': 36, 'txt': 'Австралійський долар', 'rate': 23.1561, 'cc': 'AUD', 'exchangedate': '09.11.2023'},
            {'r030': 124, 'txt': 'Канадський долар', 'rate': 26.142, 'cc': 'CAD', 'exchangedate': '09.11.2023'},
            {'r030': 156, 'txt': 'Юань Женьміньбі', 'rate': 4.9496, 'cc': 'CNY', 'exchangedate': '09.11.2023'},
            {'r030': 203, 'txt': 'Чеська крона', 'rate': 1.5584, 'cc': 'CZK', 'exchangedate': '09.11.2023'},
            {'r030': 208, 'txt': 'Данська крона', 'rate': 5.1559, 'cc': 'DKK', 'exchangedate': '09.11.2023'},
            {'r030': 344, 'txt': 'Гонконгівський долар', 'rate': 4.6109, 'cc': 'HKD', 'exchangedate': '09.11.2023'},
            {'r030': 348, 'txt': 'Форинт', 'rate': 0.101355, 'cc': 'HUF', 'exchangedate': '09.11.2023'},
            {'r030': 356, 'txt': 'Індійська рупія', 'rate': 0.43277, 'cc': 'INR', 'exchangedate': '09.11.2023'},
            {'r030': 360, 'txt': 'Рупія', 'rate': 0.0023029, 'cc': 'IDR', 'exchangedate': '09.11.2023'},
            {'r030': 376, 'txt': 'Новий ізраїльський шекель', 'rate': 9.3571, 'cc': 'ILS',
             'exchangedate': '09.11.2023'},
            {'r030': 392, 'txt': 'Єна', 'rate': 0.23885, 'cc': 'JPY', 'exchangedate': '09.11.2023'},
            {'r030': 398, 'txt': 'Теньге', 'rate': 0.076999, 'cc': 'KZT', 'exchangedate': '09.11.2023'},
            {'r030': 410, 'txt': 'Вона', 'rate': 0.02751, 'cc': 'KRW', 'exchangedate': '09.11.2023'},
            {'r030': 484, 'txt': 'Мексиканське песо', 'rate': 2.0552, 'cc': 'MXN', 'exchangedate': '09.11.2023'},
            {'r030': 498, 'txt': 'Молдовський лей', 'rate': 2.0104, 'cc': 'MDL', 'exchangedate': '09.11.2023'},
            {'r030': 554, 'txt': 'Новозеландський долар', 'rate': 21.3433, 'cc': 'NZD', 'exchangedate': '09.11.2023'},
            {'r030': 578, 'txt': 'Норвезька крона', 'rate': 3.2182, 'cc': 'NOK', 'exchangedate': '09.11.2023'},
            {'r030': 643, 'txt': 'Російський рубль', 'rate': 0.39129, 'cc': 'RUB', 'exchangedate': '09.11.2023'},
            {'r030': 702, 'txt': 'Сінгапурський долар', 'rate': 26.5532, 'cc': 'SGD', 'exchangedate': '09.11.2023'},
            {'r030': 710, 'txt': 'Ренд', 'rate': 1.9487, 'cc': 'ZAR', 'exchangedate': '09.11.2023'},
            {'r030': 752, 'txt': 'Шведська крона', 'rate': 3.2977, 'cc': 'SEK', 'exchangedate': '09.11.2023'},
            {'r030': 756, 'txt': 'Швейцарський франк', 'rate': 40.0474, 'cc': 'CHF', 'exchangedate': '09.11.2023'},
            {'r030': 818, 'txt': 'Єгипетський фунт', 'rate': 1.1666, 'cc': 'EGP', 'exchangedate': '09.11.2023'},
            {'r030': 826, 'txt': 'Фунт стерлінгів', 'rate': 44.1643, 'cc': 'GBP', 'exchangedate': '09.11.2023'},
            {'r030': 840, 'txt': 'Долар США', 'rate': 36.0407, 'cc': 'USD', 'exchangedate': '09.11.2023'},
            {'r030': 933, 'txt': 'Білоруський рубль', 'rate': 13.1, 'cc': 'BYN', 'exchangedate': '09.11.2023'},
            {'r030': 944, 'txt': 'Азербайджанський манат', 'rate': 21.2191, 'cc': 'AZN', 'exchangedate': '09.11.2023'},
            {'r030': 946, 'txt': 'Румунський лей', 'rate': 7.7422, 'cc': 'RON', 'exchangedate': '09.11.2023'},
            {'r030': 949, 'txt': 'Турецька ліра', 'rate': 1.264, 'cc': 'TRY', 'exchangedate': '09.11.2023'},
            {'r030': 960, 'txt': 'СПЗ (спеціальні права запозичення)', 'rate': 47.4349, 'cc': 'XDR',
             'exchangedate': '09.11.2023'},
            {'r030': 975, 'txt': 'Болгарський лев', 'rate': 19.6611, 'cc': 'BGN', 'exchangedate': '09.11.2023'},
            {'r030': 978, 'txt': 'Євро', 'rate': 38.4518, 'cc': 'EUR', 'exchangedate': '09.11.2023'},
            {'r030': 985, 'txt': 'Злотий', 'rate': 8.6108, 'cc': 'PLN', 'exchangedate': '09.11.2023'},
            {'r030': 12, 'txt': 'Алжирський динар', 'rate': 0.26719, 'cc': 'DZD', 'exchangedate': '09.11.2023'},
            {'r030': 50, 'txt': 'Така', 'rate': 0.32834, 'cc': 'BDT', 'exchangedate': '09.11.2023'},
            {'r030': 51, 'txt': 'Вірменський драм', 'rate': 0.090028, 'cc': 'AMD', 'exchangedate': '09.11.2023'},
            {'r030': 214, 'txt': 'Домініканське песо', 'rate': 0.64111, 'cc': 'DOP', 'exchangedate': '09.11.2023'},
            {'r030': 364, 'txt': 'Іранський ріал', 'rate': 0.00086384, 'cc': 'IRR', 'exchangedate': '09.11.2023'},
            {'r030': 368, 'txt': 'Іракський динар', 'rate': 0.027696, 'cc': 'IQD', 'exchangedate': '09.11.2023'},
            {'r030': 417, 'txt': 'Сом', 'rate': 0.4062, 'cc': 'KGS', 'exchangedate': '09.11.2023'},
            {'r030': 422, 'txt': 'Ліванський фунт', 'rate': 0.002419, 'cc': 'LBP', 'exchangedate': '09.11.2023'},
            {'r030': 434, 'txt': 'Лівійський динар', 'rate': 7.4199, 'cc': 'LYD', 'exchangedate': '09.11.2023'},
            {'r030': 458, 'txt': 'Малайзійський ринггіт', 'rate': 7.6168, 'cc': 'MYR', 'exchangedate': '09.11.2023'},
            {'r030': 504, 'txt': 'Марокканський дирхам', 'rate': 3.5295, 'cc': 'MAD', 'exchangedate': '09.11.2023'},
            {'r030': 586, 'txt': 'Пакистанська рупія', 'rate': 0.12908, 'cc': 'PKR', 'exchangedate': '09.11.2023'},
            {'r030': 682, 'txt': 'Саудівський ріял', 'rate': 9.6706, 'cc': 'SAR', 'exchangedate': '09.11.2023'},
            {'r030': 704, 'txt': 'Донг', 'rate': 0.0014768, 'cc': 'VND', 'exchangedate': '09.11.2023'},
            {'r030': 764, 'txt': 'Бат', 'rate': 1.00708, 'cc': 'THB', 'exchangedate': '09.11.2023'},
            {'r030': 784, 'txt': 'Дирхам ОАЕ', 'rate': 9.8778, 'cc': 'AED', 'exchangedate': '09.11.2023'},
            {'r030': 788, 'txt': 'Туніський динар', 'rate': 11.4448, 'cc': 'TND', 'exchangedate': '09.11.2023'},
            {'r030': 860, 'txt': 'Узбецький сум', 'rate': 0.0029655, 'cc': 'UZS', 'exchangedate': '09.11.2023'},
            {'r030': 901, 'txt': 'Новий тайванський долар', 'rate': 1.11972, 'cc': 'TWD', 'exchangedate': '09.11.2023'},
            {'r030': 934, 'txt': 'Туркменський новий манат', 'rate': 10.3661, 'cc': 'TMT',
             'exchangedate': '09.11.2023'},
            {'r030': 941, 'txt': 'Сербський динар', 'rate': 0.32881, 'cc': 'RSD', 'exchangedate': '09.11.2023'},
            {'r030': 972, 'txt': 'Сомоні', 'rate': 3.3125, 'cc': 'TJS', 'exchangedate': '09.11.2023'},
            {'r030': 981, 'txt': 'Ларі', 'rate': 13.4365, 'cc': 'GEL', 'exchangedate': '09.11.2023'},
            {'r030': 986, 'txt': 'Бразильський реал', 'rate': 7.2001, 'cc': 'BRL', 'exchangedate': '09.11.2023'},
            {'r030': 959, 'txt': 'Золото', 'rate': 70734.56, 'cc': 'XAU', 'exchangedate': '09.11.2023'},
            {'r030': 961, 'txt': 'Срібло', 'rate': 807.87, 'cc': 'XAG', 'exchangedate': '09.11.2023'},
            {'r030': 962, 'txt': 'Платина', 'rate': 31789.7, 'cc': 'XPT', 'exchangedate': '09.11.2023'},
            {'r030': 964, 'txt': 'Паладій', 'rate': 36842.25, 'cc': 'XPD', 'exchangedate': '09.11.2023'}],
        'privat_bank': [{'ccy': 'EUR', 'base_ccy': 'UAH', 'buy': '38.46000', 'sale': '40.48583'},
                        {'ccy': 'USD', 'base_ccy': 'UAH', 'buy': '36.01000', 'sale': '37.45318'}],
        'mono_bank': [
            {'currencyCodeA': 840, 'currencyCodeB': 980, 'date': 1699423806, 'rateBuy': 36.02, 'rateCross': 0,
             'rateSell': 37.2995},
            {'currencyCodeA': 978, 'currencyCodeB': 980, 'date': 1699423806, 'rateBuy': 38.48, 'rateCross': 0,
             'rateSell': 39.8804},
            {'currencyCodeA': 978, 'currencyCodeB': 840, 'date': 1699423806, 'rateBuy': 1.062, 'rateCross': 0,
             'rateSell': 1.074},
            {'currencyCodeA': 826, 'currencyCodeB': 980, 'date': 1699465316, 'rateBuy': 0, 'rateCross': 46.0707,
             'rateSell': 0},
            {'currencyCodeA': 392, 'currencyCodeB': 980, 'date': 1699465142, 'rateBuy': 0, 'rateCross': 0.2487,
             'rateSell': 0},
            {'currencyCodeA': 756, 'currencyCodeB': 980, 'date': 1699465310, 'rateBuy': 0, 'rateCross': 41.589,
             'rateSell': 0},
            {'currencyCodeA': 156, 'currencyCodeB': 980, 'date': 1699465303, 'rateBuy': 0, 'rateCross': 5.1239,
             'rateSell': 0},
            {'currencyCodeA': 784, 'currencyCodeB': 980, 'date': 1699465309, 'rateBuy': 0, 'rateCross': 10.164,
             'rateSell': 0},
            {'currencyCodeA': 971, 'currencyCodeB': 980, 'date': 1663425223, 'rateBuy': 0, 'rateCross': 0.4252,
             'rateSell': 0},
            {'currencyCodeA': 8, 'currencyCodeB': 980, 'date': 1699464838, 'rateBuy': 0, 'rateCross': 0.3809,
             'rateSell': 0},
            {'currencyCodeA': 51, 'currencyCodeB': 980, 'date': 1699465255, 'rateBuy': 0, 'rateCross': 0.093,
             'rateSell': 0},
            {'currencyCodeA': 973, 'currencyCodeB': 980, 'date': 1699461719, 'rateBuy': 0, 'rateCross': 0.0451,
             'rateSell': 0},
            {'currencyCodeA': 32, 'currencyCodeB': 980, 'date': 1699465285, 'rateBuy': 0, 'rateCross': 0.0462,
             'rateSell': 0},
            {'currencyCodeA': 36, 'currencyCodeB': 980, 'date': 1699464217, 'rateBuy': 0, 'rateCross': 24.2798,
             'rateSell': 0},
            {'currencyCodeA': 944, 'currencyCodeB': 980, 'date': 1699464953, 'rateBuy': 0, 'rateCross': 22.0022,
             'rateSell': 0},
            {'currencyCodeA': 50, 'currencyCodeB': 980, 'date': 1699464598, 'rateBuy': 0, 'rateCross': 0.339,
             'rateSell': 0},
            {'currencyCodeA': 975, 'currencyCodeB': 980, 'date': 1699465304, 'rateBuy': 0, 'rateCross': 20.4444,
             'rateSell': 0},
            {'currencyCodeA': 48, 'currencyCodeB': 980, 'date': 1699460556, 'rateBuy': 0, 'rateCross': 98.9249,
             'rateSell': 0},
            {'currencyCodeA': 108, 'currencyCodeB': 980, 'date': 1538606522, 'rateBuy': 0, 'rateCross': 0.0158,
             'rateSell': 0},
            {'currencyCodeA': 96, 'currencyCodeB': 980, 'date': 1699099931, 'rateBuy': 0, 'rateCross': 27.5553,
             'rateSell': 0},
            {'currencyCodeA': 68, 'currencyCodeB': 980, 'date': 1699409702, 'rateBuy': 0, 'rateCross': 5.4371,
             'rateSell': 0},
            {'currencyCodeA': 986, 'currencyCodeB': 980, 'date': 1699464981, 'rateBuy': 0, 'rateCross': 7.6826,
             'rateSell': 0},
            {'currencyCodeA': 72, 'currencyCodeB': 980, 'date': 1699108488, 'rateBuy': 0, 'rateCross': 2.7712,
             'rateSell': 0},
            {'currencyCodeA': 933, 'currencyCodeB': 980, 'date': 1699462995, 'rateBuy': 0, 'rateCross': 11.6563,
             'rateSell': 0},
            {'currencyCodeA': 124, 'currencyCodeB': 980, 'date': 1699465313, 'rateBuy': 0, 'rateCross': 27.3123,
             'rateSell': 0},
            {'currencyCodeA': 976, 'currencyCodeB': 980, 'date': 1692273994, 'rateBuy': 0, 'rateCross': 0.0154,
             'rateSell': 0},
            {'currencyCodeA': 152, 'currencyCodeB': 980, 'date': 1699464336, 'rateBuy': 0, 'rateCross': 0.042,
             'rateSell': 0},
            {'currencyCodeA': 170, 'currencyCodeB': 980, 'date': 1699465265, 'rateBuy': 0, 'rateCross': 0.0093,
             'rateSell': 0},
            {'currencyCodeA': 188, 'currencyCodeB': 980, 'date': 1699449630, 'rateBuy': 0, 'rateCross': 0.0699,
             'rateSell': 0},
            {'currencyCodeA': 192, 'currencyCodeB': 980, 'date': 1687102850, 'rateBuy': 0, 'rateCross': 1.5599,
             'rateSell': 0},
            {'currencyCodeA': 203, 'currencyCodeB': 980, 'date': 1699465316, 'rateBuy': 0, 'rateCross': 1.6333,
             'rateSell': 0},
            {'currencyCodeA': 262, 'currencyCodeB': 980, 'date': 1678810696, 'rateBuy': 0, 'rateCross': 0.2108,
             'rateSell': 0},
            {'currencyCodeA': 208, 'currencyCodeB': 980, 'date': 1699465256, 'rateBuy': 0, 'rateCross': 5.3744,
             'rateSell': 0},
            {'currencyCodeA': 12, 'currencyCodeB': 980, 'date': 1699465183, 'rateBuy': 0, 'rateCross': 0.2773,
             'rateSell': 0},
            {'currencyCodeA': 818, 'currencyCodeB': 980, 'date': 1699465279, 'rateBuy': 0, 'rateCross': 1.2096,
             'rateSell': 0},
            {'currencyCodeA': 230, 'currencyCodeB': 980, 'date': 1699355932, 'rateBuy': 0, 'rateCross': 0.6712,
             'rateSell': 0},
            {'currencyCodeA': 981, 'currencyCodeB': 980, 'date': 1699465277, 'rateBuy': 0, 'rateCross': 13.9432,
             'rateSell': 0},
            {'currencyCodeA': 936, 'currencyCodeB': 980, 'date': 1699435365, 'rateBuy': 0, 'rateCross': 3.1437,
             'rateSell': 0},
            {'currencyCodeA': 270, 'currencyCodeB': 980, 'date': 1699449447, 'rateBuy': 0, 'rateCross': 0.6098,
             'rateSell': 0},
            {'currencyCodeA': 324, 'currencyCodeB': 980, 'date': 1698000894, 'rateBuy': 0, 'rateCross': 0.0044,
             'rateSell': 0},
            {'currencyCodeA': 344, 'currencyCodeB': 980, 'date': 1699459573, 'rateBuy': 0, 'rateCross': 4.7711,
             'rateSell': 0},
            {'currencyCodeA': 191, 'currencyCodeB': 980, 'date': 1680625280, 'rateBuy': 0, 'rateCross': 5.4258,
             'rateSell': 0},
            {'currencyCodeA': 348, 'currencyCodeB': 980, 'date': 1699465307, 'rateBuy': 0, 'rateCross': 0.1058,
             'rateSell': 0},
            {'currencyCodeA': 360, 'currencyCodeB': 980, 'date': 1699465058, 'rateBuy': 0, 'rateCross': 0.0023,
             'rateSell': 0},
            {'currencyCodeA': 376, 'currencyCodeB': 980, 'date': 1699465231, 'rateBuy': 0, 'rateCross': 9.7127,
             'rateSell': 0},
            {'currencyCodeA': 356, 'currencyCodeB': 980, 'date': 1699465153, 'rateBuy': 0, 'rateCross': 0.4483,
             'rateSell': 0},
            {'currencyCodeA': 368, 'currencyCodeB': 980, 'date': 1699462094, 'rateBuy': 0, 'rateCross': 0.0284,
             'rateSell': 0},
            {'currencyCodeA': 352, 'currencyCodeB': 980, 'date': 1699464703, 'rateBuy': 0, 'rateCross': 0.2651,
             'rateSell': 0},
            {'currencyCodeA': 400, 'currencyCodeB': 980, 'date': 1699461400, 'rateBuy': 0, 'rateCross': 52.6487,
             'rateSell': 0},
            {'currencyCodeA': 404, 'currencyCodeB': 980, 'date': 1699464532, 'rateBuy': 0, 'rateCross': 0.2468,
             'rateSell': 0},
            {'currencyCodeA': 417, 'currencyCodeB': 980, 'date': 1699463491, 'rateBuy': 0, 'rateCross': 0.4174,
             'rateSell': 0},
            {'currencyCodeA': 116, 'currencyCodeB': 980, 'date': 1699288927, 'rateBuy': 0, 'rateCross': 0.009,
             'rateSell': 0},
            {'currencyCodeA': 410, 'currencyCodeB': 980, 'date': 1699462833, 'rateBuy': 0, 'rateCross': 0.0287,
             'rateSell': 0},
            {'currencyCodeA': 414, 'currencyCodeB': 980, 'date': 1699457396, 'rateBuy': 0, 'rateCross': 120.9648,
             'rateSell': 0},
            {'currencyCodeA': 398, 'currencyCodeB': 980, 'date': 1699465061, 'rateBuy': 0, 'rateCross': 0.0804,
             'rateSell': 0},
            {'currencyCodeA': 418, 'currencyCodeB': 980, 'date': 1698938047, 'rateBuy': 0, 'rateCross': 0.0018,
             'rateSell': 0},
            {'currencyCodeA': 422, 'currencyCodeB': 980, 'date': 1699284268, 'rateBuy': 0, 'rateCross': 0.0004,
             'rateSell': 0},
            {'currencyCodeA': 144, 'currencyCodeB': 980, 'date': 1699465310, 'rateBuy': 0, 'rateCross': 0.1141,
             'rateSell': 0},
            {'currencyCodeA': 434, 'currencyCodeB': 980, 'date': 1674670757, 'rateBuy': 0, 'rateCross': 7.8783,
             'rateSell': 0},
            {'currencyCodeA': 504, 'currencyCodeB': 980, 'date': 1699461484, 'rateBuy': 0, 'rateCross': 3.6553,
             'rateSell': 0},
            {'currencyCodeA': 498, 'currencyCodeB': 980, 'date': 1699465309, 'rateBuy': 0, 'rateCross': 2.0891,
             'rateSell': 0},
            {'currencyCodeA': 969, 'currencyCodeB': 980, 'date': 1699454258, 'rateBuy': 0, 'rateCross': 0.0083,
             'rateSell': 0},
            {'currencyCodeA': 807, 'currencyCodeB': 980, 'date': 1699465232, 'rateBuy': 0, 'rateCross': 0.6482,
             'rateSell': 0},
            {'currencyCodeA': 496, 'currencyCodeB': 980, 'date': 1699437313, 'rateBuy': 0, 'rateCross': 0.0107,
             'rateSell': 0},
            {'currencyCodeA': 480, 'currencyCodeB': 980, 'date': 1699462959, 'rateBuy': 0, 'rateCross': 0.8429,
             'rateSell': 0},
            {'currencyCodeA': 454, 'currencyCodeB': 980, 'date': 1678369785, 'rateBuy': 0, 'rateCross': 0.0368,
             'rateSell': 0},
            {'currencyCodeA': 484, 'currencyCodeB': 980, 'date': 1699464578, 'rateBuy': 0, 'rateCross': 2.1361,
             'rateSell': 0},
            {'currencyCodeA': 458, 'currencyCodeB': 980, 'date': 1699464994, 'rateBuy': 0, 'rateCross': 8.0371,
             'rateSell': 0},
            {'currencyCodeA': 943, 'currencyCodeB': 980, 'date': 1698658019, 'rateBuy': 0, 'rateCross': 0.5918,
             'rateSell': 0},
            {'currencyCodeA': 516, 'currencyCodeB': 980, 'date': 1699440291, 'rateBuy': 0, 'rateCross': 2.047,
             'rateSell': 0},
            {'currencyCodeA': 566, 'currencyCodeB': 980, 'date': 1699465194, 'rateBuy': 0, 'rateCross': 0.0467,
             'rateSell': 0},
            {'currencyCodeA': 558, 'currencyCodeB': 980, 'date': 1699414249, 'rateBuy': 0, 'rateCross': 1.0206,
             'rateSell': 0},
            {'currencyCodeA': 578, 'currencyCodeB': 980, 'date': 1699465306, 'rateBuy': 0, 'rateCross': 3.3872,
             'rateSell': 0},
            {'currencyCodeA': 524, 'currencyCodeB': 980, 'date': 1699453379, 'rateBuy': 0, 'rateCross': 0.2801,
             'rateSell': 0},
            {'currencyCodeA': 554, 'currencyCodeB': 980, 'date': 1699423483, 'rateBuy': 0, 'rateCross': 22.3017,
             'rateSell': 0},
            {'currencyCodeA': 512, 'currencyCodeB': 980, 'date': 1699464084, 'rateBuy': 0, 'rateCross': 96.9166,
             'rateSell': 0},
            {'currencyCodeA': 604, 'currencyCodeB': 980, 'date': 1699465186, 'rateBuy': 0, 'rateCross': 9.8763,
             'rateSell': 0},
            {'currencyCodeA': 608, 'currencyCodeB': 980, 'date': 1699465276, 'rateBuy': 0, 'rateCross': 0.6651,
             'rateSell': 0},
            {'currencyCodeA': 586, 'currencyCodeB': 980, 'date': 1699464013, 'rateBuy': 0, 'rateCross': 0.1311,
             'rateSell': 0},
            {'currencyCodeA': 985, 'currencyCodeB': 980, 'date': 1699465318, 'rateBuy': 0, 'rateCross': 9.0011,
             'rateSell': 0},
            {'currencyCodeA': 600, 'currencyCodeB': 980, 'date': 1699461929, 'rateBuy': 0, 'rateCross': 0.005,
             'rateSell': 0},
            {'currencyCodeA': 634, 'currencyCodeB': 980, 'date': 1699464795, 'rateBuy': 0, 'rateCross': 10.2464,
             'rateSell': 0},
            {'currencyCodeA': 946, 'currencyCodeB': 980, 'date': 1699465289, 'rateBuy': 0, 'rateCross': 8.0715,
             'rateSell': 0},
            {'currencyCodeA': 941, 'currencyCodeB': 980, 'date': 1699465279, 'rateBuy': 0, 'rateCross': 0.3406,
             'rateSell': 0},
            {'currencyCodeA': 682, 'currencyCodeB': 980, 'date': 1699465219, 'rateBuy': 0, 'rateCross': 9.9455,
             'rateSell': 0},
            {'currencyCodeA': 690, 'currencyCodeB': 980, 'date': 1699452266, 'rateBuy': 0, 'rateCross': 2.6034,
             'rateSell': 0},
            {'currencyCodeA': 938, 'currencyCodeB': 980, 'date': 1680961561, 'rateBuy': 0, 'rateCross': 0.0627,
             'rateSell': 0},
            {'currencyCodeA': 752, 'currencyCodeB': 980, 'date': 1699465318, 'rateBuy': 0, 'rateCross': 3.4315,
             'rateSell': 0},
            {'currencyCodeA': 702, 'currencyCodeB': 980, 'date': 1699465114, 'rateBuy': 0, 'rateCross': 27.6302,
             'rateSell': 0},
            {'currencyCodeA': 694, 'currencyCodeB': 980, 'date': 1664217991, 'rateBuy': 0, 'rateCross': 0.0024,
             'rateSell': 0},
            {'currencyCodeA': 706, 'currencyCodeB': 980, 'date': 1683386099, 'rateBuy': 0, 'rateCross': 0.0659,
             'rateSell': 0},
            {'currencyCodeA': 968, 'currencyCodeB': 980, 'date': 1696117310, 'rateBuy': 0, 'rateCross': 0.9686,
             'rateSell': 0},
            {'currencyCodeA': 748, 'currencyCodeB': 980, 'date': 1668614714, 'rateBuy': 0, 'rateCross': 2.1898,
             'rateSell': 0},
            {'currencyCodeA': 764, 'currencyCodeB': 980, 'date': 1699465269, 'rateBuy': 0, 'rateCross': 1.0529,
             'rateSell': 0},
            {'currencyCodeA': 972, 'currencyCodeB': 980, 'date': 1699357928, 'rateBuy': 0, 'rateCross': 3.4054,
             'rateSell': 0},
            {'currencyCodeA': 788, 'currencyCodeB': 980, 'date': 1699463529, 'rateBuy': 0, 'rateCross': 11.8678,
             'rateSell': 0},
            {'currencyCodeA': 949, 'currencyCodeB': 980, 'date': 1699465310, 'rateBuy': 0, 'rateCross': 1.314,
             'rateSell': 0},
            {'currencyCodeA': 901, 'currencyCodeB': 980, 'date': 1699463771, 'rateBuy': 0, 'rateCross': 1.1597,
             'rateSell': 0},
            {'currencyCodeA': 834, 'currencyCodeB': 980, 'date': 1699457829, 'rateBuy': 0, 'rateCross': 0.0151,
             'rateSell': 0},
            {'currencyCodeA': 800, 'currencyCodeB': 980, 'date': 1699455478, 'rateBuy': 0, 'rateCross': 0.0099,
             'rateSell': 0},
            {'currencyCodeA': 858, 'currencyCodeB': 980, 'date': 1699439184, 'rateBuy': 0, 'rateCross': 0.9345,
             'rateSell': 0},
            {'currencyCodeA': 860, 'currencyCodeB': 980, 'date': 1699465168, 'rateBuy': 0, 'rateCross': 0.003,
             'rateSell': 0},
            {'currencyCodeA': 704, 'currencyCodeB': 980, 'date': 1699463503, 'rateBuy': 0, 'rateCross': 0.0015,
             'rateSell': 0},
            {'currencyCodeA': 950, 'currencyCodeB': 980, 'date': 1699371344, 'rateBuy': 0, 'rateCross': 0.0611,
             'rateSell': 0},
            {'currencyCodeA': 952, 'currencyCodeB': 980, 'date': 1699394090, 'rateBuy': 0, 'rateCross': 0.0611,
             'rateSell': 0},
            {'currencyCodeA': 886, 'currencyCodeB': 980, 'date': 1543715495, 'rateBuy': 0, 'rateCross': 0.112,
             'rateSell': 0},
            {'currencyCodeA': 710, 'currencyCodeB': 980, 'date': 1699465106, 'rateBuy': 0, 'rateCross': 2.0473,
             'rateSell': 0}]
    }

    income_cur_list = {'USD': True, 'EUR':  True, 'PLN': True, 'GBP': True, 'TRY': True, 'CHF': True}

    instance = CurrencyTransformation(income_data, income_cur_list)
    print(instance.currency_list)
    print('national_bank', instance.currency['national_bank'])
    print('privat_bank', instance.currency['privat_bank'])
    print('mono_bank', instance.currency['mono_bank'])


# {{'bank': {'AED': {'currency_code': 'AED', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 10.164,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'AFN': {'currency_code': 'AFN', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.4252,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'ALL': {'currency_code': 'ALL', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.3809,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'AMD': {'currency_code': 'AMD', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.093,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'AOA': {'currency_code': 'AOA', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.0451,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'ARS': {'currency_code': 'ARS', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.0462,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'AUD': {'currency_code': 'AUD', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 24.2798,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'AZN': {'currency_code': 'AZN', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 22.0022,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'BDT': {'currency_code': 'BDT', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.339,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'BGN': {'currency_code': 'BGN', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 20.4444,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'BHD': {'currency_code': 'BHD', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 98.9249,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'BIF': {'currency_code': 'BIF', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.0158,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'BND': {'currency_code': 'BND', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 27.5553,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'BOB': {'currency_code': 'BOB', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 5.4371,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'BRL': {'currency_code': 'BRL', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 7.6826,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'BWP': {'currency_code': 'BWP', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 2.7712,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'BYN': {'currency_code': 'BYN', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 11.6563,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'CAD': {'currency_code': 'CAD', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 27.3123,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'CDF': {'currency_code': 'CDF', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.0154,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'CHF': {'currency_code': 'CHF', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 41.589,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'CLP': {'currency_code': 'CLP', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.042,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'CNY': {'currency_code': 'CNY', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 5.1239,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'COP': {'currency_code': 'COP', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.0093,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'CRC': {'currency_code': 'CRC', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.0699,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'CUP': {'currency_code': 'CUP', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 1.5599,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'CZK': {'currency_code': 'CZK', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 1.6333,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'DJF': {'currency_code': 'DJF', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.2108,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'DKK': {'currency_code': 'DKK', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 5.3744,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'DZD': {'currency_code': 'DZD', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.2773,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'EGP': {'currency_code': 'EGP', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 1.2096,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'ETB': {'currency_code': 'ETB', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.6712,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'EUR': {'currency_code': 'EUR', 'base_currency_code': 'UAH', 'buy_rate': 38.48, 'cross_rate': 0.0,
#                    'sale_rate': 39.8804, 'on_time': '08.11.2023 20:47'},
#            'GBP': {'currency_code': 'GBP', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 46.0707,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'GEL': {'currency_code': 'GEL', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 13.9432,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'GHS': {'currency_code': 'GHS', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 3.1437,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'GMD': {'currency_code': 'GMD', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.6098,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'GNF': {'currency_code': 'GNF', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.0044,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'HKD': {'currency_code': 'HKD', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 4.7711,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'HRK': {'currency_code': 'HRK', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 5.4258,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'HUF': {'currency_code': 'HUF', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.1058,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'IDR': {'currency_code': 'IDR', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.0023,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'ILS': {'currency_code': 'ILS', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 9.7127,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'INR': {'currency_code': 'INR', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.4483,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'IQD': {'currency_code': 'IQD', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.0284,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'ISK': {'currency_code': 'ISK', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.2651,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'JOD': {'currency_code': 'JOD', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 52.6487,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'JPY': {'currency_code': 'JPY', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.2487,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'KES': {'currency_code': 'KES', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.2468,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'KGS': {'currency_code': 'KGS', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.4174,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'KHR': {'currency_code': 'KHR', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.009,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'KRW': {'currency_code': 'KRW', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.0287,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'KWD': {'currency_code': 'KWD', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 120.9648,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'KZT': {'currency_code': 'KZT', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.0804,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'LAK': {'currency_code': 'LAK', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.0018,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'LBP': {'currency_code': 'LBP', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.0004,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'LKR': {'currency_code': 'LKR', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.1141,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'LYD': {'currency_code': 'LYD', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 7.8783,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'MAD': {'currency_code': 'MAD', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 3.6553,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'MDL': {'currency_code': 'MDL', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 2.0891,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'MGA': {'currency_code': 'MGA', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.0083,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'MKD': {'currency_code': 'MKD', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.6482,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'MNT': {'currency_code': 'MNT', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.0107,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'MUR': {'currency_code': 'MUR', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.8429,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'MWK': {'currency_code': 'MWK', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.0368,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'MXN': {'currency_code': 'MXN', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 2.1361,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'MYR': {'currency_code': 'MYR', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 8.0371,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'MZN': {'currency_code': 'MZN', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.5918,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'NAD': {'currency_code': 'NAD', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 2.047,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'NGN': {'currency_code': 'NGN', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.0467,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'NIO': {'currency_code': 'NIO', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 1.0206,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'NOK': {'currency_code': 'NOK', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 3.3872,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'NPR': {'currency_code': 'NPR', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.2801,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'NZD': {'currency_code': 'NZD', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 22.3017,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'OMR': {'currency_code': 'OMR', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 96.9166,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'PEN': {'currency_code': 'PEN', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 9.8763,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'PHP': {'currency_code': 'PHP', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.6651,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'PKR': {'currency_code': 'PKR', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.1311,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'PLN': {'currency_code': 'PLN', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 9.0011,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'PYG': {'currency_code': 'PYG', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.005,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'QAR': {'currency_code': 'QAR', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 10.2464,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'RON': {'currency_code': 'RON', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 8.0715,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'RSD': {'currency_code': 'RSD', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.3406,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'SAR': {'currency_code': 'SAR', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 9.9455,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'SCR': {'currency_code': 'SCR', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 2.6034,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'SDG': {'currency_code': 'SDG', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.0627,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'SEK': {'currency_code': 'SEK', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 3.4315,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'SGD': {'currency_code': 'SGD', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 27.6302,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'SLL': {'currency_code': 'SLL', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.0024,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'SOS': {'currency_code': 'SOS', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.0659,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'SRD': {'currency_code': 'SRD', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.9686,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'SZL': {'currency_code': 'SZL', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 2.1898,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'THB': {'currency_code': 'THB', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 1.0529,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'TJS': {'currency_code': 'TJS', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 3.4054,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'TND': {'currency_code': 'TND', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 11.8678,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'TRY': {'currency_code': 'TRY', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 1.314,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'TWD': {'currency_code': 'TWD', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 1.1597,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'TZS': {'currency_code': 'TZS', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.0151,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'UGX': {'currency_code': 'UGX', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.0099,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'USD': {'currency_code': 'USD', 'base_currency_code': 'UAH', 'buy_rate': 36.02, 'cross_rate': 0.0,
#                    'sale_rate': 37.2995, 'on_time': '08.11.2023 20:47'},
#            'UYU': {'currency_code': 'UYU', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.9345,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'UZS': {'currency_code': 'UZS', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.003,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'VND': {'currency_code': 'VND', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.0015,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'XAF': {'currency_code': 'XAF', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.0611,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'XOF': {'currency_code': 'XOF', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.0611,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'YER': {'currency_code': 'YER', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 0.112,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'},
#            'ZAR': {'currency_code': 'ZAR', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 2.0473,
#                    'sale_rate': 0.0, 'on_time': '08.11.2023 20:47'}}}}
