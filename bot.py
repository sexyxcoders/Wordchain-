# bot.py — TNC-WordChain Controller Bot
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from pyrogram.errors import UserNotParticipant
import config
from db_mongo import MongoDBSessionManager
from userbots.wordchain_player import start_userbot


# Initialize bot and database
app = Client("tnc_controller", bot_token=config.BOT_TOKEN, api_id=config.API_ID, api_hash=config.API_HASH)
db = MongoDBSessionManager()


# ────────────────────────────────
# 🔒 Must-Join Verification
# ────────────────────────────────
async def check_membership(client, user_id):
    """Ensure the user joined required channels."""
    for link in config.MUST_JOIN:
        chat = link.split("/")[-1]
        try:
            member = await client.get_chat_member(chat, user_id)
            if member.status in ("left", "kicked"):
                return False
        except UserNotParticipant:
            return False
        except Exception as e:
            print(f"⚠️ Membership check failed for {chat}: {e}")
            return False
    return True


@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    user_id = message.from_user.id

    # Must-join verification
    if not await check_membership(client, user_id):
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=config.MUST_JOIN[0])],
            [InlineKeyboardButton("✅ ɪ ᴊᴏɪɴᴇᴅ", callback_data="joined_check")]
        ])
        try:
            await message.reply_photo(
                photo=config.MUST_JOIN_IMAGE,
                caption=(
                    "⚠️ <b>ʏᴏᴜ ᴍᴜꜱᴛ ᴊᴏɪɴ ᴏᴜʀ ᴏꜰꜰɪᴄɪᴀʟ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ʙᴏᴛ.</b>\n\n"
                    f"📢 <a href='{config.MUST_JOIN[0]}'>@TechNodeCoders</a>\n\n"
                    "ᴀꜰᴛᴇʀ ᴊᴏɪɴɪɴɢ, ᴛᴀᴘ ‘ɪ ᴊᴏɪɴᴇᴅ’ ʙᴇʟᴏᴡ."
                ),
                reply_markup=buttons,
                parse_mode=ParseMode.HTML
            )
        except Exception:
            await message.reply_text(
                "⚠️ ʏᴏᴜ ᴍᴜꜱᴛ ᴊᴏɪɴ @TechNodeCoders ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ʙᴏᴛ.\nᴀꜰᴛᴇʀ ᴊᴏɪɴɪɴɢ, ᴛᴀᴘ ‘ɪ ᴊᴏɪɴᴇᴅ’.",
                reply_markup=buttons,
                parse_mode=ParseMode.HTML
            )
        return

    # Normal start message
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("👑 ᴏᴡɴᴇʀ", url=f"tg://user?id={config.OWNER_ID}")],
        [InlineKeyboardButton("📢 ᴄʜᴀɴɴᴇʟ", url=config.SUPPORT_CHANNEL),
         InlineKeyboardButton("💬 ꜱᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ", url=config.SUPPORT_CHAT)]
    ])
    caption = (
        "🤖 <b>ᴛɴᴄ-ᴡᴏʀᴅᴄʜᴀɪɴ ʙᴏᴛ</b>\n\n"
        "ꜱᴇɴᴅ <code>/connect STRING</code> ᴛᴏ ʀᴇɢɪꜱᴛᴇʀ ʏᴏᴜʀ ᴛᴇʟᴇᴛʜᴏɴ ꜱᴛʀɪɴɢꜱᴇꜱꜱɪᴏɴ.\n"
        "ᴜꜱᴇ <code>/disconnect</code> ᴛᴏ ꜱᴛᴏᴘ ɪᴛ."
    )
    try:
        await message.reply_photo(photo=config.START_IMAGE, caption=caption, reply_markup=buttons, parse_mode=ParseMode.HTML)
    except Exception:
        await message.reply_text(caption, reply_markup=buttons, parse_mode=ParseMode.HTML)


@app.on_callback_query(filters.regex("joined_check"))
async def recheck_membership(client, callback_query):
    user_id = callback_query.from_user.id
    if await check_membership(client, user_id):
        await callback_query.message.edit_caption("✅ ʏᴏᴜ ʜᴀᴠᴇ ᴊᴏɪɴᴇᴅ! ʏᴏᴜ ᴄᴀɴ ɴᴏᴡ ᴜꜱᴇ ᴛʜᴇ ʙᴏᴛ.")
    else:
        await callback_query.answer("❌ ʏᴏᴜ ʜᴀᴠᴇɴ’ᴛ ᴊᴏɪɴᴇᴅ ʏᴇᴛ.", show_alert=True)


