from __future__ import annotations

import html

from telegram import Update
from telegram.ext import ContextTypes

from .config import ALLOWED_CHATS, ADMIN_ID, MAX_STATS_ROWS
from .database import (
    add_keyword,
    get_bot_enabled,
    get_keywords,
    remove_keyword,
    set_bot_enabled,
    stats_count,
    stats_last,
    update_keyword,
)
from .keyboards import keywords_menu_keyboard, main_menu_keyboard

user_client = None


def set_user_client(client) -> None:
    global user_client
    user_client = client


def _is_admin_update(update: Update) -> bool:
    user = update.effective_user
    return bool(user and user.id == ADMIN_ID)


def _short_message(value: str, limit: int = 80) -> str:
    value = (value or "").strip()
    if len(value) <= limit:
        return value
    return value[:limit] + "..."


def _reset_keyword_state(context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop("keyword_action", None)
    context.user_data.pop("keyword_old", None)


async def _reply_main(update: Update, text: str, parse_mode: str | None = None) -> None:
    if update.message:
        await update.message.reply_text(
            text,
            parse_mode=parse_mode,
            reply_markup=main_menu_keyboard(),
        )


async def _reply_keywords(update: Update, text: str, parse_mode: str | None = None) -> None:
    if update.message:
        await update.message.reply_text(
            text,
            parse_mode=parse_mode,
            reply_markup=keywords_menu_keyboard(),
        )


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin_update(update):
        if update.message:
            await update.message.reply_text("Sizda ruxsat yo'q.")
        return
    _reset_keyword_state(context)
    text = "🤖 <b>Bot boshqaruv paneli</b>\n\nPastdagi menyu tugmalari orqali botni boshqaring."
    await _reply_main(update, text, parse_mode="HTML")


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin_update(update):
        if update.message:
            await update.message.reply_text("Sizda ruxsat yo'q.")
        return
    _reset_keyword_state(context)
    text = (
        "Yordam:\n\n"
        "/start - menyu\n"
        "/menu - menyu\n"
        "/on - yoqish\n"
        "/off - o'chirish\n"
        "/status - holat\n"
        "/chats - guruhlar\n"
        "/keywords - keywords bo'limi\n"
        "/stats - statistika\n"
        "/ping - tekshiruv"
    )
    await _reply_main(update, text)


async def cmd_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin_update(update):
        if update.message:
            await update.message.reply_text("Sizda ruxsat yo'q.")
        return
    _reset_keyword_state(context)
    await _reply_main(update, "📋 Bosh menyu ochildi.")


async def cmd_ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin_update(update):
        if update.message:
            await update.message.reply_text("Sizda ruxsat yo'q.")
        return
    _reset_keyword_state(context)
    await _reply_main(update, "Pong ✅")


async def _show_status(update: Update):
    status_text = "YOQILGAN ✅" if get_bot_enabled() else "O'CHIRILGAN ⛔"
    chats_mode = "Barcha guruhlar" if not ALLOWED_CHATS else f"{len(ALLOWED_CHATS)} ta tanlangan guruh"
    text = (
        f"📊 <b>Holat</b>\n\n"
        f"Bot: {status_text}\n"
        f"Kuzatilayotgan chatlar: {chats_mode}\n"
        f"Kalit so'zlar soni: {len(get_keywords())}\n"
        f"Ushlangan xabarlar: {stats_count()} ta"
    )
    await _reply_main(update, text, parse_mode="HTML")


async def _show_chats(update: Update):
    if user_client is None:
        await _reply_main(update, "Telethon client tayyor emas.")
        return

    dialogs = await user_client.get_dialogs()
    rows = []

    for dialog in dialogs:
        if not dialog.is_group:
            continue

        chat_name = html.escape(dialog.name or "Noma'lum guruh")
        chat_id = dialog.id
        entity = getattr(dialog, "entity", None)
        username = getattr(entity, "username", None) if entity else None

        if username:
            link = f"https://t.me/{username}"
        elif str(chat_id).startswith("-100"):
            internal_id = str(chat_id)[4:]
            link = f"https://t.me/c/{internal_id}"
        else:
            link = None

        if link:
            rows.append(f"• <a href='{link}'>{chat_name}</a>")
        else:
            rows.append(f"• {chat_name} (havola mavjud emas)")

    if not rows:
        await _reply_main(update, "Guruh topilmadi.")
        return

    text = "<b>👥 Guruhlar ro'yxati:</b>\n\n" + "\n".join(rows[:50])
    await _reply_main(update, text, parse_mode="HTML")


async def _show_keywords(update: Update):
    words = get_keywords()
    if not words:
        await _reply_keywords(update, "Kalit so'zlar yo'q.")
        return

    text = "<b>🔑 Kalit so'zlar:</b>\n\n" + "\n".join(
        [f"{i}. {html.escape(w)}" for i, w in enumerate(words, 1)]
    )
    await _reply_keywords(update, text, parse_mode="HTML")


async def _show_stats(update: Update):
    total = stats_count()
    last_rows = stats_last(MAX_STATS_ROWS)

    text = f"<b>📈 Statistika</b>\n\nJami ushlangan xabarlar: <b>{total}</b>\n\n"
    if last_rows:
        text += f"<b>Oxirgi {min(MAX_STATS_ROWS, len(last_rows))} ta:</b>\n"
        for row in last_rows:
            # tuple yoki dict/Row bo‘lishi mumkinligini hisobga oldik
            if isinstance(row, dict) or hasattr(row, "keys"):
                chat_title = row["chat_title"]
                sender_name = row["sender_name"]
                keyword = row["keyword"]
                created_at = row["created_at"]
                message_text = row["message_text"]
            else:
                chat_title, sender_name, keyword, created_at, message_text = row

            text += (
                f"\n• <b>{html.escape(str(chat_title))}</b>\n"
                f"  👤 {html.escape(str(sender_name))}\n"
                f"  🔑 {html.escape(str(keyword))}\n"
                f"  🕒 {created_at}\n"
                f"  💬 {html.escape(_short_message(str(message_text)))}\n"
            )
    else:
        text += "Hozircha statistika yo'q."

    await _reply_main(update, text, parse_mode="HTML")


async def _enter_keywords_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _reset_keyword_state(context)
    text = (
        "🔑 <b>KEYWORDS bo'limi</b>\n\n"
        "Tugmalardan birini tanlang:\n"
        "• Qo'shish\n"
        "• Tahrirlash\n"
        "• O'chirish\n"
        "• Ro'yxatni ko'rish"
    )
    await _reply_keywords(update, text, parse_mode="HTML")


async def cmd_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin_update(update):
        if update.message:
            await update.message.reply_text("Sizda ruxsat yo'q.")
        return
    _reset_keyword_state(context)
    set_bot_enabled(True)
    await _reply_main(update, "Bot yoqildi ✅")


async def cmd_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin_update(update):
        if update.message:
            await update.message.reply_text("Sizda ruxsat yo'q.")
        return
    _reset_keyword_state(context)
    set_bot_enabled(False)
    await _reply_main(update, "Bot o'chirildi ⛔")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin_update(update):
        if update.message:
            await update.message.reply_text("Sizda ruxsat yo'q.")
        return
    _reset_keyword_state(context)
    await _show_status(update)


async def cmd_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin_update(update):
        if update.message:
            await update.message.reply_text("Sizda ruxsat yo'q.")
        return
    _reset_keyword_state(context)
    await _show_chats(update)


async def cmd_keywords(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin_update(update):
        if update.message:
            await update.message.reply_text("Sizda ruxsat yo'q.")
        return
    await _enter_keywords_menu(update, context)


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin_update(update):
        if update.message:
            await update.message.reply_text("Sizda ruxsat yo'q.")
        return
    _reset_keyword_state(context)
    await _show_stats(update)


async def text_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin_update(update):
        if update.message:
            await update.message.reply_text("Sizda ruxsat yo'q.")
        return

    if not update.message:
        return

    text = (update.message.text or "").strip()
    keyword_action = context.user_data.get("keyword_action")

    if keyword_action == "add":
        if text in {"⬅️ ORQAGA", "/cancel"}:
            _reset_keyword_state(context)
            await _reply_main(update, "Keyword qo'shish bekor qilindi.")
            return
        if add_keyword(text):
            _reset_keyword_state(context)
            await _reply_keywords(update, f"✅ Yangi keyword qo'shildi: <b>{html.escape(text)}</b>", parse_mode="HTML")
        else:
            await _reply_keywords(update, "Bu keyword allaqachon mavjud yoki noto'g'ri. Yana boshqa keyword yuboring.")
        return

    if keyword_action == "delete":
        if text in {"⬅️ ORQAGA", "/cancel"}:
            _reset_keyword_state(context)
            await _reply_main(update, "Keyword o'chirish bekor qilindi.")
            return
        if remove_keyword(text):
            _reset_keyword_state(context)
            await _reply_keywords(update, f"🗑 Keyword o'chirildi: <b>{html.escape(text)}</b>", parse_mode="HTML")
        else:
            await _reply_keywords(update, "Bunday keyword topilmadi. Aynan ro'yxatdagi keywordni yuboring.")
        return

    if keyword_action == "edit_old":
        if text in {"⬅️ ORQAGA", "/cancel"}:
            _reset_keyword_state(context)
            await _reply_main(update, "Keyword tahrirlash bekor qilindi.")
            return
        words = get_keywords()
        if not any(item.lower() == text.lower() for item in words):
            await _reply_keywords(update, "Bunday keyword topilmadi. Aynan eski keywordni yuboring.")
            return
        context.user_data["keyword_old"] = text
        context.user_data["keyword_action"] = "edit_new"
        await _reply_keywords(update, f"✏️ Endi yangi keywordni yuboring.\n\nEski keyword: <b>{html.escape(text)}</b>", parse_mode="HTML")
        return

    if keyword_action == "edit_new":
        if text in {"⬅️ ORQAGA", "/cancel"}:
            _reset_keyword_state(context)
            await _reply_main(update, "Keyword tahrirlash bekor qilindi.")
            return
        old_word = context.user_data.get("keyword_old", "")
        if update_keyword(old_word, text):
            _reset_keyword_state(context)
            await _reply_keywords(update, f"✅ Keyword yangilandi:\n<b>{html.escape(old_word)}</b> ➜ <b>{html.escape(text)}</b>", parse_mode="HTML")
        else:
            await _reply_keywords(update, "Yangilash amalga oshmadi. Ehtimol yangi keyword bo'sh yoki allaqachon mavjud.")
        return

    if text == "✅ ON":
        _reset_keyword_state(context)
        set_bot_enabled(True)
        await _reply_main(update, "Bot yoqildi ✅")
    elif text == "⛔ OFF":
        _reset_keyword_state(context)
        set_bot_enabled(False)
        await _reply_main(update, "Bot o'chirildi ⛔")
    elif text == "📊 STATUS":
        _reset_keyword_state(context)
        await _show_status(update)
    elif text == "👥 CHATS":
        _reset_keyword_state(context)
        await _show_chats(update)
    elif text == "🔑 KEYWORDS":
        await _enter_keywords_menu(update, context)
    elif text == "📈 STATS":
        _reset_keyword_state(context)
        await _show_stats(update)
    elif text == "🔄 REFRESH":
        _reset_keyword_state(context)
        await _reply_main(update, "Menyu yangilandi 🔄")
    elif text == "📋 KEYWORDS RO'YXATI":
        await _show_keywords(update)
    elif text == "➕ KEYWORD QO'SHISH":
        context.user_data["keyword_action"] = "add"
        await _reply_keywords(update, "Yangi keywordni yuboring. Bekor qilish uchun ⬅️ ORQAGA ni bosing.")
    elif text == "🗑 KEYWORD O'CHIRISH":
        context.user_data["keyword_action"] = "delete"
        words = get_keywords()
        listing = "\n".join([f"• {html.escape(w)}" for w in words]) if words else "Keyword yo'q."
        await _reply_keywords(update, f"O'chirmoqchi bo'lgan keywordni aynan yuboring:\n\n{listing}", parse_mode="HTML")
    elif text == "✏️ KEYWORD TAHRIRLASH":
        context.user_data["keyword_action"] = "edit_old"
        words = get_keywords()
        listing = "\n".join([f"• {html.escape(w)}" for w in words]) if words else "Keyword yo'q."
        await _reply_keywords(update, f"Avval eski keywordni yuboring:\n\n{listing}", parse_mode="HTML")
    elif text == "⬅️ ORQAGA":
        _reset_keyword_state(context)
        await _reply_main(update, "Bosh menyuga qaytdingiz.")
    else:
        await _reply_main(update, "Noma'lum buyruq. Pastdagi menyu tugmalaridan foydalaning.")