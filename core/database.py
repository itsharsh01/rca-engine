from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings

# Initialize Async MongoDB Client
client = AsyncIOMotorClient(settings.db_url)
db = client[settings.db_name]

def get_database():
    """
    Expose the active Motor MongoDB database instance.
    """
    return db
