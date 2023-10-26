from fastapi import APIRouter

router = APIRouter(
    prefix="/get_currency",
    tags=["Currency"]
)


@router.get("/")
async def get_currency():
    return



# ORM - Object-relational model
# SQL Injection
