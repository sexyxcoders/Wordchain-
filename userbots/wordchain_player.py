import asyncio
import random
import re
import logging
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import config

log = logging.getLogger("wordchain_player")
log.setLevel(logging.INFO)

def import_words(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            words = [w.strip().lower() for w in f if w.strip()]
            log.info("Loaded %d words from %s", len(words), path)
            return words
    except FileNotFoundError:
        log.error("words.txt not found!")
        return []

def get_word(dictionary, prefix, include="", banned=None, min_len=3):
    banned = banned or []
    valid = [
        w for w in dictionary
        if w.startswith(prefix)
        and (not include or include in w)
        and all(bl not in w for bl in banned)
        and len(w) >= min_len
    ]
    return random.choice(valid) if valid else None

async def start_game_logic(client, words):
    me = await client.get_me()
    log.info("🎮 Wordchain logic started as %s (%s)", me.first_name, me.id)

    target_chat = config.WORDCHAIN_GROUP
    banned_letters = []
    min_length = 3

    @client.on(events.NewMessage(chats=target_chat))
    async def handler(event):
        text = event.raw_text or ""
        if not text:
            return
        print("📩 Group message:", text[:100])  # debug

        if re.search(r"(won the game|new round|starting a new game)", text, re.IGNORECASE):
            banned_letters.clear()
            return

        if re.search(r"(skipped due to afk|no word given)", text, re.IGNORECASE):
            await asyncio.sleep(2)
            return

        prefix_match = re.search(r"start[^A-Za-z]*with[^A-Za-z]*([A-Za-z])", text, re.IGNORECASE)
        if not prefix_match:
            return
        prefix = prefix_match.group(1).lower()

        include_match = re.search(r"include[^A-Za-z]*([A-Za-z])", text, re.IGNORECASE)
        include = include_match.group(1).lower() if include_match else ""

        bl_match = re.findall(r"[A-Za-z]", text.split("Banned letters:")[-1]) if "Banned letters:" in text else []
        banned_letters[:] = [b.lower() for b in bl_match]

        m = re.search(r"at least\s*(\d+)\s*letters", text, re.IGNORECASE)
        if m:
            min_length = int(m.group(1))

        word = get_word(words, prefix, include, banned_letters, min_length)
        if word:
            await asyncio.sleep(random.uniform(2, 4))
            try:
                await client.send_message(event.chat_id, word)
                print("✅ Sent:", word)
            except Exception as e:
                print("❌ Failed to send:", e)
        else:
            print("⚠️ No valid word for", prefix)

async def _start_userbot(session_string, user_id):
    client = TelegramClient(StringSession(session_string), config.API_ID, config.API_HASH)
    try:
        await client.start()
        me = await client.get_me()
        print(f"🤖 Started userbot for {me.first_name} ({me.id})")

        words = import_words(config.WORDS_PATH)
        if not words:
            print("❌ Empty words list; stopping userbot")
            return

        await start_game_logic(client, words)
        await client.run_until_disconnected()
    except Exception as e:
        print(f"🔥 Userbot error ({user_id}):", e)
    finally:
        await client.disconnect()
        print(f"🛑 Userbot stopped for {user_id}")

def start_userbot(session_string, user_id):
    asyncio.get_event_loop().create_task(_start_userbot(session_string, user_id))