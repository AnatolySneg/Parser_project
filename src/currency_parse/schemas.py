from datetime import datetime
from pydantic import BaseModel, Json
import httpx
import json
from sqlalchemy import ARRAY, JSON
from src.config import NATIONAL_BANK, PRIVAT_BANK, MONO_BANK
from src.config import NBU_API_URL, MONOBANK_API_URL, PRIVATBANK_API_URL


class Currency(BaseModel):
    requested_banks: list
    currency_data: Json
    user_id: int


class Banks(BaseModel):
    national_bank: bool = True
    mono_bank: bool = True
    privat_bank: bool = True

    def _get_bank_status(self):
        check_list = {}
        check_list[NATIONAL_BANK] = self.national_bank
        check_list[PRIVAT_BANK] = self.privat_bank
        check_list[MONO_BANK] = self.mono_bank
        return check_list

    async def get_banks_currency_data(self):
        request_list = {
            NATIONAL_BANK: NBU_API_URL,
            PRIVAT_BANK: PRIVATBANK_API_URL,
            MONO_BANK: MONOBANK_API_URL,
        }
        check_list = self._get_bank_status()
        client = httpx.AsyncClient()
        response_list: dict = {bank: (await client.get(request_list[bank])).json() for bank in check_list if
                               check_list[bank]}
        return response_list
