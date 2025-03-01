from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from app.config.settings import MONGO_URI, DB_NAME
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    async def connect_to_mongo(cls):
        """Connect to MongoDB."""
        if cls.client is None:
            try:
                cls.client = AsyncIOMotorClient(MONGO_URI)
                # Check if connection is valid
                await cls.client.admin.command('ping')
                cls.db = cls.client[DB_NAME]
                logger.info(f"Connected to MongoDB: {MONGO_URI}")
            except ConnectionFailure as e:
                logger.error(f"Failed to connect to MongoDB: {e}")
                raise

    @classmethod
    async def close_mongo_connection(cls):
        """Close MongoDB connection."""
        if cls.client is not None:
            cls.client.close()
            cls.client = None
            logger.info("Closed MongoDB connection")

    @classmethod
    def get_collection(cls, collection_name: str):
        """Get a MongoDB collection by name."""
        return cls.db[collection_name]

# Database collections
USERS_COLLECTION = "users"
