import datetime

from fastapi import APIRouter, Depends
from src.auth.utils import User
from src.auth.base_config import auth_backend
from src.auth.manager import get_user_manager
from sqlalchemy.ext.asyncio import AsyncSession

from src.logic.report_logic import XclCurrencyReport
from src.database import get_async_session
from fastapi_users import FastAPIUsers
from src.logic.currency_logic import CurrencyTransformation
from src.models.models import add_currency_data
from src.currency_parse.schemas import Banks, CurrencyOption

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

router = APIRouter(
    prefix="/currency",
    tags=["Currency"]
)

current_user = fastapi_users.current_user()


@router.post("/get_all_course")
async def get_all_currency(req_cur: CurrencyOption, banks: Banks, report: bool = False,
                           current_user: FastAPIUsers = Depends(current_user),
                           session: AsyncSession = Depends(get_async_session)):
    start_time = datetime.datetime.now()
    data_source = await banks.get_banks_currency_data()
    currency: dict[str, dict] = CurrencyTransformation(data_source, req_cur.get_requested_currency()).currency
    statement_status = await add_currency_data(currency_data=currency, user_id=current_user.id, session=session)
    if report:
        report = XclCurrencyReport(currency_data=currency, user_id=current_user.id)
        report.create_report_file()
    print(statement_status, type(statement_status))
    time_delta = datetime.datetime.now() - start_time
    print(time_delta)
    return currency
