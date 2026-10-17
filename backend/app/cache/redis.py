import logging
import redis
from app.config import settings

logger = logging.getLogger(__name__)

_raw_client = redis.Redis.from_url(
    settings.redis_url,
    decode_responses=True,
    socket_timeout=2.0,
    socket_connect_timeout=2.0,
)


class ResilientRedis:
    """
    Resilient Redis client wrapper providing graceful degradation.
    If Redis is down or unreachable, operations log a warning and fallback safely
    without crashing the caller (PostgreSQL fallback for reads).
    """

    def __init__(self, client: redis.Redis):
        self._client = client

    def get(self, key: str):
        try:
            return self._client.get(key)
        except (redis.RedisError, OSError) as exc:
            logger.warning("Redis GET failed for %s, degrading to DB fallback: %s", key, exc)
            return None

    def set(self, key: str, value: str, ex=None, nx=False):
        try:
            return self._client.set(key, value, ex=ex, nx=nx)
        except (redis.RedisError, OSError) as exc:
            logger.warning("Redis SET failed for %s: %s", key, exc)
            # If nx=True was requested, caller expects a boolean claim result
            return False if nx else None

    def delete(self, *keys):
        try:
            return self._client.delete(*keys)
        except (redis.RedisError, OSError) as exc:
            logger.warning("Redis DELETE failed for %s: %s", keys, exc)
            return 0

    def ping(self) -> bool:
        try:
            return bool(self._client.ping())
        except Exception:
            return False


redis_client = ResilientRedis(_raw_client)