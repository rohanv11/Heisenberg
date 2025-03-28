from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import asyncpg
import logging
from app.config.settings import MONGO_URI, DB_NAME, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_HOST

# Get logger for this module
logger = logging.getLogger(__name__)

class DatabaseManager:
    mongo_client: AsyncIOMotorClient = None
    mongo_db = None

    @classmethod
    async def connect_to_mongo(cls):
        """Connect to MongoDB."""
        if cls.mongo_client is None:
            try:
                cls.mongo_client = AsyncIOMotorClient(MONGO_URI)
                # Check if connection is valid
                await cls.mongo_client.admin.command('ping')
                cls.mongo_db = cls.mongo_client[DB_NAME]
                logger.info(f"Connected to MongoDB: {MONGO_URI}")
            except ConnectionFailure as e:
                logger.error(f"Failed to connect to MongoDB: {e}")
                raise

    @classmethod
    async def close_mongo_connection(cls):
        """Close MongoDB connection."""
        if cls.mongo_client is not None:
            cls.mongo_client.close()
            cls.mongo_client = None
            logger.info("Closed MongoDB connection")

    @classmethod
    def get_collection(cls, collection_name: str):
        """Get a MongoDB collection by name."""
        return cls.mongo_db[collection_name]

# Database collections
USERS_COLLECTION = "users"

class PostgresManager:
    _pool = None

    @classmethod
    async def connect_to_postgres(cls):
        """Connect to PostgreSQL."""
        if cls._pool is None:
            try:
                cls._pool = await asyncpg.create_pool(
                    user=POSTGRES_USER,
                    password=POSTGRES_PASSWORD,
                    database=POSTGRES_DB,
                    host=POSTGRES_HOST
                )
                logger.info("Connected to PostgreSQL")
            except Exception as e:
                logger.error(f"Failed to connect to PostgreSQL: {e}")
                raise

    @classmethod
    async def close_postgres_connection(cls):
        """Close PostgreSQL connection."""
        if cls._pool is not None:
            await cls._pool.close()
            cls._pool = None
            logger.info("Closed PostgreSQL connection")

    @classmethod
    async def get_pool(cls):
        """Get the PostgreSQL connection pool."""
        if cls._pool is None:
            await cls.connect_to_postgres()
        return cls._pool
