import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from src.auth.utils import User
from src.auth.base_config import auth_backend
from src.auth.manager import get_user_manager
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.models import currency, user
from src.database import get_async_session
from fastapi_users import FastAPIUsers
import httpx
from src.config import PRIVATBANK_API_URL, MONOBANK_API_URL, NBU_API_URL
from src.logic.currency_logic import CurrencyTransformation
from src.models.models import add_currency_data
from src.currency_parse.schemas import Banks


fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

router = APIRouter(
    prefix="/currency",
    tags=["Currency"]
)

current_user = fastapi_users.current_user()

# @router.get("/")
# async def get_currency(session: AsyncSession = Depends(get_async_session)):
#     statment = select(currency)
#     await session.execute(statment)


@router.post("/get_all_course")
async def get_cuget_all_courserrency(banks: Banks, current_user: FastAPIUsers = Depends(current_user),
                                     session: AsyncSession = Depends(get_async_session)):
    start_time = datetime.datetime.now()
    data_source = await banks.get_banks_currency_data()
    currency: dict[str, dict] = CurrencyTransformation(data_source).currency
    statement_status = await add_currency_data(currency_data=currency, user_id=current_user.id, session=session)
    print(statement_status, type(statement_status))
    time_delta = datetime.datetime.now()-start_time
    print(time_delta)
    return [statement_status, currency]

# ORM - Object-relational model
# SQL Injection

