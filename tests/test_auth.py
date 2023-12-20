import json

from conftest import client, async_session_maker
# from src.database import async_session_maker
from sqlalchemy import insert, select
from src.models.models import user_status
import pytest
from httpx import AsyncClient


@pytest.fixture(scope="session")  # `"function"`` (default), ``"class"``, ``"module"``, ``"package"`` or ``"session"``
async def authenticated_client(ac: AsyncClient):
    data_register = {
        "email": "user@example.com",
        "password": "string",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
        "username": "VASILIJ",
        "user_status_id": 1
    }
    await ac.post("/auth/register",
                  json=data_register)

    data_login = {
        "username": data_register["email"],
        "password": data_register["password"],
    }

    response = await ac.post("/auth/redis_strategy/login",
                             data=data_login)
    token = response.json()
    ac.cookies["currency"] = f'cookie {token["access_token"]}'
    yield ac


# def get_digit(value):
#     return value + 1
#
#
# def test_get_digit():
#     assert get_digit(5) == 6


# async def test_add_user_status():
#     async with async_session_maker() as session:
#         stmt = insert(user_status).values(id=1, name="newbie")
#         await session.execute(stmt)
#         await session.commit()
#
#         query = select(user_status)
#         result = await session.execute(query)
#         assert result.all() == [(1, 'newbie', None)], "Роль добавилась"


# def test_register(ac):
#     response = client.post(
#         "/auth/register",
#         json={
#             "email": "user@example.com",
#             "password": "string",
#             "is_active": True,
#             "is_superuser": False,
#             "is_verified": False,
#             "username": "VASILIJ",
#             "user_status_id": 1
#         }
#     )
#
#     # print(response.json())
#     assert response.status_code == 201
#     result = {
#         'id': 1,
#         'email': 'user@example.com',
#         'is_active': True,
#         'is_superuser': False,
#         'is_verified': False,
#         'username': 'VASILIJ',
#         'user_status_id': 1
#     }
#     assert response.json() == result


def test_get_all_currency(authenticated_client):
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
                "national_bank": False,
                "mono_bank": False,
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


class TestUser:
    async def test_add_user_status(self):
        async with async_session_maker() as session:
            stmt = insert(user_status).values(id=1, name="newbie")
            await session.execute(stmt)
            await session.commit()

            query = select(user_status)
            result = await session.execute(query)
            assert result.all() == [(1, 'newbie', None)], "Роль добавилась"

    def test_register(self, ac):
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

    # def test_get_all_currency(self, ac):
    #     response = client.post(
    #         "/currency/get_all_course",
    #         json={
    #             'national_bank': False,
    #             'mono_bank': False,
    #             'privat_bank': True,
    #             'USD': True,
    #             'EUR': True,
    #             'CHF': False,
    #             'GBP': False,
    #             'PLN': False,
    #             'TRY': False,
    #             'report': False,
    #             'id': 1,
    #             "email": "user@example.com",
    #             "is_active": True,
    #             "is_superuser": False,
    #             "is_verified": False,
    #             "username": "VASILIJ",
    #             "user_status_id": 1
    #
    #         }
    #     )
    #     assert response.status_code == 200

    def test_login(self, ac):
        body = {
            "username": "user@example.com",
            "password": "string",
            "client_id": "None",
            "client_secret": "None",
            "grant_type": "None",
            "scope": [],
        }
        response = client.post(
            "/auth/redis_strategy/login",
            data={
                "username": "user@example.com",
                "password": "string",
            }
        )
        assert response.status_code == 204
    # result = {
    #     'id': 1,
    #     'email': 'user@example.com',
    #     'is_active': True,
    #     'is_superuser': False,
    #     'is_verified': False,
    #     'username': 'VASILIJ',
    #     'user_status_id': 1
    # }
    # assert response.json() == result
