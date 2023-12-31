from datetime import datetime
import json

from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean, ARRAY

from src.database import Base
from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import select, update, insert
from sqlalchemy.ext.asyncio import AsyncSession
from src.currency_parse.schemas import Currency

metadata = MetaData()

user_status = Table(
    "user_status",
    metadata,
    Column("id", Integer, unique=True, primary_key=True),
    Column('name', String, nullable=False),
    Column("permissions", JSON),
)
# TODO: implement CoiceType from sqlalchemy-utils: https://sqlalchemy-utils.readthedocs.io/en/latest/data_types.html#module-sqlalchemy_utils.types.choice


user = Table(
    "user",
    metadata,
    Column("id", Integer, unique=True, primary_key=True),
    Column('email', String(length=320), unique=True, index=True, nullable=False),
    Column('phone_number', String),
    Column('username', String, nullable=False),
    Column('first_name', String(50)),
    Column('last_name', String(50)),
    Column("registered_at", TIMESTAMP, default=datetime.utcnow),
    Column("user_status_id", Integer, ForeignKey(user_status.c.id), nullable=False, default=1),

    Column("hashed_password", String(length=1024), nullable=False),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("is_superuser", Boolean, default=False, nullable=False),
    Column("is_verified", Boolean, default=False, nullable=False),
)


class User(SQLAlchemyBaseUserTable[int], Base):
    # Columns from models:
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    phone_number: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str] = mapped_column(String, nullable=False)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    registered_at = mapped_column(TIMESTAMP, default=datetime.utcnow)
    user_status_id = mapped_column(Integer, ForeignKey(user_status.c.id))

    # Default fastapi_users.db columns:
    email: Mapped[str] = mapped_column(String(length=320), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


currency = Table(
    "currency",
    metadata,
    Column("id", Integer, unique=True, primary_key=True, autoincrement=True),
    Column("request_date", TIMESTAMP, default=datetime.utcnow()),
    Column("requested_banks", ARRAY(String)),
    Column("request_source", String(50), default="UNKNOWN by default"),
    Column("currency_data", JSON),
    Column("user_id", Integer, ForeignKey(user.c.id), nullable=False),
)


async def add_currency_data(currency_data, user_id: int, session: AsyncSession):
    requested_banks = [bank for bank in currency_data]
    currency_data_json = json.dumps(currency_data)
    currency_instance = Currency(requested_banks=requested_banks, currency_data=currency_data_json, user_id=user_id)
    statement = insert(currency).values(**currency_instance.model_dump())
    await session.execute(statement)
    await session.commit()
    return "currency table was updated successfully"
