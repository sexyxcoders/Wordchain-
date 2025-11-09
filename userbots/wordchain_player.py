# userbots/wordchain_player.py
import asyncio
import random
import re
import json
import logging
from pathlib import Path
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import config

# ────────────────────────────────
# Logging setup
# ────────────────────────────────
log = logging.getLogger("wordchain_player")
log.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(levelname)s] %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)

# ────────────────────────────────
# File Paths
# ────────────────────────────────
USED_WORDS_FILE = Path("used_words.json")

# ────────────────────────────────
# 📖 Word List Loader
# ────────────────────────────────
def import_words(path):
    """Load all words from file into memory."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [w.strip().lower() for w in f if w.strip()]
    except FileNotFoundError:
        log.error("❌ words.txt not found!")
        return []

# ────────────────────────────────
# Persistent Used Words
# ────────────────────────────────
def load_used_words():
    if USED_WORDS_FILE.exists():
        try:
            return json.loads(USED_WORDS_FILE.read_text(encoding="utf-8"))
        except Exception as e:
            log.warning(f"⚠️ Failed to load used words: {e}")
    return {}

def save_used_words(data):
    try:
        USED_WORDS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        log.warning(f"⚠️ Failed to save used words: {e}")

# ────────────────────────────────
# 🧩 Game Logic Helpers
# ────────────────────────────────
def get_word(dictionary, prefix, include="", banned=None, min_len=3, used=None):
    """Find a valid word based on rules."""
    banned = banned or []
    used = used or set()
    valid = [
        w for w in dictionary
        if w.startswith(prefix)
        and (not include or include in w)
        and all(bl not in w for bl in banned)
        and len(w) >= min_len
        and w not in used
    ]
    return random.choice(valid) if valid else None

def extract_turn_id(text: str):
    """Try to extract a user ID from message text."""
    match = re.search(r"Turn:\s*(\d+)", text)
    return int(match.group(1)) if match else None

# ────────────────────────────────
# 🎮 Wordchain Game Automation
# ────────────────────────────────
async def start_game_logic(client, words):
    me = await client.get_me()
    my_id = me.id
    my_name = (me.first_name or "").lower()
    log.info("🤖 Userbot active: %s (%s)", my_name, my_id)

    banned_letters = []
    min_length = 3
    used_words_data = load_used_words()  # Persistent dictionary {chat_id: [words]}

    @client.on(events.NewMessage)
    async def handler(event):
        nonlocal banned_letters, min_length, used_words_data
        text = event.raw_text or ""
        if not text:
            return

        chat_id = str(event.chat_id)
        text_lower = text.lower()

        # Ensure used words for this chat exists
        if chat_id not in used_words_data:
            used_words_data[chat_id] = []

        # Reset on new round or win
        if re.search(r"(new round|starting a new game|won the game)", text_lower):
            banned_letters.clear()
            min_length = 3
            used_words_data[chat_id] = []
            save_used_words(used_words_data)
            return

        # Skip AFK / invalid messages
        if re.search(r"(skipped due to afk|no word given)", text_lower):
            await asyncio.sleep(2)
            return

        # Only process messages that mention "start with" or turn indicators
        if "start with" not in text_lower and "your turn" not in text_lower:
            return

        # Detect turn
        turn_id = extract_turn_id(text)
        if turn_id and turn_id != my_id:
            return  # Not our turn
        if not turn_id and my_name not in text_lower and "your turn" not in text_lower:
            return  # Not explicitly our turn

        # Extract banned letters
        if "banned letters" in text_lower:
            bl = re.findall(r"[A-Za-z]", text.split("Banned letters:")[-1])
            banned_letters = [b.lower() for b in bl]

        # Extract minimum length
        m = re.search(r"at least\s*(\d+)\s*letters", text, re.IGNORECASE)
        if m:
            min_length = int(m.group(1))

        # Extract included letter
        include_match = re.search(r"include[^A-Za-z]*([A-Za-z])", text, re.IGNORECASE)
        include = include_match.group(1).lower() if include_match else ""

        # Extract prefix
        prefix_match = re.search(r"start[^A-Za-z]*with[^A-Za-z]*([A-Za-z])", text, re.IGNORECASE)
        if not prefix_match:
            return
        prefix = prefix_match.group(1).lower()

        # Choose a valid word
        used_set = set(used_words_data[chat_id])
        word = get_word(words, prefix, include, banned_letters, min_length, used_set)
        if word:
            await asyncio.sleep(random.uniform(1.8, 3.5))  # human-like delay
            try:
                await client.send_message(event.chat_id, word)
                log.info(f"💬 Sent word: {word}")
                used_words_data[chat_id].append(word)
                save_used_words(used_words_data)
            except Exception as e:
                log.warning(f"⚠️ Failed to send word: {e}")
        else:
            log.info(f"😕 No valid word found for prefix '{prefix}' (include '{include}')")

# ────────────────────────────────
# 🚀 Userbot Start
# ────────────────────────────────
async def _start_userbot(session_string, user_id):
    client = TelegramClient(StringSession(session_string), config.API_ID, config.API_HASH)
    try:
        await client.start()
        me = await client.get_me()
        log.info("🤖 Started userbot for %s (%s)", me.first_name, me.id)

        words = import_words(config.WORDS_PATH)
        if not words:
            log.error("⚠️ Word list empty, stopping.")
            await client.disconnect()
            return

        await start_game_logic(client, words)
        await client.run_until_disconnected()
    except Exception as e:
        log.error(f"🔥 Userbot error ({user_id}): {e}")
    finally:
        try:
            await client.disconnect()
        except Exception:
            pass
        log.info("🛑 Userbot stopped for %s", user_id)

def start_userbot(session_string, user_id):
    """Launch userbot in background safely."""
    loop = asyncio.get_event_loop()
    loop.create_task(_start_userbot(session_string, user_id))
