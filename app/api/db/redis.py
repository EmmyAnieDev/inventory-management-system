import redis
from urllib.parse import urlparse

from config import config

redis_url = urlparse(config.REDIS_URL)

jti_blocklist = redis.Redis(
    host=redis_url.hostname,
    port=redis_url.port,
    db=int(redis_url.path.lstrip("/")),
    password=redis_url.password,
    decode_responses=True
)

def add_jti_to_blocklist(jti: str) -> None:
    """ Adds a JTI to the Redis blocklist with an expiration time. """
    jti_blocklist.set(name=jti, value="", ex=config.JTI_EXPIRY)

def jti_in_blocklist(jti: str) -> bool:
    """ Checks if a JTI exists in the Redis blocklist. """
    result = jti_blocklist.get(jti)
    return result is not None