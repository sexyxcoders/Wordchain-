# bot.py — TNC WordChain Controller Bot (Final Stable Version)
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
import config
from db_mongo import MongoDBSessionManager
from userbots.wordchain_player import start_userbot


# ────────────────────────────────
# 🚀 Initialize bot + database
# ────────────────────────────────
app = Client(
    "tnc_controller",
    bot_token=config.BOT_TOKEN,
    api_id=config.API_ID,
    api_hash=config.API_HASH
)
db = MongoDBSessionManager()


# ────────────────────────────────
# 🧩 Must-Join Channels
# ────────────────────────────────
MUST_JOIN_CHANNELS = [
    "https://t.me/Sxnpe",
    "https://t.me/TechNodeCoders"
]

# ────────────────────────────────
# 🏁 Start Command
# ────────────────────────────────
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    user_id = message.from_user.id

    # Show join verification panel
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 ᴊᴏɪɴ @Sxnpe", url=MUST_JOIN_CHANNELS[0])],
        [InlineKeyboardButton("📢 ᴊᴏɪɴ @TechNodeCoders", url=MUST_JOIN_CHANNELS[1])],
        [InlineKeyboardButton("✅ ɪ ᴊᴏɪɴᴇᴅ", callback_data="joined_check")]
    ])

    try:
        await message.reply_photo(
            photo=config.MUST_JOIN_IMAGE,
            caption=(
                "⚠️ <b>ʏᴏᴜ ᴍᴜꜱᴛ ᴊᴏɪɴ ᴏᴜʀ ᴏꜰꜰɪᴄɪᴀʟ ᴄʜᴀɴɴᴇʟꜱ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ʙᴏᴛ.</b>\n\n"
                "📢 @Sxnpe\n📢 @TechNodeCoders\n\n"
                "ᴀꜰᴛᴇʀ ᴊᴏɪɴɪɴɢ ʙᴏᴛʜ, ᴛᴀᴘ ‘ɪ ᴊᴏɪɴᴇᴅ’ ʙᴇʟᴏᴡ."
            ),
            reply_markup=buttons,
            parse_mode=ParseMode.HTML
        )
    except Exception:
        await message.reply_text(
            "⚠️ ᴘʟᴇᴀꜱᴇ ᴊᴏɪɴ @Sxnpe & @TechNodeCoders ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ʙᴏᴛ.",
            reply_markup=buttons,
            parse_mode=ParseMode.HTML
        )


# ────────────────────────────────
# 🔁 “I Joined” Button
# ────────────────────────────────
@app.on_callback_query(filters.regex("joined_check"))
async def joined_check(client, callback_query):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("👑 ᴏᴡɴᴇʀ", url=f"tg://user?id={config.OWNER_ID}")],
        [InlineKeyboardButton("📢 ᴄʜᴀɴɴᴇʟ", url=config.SUPPORT_CHANNEL),
         InlineKeyboardButton("💬 ꜱᴜᴘᴘᴏʀᴛ", url=config.SUPPORT_CHAT)]
    ])
    caption = (
        "🤖 <b>ᴛɴᴄ-ᴡᴏʀᴅᴄʜᴀɪɴ ʙᴏᴛ</b>\n\n"
        "ꜱᴇɴᴅ <code>/connect STRING</code> ᴛᴏ ʀᴇɢɪꜱᴛᴇʀ ʏᴏᴜʀ ᴛᴇʟᴇᴛʜᴏɴ ꜱᴛʀɪɴɢꜱᴇꜱꜱɪᴏɴ.\n"
        "ᴜꜱᴇ <code>/disconnect</code> ᴛᴏ ꜱᴛᴏᴘ ɪᴛ."
    )

    try:
        await callback_query.message.edit_caption(caption, reply_markup=buttons, parse_mode=ParseMode.HTML)
    except Exception:
        await callback_query.message.edit_text(caption, reply_markup=buttons, parse_mode=ParseMode.HTML)


