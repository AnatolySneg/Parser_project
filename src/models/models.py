from datetime import datetime

from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON

metadata = MetaData()

user_status = Table(
    "user_status",
    metadata,
    Column("id", Integer, primary_key=True),
    Column('name', String, nullable=False),
    Column("permissions", JSON),
)


user = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column('email', String, nullable=False),
    Column('phone_number', String, nullable=False),
    Column('username', String, nullable=False),
    Column('first_name', String(50)),
    Column('last_name', String(50)),
    Column("registered_at", TIMESTAMP, default=datetime.utcnow),
    Column("user_status_id", Integer, ForeignKey("user_status.id")),
)


