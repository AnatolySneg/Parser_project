from pydantic import BaseModel, Json
import httpx
from src.config import NATIONAL_BANK, PRIVAT_BANK, MONO_BANK
from src.config import NBU_API_URL, MONOBANK_API_URL, PRIVATBANK_API_URL


class Currency(BaseModel):
    requested_banks: list
    currency_data: Json
    user_id: int


class CurrencyOption(BaseModel):
    USD: bool = True
    EUR: bool = True
    PLN: bool = False
    GBP: bool = False
    TRY: bool = False
    CHF: bool = False

    def get_requested_currency(self):
        return {
            'USD': self.USD,
            'EUR': self.EUR,
            'PLN': self.PLN,
            'GBP': self.GBP,
            'TRY': self.TRY,
            'CHF': self.CHF,
        }


class Banks(BaseModel):
    national_bank: bool = True
    mono_bank: bool = True
    privat_bank: bool = True

    async def get_banks_currency_data(self):
        request_list = {
            NATIONAL_BANK: NBU_API_URL,
            PRIVAT_BANK: PRIVATBANK_API_URL,
            MONO_BANK: MONOBANK_API_URL,
        }
        check_list = {NATIONAL_BANK: self.national_bank, PRIVAT_BANK: self.privat_bank, MONO_BANK: self.mono_bank}
        client = httpx.AsyncClient()
        response_list: dict = {bank: (await client.get(request_list[bank])).json() for bank in check_list if
                               check_list[bank]}
        return response_list
