import datetime
from asyncio import run
from typing import Union, Annotated
from logic.currency_logic import CurrencyTransformation
import iso4217parse

import httpx
import uvicorn

import asyncio
from fastapi import FastAPI, File, UploadFile, Form
from pydantic import BaseModel, EmailStr, json
from starlette import status, requests
import json

from ..config import DB_NAME

x = DB_NAME

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello_world", "db_name": str(x)}


@app.post("/items/", status_code=status.HTTP_201_CREATED)
async def create_item(name: str):
    return {"name": name}


PRIVATBANK_API_URL = "https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11"
MONOBANK_API_URL = "https://api.monobank.ua/bank/currency"
NBU_API_URL = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"


@app.post("/files/")
async def create_file(
        file: Annotated[bytes, File()],
        fileb: Annotated[UploadFile, File()],
        token: Annotated[str, Form()],
):
    return {
        "file_size": len(file),
        "token": token,
        "fileb_content_type": fileb.content_type,
    }


@app.get('/get_privat_course')
async def get_privat_course():
    client = httpx.AsyncClient()
    response = await client.get(PRIVATBANK_API_URL)
    return response.json()


@app.get('/get_mono_course')
async def get_mono_course():
    client = httpx.AsyncClient()
    response = await client.get(MONOBANK_API_URL)
    result = iso4217parse.by_code_num(980)
    print(result.name, result.alpha3)
    print(response.json())
    print(type(response.json()))
    return {"currency": response.json()}


@app.get('/get_nbu_course')
async def get_nbu_course():
    client = httpx.AsyncClient()
    response = await client.get(NBU_API_URL)
    result = iso4217parse.parse(980)
    for i in result:
        print("*", i)
    # print(result.name, result.alpha3, result.name)
    print(response.json())
    print(type(response.json()))
    return {"currency": response.json()}


@app.get('/get_all_course')
async def get_all_course():
    # start_time = datetime.datetime.now()
    client = httpx.AsyncClient()
    response_privat = await client.get(PRIVATBANK_API_URL)
    response_mono = await client.get(MONOBANK_API_URL)
    response_nbu = await client.get(NBU_API_URL)
    privat = response_privat.json()
    mono = response_mono.json()
    nbu = response_nbu.json()
    banks_data = (nbu, mono, privat)
    currency = CurrencyTransformation(nbu, mono, privat).currency
    # time_delta = datetime.datetime.now()-start_time
    # print("Execution time of async def,  in seconds: ", time_delta.total_seconds())
    return currency


if __name__ == "__main__":
    # uvicorn.run(app="main:app", reload=True)
    uvicorn.run(app="main:app", port=8888, reload=True)
    # uvicorn.run(app="main_bot:bot", port=9999, reload=True)

    """
    From command line$ uvicorn main:app --host 192.168.0.165 --port 8000 --reload
    or
    $ uvicorn main:app  --reload
    """