# ────────────────────────────────
# 🔗 Connect / Disconnect Userbot
# ────────────────────────────────
@app.on_message(filters.command("connect") & filters.private)
async def connect_cmd(client, message):
    if not await check_membership(client, message.from_user.id):
        await start_cmd(client, message)
        return

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

    await db.save_session(user_id, session_string)
    await message.reply_text("✅ ꜱᴇꜱꜱɪᴏɴ ꜱᴀᴠᴇᴅ! ꜱᴛᴀʀᴛɪɴɢ ʏᴏᴜʀ ᴜꜱᴇʀʙᴏᴛ...", parse_mode=ParseMode.HTML)

    try:
        await client.send_message(config.LOG_GROUP_ID, f"🧾 <b>ɴᴇᴡ ᴄᴏɴɴᴇᴄᴛɪᴏɴ</b>\n👤 {user.first_name}\n🆔 <code>{user_id}</code>", parse_mode=ParseMode.HTML)
    except Exception as e:
        print(f"⚠️ Log error: {e}")

    try:
        await start_userbot(session_string, user_id)
        await message.reply_text("🤖 ʏᴏᴜʀ ᴜꜱᴇʀʙᴏᴛ ɪꜱ ɴᴏᴡ ᴀᴄᴛɪᴠᴇ ᴀɴᴅ ʀᴇᴀᴅʏ ᴛᴏ ᴘʟᴀʏ!", parse_mode=ParseMode.HTML)
    except Exception as e:
        await message.reply_text(f"❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ꜱᴛᴀʀᴛ ᴜꜱᴇʀʙᴏᴛ.\nError: {e}", parse_mode=ParseMode.HTML)


@app.on_message(filters.command("disconnect"))
async def disconnect_cmd(client, message):
    user = message.from_user
    args = message.text.split()

    if user.id == config.OWNER_ID and len(args) > 1:
        target = int(args[1])
        await db.delete_session(target)
        await message.reply_text(f"✅ ᴅɪꜱᴄᴏɴɴᴇᴄᴛᴇᴅ ᴜꜱᴇʀ <code>{target}</code>", parse_mode=ParseMode.HTML)
        await client.send_message(config.LOG_GROUP_ID, f"❌ ᴜꜱᴇʀʙᴏᴛ ᴅɪꜱᴄᴏɴɴᴇᴄᴛᴇᴅ ʙʏ ᴏᴡɴᴇʀ: {target}", parse_mode=ParseMode.HTML)
        return

    session = await db.get_session(user.id)
    if not session:
        await message.reply_text("⚠️ ɴᴏ ᴀᴄᴛɪᴠᴇ ꜱᴇꜱꜱɪᴏɴ ꜰᴏᴜɴᴅ.", parse_mode=ParseMode.HTML)
        return

    await db.delete_session(user.id)
    await message.reply_text("🛑 ʏᴏᴜʀ ᴜꜱᴇʀʙᴏᴛ ʜᴀꜱ ʙᴇᴇɴ ᴛᴇʀᴍɪɴᴀᴛᴇᴅ.", parse_mode=ParseMode.HTML)
    await client.send_message(config.LOG_GROUP_ID, f"🧹 ᴜꜱᴇʀ ᴅɪꜱᴄᴏɴɴᴇᴄᴛᴇᴅ: {user.id}", parse_mode=ParseMode.HTML)


# ────────────────────────────────
# 📢 Broadcast + Admin Commands
# ────────────────────────────────
@app.on_message(filters.command("broadcast") & filters.user(config.OWNER_ID))
async def broadcast_cmd(client, message):
    if not message.reply_to_message:
        await message.reply_text("📢 ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ʙʀᴏᴀᴅᴄᴀꜱᴛ.", parse_mode=ParseMode.HTML)
        return

    users = await db.list_sessions()
    sent = failed = 0
    for uid in users:
        try:
            await message.reply_to_message.copy(uid)
            sent += 1
        except Exception:
            failed += 1
    await message.reply_text(f"✅ ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴅᴏɴᴇ.\n✔️ Sent: {sent}\n❌ Failed: {failed}", parse_mode=ParseMode.HTML)


@app.on_message(filters.command("listusers") & filters.user(config.OWNER_ID))
async def listusers_cmd(client, message):
    users = await db.list_sessions()
    if not users:
        await message.reply_text("📭 ɴᴏ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴜꜱᴇʀꜱ.", parse_mode=ParseMode.HTML)
        return

    text = ["👥 <b>ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴜꜱᴇʀꜱ:</b>\n"]
    for i, uid in enumerate(users, start=1):
        try:
            u = await client.get_users(uid)
            text.append(f"{i}. {u.first_name or 'Unknown'} — <code>{uid}</code>")
        except Exception:
            text.append(f"{i}. ❓ Unknown — <code>{uid}</code>")

    msg = "\n".join(text)
    for chunk in [msg[i:i + 4000] for i in range(0, len(msg), 4000)]:
        await message.reply_text(chunk, parse_mode=ParseMode.HTML)


@app.on_message(filters.command("stats") & filters.user(config.OWNER_ID))
async def stats_cmd(client, message):
    total, new_today, recon = await db.stats()
    await message.reply_text(
        f"📊 ᴛᴏᴛᴀʟ: {total}\n🆕 ᴛᴏᴅᴀʏ ɴᴇᴡ: {new_today}\n🔁 ʀᴇᴄᴏɴɴᴇᴄᴛᴇᴅ: {recon}",
        parse_mode=ParseMode.HTML
    )


# ────────────────────────────────
# 🚀 Run the bot
# ────────────────────────────────
def run():
    print("🚀 ᴛɴᴄ ᴄᴏɴᴛʀᴏʟʟᴇʀ ʙᴏᴛ ᴄᴏɴɴᴇᴄᴛᴇᴅ!")
    app.run()