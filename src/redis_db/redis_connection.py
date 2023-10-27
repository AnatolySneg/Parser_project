import redis
import redis.asyncio
from src.config import RADIS_HOST, RADIS_PORT

client = redis.Redis(host=RADIS_HOST, port=RADIS_PORT, decode_responses=True)


aio_redis = redis.asyncio.from_url(f"redis://{RADIS_HOST}:{RADIS_PORT}", decode_responses=True)
