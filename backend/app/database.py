import os
from motor.motor_asyncio import AsyncIOMotorClient
from typing import AsyncGenerator

# MongoDB connection details
MONGO_DETAILS = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("MONGO_DB_NAME", "your_database_name")

client: AsyncIOMotorClient = None

async def connect_to_mongo():
    global client
    client = AsyncIOMotorClient(MONGO_DETAILS)
    print(f"Connected to MongoDB at {MONGO_DETAILS}")

async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("Closed MongoDB connection")

async def get_database() -> AsyncGenerator[AsyncIOMotorClient, None]:
    if client is None:
        await connect_to_mongo()
    yield client.get_database(DATABASE_NAME)
