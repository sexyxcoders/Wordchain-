# db_mongo.py — Async MongoDB session manager (Motor)
import motor.motor_asyncio
import datetime
import config

class MongoDBSessionManager:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(config.MONGO_URI)
        self.db = self.client[config.DB_NAME]
        self.sessions = self.db["sessions"]

    async def init_indexes(self):
        await self.sessions.create_index("user_id", unique=True)

    async def save_session(self, user_id: int, string_session: str):
        """Save or update a user's string session."""
        await self.sessions.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "string_session": string_session,
                    "updated_at": datetime.datetime.utcnow(),
                },
                "$setOnInsert": {"created_at": datetime.datetime.utcnow()},
            },
            upsert=True,
        )

    async def get_session(self, user_id: int):
        doc = await self.sessions.find_one({"user_id": user_id})
        return doc["string_session"] if doc else None

    async def delete_session(self, user_id: int):
        await self.sessions.delete_one({"user_id": user_id})

    async def list_sessions(self):
        users = await self.sessions.distinct("user_id")
        return users

    async def stats(self):
        now = datetime.datetime.utcnow()
        start_of_day = datetime.datetime(now.year, now.month, now.day)
        total = await self.sessions.count_documents({})
        new_today = await self.sessions.count_documents({"created_at": {"$gte": start_of_day}})
        recon_today = await self.sessions.count_documents({"updated_at": {"$gte": start_of_day}})
        return total, new_today, recon_today