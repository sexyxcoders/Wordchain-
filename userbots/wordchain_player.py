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
    """Load words into memory."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [w.strip().lower() for w in f if w.strip()]
    except FileNotFoundError:
        log.error("❌ words.txt not found!")
        return []


# ────────────────────────────────
# 🧩 Word Finder Helper
# ────────────────────────────────
def get_word(dictionary, prefix, include="", banned=None, min_len=3):
    """Find a valid word from dictionary based on prefix, include, and bans."""
    banned = banned or []
    valid = [
        w for w in dictionary
        if w.startswith(prefix)
        and (not include or include in w)
        and all(bl not in w for bl in banned)
        and len(w) >= min_len
    ]
    return random.choice(valid) if valid else None


# ────────────────────────────────
# 🎮 Wordchain Game Logic
# ────────────────────────────────
async def start_game_logic(client, words):
    me = await client.get_me()
    my_first = (me.first_name or "").lower()
    my_username = (me.username or "").lower()

    log.info(f"🤖 Active as {my_first} (@{my_username})")

    banned_letters = []
    min_length = 3

    @client.on(events.NewMessage)
    async def handler(event):
        nonlocal banned_letters, min_length

        text = event.raw_text or ""
        if not text:
            return

        lower = text.lower()

        # ───── Reset / Game Restart ─────
        if re.search(r"(new round|starting a new game|won the game)", lower):
            banned_letters.clear()
            log.info("🔁 New round detected, clearing used letters.")
            return

        # ───── Skip AFK/Timeout Messages ─────
        if re.search(r"(skipped due to afk|no word given)", lower):
            await asyncio.sleep(2)
            return

        # ───── Must be a valid turn message ─────
        if not re.search(r"(your word must start with|turn:|next:)", lower):
            return

        # ───── Extract Turn & Next player ─────
        turn_match = re.search(r"turn:\s*([^(\n]+)", text, re.IGNORECASE)
        next_match = re.search(r"next:\s*([^(\n]+)", text, re.IGNORECASE)

        turn_name = turn_match.group(1).strip().lower() if turn_match else ""
        next_name = next_match.group(1).strip().lower() if next_match else ""

        # Normalize text (remove emojis/stars)
        turn_name = re.sub(r"[^\w@ ]+", "", turn_name)
        next_name = re.sub(r"[^\w@ ]+", "", next_name)

        # ───── Determine if it's our turn ─────
        is_my_turn = (
            my_first in turn_name
            or (my_username and my_username in turn_name)
        )
        is_next_turn = (
            my_first in next_name
            or (my_username and my_username in next_name)
        )

        # 🚫 Ignore if it's not my turn or if I'm just "Next"
        if not is_my_turn or is_next_turn:
            return

        # ───── Extract prefix (start with letter) ─────
        prefix_match = re.search(r"start[^A-Za-z]*with[^A-Za-z]*([A-Za-z])", text, re.IGNORECASE)
        if not prefix_match:
            return
        prefix = prefix_match.group(1).lower()

        # ───── Extract minimum length ─────
        m = re.search(r"at least\s*(\d+)\s*letters", text, re.IGNORECASE)
        if m:
            min_length = int(m.group(1))

        # ───── Extract included letter (if any) ─────
        include_match = re.search(r"include[^A-Za-z]*([A-Za-z])", text, re.IGNORECASE)
        include = include_match.group(1).lower() if include_match else ""

        # ───── Extract banned letters ─────
        if "banned letters" in lower:
            bl = re.findall(r"[A-Za-z]", text.split("Banned letters:")[-1])
            banned_letters = [b.lower() for b in bl]
            log.info(f"🚫 Banned letters updated: {banned_letters}")

        # ───── Choose a valid word ─────
        word = get_word(words, prefix, include, banned_letters, min_length)
        if not word:
            log.info(f"😕 No valid word found for prefix '{prefix}' (include '{include}')")
            return

        # ───── Send word with human-like delay ─────
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
        log.info(f"🤖 Started userbot for {me.first_name} ({me.id})")

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
        log.info(f"🛑 Userbot stopped for {user_id}")


def start_userbot(session_string, user_id):
    """Safely start userbot in background."""
    loop = asyncio.get_event_loop()
    loop.create_task(_start_userbot(session_string, user_id))