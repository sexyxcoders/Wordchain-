# db_mongo.py — Async MongoDB session manager (Motor) for WordChain per user/chat
import motor.motor_asyncio
import datetime
import config
import logging

log = logging.getLogger("db_mongo")


class MongoDBSessionManager:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(config.MONGO_URI)
        self.db = self.client[config.DB_NAME]
        self.sessions = self.db["sessions"]

    async def init_indexes(self):
        """Ensure unique index on (user_id, chat_id)."""
        try:
            await self.sessions.create_index(
                [("user_id", 1), ("chat_id", 1)], unique=True
            )
            log.info("✅ Index on (user_id, chat_id) ensured.")
        except Exception as e:
            log.error(f"⚠️ Failed to create index: {e}")

    async def save_session(
        self, user_id: int, chat_id: int, string_session: str
    ):
        """Save or update a user's string session in a chat."""
        now = datetime.datetime.utcnow()
        try:
            await self.sessions.update_one(
                {"user_id": user_id, "chat_id": chat_id},
                {
                    "$set": {
                        "string_session": string_session,
                        "updated_at": now,
                    },
                    "$setOnInsert": {"created_at": now},
                },
                upsert=True,
            )
            log.info(f"💾 Session saved for user {user_id} in chat {chat_id}")
        except Exception as e:
            log.error(f"⚠️ Failed to save session for user {user_id} in chat {chat_id}: {e}")

    async def get_session(self, user_id: int, chat_id: int) -> str | None:
        """Retrieve a user's string session in a chat."""
        try:
            doc = await self.sessions.find_one({"user_id": user_id, "chat_id": chat_id})
            return doc.get("string_session") if doc else None
        except Exception as e:
            log.error(f"⚠️ Failed to get session for user {user_id} in chat {chat_id}: {e}")
            return None

    async def delete_session(self, user_id: int, chat_id: int):
        """Delete a user's session in a chat."""
        try:
            result = await self.sessions.delete_one({"user_id": user_id, "chat_id": chat_id})
            if result.deleted_count:
                log.info(f"🗑️ Session deleted for user {user_id} in chat {chat_id}")
            else:
                log.warning(f"⚠️ No session found to delete for user {user_id} in chat {chat_id}")
        except Exception as e:
            log.error(f"⚠️ Failed to delete session for user {user_id} in chat {chat_id}: {e}")

    async def list_sessions(self) -> list[tuple[int, int]]:
        """List all (user_id, chat_id) with saved sessions."""
        try:
            sessions = await self.sessions.find({}, {"user_id": 1, "chat_id": 1}).to_list(None)
            return [(s["user_id"], s["chat_id"]) for s in sessions]
        except Exception as e:
            log.error(f"⚠️ Failed to list sessions: {e}")
            return []

    async def stats(self) -> tuple[int, int, int]:
        """Return (total sessions, new today, updated today)."""
        now = datetime.datetime.utcnow()
        start_of_day = datetime.datetime(now.year, now.month, now.day)
        try:
            total = await self.sessions.count_documents({})
            new_today = await self.sessions.count_documents({"created_at": {"$gte": start_of_day}})
            recon_today = await self.sessions.count_documents({"updated_at": {"$gte": start_of_day}})
            return total, new_today, recon_today
        except Exception as e:
            log.error(f"⚠️ Failed to get stats: {e}")
            return 0, 0, 0