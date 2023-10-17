from fastapi_users.authentication import CookieTransport, AuthenticationBackend

import redis.asyncio
from fastapi_users.authentication import RedisStrategy
from config import RADIS_HOST

cookie_transport = CookieTransport(cookie_name="currency", cookie_max_age=3600)

redis = redis.asyncio.from_url(RADIS_HOST, decode_responses=True)


def get_redis_strategy() -> RedisStrategy:
    return RedisStrategy(redis, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="redis_strat",
    transport=cookie_transport,
    get_strategy=get_redis_strategy,
)
