from src.config import BUY_RATE, CROSS_RATE, SELL_RATE


output_data = \
    {
        'national_bank': {
            'USD': {'currency_code': 'USD', 'base_currency_code': 'UAH', 'buy_rate': 36.0407, 'cross_rate': 0.0,
                    'sale_rate': 36.0407, 'on_time': '10.11.2023 15:24'},
            'EUR': {'currency_code': 'EUR', 'base_currency_code': 'UAH', 'buy_rate': 38.4518, 'cross_rate': 0.0,
                    'sale_rate': 38.4518, 'on_time': '10.11.2023 15:24'},
            'CHF': {'currency_code': 'CHF', 'base_currency_code': 'UAH', 'buy_rate': 40.0474, 'cross_rate': 0.0,
                    'sale_rate': 40.0474, 'on_time': '10.11.2023 15:24'},
            'GBP': {'currency_code': 'GBP', 'base_currency_code': 'UAH', 'buy_rate': 44.1643, 'cross_rate': 0.0,
                    'sale_rate': 44.1643, 'on_time': '10.11.2023 15:24'},
            'PLN': {'currency_code': 'PLN', 'base_currency_code': 'UAH', 'buy_rate': 8.6108, 'cross_rate': 0.0,
                    'sale_rate': 8.6108, 'on_time': '10.11.2023 15:24'},
            'TRY': {'currency_code': 'TRY', 'base_currency_code': 'UAH', 'buy_rate': 1.264, 'cross_rate': 0.0,
                    'sale_rate': 1.264, 'on_time': '10.11.2023 15:24'}},

        'privat_bank': {
            'USD': {'currency_code': 'USD', 'base_currency_code': 'UAH', 'buy_rate': 36.01, 'cross_rate': 0.0,
                    'sale_rate': 37.45318, 'on_time': '10.11.2023 15:24'},
            'EUR': {'currency_code': 'EUR', 'base_currency_code': 'UAH', 'buy_rate': 38.46, 'cross_rate': 0.0,
                    'sale_rate': 40.48583, 'on_time': '10.11.2023 15:24'}},

        'mono_bank': {
            'USD': {'currency_code': 'USD', 'base_currency_code': 'UAH', 'buy_rate': 36.02, 'cross_rate': 0.0,
                    'sale_rate': 37.2995, 'on_time': '10.11.2023 15:24'},
            'EUR': {'currency_code': 'EUR', 'base_currency_code': 'UAH', 'buy_rate': 38.48, 'cross_rate': 0.0,
                    'sale_rate': 39.8804, 'on_time': '10.11.2023 15:24'},
            'CHF': {'currency_code': 'CHF', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 41.589,
                    'sale_rate': 0.0, 'on_time': '10.11.2023 15:24'},
            'GBP': {'currency_code': 'GBP', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 46.0707,
                    'sale_rate': 0.0, 'on_time': '10.11.2023 15:24'},
            'PLN': {'currency_code': 'PLN', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 9.0011,
                    'sale_rate': 0.0, 'on_time': '10.11.2023 15:24'},
            'TRY': {'currency_code': 'TRY', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 1.314,
                    'sale_rate': 0.0,
                    'on_time': '10.11.2023 15:24'}}}


class XclReport:
    TABLE_START_LETTER = 66  # Letter "B" by ASCII
    TABLE_START_NUMBER = 2  # Digit "2"
    COLUMNS = 'columns'

    def _get_table_header(self):
        header_list = []
        for bank in self.currency_data:
            header = [{'header': 'Bank'}]
            for currency in self.currency_data.get(bank):
                header.extend([{'header': currency + ' (buy-rate)'}, {'header': currency + ' (cross-rate)'},
                               {'header': currency + ' (sell-rate)'}])
            header_list.append(header)
        table_header = max(header_list, key=lambda item: len(item))
        return table_header

    def _get_data(self):
        data = []
        for bank in self.currency_data:
            bank_data = self.currency_data.get(bank)
            row = [bank, bank_data[BUY_RATE], bank_data[CROSS_RATE], bank_data[SELL_RATE], ]
            data.append(row)
        return data

    def __init__(self, currency_data: dict[str, dict[str, dict[str, str | float]]]):
        self.currency_data = currency_data
        self.table_header = self._get_table_header()
        self.table_end_letter = chr(len(self.table_header))
        self.table_end_number = self.TABLE_START_NUMBER + len(self.currency_data)
        self.data = self._get_data()

