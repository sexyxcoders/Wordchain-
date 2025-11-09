# ─────────────────────────────────────────────
# 🧠 TNC WordChain Controller Bot — Chat-Independent Sessions
# ─────────────────────────────────────────────
import os
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
# 🖼 Resolve image paths for Heroku
# ────────────────────────────────
START_IMAGE = getattr(config, "START_IMAGE", None)
if START_IMAGE:
    START_IMAGE = os.path.join(os.path.dirname(__file__), START_IMAGE)

MUST_JOIN_IMAGE = getattr(config, "MUST_JOIN_IMAGE", None)
if MUST_JOIN_IMAGE:
    MUST_JOIN_IMAGE = os.path.join(os.path.dirname(__file__), MUST_JOIN_IMAGE)

# ────────────────────────────────
# 🔒 Membership Verification
# ────────────────────────────────
async def check_membership(client, user_id: int):
    """Ensure the user joined all required channels."""
    required_channels = ["Sxnpe", "TncNetwork"]
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
# 🏁 /start Command
# ────────────────────────────────
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    user_id = message.from_user.id

    if not await check_membership(client, user_id):
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 ᴊᴏɪɴ @Sxnpe", url="https://t.me/Sxnpe")],
            [InlineKeyboardButton("📢 ᴊᴏɪɴ @TncNetwork", url="https://t.me/TncNetwork")],
            [InlineKeyboardButton("✅ ɪ ᴊᴏɪɴᴇᴅ", callback_data="joined_check")]
        ])
        caption = (
            "⚠️ <b>ʏᴏᴜ ᴍᴜꜱᴛ ᴊᴏɪɴ ʙᴏᴛʜ ᴄʜᴀɴɴᴇʟꜱ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ʙᴏᴛ.</b>\n\n"
            "📢 @Sxnpe\n📢 @TechNodeCoders\n\n"
            "ᴀꜰᴛᴇʀ ᴊᴏɪɴɪɴɢ, ᴛᴀᴘ ‘ɪ ᴊᴏɪɴᴇᴅ’ ʙᴇʟᴏᴡ."
        )
        try:
            if MUST_JOIN_IMAGE:
                await message.reply_photo(
                    photo=MUST_JOIN_IMAGE,
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

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("👑 ᴏᴡɴᴇʀ", url=f"tg://user?id={config.OWNER_ID}")],
        [InlineKeyboardButton("📢 ᴄʜᴀɴɴᴇʟ", url=config.SUPPORT_CHANNEL),
         InlineKeyboardButton("💬 ꜱᴜᴘᴘᴏʀᴛ", url=config.SUPPORT_CHAT)]
    ])
    caption = (
        "🤖 <b>ᴛɴᴄ-ᴡᴏʀᴅᴄʜᴀɪɴ ʙᴏᴛ</b>\n\n"
        "Send <code>/connect STRING</code> to register your Telethon string session.\n"
        "Use <code>/disconnect</code> to stop it."
    )
    try:
        if START_IMAGE:
            await message.reply_photo(
                photo=START_IMAGE,
                caption=caption,
                reply_markup=buttons,
                parse_mode=ParseMode.HTML
            )
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
        await callback_query.message.edit_caption(
            "✅ You have joined both channels! Now you can use the bot."
        )
    else:
        await callback_query.answer(
            "❌ Please join @Sxnpe & @TechNodeCoders first.",
            show_alert=True
        )

# ────────────────────────────────
# 🔗 /connect Command
# ────────────────────────────────
@app.on_message(filters.command("connect") & filters.private)
async def connect_cmd(client, message):
    if not await check_membership(client, message.from_user.id):
        await start_cmd(client, message)
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply_text(
            "⚠️ Send your Telethon string session after /connect.",
            parse_mode=ParseMode.HTML
        )
        return

    session_string = args[1].strip()
    user = message.from_user

    # ✅ Chat-independent save
    await db.save_session(user.id, session_string)

    await message.reply_text(
        "✅ Session saved! Your userbot is now active.",
        parse_mode=ParseMode.HTML
    )

    try:
        await client.send_message(
            config.LOG_GROUP_ID,
            f"🧾 <b>New Connection</b>\n👤 {user.mention}\n🆔 <code>{user.id}</code>",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        print("⚠️ Log error:", e)

    try:
        start_userbot(session_string, user.id)
        await message.reply_text(
            "🤖 Your userbot is now active and ready!",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await message.reply_text(f"❌ Failed to start userbot.\nError: {e}", parse_mode=ParseMode.HTML)

# ────────────────────────────────
# 🛑 /disconnect Command
# ────────────────────────────────
@app.on_message(filters.command("disconnect"))
async def disconnect_cmd(client, message):
    user = message.from_user
    args = message.text.split()

    if user.id == config.OWNER_ID and len(args) > 1:
        target = int(args[1])
        await db.delete_session(target)
        await message.reply_text(
            f"✅ User <code>{target}</code> disconnected.",
            parse_mode=ParseMode.HTML
        )
        return

    session = await db.get_session(user.id)
    if not session:
        await message.reply_text("⚠️ No active session found.", parse_mode=ParseMode.HTML)
        return

    await db.delete_session(user.id)
    await message.reply_text(
        "🛑 Your userbot has been terminated.",
        parse_mode=ParseMode.HTML
    )

# ────────────────────────────────
# 📊 Admin Commands
# ────────────────────────────────
@app.on_message(filters.command("listusers") & filters.user(config.OWNER_ID))
async def listusers_cmd(client, message):
    users = await db.list_sessions()
    if not users:
        await message.reply_text("📭 No users connected.", parse_mode=ParseMode.HTML)
        return

    lines = ["👥 <b>Connected Users:</b>\n"]
    for i, (uid, _) in enumerate(users, start=1):
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
        f"📊 Total: {total}\n🆕 New Today: {new_today}\n🔁 Reconnected: {recon}",
        parse_mode=ParseMode.HTML
    )

@app.on_message(filters.command("broadcast") & filters.user(config.OWNER_ID))
async def broadcast_cmd(client, message):
    if not message.reply_to_message:
        await message.reply_text(
            "📢 Reply to a message to broadcast.",
            parse_mode=ParseMode.HTML
        )
        return

    users = await db.list_sessions()
    sent = failed = 0
    for uid, _ in users:
        try:
            await message.reply_to_message.copy(uid)
            sent += 1
        except Exception:
            failed += 1

    await message.reply_text(
        f"✅ Broadcast done.\n✔️ {sent}\n❌ {failed}",
        parse_mode=ParseMode.HTML
    )

# ────────────────────────────────
# 🟢 Run Bot
# ────────────────────────────────
def run():
    print("🚀 TNC Controller Bot connected!")
    app.run()