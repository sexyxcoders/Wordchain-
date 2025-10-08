# bot.py - Pyrogram controller
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
import config
from db_mongo import MongoDBSessionManager
from userbots.wordchain_player import start_userbot

app = Client("tnc_controller", bot_token=config.BOT_TOKEN, api_id=config.API_ID, api_hash=config.API_HASH)
db = MongoDBSessionManager()

@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("👑 Owner", url=f"tg://user?id={config.OWNER_ID}")],
        [InlineKeyboardButton("📢 Channel", url=config.SUPPORT_CHANNEL),
         InlineKeyboardButton("💬 Support Chat", url=config.SUPPORT_CHAT)]
    ])
    caption = ("🤖 <b>TNC-WordChain Bot</b>\n\n"
               "Send /connect STRING to register your Telethon StringSession (keeps it private) and start your userbot.\n"
               "Use /disconnect to stop it.")
    try:
        await message.reply_photo(photo=config.START_IMAGE, caption=caption, reply_markup=buttons, parse_mode=ParseMode.HTML)
    except Exception:
        await message.reply_text(caption, reply_markup=buttons, parse_mode=ParseMode.HTML)

@app.on_message(filters.command("connect") & filters.private)
async def connect_cmd(client, message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply_text("⚠️ Please send your Telethon StringSession after /connect.\n\nExample:\n/connect STRING_HERE", parse_mode=ParseMode.HTML)
        return
    session_string = args[1].strip()
    user = message.from_user
    user_id = user.id

    db.save_session(user_id, session_string)
    await message.reply_text("✅ Session saved! Starting your userbot...", parse_mode=ParseMode.HTML)

    try:
        await client.send_message(config.LOG_GROUP_ID, f"🧾 <b>New Connection</b>\n👤 {user.first_name}\n🆔 <code>{user_id}</code>", parse_mode=ParseMode.HTML)
    except Exception as e:
        print("Log failed:", e)

    try:
        start_userbot(session_string, user_id)
        await message.reply_text("🤖 Your userbot is now active and ready to play WordChain!", parse_mode=ParseMode.HTML)
    except Exception as e:
        await message.reply_text(f"❌ Failed to start userbot.\nError: {e}", parse_mode=ParseMode.HTML)

@app.on_message(filters.command("disconnect"))
async def disconnect_cmd(client, message):
    user = message.from_user
    args = message.text.split()
    if user.id == config.OWNER_ID and len(args) > 1:
        try:
            target = int(args[1])
            db.delete_session(target)
            await message.reply_text(f"✅ Disconnected user {target}", parse_mode=ParseMode.HTML)
            await client.send_message(config.LOG_GROUP_ID, f"❌ Userbot disconnected by owner: {target}", parse_mode=ParseMode.HTML)
        except Exception:
            await message.reply_text("❌ Invalid user id", parse_mode=ParseMode.HTML)
        return
    if not db.get_session(user.id):
        await message.reply_text("⚠️ You have no active session.", parse_mode=ParseMode.HTML)
        return
    db.delete_session(user.id)
    await message.reply_text("🛑 Your userbot has been terminated.", parse_mode=ParseMode.HTML)
    try:
        await client.send_message(config.LOG_GROUP_ID, f"🧹 User disconnected: {user.id}", parse_mode=ParseMode.HTML)
    except Exception:
        pass

@app.on_message(filters.command("broadcast") & filters.user(config.OWNER_ID))
async def broadcast_cmd(client, message):
    if not message.reply_to_message:
        await message.reply_text("📢 Reply to a message to broadcast it to all connected users.", parse_mode=ParseMode.HTML)
        return
    users = db.list_sessions()
    sent = failed = 0
    for uid in users:
        try:
            await message.reply_to_message.copy(uid)
            sent += 1
        except Exception:
            failed += 1
    await message.reply_text(f"✅ Broadcast complete. Sent: {sent}, Failed: {failed}", parse_mode=ParseMode.HTML)

@app.on_message(filters.command("listusers") & filters.user(config.OWNER_ID))
async def listusers_cmd(client, message):
    users = db.list_sessions()
    if not users:
        await message.reply_text("📭 No connected users.", parse_mode=ParseMode.HTML)
        return
    lines = ["👥 <b>Connected Users:</b>\n"]
    for i, uid in enumerate(users, start=1):
        try:
            u = await client.get_users(uid)
            lines.append(f"{i}. {u.first_name or 'Unknown'} — <code>{uid}</code>")
        except Exception:
            lines.append(f"{i}. ❓ Unknown — <code>{uid}</code>")
    text = "\n".join(lines)
    for chunk in [text[i:i+4000] for i in range(0, len(text), 4000)]:
        await message.reply_text(chunk, parse_mode=ParseMode.HTML)

@app.on_message(filters.command("stats") & filters.user(config.OWNER_ID))
async def stats_cmd(client, message):
    total, new_today, recon = db.stats()
    await message.reply_text(f"📊 Total connected: {total}\n🆕 New today: {new_today}\n🔁 Reconnected today: {recon}", parse_mode=ParseMode.HTML)

def run():
    print("🚀 Starting controller bot...")
    app.run()
