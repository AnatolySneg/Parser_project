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
from src.currency_parse.schemas import Banks, CurrencyOption
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


if __name__ == "__main__":
    # uvicorn.run(app="main:app", reload=True)
    uvicorn.run(app="main:app", port=8888, reload=True)
    # uvicorn.run(app="main_bot:bot", port=9999, reload=True)

    """
    From command line$ uvicorn main:app --host 192.168.0.165 --port 8000 --reload
    or
    $ uvicorn main:app  --reload
    """
