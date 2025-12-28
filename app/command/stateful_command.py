from abc import abstractmethod
from typing import Optional
from app.command.command import Command
from app.scraper.scraper import Scraper
from app.storage.state_storage import StateStorage


class StatefulCommand(Command):
    """
    Base class for commands that require persistent state storage.
    
    Subclasses should use the provided storage methods to persist state
    across application restarts and share state across multiple replicas.
    """

    def __init__(self, kind: str, name: str, url: str, scraper: Scraper, storage: Optional[StateStorage] = None) -> None:
        """
        Initialize a stateful command.
        
        Args:
            kind: The command type/kind
            name: The command name (used as part of storage keys)
            url: The URL to scrape
            scraper: The scraper instance to use
            storage: Optional storage backend for state persistence
        """
        super().__init__(kind, name, url, scraper)
        self._storage = storage
        self._name = name

    def _get_state(self, key: str) -> Optional[str]:
        """
        Retrieve state from storage.
        
        Args:
            key: The state key (will be prefixed with command name)
            
        Returns:
            The stored value or None if not found
        """
        if self._storage:
            storage_key = f"command:{self._name}:{key}"
            return self._storage.get(storage_key)
        return None

    def _set_state(self, key: str, value: str) -> None:
        """
        Store state in storage.
        
        Args:
            key: The state key (will be prefixed with command name)
            value: The value to store
        """
        if self._storage:
            storage_key = f"command:{self._name}:{key}"
            self._storage.set(storage_key, value)

    def _delete_state(self, key: str) -> None:
        """
        Delete state from storage.
        
        Args:
            key: The state key (will be prefixed with command name)
        """
        if self._storage:
            storage_key = f"command:{self._name}:{key}"
            self._storage.delete(storage_key)

    def _state_exists(self, key: str) -> bool:
        """
        Check if state exists in storage.
        
        Args:
            key: The state key (will be prefixed with command name)
            
        Returns:
            True if the state exists, False otherwise
        """
        if self._storage:
            storage_key = f"command:{self._name}:{key}"
            return self._storage.exists(storage_key)
        return False

    @abstractmethod
    def execute(self) -> bool:
        """
        Execute the command.
        
        Returns:
            True if callback should be triggered, False otherwise
        """
        pass
