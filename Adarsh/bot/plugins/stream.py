import os
import asyncio
from asyncio import TimeoutError
from Adarsh.bot import StreamBot
from Adarsh.utils.database import Database
from Adarsh.utils.human_readable import humanbytes
from Adarsh.vars import Var
from urllib.parse import quote
from pyrogram import filters, Client
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from Adarsh.utils.file_properties import get_name, get_hash, get_media_file_size

db = Database(Var.DATABASE_URL, Var.name)
MY_PASS = os.environ.get("MY_PASS", None)
pass_dict = {}
pass_db = Database(Var.DATABASE_URL, "ag_passwords")

@StreamBot.on_message((filters.regex("login🔑") | filters.command("login")), group=4)
async def login_handler(c: Client, m: Message):
    try:
        ag = await m.reply_text("Now send me password.\n\nIf you don't know, check the MY_PASS variable in Heroku.\n\n(You can use /cancel command to cancel the process)")
        _text = await c.listen(m.chat.id, filters=filters.text, timeout=90)
        if _text.text:
            textp = _text.text
            if textp == "/cancel":
                await ag.edit("Process Cancelled Successfully")
                return
        else:
            return
        if textp == MY_PASS:
            await pass_db.add_user_pass(m.chat.id, textp)
            ag_text = "Yeah! You entered the password correctly."
        else:
            ag_text = "Wrong password, try again."
        await ag.edit(ag_text)
    except TimeoutError:
        await ag.edit("I can't wait more for the password. Try again.")
    except Exception as e:
        print(e)

@StreamBot.on_message((filters.private) & (filters.document | filters.video | filters.audio | filters.photo), group=4)
async def private_receive_handler(c: Client, m: Message):
    if MY_PASS:
        check_pass = await pass_db.get_user_pass(m.chat.id)
        if check_pass is None:
            await m.reply_text("Login first using /login cmd.\nDon’t know the pass? Request it from the Developer.")
            return
        if check_pass != MY_PASS:
            await pass_db.delete_user(m.chat.id)
            return
    if not await db.is_user_exist(m.from_user.id):
        await db.add_user(m.from_user.id)
        await c.send_message(
            Var.BIN_CHANNEL,
            f"New User Joined! : \n\n Name : [{m.from_user.first_name}](tg://user?id={m.from_user.id}) Started Your Bot!!"
        )
    try:
        log_msg = await m.forward(chat_id=Var.BIN_CHANNEL)
        file_name = get_name(log_msg)
        stream_link = f"{Var.URL}watch/{str(log_msg.id)}/{quote(file_name, safe='')}?hash={get_hash(log_msg)}"
        online_link = f"{Var.URL}{str(log_msg.id)}/{quote(file_name, safe='')}?hash={get_hash(log_msg)}"
        
        msg_text = """<i><u>Le Re Lund ke Ye Teri File</u></i>\n\n<b>📂 Fɪʟᴇ ɴᴀᴍᴇ :</b> <i>{}</i>\n\n<b>📦 Fɪʟᴇ ꜱɪᴢᴇ :</b> <i>{}</i>\n\n<b>📥 Dᴏᴡɴʟᴏᴀᴅ :</b> <i>{}</i>\n\n<b> 🖥WATCH  :</b> <i>{}</i>\n\n<b>🚸 Nᴏᴛᴇ : Isloo Kisika Baap Delete Nhi Kar Skta</b>"""

        await log_msg.reply_text(
            text=f"**RᴇQᴜᴇꜱᴛᴇᴅ ʙʏ :** [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n**Uꜱᴇʀ ɪᴅ :** {m.from_user.id}\n**Stream ʟɪɴᴋ :** {stream_link}",
            disable_web_page_preview=True, 
            quote=True
        )
        await m.reply_text(
            text=msg_text.format(file_name, humanbytes(get_media_file_size(m)), online_link, stream_link),
            quote=True,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("STREAM 🖥", url=stream_link), 
                 InlineKeyboardButton('DOWNLOAD 📥', url=online_link)]
            ])
        )
    except FloodWait as e:
        print(f"Sleeping for {str(e.x)}s")
        await asyncio.sleep(e.x)
        await c.send_message(chat_id=Var.BIN_CHANNEL, text=f"FloodWait: {str(e.x)}s from [{m.from_user.first_name}](tg://user?id={m.from_user.id})")
