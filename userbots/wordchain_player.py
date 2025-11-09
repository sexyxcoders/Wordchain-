# wordchain_player.py — WordChain Telegram Userbot (fully human-like)
import asyncio
import random
import re
import os
import logging
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import config

# ────────────────────────────────
# Logging
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
# Load words
# ────────────────────────────────
def import_words(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [w.strip().lower() for w in f if w.strip()]
    except FileNotFoundError:
        log.error(f"❌ Word list not found: {path}")
        return []

# ────────────────────────────────
# Word selector
# ────────────────────────────────
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

# ────────────────────────────────
# Human-like typing and thinking
# ────────────────────────────────
def human_delay(word):
    base = random.uniform(0.8, 1.5)
    extra = min(len(word) * 0.12, 2.0)
    return base + extra

def maybe_typo(word, chance=0.15):
    if random.random() < chance and len(word) > 1:
        idx = random.randint(0, len(word) - 1)
        typo_char = random.choice("abcdefghijklmnopqrstuvwxyz")
        return word[:idx] + typo_char + word[idx + 1:]
    return word

async def simulate_thinking(client, chat_id):
    """Send temporary thinking messages like '…', '🤔', 'hmm…'"""
    thinking_messages = ["…", "🤔", "hmm…", "thinking…"]
    msg_text = random.choice(thinking_messages)
    try:
        msg = await client.send_message(chat_id, msg_text)
        await asyncio.sleep(random.uniform(0.5, 1.2))
        await client.delete_messages(chat_id, msg)
    except Exception:
        await asyncio.sleep(random.uniform(0.5, 1.2))

async def simulate_typing_and_send(client, chat_id, word, opponent_speed=None):
    """
    Simulate human-like typing with typos, corrections, thinking, and variable delays.
    """
    # Random hesitation
    if random.random() < 0.2:
        await asyncio.sleep(random.uniform(1.0, 2.0))

    # Reaction delay based on opponent speed
    if opponent_speed is not None:
        reaction_delay = min(max(0.5, 2.5 - opponent_speed), 2.0)
        await asyncio.sleep(reaction_delay)

    # Random thinking
    if random.random() < 0.3:
        await simulate_thinking(client, chat_id)

    # Decide typo
    word_to_send = maybe_typo(word)
    delay = human_delay(word_to_send)

    # Typing simulation
    try:
        async with client.action(chat_id, "typing"):
            if len(word_to_send) <= 3:
                await asyncio.sleep(delay + random.uniform(0.3, 0.8))
            else:
                await asyncio.sleep(delay)
    except Exception:
        await asyncio.sleep(delay)

    # If typo, send it first and delete
    if word_to_send != word:
        message = await client.send_message(chat_id, word_to_send)
        await asyncio.sleep(random.uniform(0.5, 1.2))
        try:
            await client.delete_messages(chat_id, message)
        except Exception:
            pass

    # Send correct word
    await client.send_message(chat_id, word)
    log.info(f"💬 Sent word in chat {chat_id}: {word}")

# ────────────────────────────────
# WordChain Game Logic
# ────────────────────────────────
async def start_game_logic(client, words):
    me = await client.get_me()
    my_first = (me.first_name or "").lower()
    my_username = (me.username or "").lower()
    log.info(f"🤖 Logged in as {me.first_name} (@{my_username})")

    banned_letters = []
    min_length = 3
    last_player_time = None

    @client.on(events.NewMessage)
    async def handler(event):
        nonlocal banned_letters, min_length, last_player_time

        text = event.raw_text or ""
        if not text:
            return
        lower = text.lower()
        chat_id = event.chat_id

        # Reset round
        if re.search(r"(new round|starting a new game|won the game)", lower):
            banned_letters.clear()
            last_player_time = None
            log.info(f"🔁 New round in chat {chat_id} — banned letters cleared.")
            return

        # Skip AFK or timeout
        if re.search(r"(skipped due to afk|no word given)", lower):
            await asyncio.sleep(1.5)
            return

        # Only react to turn messages
        if not re.search(r"(your word must start with|turn:|next:)", lower):
            return

        # Extract player names
        turn_match = re.search(r"turn:\s*([^(\n]+)", text, re.IGNORECASE)
        next_match = re.search(r"next:\s*([^(\n]+)", text, re.IGNORECASE)
        turn_name = turn_match.group(1).strip().lower() if turn_match else ""
        next_name = next_match.group(1).strip().lower() if next_match else ""

        turn_name = re.sub(r"[^\w@ ]+", "", turn_name)
        next_name = re.sub(r"[^\w@ ]+", "", next_name)

        is_my_turn = my_first in turn_name or (my_username and my_username in turn_name)
        is_next_turn = my_first in next_name or (my_username and my_username in next_name)
        if not is_my_turn or is_next_turn:
            last_player_time = asyncio.get_event_loop().time()
            return

        # Extract starting letter
        prefix_match = re.search(r"start[^A-Za-z]*with[^A-Za-z]*([A-Za-z])", text, re.IGNORECASE)
        if not prefix_match:
            return
        prefix = prefix_match.group(1).lower()

        # Minimum length
        len_match = re.search(r"at least\s*(\d+)\s*letters", text, re.IGNORECASE)
        if len_match:
            min_length = int(len_match.group(1))

        # Include letter
        include_match = re.search(r"include[^A-Za-z]*([A-Za-z])", text, re.IGNORECASE)
        include = include_match.group(1).lower() if include_match else ""

        # Banned letters
        if "banned letters" in lower:
            banned_letters = [b.lower() for b in re.findall(r"[A-Za-z]", text.split("Banned letters:")[-1])]
            log.info(f"🚫 Updated banned letters in chat {chat_id}: {banned_letters}")

        # Select a valid word
        word = get_word(words, prefix, include, banned_letters, min_length)
        if not word:
            log.warning(f"😕 No valid word found in chat {chat_id} for prefix '{prefix}'")
            return

        # Calculate opponent speed
        opponent_speed = None
        if last_player_time is not None:
            opponent_speed = asyncio.get_event_loop().time() - last_player_time

        await simulate_typing_and_send(client, chat_id, word, opponent_speed)
        last_player_time = asyncio.get_event_loop().time()

# ────────────────────────────────
# Userbot runner
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
    loop = asyncio.get_event_loop()
    loop.create_task(_start_userbot(session_string, user_id))