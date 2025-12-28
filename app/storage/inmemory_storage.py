import logging
from typing import Dict, Optional
from app.storage.state_storage import StateStorage


class InMemoryStorage(StateStorage):
    """In-memory implementation of state storage using a dictionary."""

    def __init__(self) -> None:
        self._storage: Dict[str, str] = {}
        logging.info("Initialized in-memory state storage")

    def get(self, key: str) -> Optional[str]:
        """Retrieve a value from in-memory storage."""
        return self._storage.get(key)

    def set(self, key: str, value: str) -> None:
        """Store a value in memory."""
        self._storage[key] = value

    def delete(self, key: str) -> None:
        """Delete a value from in-memory storage."""
        if key in self._storage:
            del self._storage[key]

    def exists(self, key: str) -> bool:
        """Check if a key exists in in-memory storage."""
        return key in self._storage
