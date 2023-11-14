from datetime import datetime
import xlsxwriter
from src.config import BUY_RATE, CROSS_RATE, SELL_RATE
import os.path




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

valid_data = \
    {
        'national_bank': {
            'USD': {'currency_code': 'USD', 'base_currency_code': 'UAH', 'buy_rate': 36.0407, 'cross_rate': 0.0,
                    'sale_rate': 36.0407, 'on_time': '13.11.2023 16:05'},
            'EUR': {'currency_code': 'EUR', 'base_currency_code': 'UAH', 'buy_rate': 38.4518, 'cross_rate': 0.0,
                    'sale_rate': 38.4518, 'on_time': '13.11.2023 16:05'},
            'CHF': {'currency_code': 'CHF', 'base_currency_code': 'UAH', 'buy_rate': 40.0474, 'cross_rate': 0.0,
                    'sale_rate': 40.0474, 'on_time': '13.11.2023 16:05'},
            'GBP': {'currency_code': 'GBP', 'base_currency_code': 'UAH', 'buy_rate': 44.1643, 'cross_rate': 0.0,
                    'sale_rate': 44.1643, 'on_time': '13.11.2023 16:05'},
            'PLN': {'currency_code': 'PLN', 'base_currency_code': 'UAH', 'buy_rate': 8.6108, 'cross_rate': 0.0,
                    'sale_rate': 8.6108, 'on_time': '13.11.2023 16:05'},
            'TRY': {'currency_code': 'TRY', 'base_currency_code': 'UAH', 'buy_rate': 1.264, 'cross_rate': 0.0,
                    'sale_rate': 1.264, 'on_time': '13.11.2023 16:05'}}, 'privat_bank': {
        'USD': {'currency_code': 'USD', 'base_currency_code': 'UAH', 'buy_rate': 36.01, 'cross_rate': 0.0,
                'sale_rate': 37.45318, 'on_time': '13.11.2023 16:05'},
        'EUR': {'currency_code': 'EUR', 'base_currency_code': 'UAH', 'buy_rate': 38.46, 'cross_rate': 0.0,
                'sale_rate': 40.48583, 'on_time': '13.11.2023 16:05'}}, 'mono_bank': {
        'USD': {'currency_code': 'USD', 'base_currency_code': 'UAH', 'buy_rate': 36.02, 'cross_rate': 0.0,
                'sale_rate': 37.2995, 'on_time': '13.11.2023 16:05'},
        'EUR': {'currency_code': 'EUR', 'base_currency_code': 'UAH', 'buy_rate': 38.48, 'cross_rate': 0.0,
                'sale_rate': 39.8804, 'on_time': '13.11.2023 16:05'},
        'CHF': {'currency_code': 'CHF', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 41.589,
                'sale_rate': 0.0, 'on_time': '13.11.2023 16:05'},
        'GBP': {'currency_code': 'GBP', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 46.0707,
                'sale_rate': 0.0, 'on_time': '13.11.2023 16:05'},
        'PLN': {'currency_code': 'PLN', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 9.0011,
                'sale_rate': 0.0, 'on_time': '13.11.2023 16:05'},
        'TRY': {'currency_code': 'TRY', 'base_currency_code': 'UAH', 'buy_rate': 0.0, 'cross_rate': 1.314,
                'sale_rate': 0.0,
                'on_time': '13.11.2023 16:05'}}}


class XclCurrencyReport:
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
            bank_row = [bank]
            for currency in bank_data:
                currency_data = bank_data.get(currency)
                currency_row = [
                    currency_data[BUY_RATE],
                    currency_data[CROSS_RATE],
                    currency_data[SELL_RATE],
                ]
                bank_row.extend(currency_row)
            data.append(bank_row)
        return data

    def create_report_file(self):
        first_table_letter = chr(self.TABLE_START_LETTER)
        first_table_number = self.TABLE_START_NUMBER
        last_table_letter = chr(self.table_end_letter_numeric + self.TABLE_START_LETTER)
        last_table_number = self.table_end_number

        directory_path = f"Parser_project/src/reports/xlsx_reports/user_{self.user_id}"
        directory_path_exists = os.path.exists(directory_path)
        if not directory_path_exists:
            os.makedirs(directory_path)

        file_nmae = datetime.now().strftime("%Y-%m-%d__%H-%M")
        path = os.path.realpath(directory_path + f"/{file_nmae}.xlsx")

        workbook = xlsxwriter.Workbook(path)
        worksheet = workbook.add_worksheet('Currency table')
        worksheet.add_table(
            f'{first_table_letter}{first_table_number}:{last_table_letter}{last_table_number}',
            {'name': "Currency_data_table",
             'columns': self.table_header,
             'data': self.data}
        )

        worksheet.autofit()
        workbook.close()

    def __init__(self, currency_data: dict[str, dict[str, dict[str, str | float]]], user_id: int):
        self.currency_data = currency_data
        self.user_id = user_id
        self.table_header = self._get_table_header()
        self.table_end_letter_numeric = len(self.table_header)
        self.table_end_number = self.TABLE_START_NUMBER + len(self.currency_data)
        self.data = self._get_data()


if __name__ == '__main__':
    instance = XclCurrencyReport(valid_data, 1)
    print(instance.table_header)
    print(instance.data)

    instance.create_report_file()

