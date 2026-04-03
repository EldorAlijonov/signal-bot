import asyncio
import logging

from telegram.ext import Application, CommandHandler, CallbackQueryHandler

from app.config import BOT_TOKEN, ADMIN_ID
from app.database import init_db
from app.keyboards import main_menu_keyboard
from app.telethon_handler import user_client, set_bot_app
from app.bot_handlers import (
    set_user_client,
    cmd_start,
    cmd_help,
    cmd_menu,
    cmd_on,
    cmd_off,
    cmd_status,
    cmd_chats,
    cmd_keywords,
    cmd_stats,
    button_handler,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    init_db()

    bot_app = Application.builder().token(BOT_TOKEN).build()

    set_bot_app(bot_app)
    set_user_client(user_client)

    bot_app.add_handler(CommandHandler("start", cmd_start))
    bot_app.add_handler(CommandHandler("help", cmd_help))
    bot_app.add_handler(CommandHandler("menu", cmd_menu))
    bot_app.add_handler(CommandHandler("on", cmd_on))
    bot_app.add_handler(CommandHandler("off", cmd_off))
    bot_app.add_handler(CommandHandler("status", cmd_status))
    bot_app.add_handler(CommandHandler("chats", cmd_chats))
    bot_app.add_handler(CommandHandler("keywords", cmd_keywords))
    bot_app.add_handler(CommandHandler("stats", cmd_stats))
    bot_app.add_handler(CallbackQueryHandler(button_handler))

    await user_client.start()
    me = await user_client.get_me()
    logger.info("Telethon userbot ulandi: %s (%s)", getattr(me, "first_name", "NoName"), me.id)

    await bot_app.initialize()
    await bot_app.start()
    if bot_app.updater is None:
        raise RuntimeError("Updater ishga tushmadi")
    await bot_app.updater.start_polling()

    logger.info("BotFather bot ishga tushdi")

    await bot_app.bot.send_message(
        chat_id=ADMIN_ID,
        text="✅ Bot ishga tushdi va tugmalar tayyor.",
        reply_markup=main_menu_keyboard()
    )

    await user_client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
