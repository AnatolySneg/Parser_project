import redis
from config import RADIS_HOST, RADIS_PORT

client = redis.Redis(host=RADIS_HOST, port=RADIS_PORT, decode_responses=True)
