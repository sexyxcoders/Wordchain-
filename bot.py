# ─────────────────────────────────────────────
# 🧠 TNC WordChain Controller Bot
# ─────────────────────────────────────────────
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from pyrogram.errors import UserNotParticipant
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
# 🔒 Must-Join Verification
# ────────────────────────────────
async def check_membership(client, user_id: int):
    """Ensure the user joined all required channels."""
    required_channels = ["Sxnpe", "TechNodeCoders"]
    for username in required_channels:
        try:
            member = await client.get_chat_member(username, user_id)
            if member.status in ("left", "kicked"):
                return False
        except UserNotParticipant:
            return False
        except Exception as e:
            print(f"⚠️ Membership check failed for {username}: {e}")
            return False
    return True


# ────────────────────────────────
# 🏁 Start Command
# ────────────────────────────────
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    user_id = message.from_user.id

    if not await check_membership(client, user_id):
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 ᴊᴏɪɴ @Sxnpe", url="https://t.me/Sxnpe")],
            [InlineKeyboardButton("📢 ᴊᴏɪɴ @TechNodeCoders", url="https://t.me/TechNodeCoders")],
            [InlineKeyboardButton("✅ ɪ ᴊᴏɪɴᴇᴅ", callback_data="joined_check")]
        ])
        caption = (
            "⚠️ <b>ʏᴏᴜ ᴍᴜꜱᴛ ᴊᴏɪɴ ʙᴏᴛʜ ᴄʜᴀɴɴᴇʟꜱ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ʙᴏᴛ.</b>\n\n"
            "📢 @Sxnpe\n📢 @TechNodeCoders\n\n"
            "ᴀꜰᴛᴇʀ ᴊᴏɪɴɪɴɢ, ᴛᴀᴘ ‘ɪ ᴊᴏɪɴᴇᴅ’ ʙᴇʟᴏᴡ."
        )
        try:
            if getattr(config, "MUST_JOIN_IMAGE", None):
                await message.reply_photo(
                    photo=config.MUST_JOIN_IMAGE,
                    caption=caption,
                    reply_markup=buttons,
                    parse_mode=ParseMode.HTML
                )
            else:
                await message.reply_text(caption, reply_markup=buttons, parse_mode=ParseMode.HTML)
        except Exception as e:
            print("⚠️ Failed to send must-join image, sending text instead.", e)
            await message.reply_text(caption, reply_markup=buttons, parse_mode=ParseMode.HTML)
        return

    # Main menu
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
        if getattr(config, "START_IMAGE", None):
            await message.reply_photo(photo=config.START_IMAGE, caption=caption, reply_markup=buttons, parse_mode=ParseMode.HTML)
        else:
            await message.reply_text(caption, reply_markup=buttons, parse_mode=ParseMode.HTML)
    except Exception as e:
        print("⚠️ Failed to send start image, sending text instead.", e)
        await message.reply_text(caption, reply_markup=buttons, parse_mode=ParseMode.HTML)


# ────────────────────────────────
# 🔁 "I Joined" Button
# ────────────────────────────────
@app.on_callback_query(filters.regex("joined_check"))
async def joined_check(client, callback_query):
    user_id = callback_query.from_user.id
    if await check_membership(client, user_id):
        await callback_query.message.edit_caption("✅ ʏᴏᴜ ʜᴀᴠᴇ ᴊᴏɪɴᴇᴅ ʙᴏᴛʜ ᴄʜᴀɴɴᴇʟꜱ! ɴᴏᴡ ʏᴏᴜ ᴄᴀɴ ᴜꜱᴇ ᴛʜᴇ ʙᴏᴛ.")
    else:
        await callback_query.answer("❌ ᴘʟᴇᴀꜱᴇ ᴊᴏɪɴ @Sxnpe & @TechNodeCoders ꜰɪʀꜱᴛ.", show_alert=True)


