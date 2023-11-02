import datetime
from asyncio import run
from typing import Union, Annotated
from fastapi import Request

from fastapi_users import FastAPIUsers

from logic.currency_logic import CurrencyTransformation
import iso4217parse

import httpx
import uvicorn

import asyncio
from fastapi import Depends
from fastapi import FastAPI, File, UploadFile, Form
from pydantic import BaseModel, EmailStr, json
from starlette import status, requests
import json

from src.auth.base_config import auth_backend
from src.auth.utils import User
from src.auth.manager import get_user_manager
from src.auth.schemas import UserRead, UserCreate, UserUpdate
from src.currency_parse.schemas import Banks
from src.models.models import add_currency_data
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_async_session
from src.currency_parse.currency_router import router as currency_router

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

app = FastAPI()

current_user = fastapi_users.current_user()

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/redis_strategiiii",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

app.include_router(currency_router)


# async def startup_event():
#     keys = Keys()
#     await initialize_redis(keys)


@app.get("/")
async def root():
    return {"message": "Hello_world"}


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
async def get_all_course(banks: Banks, current_user: FastAPIUsers = Depends(current_user), session: AsyncSession = Depends(get_async_session), ):
    currency: dict[str, dict] = CurrencyTransformation(banks).currency
    statement_status = await add_currency_data(currency_data=currency, user_id=current_user.id, session=session)
    print(statement_status, type(statement_status))
    # time_delta = datetime.datetime.now()-start_time
    return [statement_status, currency]


# @app.get('/get_all_course')
# async def get_all_course(banks: Banks, current_user: FastAPIUsers = Depends(current_user), session: AsyncSession = Depends(get_async_session), ):
#     # start_time = datetime.datetime.now()
#     included_banks = banks.model_dump()
#     user_id = current_user.id
#     client = httpx.AsyncClient()
#     response_privat = await client.get(PRIVATBANK_API_URL)
#     response_mono = await client.get(MONOBANK_API_URL)
#     response_nbu = await client.get(NBU_API_URL)
#     privat = response_privat.json()
#     mono = response_mono.json()
#     nbu = response_nbu.json()
#     banks_data = (nbu, mono, privat)
#     currency = CurrencyTransformation(banks).currency
#     statement_status = await add_currency_data(currency_data=currency, user_id=user_id, session=session)
#     print(type(currency))
#     # time_delta = datetime.datetime.now()-start_time
#     # print("Execution time of async def,  in seconds: ", time_delta.total_seconds())
#     return [statement_status, currency]
#

def test_1(a, b, c):
    return {'a': a,
            'b': b,
            'c': c}


def test_2(d, e, f):
    return {'d': d,
            'e': e,
            'f': f}


def test_3(g, h, i=999):
    return {'g': g,
            'h': h,
            'i': i}


@app.get('/test_test')
def test_test(one: dict = Depends(test_1), two: dict = Depends(test_2), three: dict = Depends(test_3)):
    print('one', one)
    print('two', two)
    print('three', three)
    return {'one': one,
            'two': two,
            'three': three}


if __name__ == "__main__":
    # uvicorn.run(app="main:app", reload=True)
    uvicorn.run(app="main:app", port=8888, reload=True)
    # uvicorn.run(app="main_bot:bot", port=9999, reload=True)

    """
    From command line$ uvicorn main:app --host 192.168.0.165 --port 8000 --reload
    or
    $ uvicorn main:app  --reload
    """
