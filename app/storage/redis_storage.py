import logging
import redis
from typing import Optional
from app.storage.state_storage import StateStorage


class RedisStorage(StateStorage):
    """Redis implementation of state storage."""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, 
                 password: Optional[str] = None, key_prefix: str = "website-webhook") -> None:
        """
        Initialize Redis storage.
        
        Args:
            host: Redis host address
            port: Redis port number
            db: Redis database number
            password: Optional Redis password
            key_prefix: Prefix for all keys to isolate multiple applications
        """
        self._key_prefix = key_prefix
        self._redis = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        
        # Test connection
        try:
            self._redis.ping()
            logging.info(f"Initialized Redis state storage at {host}:{port} (db={db}, prefix={key_prefix})")
        except Exception as e:
            logging.error(f"Failed to connect to Redis at {host}:{port}: {e}")
            raise ConnectionError(f"Could not connect to Redis: {e}")

    def _prefixed_key(self, key: str) -> str:
        """Add prefix to key for isolation."""
        return f"{self._key_prefix}:{key}"

    def get(self, key: str) -> Optional[str]:
        """Retrieve a value from Redis."""
        try:
            prefixed_key = self._prefixed_key(key)
            value = self._redis.get(prefixed_key)
            return value if value is not None else None
        except Exception as e:
            logging.error(f"Error getting key '{key}' from Redis: {e}")
            raise

    def set(self, key: str, value: str) -> None:
        """Store a value in Redis."""
        try:
            prefixed_key = self._prefixed_key(key)
            self._redis.set(prefixed_key, value)
        except Exception as e:
            logging.error(f"Error setting key '{key}' in Redis: {e}")
            raise

    def delete(self, key: str) -> None:
        """Delete a value from Redis."""
        try:
            prefixed_key = self._prefixed_key(key)
            self._redis.delete(prefixed_key)
        except Exception as e:
            logging.error(f"Error deleting key '{key}' from Redis: {e}")
            raise

    def exists(self, key: str) -> bool:
        """Check if a key exists in Redis."""
        try:
            prefixed_key = self._prefixed_key(key)
            return bool(self._redis.exists(prefixed_key))
        except Exception as e:
            logging.error(f"Error checking existence of key '{key}' in Redis: {e}")
            raise