# ────────────────────────────────
# 🔗 Connect Userbot
# ────────────────────────────────
@app.on_message(filters.command("connect") & filters.private)
async def connect_cmd(client, message):
    if not await check_membership(client, message.from_user.id):
        await start_cmd(client, message)
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply_text(
            "⚠️ ꜱᴇɴᴅ ʏᴏᴜʀ ᴛᴇʟᴇᴛʜᴏɴ ꜱᴛʀɪɴɢꜱᴇꜱꜱɪᴏɴ ᴀꜰᴛᴇʀ /connect.",
            parse_mode=ParseMode.HTML
        )
        return

    session_string = args[1].strip()
    user = message.from_user

    await db.save_session(user.id, session_string)
    await message.reply_text("✅ ꜱᴇꜱꜱɪᴏɴ ꜱᴀᴠᴇᴅ! ʏᴏᴜʀ ᴜꜱᴇʀʙᴏᴛ ɪꜱ ɴᴏᴡ ᴀᴄᴛɪᴠᴇ.", parse_mode=ParseMode.HTML)

    try:
        await client.send_message(
            config.LOG_GROUP_ID,
            f"🧾 <b>ɴᴇᴡ ᴄᴏɴɴᴇᴄᴛɪᴏɴ</b>\n👤 {user.mention}\n🆔 <code>{user.id}</code>",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        print("⚠️ Log error:", e)

    try:
        start_userbot(session_string, user.id)
        await message.reply_text("🤖 ʏᴏᴜʀ ᴜꜱᴇʀʙᴏᴛ ɪꜱ ɴᴏᴡ ᴀᴄᴛɪᴠᴇ ᴀɴᴅ ʀᴇᴀᴅʏ!", parse_mode=ParseMode.HTML)
    except Exception as e:
        await message.reply_text(f"❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ꜱᴛᴀʀᴛ ᴜꜱᴇʀʙᴏᴛ.\nError: {e}", parse_mode=ParseMode.HTML)


# ────────────────────────────────
# 🛑 Disconnect
# ────────────────────────────────
@app.on_message(filters.command("disconnect"))
async def disconnect_cmd(client, message):
    user = message.from_user
    args = message.text.split()
    if user.id == config.OWNER_ID and len(args) > 1:
        target = int(args[1])
        await db.delete_session(target)
        await message.reply_text(f"✅ ᴜꜱᴇʀ <code>{target}</code> ᴅɪꜱᴄᴏɴɴᴇᴄᴛᴇᴅ.", parse_mode=ParseMode.HTML)
        return

    if not await db.get_session(user.id):
        await message.reply_text("⚠️ ɴᴏ ᴀᴄᴛɪᴠᴇ ꜱᴇꜱꜱɪᴏɴ ꜰᴏᴜɴᴅ.", parse_mode=ParseMode.HTML)
        return

    await db.delete_session(user.id)
    await message.reply_text("🛑 ʏᴏᴜʀ ᴜꜱᴇʀʙᴏᴛ ʜᴀꜱ ʙᴇᴇɴ ᴛᴇʀᴍɪɴᴀᴛᴇᴅ.", parse_mode=ParseMode.HTML)


# ────────────────────────────────
# 📊 Admin Commands
# ────────────────────────────────
@app.on_message(filters.command("listusers") & filters.user(config.OWNER_ID))
async def listusers_cmd(client, message):
    users = await db.list_sessions()
    if not users:
        await message.reply_text("📭 ɴᴏ ᴜꜱᴇʀꜱ ᴄᴏɴɴᴇᴄᴛᴇᴅ.", parse_mode=ParseMode.HTML)
        return
    lines = ["👥 <b>ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴜꜱᴇʀꜱ:</b>\n"]
    for i, uid in enumerate(users, start=1):
        try:
            u = await client.get_users(uid)
            lines.append(f"{i}. {u.first_name or 'Unknown'} — <code>{uid}</code>")
        except Exception:
            lines.append(f"{i}. ❓ Unknown — <code>{uid}</code>")
    await message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)


@app.on_message(filters.command("stats") & filters.user(config.OWNER_ID))
async def stats_cmd(client, message):
    total, new_today, recon = await db.stats()
    await message.reply_text(
        f"📊 ᴛᴏᴛᴀʟ: {total}\n🆕 ɴᴇᴡ ᴛᴏᴅᴀʏ: {new_today}\n🔁 ʀᴇᴄᴏɴɴᴇᴄᴛᴇᴅ: {recon}",
        parse_mode=ParseMode.HTML
    )


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
    await message.reply_text(f"✅ ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴅᴏɴᴇ.\n✔️ {sent}\n❌ {failed}", parse_mode=ParseMode.HTML)


# ────────────────────────────────
# 🟢 Run Bot
# ────────────────────────────────
def run():
    print("🚀 ᴛɴᴄ ᴄᴏɴᴛʀᴏʟʟᴇʀ ʙᴏᴛ ᴄᴏɴɴᴇᴄᴛᴇᴅ!")
    app.run()