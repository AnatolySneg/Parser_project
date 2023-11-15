from fastapi_users.authentication import CookieTransport, AuthenticationBackend
from fastapi_users.authentication import RedisStrategy
from src.redis_db.redis_connection import aio_redis

cookie_transport = CookieTransport(cookie_name="currency", cookie_max_age=3600)


def get_redis_strategy() -> RedisStrategy:
    return RedisStrategy(aio_redis, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="redis_strat",
    transport=cookie_transport,
    get_strategy=get_redis_strategy,
)
