import pytest
from app.storage.inmemory_storage import InMemoryStorage
from app.storage.storage_factory import create_storage


def test_inmemory_storage_set_and_get():
    """Test setting and getting values in in-memory storage."""
    storage = InMemoryStorage()
    
    storage.set("test_key", "test_value")
    assert storage.get("test_key") == "test_value"


def test_inmemory_storage_get_nonexistent():
    """Test getting a non-existent key returns None."""
    storage = InMemoryStorage()
    
    assert storage.get("nonexistent") is None


def test_inmemory_storage_exists():
    """Test checking if a key exists."""
    storage = InMemoryStorage()
    
    assert not storage.exists("test_key")
    storage.set("test_key", "value")
    assert storage.exists("test_key")


def test_inmemory_storage_delete():
    """Test deleting a key."""
    storage = InMemoryStorage()
    
    storage.set("test_key", "value")
    assert storage.exists("test_key")
    
    storage.delete("test_key")
    assert not storage.exists("test_key")


def test_inmemory_storage_delete_nonexistent():
    """Test deleting a non-existent key doesn't raise error."""
    storage = InMemoryStorage()
    
    storage.delete("nonexistent")  # Should not raise


def test_inmemory_storage_overwrite():
    """Test overwriting an existing value."""
    storage = InMemoryStorage()
    
    storage.set("test_key", "value1")
    assert storage.get("test_key") == "value1"
    
    storage.set("test_key", "value2")
    assert storage.get("test_key") == "value2"


def test_storage_factory_creates_memory_by_default():
    """Test factory creates in-memory storage by default."""
    storage = create_storage()
    
    assert isinstance(storage, InMemoryStorage)


def test_storage_factory_creates_memory_explicitly():
    """Test factory creates in-memory storage when specified."""
    storage = create_storage(backend="memory")
    
    assert isinstance(storage, InMemoryStorage)


def test_storage_factory_unknown_backend_fallback():
    """Test factory falls back to in-memory for unknown backend."""
    storage = create_storage(backend="unknown")
    
    assert isinstance(storage, InMemoryStorage)


def test_command_state_persistence():
    """Test that command state persists across multiple operations."""
    storage = InMemoryStorage()
    
    # Simulate command storing previous and current values
    storage.set("command:test:previous", "old_value")
    storage.set("command:test:current", "new_value")
    
    assert storage.get("command:test:previous") == "old_value"
    assert storage.get("command:test:current") == "new_value"
    
    # Simulate updating values
    current_value = storage.get("command:test:current")
    if current_value:
        storage.set("command:test:previous", current_value)
    storage.set("command:test:current", "newer_value")
    
    assert storage.get("command:test:previous") == "new_value"
    assert storage.get("command:test:current") == "newer_value"
