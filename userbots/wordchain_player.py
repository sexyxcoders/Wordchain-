# userbots/wordchain_player.py
import asyncio
import random
import re
import logging
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import config

# Logging setup
log = logging.getLogger("wordchain_player")
log.setLevel(logging.INFO)

# ────────────────────────────────
# 📖 Word List Loader
# ────────────────────────────────
def import_words(path):
    """Load all words from the file into memory."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [w.strip().lower() for w in f if w.strip()]
    except FileNotFoundError:
        log.error("❌ words.txt not found!")
        return []


# ────────────────────────────────
# 🧩 Game Logic Helpers
# ────────────────────────────────
def get_word(dictionary, prefix, include="", banned=None, min_len=3):
    """Find a valid word based on rules."""
    banned = banned or []
    valid = [
        w for w in dictionary
        if w.startswith(prefix)
        and (not include or include in w)
        and all(bl not in w for bl in banned)
        and len(w) >= min_len
    ]
    return random.choice(valid) if valid else None


def extract_turn_id(text: str):
    """Try to extract a user ID or turn info from message text."""
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

    @client.on(events.NewMessage)  # Listens to all chats
    async def handler(event):
        nonlocal banned_letters, min_length
        text = event.raw_text or ""
        if not text:
            return

        # Detect reset/start messages
        if re.search(r"(new round|starting a new game|won the game)", text, re.IGNORECASE):
            banned_letters.clear()
            return

        # Skip AFK / invalid turns
        if re.search(r"(skipped due to afk|no word given)", text, re.IGNORECASE):
            await asyncio.sleep(2)
            return

        # Ignore irrelevant chats
        if "start with" not in text.lower():
            return

        # Detect if it’s our turn
        turn_id = extract_turn_id(text)
        if turn_id and turn_id != my_id:
            return
        if my_name not in text.lower() and not turn_id:
            return

        # Extract banned letters
        if "banned letters" in text.lower():
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
        word = get_word(words, prefix, include, banned_letters, min_length)
        if word:
            await asyncio.sleep(random.uniform(1.8, 3.5))  # mimic human delay
            try:
                await client.send_message(event.chat_id, word)
                log.info(f"💬 Sent word: {word}")
            except Exception as e:
                log.warning(f"⚠️ Failed to send: {e}")
        else:
            log.info(f"😕 No valid word found for prefix '{prefix}' (include '{include}')")


# ────────────────────────────────
# 🚀 Userbot Start Function
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