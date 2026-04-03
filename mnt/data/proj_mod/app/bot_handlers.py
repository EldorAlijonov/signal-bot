from __future__ import annotations

import html

from telegram import Update
from telegram.ext import ContextTypes

from .config import ALLOWED_CHATS, ADMIN_ID
from .database import (
    get_bot_enabled,
    set_bot_enabled,
    get_keywords,
    stats_count,
    stats_last,
)
from .keyboards import main_menu_keyboard
from .utils import is_admin_user_id

user_client = None


def set_user_client(client) -> None:
    global user_client
    user_client = client


def _is_admin_update(update: Update) -> bool:
    user = update.effective_user
    return bool(user and user.id == ADMIN_ID)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin_update(update):
        await update.message.reply_text("Sizda ruxsat yo'q.")
        return

    text = "🤖 Bot boshqaruv paneli\n\nPastdagi tugmalar orqali botni boshqaring."
    await update.message.reply_text(text, reply_markup=main_menu_keyboard())


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin_update(update):
        await update.message.reply_text("Sizda ruxsat yo'q.")
        return

    text = (
        "Yordam:\n\n"
        "/start - menyu\n"
        "/menu - menyu\n"
        "/on - yoqish\n"
        "/off - o'chirish\n"
        "/status - holat\n"
        "/chats - guruhlar\n"
        "/keywords - kalit so'zlar\n"
        "/stats - statistika"
    )
    await update.message.reply_text(text, reply_markup=main_menu_keyboard())


async def cmd_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin_update(update):
        await update.message.reply_text("Sizda ruxsat yo'q.")
        return
    await update.message.reply_text("Bosh menyu:", reply_markup=main_menu_keyboard())


async def cmd_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin_update(update):
        await update.message.reply_text("Sizda ruxsat yo'q.")
        return
    set_bot_enabled(True)
    await update.message.reply_text("Bot yoqildi ✅", reply_markup=main_menu_keyboard())


async def cmd_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin_update(update):
        await update.message.reply_text("Sizda ruxsat yo'q.")
        return
    set_bot_enabled(False)
    await update.message.reply_text("Bot o'chirildi ⛔", reply_markup=main_menu_keyboard())


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin_update(update):
        await update.message.reply_text("Sizda ruxsat yo'q.")
        return

    status_text = "YOQILGAN ✅" if get_bot_enabled() else "O'CHIRILGAN ⛔"
    chats_mode = "Barcha guruhlar" if not ALLOWED_CHATS else f"{len(ALLOWED_CHATS)} ta tanlangan guruh"

    text = (
        f"📊 Holat\n\n"
        f"Bot: {status_text}\n"
        f"Kuzatilayotgan chatlar: {chats_mode}\n"
        f"Kalit so'zlar soni: {len(get_keywords())}\n"
        f"Ushlangan xabarlar: {stats_count()} ta"
    )
    await update.message.reply_text(text, reply_markup=main_menu_keyboard())


async def cmd_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin_update(update):
        await update.message.reply_text("Sizda ruxsat yo'q.")
        return

    if user_client is None:
        await update.message.reply_text("Telethon client tayyor emas.")
        return

    dialogs = await user_client.get_dialogs()
    rows = [f"• {dialog.name} → <code>{dialog.id}</code>" for dialog in dialogs if dialog.is_group]

    if not rows:
        await update.message.reply_text("Guruh topilmadi.", reply_markup=main_menu_keyboard())
        return

    text = "<b>👥 Guruhlar ro'yxati:</b>\n\n" + "\n".join(rows[:50])
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=main_menu_keyboard())


async def cmd_keywords(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin_update(update):
        await update.message.reply_text("Sizda ruxsat yo'q.")
        return

    words = get_keywords()
    if not words:
        await update.message.reply_text("Kalit so'zlar yo'q.", reply_markup=main_menu_keyboard())
        return

    text = "<b>🔑 Kalit so'zlar:</b>\n\n" + "\n".join([f"• {html.escape(w)}" for w in words])
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=main_menu_keyboard())


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin_update(update):
        await update.message.reply_text("Sizda ruxsat yo'q.")
        return

    total = stats_count()
    last_rows = stats_last(5)

    text = f"<b>📈 Statistika</b>\n\nJami ushlangan xabarlar: <b>{total}</b>\n\n"
    if last_rows:
        text += "<b>Oxirgi 5 ta:</b>\n"
        for row in last_rows:
            text += (
                f"\n• <b>{html.escape(row['chat_title'])}</b>\n"
                f"  👤 {html.escape(row['sender_name'])}\n"
                f"  🔑 {html.escape(row['keyword'])}\n"
                f"  🕒 {row['created_at']}\n"
            )
    else:
        text += "Hozircha statistika yo'q."

    await update.message.reply_text(text, parse_mode="HTML", reply_markup=main_menu_keyboard())


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin_user_id(query.from_user.id, ADMIN_ID):
        await query.message.reply_text("Sizda ruxsat yo'q.")
        return

    data = query.data

    if data == "bot_on":
        set_bot_enabled(True)
        await query.edit_message_text("Bot yoqildi ✅", reply_markup=main_menu_keyboard())

    elif data == "bot_off":
        set_bot_enabled(False)
        await query.edit_message_text("Bot o'chirildi ⛔", reply_markup=main_menu_keyboard())

    elif data == "bot_status":
        status_text = "YOQILGAN ✅" if get_bot_enabled() else "O'CHIRILGAN ⛔"
        chats_mode = "Barcha guruhlar" if not ALLOWED_CHATS else f"{len(ALLOWED_CHATS)} ta tanlangan guruh"
        text = (
            f"📊 Holat\n\n"
            f"Bot: {status_text}\n"
            f"Kuzatilayotgan chatlar: {chats_mode}\n"
            f"Kalit so'zlar soni: {len(get_keywords())}\n"
            f"Ushlangan xabarlar: {stats_count()} ta"
        )
        await query.edit_message_text(text, reply_markup=main_menu_keyboard())

    elif data == "bot_chats":
        if user_client is None:
            await query.edit_message_text("Telethon client tayyor emas.", reply_markup=main_menu_keyboard())
            return

        dialogs = await user_client.get_dialogs()
        rows = [f"• {dialog.name} → {dialog.id}" for dialog in dialogs if dialog.is_group]
        text = "👥 Guruhlar ro'yxati:\n\n" + ("\n".join(rows[:40]) if rows else "Guruh topilmadi.")
        await query.edit_message_text(text, reply_markup=main_menu_keyboard())

    elif data == "bot_keywords":
        words = get_keywords()
        text = "🔑 Kalit so'zlar:\n\n" + ("\n".join([f"• {w}" for w in words]) if words else "Kalit so'zlar yo'q.")
        await query.edit_message_text(text, reply_markup=main_menu_keyboard())

    elif data == "bot_stats":
        total = stats_count()
        last_rows = stats_last(5)

        text = f"📈 Statistika\n\nJami: {total} ta\n\n"
        if last_rows:
            text += "Oxirgi 5 ta:\n"
            for row in last_rows:
                text += (
                    f"\n• {row['chat_title']}\n"
                    f"  👤 {row['sender_name']}\n"
                    f"  🔑 {row['keyword']}\n"
                    f"  🕒 {row['created_at']}\n"
                )
        else:
            text += "Hozircha statistika yo'q."

        await query.edit_message_text(text, reply_markup=main_menu_keyboard())

    elif data == "bot_menu":
        await query.edit_message_text(
            "🤖 Bot boshqaruv paneli\n\nPastdagi tugmalar orqali boshqaring.",
            reply_markup=main_menu_keyboard(),
        )
