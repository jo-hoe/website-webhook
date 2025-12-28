import logging
import os
from typing import Optional
from app.storage.state_storage import StateStorage
from app.storage.inmemory_storage import InMemoryStorage
from app.storage.redis_storage import RedisStorage


def create_storage(
    backend: Optional[str] = None,
    redis_host: Optional[str] = None,
    redis_port: Optional[int] = None,
    redis_db: Optional[int] = None,
    redis_password: Optional[str] = None,
    redis_key_prefix: Optional[str] = None
) -> StateStorage:
    """
    Factory function to create a state storage instance.
    
    Priority order for configuration:
    1. Function parameters
    2. Environment variables
    3. Defaults
    
    Args:
        backend: Storage backend type ("memory" or "redis")
        redis_host: Redis host address
        redis_port: Redis port number
        redis_db: Redis database number
        redis_password: Redis password
        redis_key_prefix: Key prefix for Redis isolation
        
    Returns:
        StateStorage instance
        
    Environment Variables:
        STORAGE_BACKEND: "memory" or "redis"
        REDIS_HOST: Redis host address
        REDIS_PORT: Redis port number
        REDIS_DB: Redis database number
        REDIS_PASSWORD: Redis password
        REDIS_KEY_PREFIX: Key prefix for isolation
    """
    # Determine backend from parameter or environment variable, default to memory
    backend = backend or os.getenv("STORAGE_BACKEND", "memory").lower()
    
    if backend == "redis":
        # Get Redis configuration with priority: parameter > env var > default
        host = redis_host or os.getenv("REDIS_HOST", "localhost")
        port = redis_port or int(os.getenv("REDIS_PORT", "6379"))
        db = redis_db if redis_db is not None else int(os.getenv("REDIS_DB", "0"))
        password = redis_password or os.getenv("REDIS_PASSWORD")
        key_prefix = redis_key_prefix or os.getenv("REDIS_KEY_PREFIX", "website-webhook")
        
        logging.info(f"Creating Redis storage: {host}:{port} (db={db}, prefix={key_prefix})")
        return RedisStorage(host=host, port=port, db=db, password=password, key_prefix=key_prefix)
    elif backend == "memory":
        logging.info("Creating in-memory storage")
        return InMemoryStorage()
    else:
        logging.warning(f"Unknown storage backend '{backend}', falling back to in-memory storage")
        return InMemoryStorage()
