from datetime import datetime

from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean

metadata = MetaData()

user_status = Table(
    "user_status",
    metadata,
    Column("id", Integer, unique=True, primary_key=True),
    Column('name', String, nullable=False),
    Column("permissions", JSON),
)
# TODO implement CoiceType from sqlalchemy-utils: https://sqlalchemy-utils.readthedocs.io/en/latest/data_types.html#module-sqlalchemy_utils.types.choice


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
