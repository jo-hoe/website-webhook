from abc import ABC, abstractmethod
from typing import Optional


class StateStorage(ABC):
    """Abstract base class for state storage backends."""

    @abstractmethod
    def get(self, key: str) -> Optional[str]:
        """
        Retrieve a value from storage.
        
        Args:
            key: The storage key
            
        Returns:
            The stored value or None if not found
        """
        pass

    @abstractmethod
    def set(self, key: str, value: str) -> None:
        """
        Store a value.
        
        Args:
            key: The storage key
            value: The value to store
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """
        Delete a value from storage.
        
        Args:
            key: The storage key
        """
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """
        Check if a key exists in storage.
        
        Args:
            key: The storage key
            
        Returns:
            True if the key exists, False otherwise
        """
        pass
