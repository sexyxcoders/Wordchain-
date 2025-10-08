import os
from dotenv import load_dotenv

# Load .env file if exists (useful for local testing)
load_dotenv()

# ─────────────────────────────
# 🔧 Telegram Bot Configuration
# ─────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
API_ID = int(os.getenv("API_ID", "29308061"))
API_HASH = os.getenv("API_HASH", "462de3dfc98fd938ef9c6ee31a72d099")

# ─────────────────────────────
# 🗄️ Database
# ─────────────────────────────
MONGO_URI = os.getenv("MONGO_URI", "")
DB_NAME = os.getenv("DB_NAME", "")
DB_PATH = os.getenv("DB_PATH", "sessions.db")

# ─────────────────────────────
# 📚 Wordchain Configuration
# ─────────────────────────────
WORDS_PATH = os.getenv("WORDS_PATH", "words.txt")
WORDCHAIN_GROUP = os.getenv("WORDCHAIN_GROUP", "-1001234567890")
try:
    # Convert if numeric
    if WORDCHAIN_GROUP.lstrip("-").isdigit():
        WORDCHAIN_GROUP = int(WORDCHAIN_GROUP)
except Exception:
    pass

# ─────────────────────────────
# 👑 Owner & Support
# ─────────────────────────────
OWNER_ID = int(os.getenv("OWNER_ID", "8157752411"))
SUPPORT_CHAT = os.getenv("SUPPORT_CHAT", "https://t.me/TNCmeetup")
SUPPORT_CHANNEL = os.getenv("SUPPORT_CHANNEL", "https://t.me/TechNodeCoders")

# ─────────────────────────────
# 🧾 Logs & Media
# ─────────────────────────────
LOG_GROUP_ID = os.getenv("LOG_GROUP_ID", "Datauserbotx")
# Handle both @username or numeric ID
try:
    if LOG_GROUP_ID.lstrip("@").isdigit():
        LOG_GROUP_ID = int(LOG_GROUP_ID)
except Exception:
    pass

START_IMAGE = os.getenv("START_IMAGE", "assets/start_banner.jpg")
MUST_JOIN_IMAGE = os.getenv("MUST_JOIN_IMAGE", "https://files.catbox.moe/sdlf66.jpg")

# ─────────────────────────────
# 📢 Must Join Channels
# ─────────────────────────────
MUST_JOIN = [
    "https://t.me/TechNodeCoders",
    "https://t.me/Sxnpe"
]

# ─────────────────────────────
# ✅ Debug Print (optional)
# ─────────────────────────────
if __name__ == "__main__":
    print("✅ Config loaded successfully!")
    print("LOG_GROUP_ID →", LOG_GROUP_ID)
    print("WORDCHAIN_GROUP →", WORDCHAIN_GROUP)