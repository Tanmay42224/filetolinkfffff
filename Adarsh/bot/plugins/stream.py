# (c) Adarsh-Goel
import os
import asyncio
from asyncio import TimeoutError
from urllib.parse import quote_plus

from Adarsh.bot import StreamBot
from Adarsh.utils.database import Database
from Adarsh.utils.human_readable import humanbytes
from Adarsh.utils.file_properties import get_name, get_hash, get_media_file_size
from Adarsh.vars import Var

from pyrogram import filters, Client
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# Database setup
db = Database(Var.DATABASE_URL, Var.name)
pass_db = Database(Var.DATABASE_URL, "ag_passwords")

# Password
MY_PASS = os.environ.get("MY_PASS", None)

def is_valid_url(url: str) -> bool:
    """Validate that the URL is properly formatted and starts with http or https."""
    return url.startswith("http://") or url.startswith("https://")


@StreamBot.on_message((filters.regex("login🔑") | filters.command("login")), group=4)
async def login_handler(c: Client, m: Message):
    try:
        ag = await m.reply_text(
            "Send me the password.\n\n"
            "If you don't know, check the `MY_PASS` variable in Heroku.\n\n"
            "(You can use /cancel command to cancel the process.)"
        )
        try:
            _text = await c.listen(m.chat.id, filters=filters.text, timeout=90)
            textp = _text.text if _text.text else None
            if textp == "/cancel":
                await ag.edit("Process Cancelled Successfully")
                return
        except TimeoutError:
            await ag.edit("Timeout! I cannot wait longer for the password. Try again.")
            return

        if textp == MY_PASS:
            await pass_db.add_user_pass(m.chat.id, textp)
            ag_text = "Password correct! Login successful."
        else:
            ag_text = "Wrong password! Please try again."
        await ag.edit(ag_text)
    except Exception as e:
        print(f"Error in login handler: {e}")


@StreamBot.on_message((filters.private) & (filters.document | filters.video | filters.audio | filters.photo), group=4)
async def private_receive_handler(c: Client, m: Message):
    try:
        if MY_PASS:
            check_pass = await pass_db.get_user_pass(m.chat.id)
            if check_pass is None:
                await m.reply_text("Login first using /login.\nIf you don't know the password, contact the developer.")
                return
            if check_pass != MY_PASS:
                await pass_db.delete_user(m.chat.id)
                return

        if not await db.is_user_exist(m.from_user.id):
            await db.add_user(m.from_user.id)
            await c.send_message(
                Var.BIN_CHANNEL,
                f"New User Joined:\n\nName: [{m.from_user.first_name}](tg://user?id={m.from_user.id}) Started Your Bot!"
            )

        if Var.UPDATES_CHANNEL != "None":
            try:
                user = await c.get_chat_member(Var.UPDATES_CHANNEL, m.chat.id)
                if user.status == "kicked":
                    await c.send_message(
                        chat_id=m.chat.id,
                        text="You are banned!\n\n**Contact Developer [VJ](https://t.me/vj_bots) for assistance.**",
                        disable_web_page_preview=True
                    )
                    return
            except UserNotParticipant:
                await c.send_message(
                    chat_id=m.chat.id,
                    text="<i>Join the Updates Channel to use me 🔐</i>",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("Join Now 🔓", url=f"https://t.me/{Var.UPDATES_CHANNEL}")]]
                    )
                )
                return

        log_msg = await m.forward(chat_id=Var.BIN_CHANNEL)
        file_name = get_name(log_msg) or "file"
        safe_file_name = quote_plus(file_name)
        stream_link = f"{Var.URL}watch/{log_msg.id}/{safe_file_name}?hash={get_hash(log_msg)}"
        online_link = f"{Var.URL}{log_msg.id}/{safe_file_name}?hash={get_hash(log_msg)}"

        if not (is_valid_url(stream_link) and is_valid_url(online_link)):
            raise ValueError("Invalid URLs generated. Please check the configurations.")

        msg_text = (
            "<i><u>Your Link Generated!</u></i>\n\n"
            f"<b>📂 File Name:</b> <i>{file_name}</i>\n\n"
            f"<b>📦 File Size:</b> <i>{humanbytes(get_media_file_size(m))}</i>\n\n"
            f"<b>📥 Download:</b> <i>{online_link}</i>\n\n"
            f"<b>🖥 Watch:</b> <i>{stream_link}</i>\n\n"
            "<b>🚸 Note: Links won't expire until I delete them.</b>"
        )

        await log_msg.reply_text(
            text=f"**Requested by:** [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n**User ID:** `{m.from_user.id}`\n**Stream Link:** {stream_link}",
            disable_web_page_preview=True,
            quote=True
        )
        await m.reply_text(
            text=msg_text,
            quote=True,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("STREAM 🖥", url=stream_link), InlineKeyboardButton("DOWNLOAD 📥", url=online_link)]]
            )
        )
    except FloodWait as e:
        print(f"FloodWait: Sleeping for {e.x} seconds.")
        await asyncio.sleep(e.x)
    except Exception as e:
        print(f"Error in private receive handler: {e}")
        await m.reply_text("An error occurred while processing your request. Please try again later.")
