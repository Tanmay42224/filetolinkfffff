# (c) Adarsh-Goel
import logging
from Adarsh.bot import StreamBot
from Adarsh.vars import Var
from Adarsh.utils.database import Database
from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
)
from pyrogram.errors import UserNotParticipant

logger = logging.getLogger(__name__)

# Initialize database
db = Database(Var.DATABASE_URL, Var.name)

# Dynamic button setup
MY_PASS = getattr(Var, "MY_PASS", None)
buttonz = ReplyKeyboardMarkup(
    [
        ["start⚡️", "help📚", "login🔑" if MY_PASS else None, "DC"],
        ["follow❤️", "ping📡", "status📊", "maintainers😎"],
    ],
    resize_keyboard=True,
).keyboard

# Helper function to check if user is a participant in the updates channel
async def ensure_channel_subscription(bot, chat_id):
    if Var.UPDATES_CHANNEL == "None":
        return True

    try:
        user_status = await bot.get_chat_member(Var.UPDATES_CHANNEL, chat_id)
        if user_status.status == "kicked":
            await bot.send_message(
                chat_id,
                text="You are banned from using this bot. Contact the developer for assistance.",
                disable_web_page_preview=True,
            )
            return False
    except UserNotParticipant:
        await bot.send_photo(
            chat_id=chat_id,
            photo="https://te.legra.ph/file/5f5e1b0a5752b55c90f02.jpg",
            caption="Join the updates channel to use this bot.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Join Now", url=f"https://t.me/{Var.UPDATES_CHANNEL}")]
                ]
            ),
        )
        return False
    except Exception as e:
        logger.error(f"Error in ensure_channel_subscription: {e}")
        await bot.send_message(
            chat_id,
            text="Something went wrong. Contact support for assistance.",
            disable_web_page_preview=True,
        )
        return False

    return True


@StreamBot.on_message((filters.command("start") | filters.regex("start⚡️")) & filters.private)
async def start_handler(bot, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id)
        await bot.send_message(
            Var.BIN_CHANNEL,
            f"**New User Joined:**\n\n__New Friend__ [{message.from_user.first_name}](tg://user?id={message.from_user.id}) has started your bot.",
        )

    if not await ensure_channel_subscription(bot, message.chat.id):
        return

    await bot.send_photo(
        chat_id=message.chat.id,
        photo="https://te.legra.ph/file/119729ea3cdce4fefb6a1.jpg",
        caption=(
            f"Hi {message.from_user.mention(style='md')}!\n"
            "I am a Telegram File-to-Link Generator Bot with channel support.\n"
            "Send me any file to receive a direct download link and streamable link."
        ),
        reply_markup=ReplyKeyboardMarkup(buttonz, resize_keyboard=True),
    )


@StreamBot.on_message((filters.command("help") | filters.regex("help📚")) & filters.private)
async def help_handler(bot, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id)
        await bot.send_message(
            Var.BIN_CHANNEL,
            f"**New User Joined:**\n\n__New Friend__ [{message.from_user.first_name}](tg://user?id={message.from_user.id}) has started your bot.",
        )

    if not await ensure_channel_subscription(bot, message.chat.id):
        return

    await message.reply_text(
        text=(
            "<b>Send me any file or video, and I will provide you with a streamable link and download link.</b>\n\n"
            "<b>I also support channels. Add me to your channel, send media files, and watch the magic happen!</b>\n"
            "Use /list to see all commands."
        ),
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("💁‍♂️ DEV", url="https://t.me/anjel_neha")],
                [InlineKeyboardButton("💥 Source Code", url="https://t.me/anjel_neha")],
            ]
        ),
    )
