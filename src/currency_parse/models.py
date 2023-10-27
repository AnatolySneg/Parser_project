from datetime import datetime
from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, Date, ARRAY, JSON
from src.models.models import user

metadata = MetaData()

currency_requests = Table(
    "currency_requests",
    metadata,
    Column("id", Integer, unique=True, primary_key=True),
    Column("request_date", TIMESTAMP, default=datetime.utcnow()),
    Column("requested_banks", ARRAY(String, dimensions=30)),
    Column("request_source", String(50), default="UNKNOWN by default"),
    Column("currency_data", JSON),
    Column("user_id", Integer, ForeignKey(user.c.id), nullable=False),


)