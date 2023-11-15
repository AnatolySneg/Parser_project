from datetime import datetime
import xlsxwriter
from src.config import BUY_RATE, CROSS_RATE, SELL_RATE
import os.path


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
        file_name = datetime.now().strftime("%Y-%m-%d__%H-%M")
        path = os.path.realpath(directory_path + f"/{file_name}.xlsx")

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
        self.table_end_letter_numeric = len(self.table_header) - 1
        self.table_end_number = self.TABLE_START_NUMBER + len(self.currency_data)
        self.data = self._get_data()

