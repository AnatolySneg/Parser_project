from conftest import client, async_session_maker
# from src.database import async_session_maker
from sqlalchemy import insert, select
from src.models.models import user_status


# def get_digit(value):
#     return value + 1
#
#
# def test_get_digit():
#     assert get_digit(5) == 6


async def test_add_user_status():
    async with async_session_maker() as session:
        stmt = insert(user_status).values(id=1, name="newbie")
        await session.execute(stmt)
        await session.commit()

        query = select(user_status)
        result = await session.execute(query)
        assert result.all() == [(1, 'newbie', None)], "Роль добавилась"


def test_register(ac):
    response = client.post(
        "/auth/register",
        json={
            "email": "user@example.com",
            "password": "string",
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
            "username": "VASILIJ",
            "user_status_id": 1
        }
    )

    # print(response.json())
    assert response.status_code == 201
    result = {
        'id': 1,
        'email': 'user@example.com',
        'is_active': True,
        'is_superuser': False,
        'is_verified': False,
        'username': 'VASILIJ',
        'user_status_id': 1
    }
    assert response.json() == result


def test_get_all_currency(ac):
    response = client.post(
        "/currency/get_all_course",
        json={
            "req_cur": {
                "USD": True,
                "EUR": True,
                "PLN": False,
                "GBP": False,
                "TRY": False,
                "CHF": False
            },
            "banks": {
                "national_bank": True,
                "mono_bank": True,
                "privat_bank": True
            }
        }
    )

    # print(response.status_code, '!' * 50)
    # print(response.json())
    # print(response.status_code, '!' * 50)
    # print(response.status_code, '!' * 50)

    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}





