import asyncio
import random
import re
import logging
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import config
from db_mongo import MongoDBSessionManager

db = MongoDBSessionManager()

log = logging.getLogger("wordchain_player")
log.setLevel(logging.INFO)

def import_words(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [w.strip().lower() for w in f if w.strip()]
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

def _extract_turn_id(text: str):
    m = re.search(r"Turn:\s*([^\n]+)", text, re.IGNORECASE)
    if not m:
        return None
    segment = m.group(1)
    digits = re.search(r"(\d{5,})", segment)
    if digits:
        try:
            return int(digits.group(1))
        except Exception:
            return None
    return None

async def start_game_logic(client, words):
    me = await client.get_me()
    my_id = me.id
    my_name = (me.first_name or "").strip().lower()
    log.info("Userbot running as %s (%s)", my_name, my_id)

    banned_letters = []
    min_length = 3
    target_chat = getattr(config, "WORDCHAIN_GROUP", None)

    @client.on(events.NewMessage(chats=target_chat))
    async def handler(event):
        nonlocal banned_letters, min_length
        text = event.raw_text or ""
        if not text:
            return
        if re.search(r"(won the game|new round|starting a new game)", text, re.IGNORECASE):
            banned_letters.clear()
            return
        if re.search(r"(skipped due to afk|no word given)", text, re.IGNORECASE):
            await asyncio.sleep(2)
            return

        turn_id = _extract_turn_id(text)
        if turn_id is not None:
            if turn_id != my_id:
                return
        else:
            if my_name and my_name not in text.lower():
                return

        if "banned letters" in text.lower():
            bl = re.findall(r"[A-Za-z]", text.split("Banned letters:")[-1])
            banned_letters[:] = [b.lower() for b in bl]

        m = re.search(r"at least\s*(\d+)\s*letters", text, re.IGNORECASE)
        if m:
            min_length = int(m.group(1))

        include_match = re.search(r"include[^A-Za-z]*([A-Za-z])", text, re.IGNORECASE)
        include = include_match.group(1).lower() if include_match else ""

        prefix_match = re.search(r"start[^A-Za-z]*with[^A-Za-z]*([A-Za-z])", text, re.IGNORECASE)
        if not prefix_match:
            return

        prefix = prefix_match.group(1).lower()
        word = get_word(words, prefix, include, banned_letters, min_length)
        if word:
            await asyncio.sleep(random.uniform(1.5, 3.0))
            try:
                await client.send_message(event.chat_id, word)
                log.info("Sent word %s", word)
            except Exception as e:
                log.warning("Failed to send: %s", e)
        else:
            log.info("No valid word for prefix '%s' include '%s'", prefix, include)

async def _start_userbot(session_string, user_id):
    client = TelegramClient(StringSession(session_string), config.API_ID, config.API_HASH)
    try:
        await client.start()
        me = await client.get_me()
        log.info("Started userbot for %s (%s)", me.first_name, me.id)

        words = import_words(config.WORDS_PATH)
        if not words:
            log.error("Empty words list; stopping")
            await client.disconnect()
            return

        await start_game_logic(client, words)
        await client.run_until_disconnected()
    except Exception as e:
        log.error("Error in userbot %s: %s", user_id, e)
    finally:
        try:
            await client.disconnect()
        except Exception:
            pass
        log.info("Userbot stopped for %s", user_id)

def start_userbot(session_string, user_id):
    loop = asyncio.get_event_loop()
    loop.create_task(_start_userbot(session_string, user_id))
