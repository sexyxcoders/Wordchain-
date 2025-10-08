# db_mongo.py - synchronous pymongo-backed session manager with SQLite fallback
from pymongo import MongoClient, ASCENDING
import datetime
import sqlite3
import os
import config

class MongoDBSessionManager:
    def __init__(self):
        self.col = None
        try:
            self.client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=5000)
            self.db = self.client[config.DB_NAME]
            self.col = self.db.sessions
            self.col.create_index([("user_id", ASCENDING)], unique=True)
            print("✅ Connected to MongoDB (sync pymongo).")
        except Exception as e:
            print("⚠️ MongoDB connection failed, using SQLite fallback:", e)
            self._init_sqlite()

    def _init_sqlite(self):
        self.sqlite_path = config.DB_PATH or "sessions.db"
        self.conn = sqlite3.connect(self.sqlite_path, check_same_thread=False)
        cur = self.conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS sessions (user_id INTEGER PRIMARY KEY, session_text TEXT, created_at TIMESTAMP, updated_at TIMESTAMP)')
        self.conn.commit()

    def save_session(self, user_id, session_text):
        now = datetime.datetime.utcnow()
        if self.col is not None:
            self.col.update_one({"user_id": user_id}, {"$set": {"session": session_text, "updated_at": now}, "$setOnInsert": {"created_at": now}}, upsert=True)
            return
        # sqlite fallback
        cur = self.conn.cursor()
        cur.execute("REPLACE INTO sessions (user_id, session_text, created_at, updated_at) VALUES (?, ?, ?, ?)", (user_id, session_text, now, now))
        self.conn.commit()

    def get_session(self, user_id):
        if self.col is not None:
            doc = self.col.find_one({"user_id": user_id})
            return doc["session"] if doc else None
        cur = self.conn.cursor()
        cur.execute("SELECT session_text FROM sessions WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        return row[0] if row else None

    def delete_session(self, user_id):
        if self.col is not None:
            self.col.delete_one({"user_id": user_id})
            return
        cur = self.conn.cursor()
        cur.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
        self.conn.commit()

    def list_sessions(self):
        if self.col is not None:
            return [d["user_id"] for d in self.col.find({}, {"user_id": 1})]
        cur = self.conn.cursor()
        cur.execute("SELECT user_id FROM sessions")
        return [r[0] for r in cur.fetchall()]

    def stats(self):
        if self.col is not None:
            total = self.col.count_documents({})
            now = datetime.datetime.utcnow()
            start_of_day = datetime.datetime(now.year, now.month, now.day)
            new_today = self.col.count_documents({"created_at": {"$gte": start_of_day}})
            reconnected_today = self.col.count_documents({"updated_at": {"$gte": start_of_day}})
            return total, new_today, reconnected_today
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM sessions")
        total = cur.fetchone()[0]
        today = datetime.datetime.utcnow().date()
        start_of_today = datetime.datetime(today.year, today.month, today.day)
        cur.execute("SELECT COUNT(*) FROM sessions WHERE created_at >= ?", (start_of_today,))
        new_today = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM sessions WHERE updated_at >= ?", (start_of_today,))
        reconnected_today = cur.fetchone()[0]
        return total, new_today, reconnected_today
