import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "foodOrdering")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
products_collection = db["products"]

async def ping_database() -> None:
    await db.command("ping")
