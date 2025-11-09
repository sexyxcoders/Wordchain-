import asyncio
import random
import re
import os
import logging
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import config


# ────────────────────────────────
# 🧾 Setup Logging (console + file)
# ────────────────────────────────
os.makedirs("logs", exist_ok=True)
LOG_FILE = "logs/wordchain.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

log = logging.getLogger("wordchain_player")


# ────────────────────────────────
# 📖 Load Word List
# ────────────────────────────────
def import_words(path):
    """Load valid words into memory."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [w.strip().lower() for w in f if w.strip()]
    except FileNotFoundError:
        log.error(f"❌ Word list not found: {path}")
        return []


# ────────────────────────────────
# 🧩 Word Selector (avoids repeats)
# ────────────────────────────────
def get_word(dictionary, prefix, include="", banned=None, min_len=3, used_words=None):
    """Select a word that fits all game rules and hasn't been used yet."""
    banned = banned or []
    used_words = used_words or set()
    
    valid = [
        w for w in dictionary
        if w.startswith(prefix)
        and (not include or include in w)
        and all(bl not in w for bl in banned)
        and len(w) >= min_len
        and w not in used_words
    ]
    
    return random.choice(valid) if valid else None


# ────────────────────────────────
# 🎮 WordChain Game Logic
# ────────────────────────────────
async def start_game_logic(client, words):
    me = await client.get_me()
    my_first = (me.first_name or "").lower()
    my_username = (me.username or "").lower()
    log.info(f"🤖 Logged in as {me.first_name} (@{my_username})")

    banned_letters = []
    used_words = set()
    min_length = 3

    @client.on(events.NewMessage)
    async def handler(event):
        nonlocal banned_letters, min_length, used_words

        text = event.raw_text or ""
        if not text:
            return
        lower = text.lower()

        # ───── Game Reset ─────
        if re.search(r"(new round|starting a new game|won the game)", lower):
            banned_letters.clear()
            used_words.clear()
            log.info("🔁 New round detected — banned letters and used words reset.")
            return

        # ───── Skip AFK or Timeout ─────
        if re.search(r"(skipped due to afk|no word given)", lower):
            await asyncio.sleep(2)
            return

        # ───── Only react to turn messages ─────
        if not re.search(r"(your word must start with|turn:|next:)", lower):
            return

        # ───── Extract player names ─────
        turn_match = re.search(r"turn:\s*([^(\n]+)", text, re.IGNORECASE)
        next_match = re.search(r"next:\s*([^(\n]+)", text, re.IGNORECASE)
        turn_name = turn_match.group(1).strip().lower() if turn_match else ""
        next_name = next_match.group(1).strip().lower() if next_match else ""

        # Clean names (remove emojis, symbols)
        turn_name = re.sub(r"[^\w@ ]+", "", turn_name)
        next_name = re.sub(r"[^\w@ ]+", "", next_name)

        # Determine if it's our turn
        is_my_turn = my_first in turn_name or (my_username and my_username in turn_name)
        is_next_turn = my_first in next_name or (my_username and my_username in next_name)

        # Skip if not our turn
        if not is_my_turn or is_next_turn:
            return

        # ───── Extract starting letter ─────
        prefix_match = re.search(r"start[^A-Za-z]*with[^A-Za-z]*([A-Za-z])", text, re.IGNORECASE)
        if not prefix_match:
            return
        prefix = prefix_match.group(1).lower()

        # ───── Extract minimum length ─────
        len_match = re.search(r"at least\s*(\d+)\s*letters", text, re.IGNORECASE)
        if len_match:
            min_length = int(len_match.group(1))

        # ───── Extract included letter (optional) ─────
        include_match = re.search(r"include[^A-Za-z]*([A-Za-z])", text, re.IGNORECASE)
        include = include_match.group(1).lower() if include_match else ""

        # ───── Extract banned letters ─────
        if "banned letters" in lower:
            banned_letters = [b.lower() for b in re.findall(r"[A-Za-z]", text.split("Banned letters:")[-1])]
            log.info(f"🚫 Updated banned letters: {banned_letters}")

        # ───── Select a valid word ─────
        word = get_word(words, prefix, include, banned_letters, min_length, used_words)
        if not word:
            log.warning(f"😕 No valid word found for prefix '{prefix}' (include '{include}')")
            return

        used_words.add(word)  # mark word as used

        # ───── Send word with delay ─────
        await asyncio.sleep(random.uniform(1.8, 3.8))
        try:
            await client.send_message(event.chat_id, word)
            log.info(f"💬 Sent word: {word}")
        except Exception as e:
            log.warning(f"⚠️ Failed to send: {e}")


# ────────────────────────────────
# 🚀 Userbot Runner
# ────────────────────────────────
async def _start_userbot(session_string, user_id):
    client = TelegramClient(StringSession(session_string), config.API_ID, config.API_HASH)
    try:
        await client.start()
        me = await client.get_me()
        log.info(f"✅ Userbot started: {me.first_name} ({me.id})")

        words = import_words(config.WORDS_PATH)
        if not words:
            log.error("⚠️ Word list is empty, shutting down userbot.")
            await client.disconnect()
            return

        await start_game_logic(client, words)
        await client.run_until_disconnected()

    except Exception as e:
        log.error(f"🔥 Error for user {user_id}: {e}")
    finally:
        try:
            await client.disconnect()
        except Exception:
            pass
        log.info(f"🛑 Userbot stopped for {user_id}")


def start_userbot(session_string, user_id):
    """Run userbot in background safely."""
    loop = asyncio.get_event_loop()
    loop.create_task(_start_userbot(session_string, user_id))