# ────────────────────────────────
# 🔗 Connect / Disconnect
# ────────────────────────────────
@app.on_message(filters.command("connect") & filters.private)
async def connect_cmd(client, message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply_text(
            "⚠️ ᴘʟᴇᴀꜱᴇ ꜱᴇɴᴅ ʏᴏᴜʀ ᴛᴇʟᴇᴛʜᴏɴ ꜱᴛʀɪɴɢꜱᴇꜱꜱɪᴏɴ ᴀꜰᴛᴇʀ /connect.\n\nExample:\n/connect STRING_HERE",
            parse_mode=ParseMode.HTML
        )
        return

    session_string = args[1].strip()
    user = message.from_user
    user_id = user.id

    db.save_session(user_id, session_string)
    await message.reply_text("✅ ꜱᴇꜱꜱɪᴏɴ ꜱᴀᴠᴇᴅ! ꜱᴛᴀʀᴛɪɴɢ ʏᴏᴜʀ ᴜꜱᴇʀʙᴏᴛ...", parse_mode=ParseMode.HTML)

    try:
        await client.send_message(
            config.LOG_GROUP_ID,
            f"🧾 <b>ɴᴇᴡ ᴄᴏɴɴᴇᴄᴛɪᴏɴ</b>\n👤 {user.first_name}\n🆔 <code>{user_id}</code>",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        print(f"⚠️ Log error: {e}")

    try:
        await start_userbot(session_string, user_id)
        await message.reply_text("🤖 ʏᴏᴜʀ ᴜꜱᴇʀʙᴏᴛ ɪꜱ ɴᴏᴡ ᴀᴄᴛɪᴠᴇ!", parse_mode=ParseMode.HTML)
    except Exception as e:
        await message.reply_text(f"❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ꜱᴛᴀʀᴛ ᴜꜱᴇʀʙᴏᴛ.\nError: {e}", parse_mode=ParseMode.HTML)


@app.on_message(filters.command("disconnect"))
async def disconnect_cmd(client, message):
    user = message.from_user
    args = message.text.split()

    if user.id == config.OWNER_ID and len(args) > 1:
        target = int(args[1])
        db.delete_session(target)
        await message.reply_text(f"✅ ᴅɪꜱᴄᴏɴɴᴇᴄᴛᴇᴅ <code>{target}</code>", parse_mode=ParseMode.HTML)
        return

    if not db.get_session(user.id):
        await message.reply_text("⚠️ ɴᴏ ᴀᴄᴛɪᴠᴇ ꜱᴇꜱꜱɪᴏɴ ꜰᴏᴜɴᴅ.", parse_mode=ParseMode.HTML)
        return

    db.delete_session(user.id)
    await message.reply_text("🛑 ʏᴏᴜʀ ᴜꜱᴇʀʙᴏᴛ ʜᴀꜱ ʙᴇᴇɴ ᴛᴇʀᴍɪɴᴀᴛᴇᴅ.", parse_mode=ParseMode.HTML)


# ────────────────────────────────
# 📊 Admin Commands
# ────────────────────────────────
@app.on_message(filters.command("listusers") & filters.user(config.OWNER_ID))
async def listusers_cmd(client, message):
    users = db.list_sessions()
    if not users:
        await message.reply_text("📭 ɴᴏ ᴜꜱᴇʀꜱ ᴄᴏɴɴᴇᴄᴛᴇᴅ.", parse_mode=ParseMode.HTML)
        return

    msg = ["👥 <b>ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴜꜱᴇʀꜱ:</b>\n"]
    for i, uid in enumerate(users, start=1):
        try:
            u = await client.get_users(uid)
            msg.append(f"{i}. {u.first_name or 'Unknown'} — <code>{uid}</code>")
        except Exception:
            msg.append(f"{i}. ❓ Unknown — <code>{uid}</code>")
    await message.reply_text("\n".join(msg), parse_mode=ParseMode.HTML)


@app.on_message(filters.command("stats") & filters.user(config.OWNER_ID))
async def stats_cmd(client, message):
    total, new_today, recon = db.stats()
    await message.reply_text(
        f"📊 ᴛᴏᴛᴀʟ: {total}\n🆕 ᴛᴏᴅᴀʏ ɴᴇᴡ: {new_today}\n🔁 ʀᴇᴄᴏɴɴᴇᴄᴛᴇᴅ: {recon}",
        parse_mode=ParseMode.HTML
    )


@app.on_message(filters.command("broadcast") & filters.user(config.OWNER_ID))
async def broadcast_cmd(client, message):
    if not message.reply_to_message:
        await message.reply_text("📢 ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ʙʀᴏᴀᴅᴄᴀꜱᴛ.", parse_mode=ParseMode.HTML)
        return

    users = db.list_sessions()
    sent = failed = 0
    for uid in users:
        try:
            await message.reply_to_message.copy(uid)
            sent += 1
        except Exception:
            failed += 1
    await message.reply_text(f"✅ ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴅᴏɴᴇ.\n✔️ {sent}\n❌ {failed}", parse_mode=ParseMode.HTML)


# ────────────────────────────────
# 🟢 Run the Bot
# ────────────────────────────────
def run():
    print("🚀 ᴛɴᴄ ᴄᴏɴᴛʀᴏʟʟᴇʀ ʙᴏᴛ ᴄᴏɴɴᴇᴄᴛᴇᴅ!")
    app.run()