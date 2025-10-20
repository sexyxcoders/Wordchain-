import os
from dotenv import load_dotenv

# Load .env for local testing (ignored on Heroku)
load_dotenv()

# ─────────────────────────────
# 🤖 Telegram Bot Configuration
# ─────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
API_ID = int(os.getenv("API_ID", "29308061"))
API_HASH = os.getenv("API_HASH", "462de3dfc98fd938ef9c6ee31a72d099")

# ─────────────────────────────
# 🗄️ Database
# ─────────────────────────────
MONGO_URI = os.getenv("MONGO_URI", "")
DB_NAME = os.getenv("DB_NAME", "TNCWordChain")
DB_PATH = os.getenv("DB_PATH", "sessions.db")

# ─────────────────────────────
# 📚 Words Configuration
# ─────────────────────────────
WORDS_PATH = os.getenv("WORDS_PATH", "words.txt")

# ─────────────────────────────
# 👑 Owner & Support
# ─────────────────────────────
OWNER_ID = int(os.getenv("OWNER_ID", "8492095841"))
SUPPORT_CHAT = os.getenv("SUPPORT_CHAT", "https://t.me/TNCmeetup")
SUPPORT_CHANNEL = os.getenv("SUPPORT_CHANNEL", "https://t.me/TechNodeCoders")

# ─────────────────────────────
# 🧾 Logs & Media
# ─────────────────────────────
LOG_GROUP_ID = os.getenv("LOG_GROUP_ID", "@Datauserbotx")
try:
    if LOG_GROUP_ID.lstrip("@").isdigit():
        LOG_GROUP_ID = int(LOG_GROUP_ID)
except Exception:
    pass

START_IMAGE = os.getenv("START_IMAGE", "assets/start_banner.jpg")
MUST_JOIN_IMAGE = os.getenv("MUST_JOIN_IMAGE", "https://files.catbox.moe/mibomi.jpg")

# ─────────────────────────────
# 📢 Must Join Channels
# ─────────────────────────────
MUST_JOIN = [
    "https://t.me/TechNodeCoders",
    "https://t.me/Sxnpe"
]