from conftest import async_session_maker
from sqlalchemy import insert, select
from src.models.models import user_status


class TestUser:
    async def test_add_user_status(self):
        async with async_session_maker() as session:
            stmt = insert(user_status).values(id=1, name="newbie")
            await session.execute(stmt)
            await session.commit()

            query = select(user_status)
            result = await session.execute(query)
            assert result.all() == [(1, 'newbie', None)], "Роль добавилась"

    async def test_register(self, ac):
        response = await ac.post(
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

    async def test_login(self, ac):
        response = await ac.post(
            "/auth/redis_strategy/login",
            data={
                "username": "user@example.com",
                "password": "string",
            }
        )

        header_string = response.headers["set-cookie"]
        header_split = header_string.split(";")
        cookie_header = header_split[0]
        ac.headers.update({"cookie": cookie_header})
        assert response.status_code == 204

    async def test_get_current_user(self, ac):
        response = await ac.get(
            "/users/me",
        )
        user = {
            'id': 1,
            'email': 'user@example.com',
            'is_active': True,
            'is_superuser': False,
            'is_verified': False,
            'username': 'VASILIJ',
            'user_status_id': 1
        }
        print("Printing test_get_current_user")
        assert response.json() == user
        assert response.status_code == 200

    async def test_get_all_currency(self, ac):
        some_data = {
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
            },
            "report": {
                "report": False
            }
        }

        response = await ac.post(
            "/currency/get_all_course",
            json=some_data,
        )
        print("check get currency")
        assert response.status_code == 200
