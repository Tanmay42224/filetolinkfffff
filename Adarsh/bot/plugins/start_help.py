# (c) adarsh-goel 
from Adarsh.bot import StreamBot
from Adarsh.vars import Var
import logging
from Adarsh.utils.database import Database
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup

logger = logging.getLogger(__name__)

db = Database(Var.DATABASE_URL, Var.name)

buttonz = ReplyKeyboardMarkup(
    [
        ["start⚡️", "help📚", "login🔑", "DC"],
        ["follow❤️", "ping📡", "status📊", "maintainers😎"]
    ],
    resize_keyboard=True
)


@StreamBot.on_message((filters.command("start") | filters.regex('start⚡️')) & filters.private)
async def start(b, m):
    if not await db.is_user_exist(m.from_user.id):
        await db.add_user(m.from_user.id)
        await b.send_message(
            Var.BIN_CHANNEL,
            f"**New User Joined:** \n\n[{m.from_user.first_name}](tg://user?id={m.from_user.id}) started your bot!"
        )
    await StreamBot.send_photo(
        chat_id=m.chat.id,
        photo="https://te.legra.ph/file/119729ea3cdce4fefb6a1.jpg",
        caption=f"Hi {m.from_user.mention(style='md')}! I am a Telegram File to Link Generator Bot. "
                f"Send me any file, and I'll provide a direct download link and a streamable link.",
        reply_markup=buttonz
    )


@StreamBot.on_message((filters.command("help") | filters.regex('help📚')) & filters.private)
async def help_handler(bot, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id)
        await bot.send_message(
            Var.BIN_CHANNEL,
            f"**New User Joined:** [{message.from_user.first_name}](tg://user?id={message.from_user.id}) started your bot!"
        )
    await message.reply_text(
        text="Send me any file or video, and I'll provide a streamable link and a download link. "
             "You can also add me to your channel and send media files for channel support features.",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Developer 💁‍♂️", url="https://t.me/anjel_neha")],
                [InlineKeyboardButton("Source Code 💥", url="https://t.me/anjel_neha")]
            ]
        )
    )
