from app.config.settings import STORAGE_BACKEND
from .storage_interface import Storage
from .memory_storage import MemoryStorage
from .postgres_storage import PostgresStorage

def get_storage() -> Storage:
    if STORAGE_BACKEND == 'postgres':
        return PostgresStorage()
    return MemoryStorage()
