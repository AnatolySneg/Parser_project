import redis
from config import RADIS_HOST, RADIS_PORT

r = redis.Redis(host=RADIS_HOST, port=RADIS_PORT, decode_responses=True)
