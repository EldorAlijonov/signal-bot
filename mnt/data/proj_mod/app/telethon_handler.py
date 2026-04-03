from __future__ import annotations

import html
import logging

from telethon import TelegramClient, events

from .config import API_ID, API_HASH, SESSION_NAME, ALLOWED_CHATS, ADMIN_ID
from .database import get_bot_enabled, get_keywords, stats_add
from .utils import normalize_text

logger = logging.getLogger(__name__)

user_client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
bot_app = None


def set_bot_app(app) -> None:
    global bot_app
    bot_app = app


@user_client.on(events.NewMessage)
async def handle_new_message(event):
    try:
        if not get_bot_enabled():
            return

        if not event.message:
            return

        text_raw = event.message.text or event.message.message or ""
        if not text_raw.strip():
            return

        if ALLOWED_CHATS and event.chat_id not in ALLOWED_CHATS:
            return

        matched_keyword = None
        text_lower = normalize_text(text_raw)

        for word in get_keywords():
            if normalize_text(word) in text_lower:
                matched_keyword = word
                break

        if not matched_keyword:
            return

        sender = await event.get_sender()
        chat = await event.get_chat()

        full_name = f"{getattr(sender, 'first_name', '') or ''} {getattr(sender, 'last_name', '') or ''}".strip()
        if not full_name:
            full_name = "Noma'lum foydalanuvchi"

        sender_username = getattr(sender, "username", None)
        phone_number = getattr(sender, "phone", None) or "Telefon yo'q"
        chat_title = getattr(chat, "title", None) or "Noma'lum guruh"
        chat_username = getattr(chat, "username", None)

        if isinstance(phone_number, str) and phone_number.startswith("998"):
            phone_number = "+" + phone_number

        username_text = f"@{sender_username}" if sender_username else "Username yo'q"

        message_text = (
            f"<b>💬 Yangi signal topildi</b>\n\n"
            f"<blockquote>{html.escape(text_raw)}</blockquote>\n\n"
            f"<b>👤 Yozgan:</b> {html.escape(full_name)}\n"
            f"<b>📞 Telefon:</b> {phone_number}\n"
            f"<b>🔗 Username:</b> {html.escape(username_text)}\n"
            f"<b>👥 Guruh:</b> {html.escape(chat_title)}\n"
            f"<b>🆔 Chat ID:</b> <code>{event.chat_id}</code>\n"
            f"<b>🔑 Topilgan kalit so'z:</b> {html.escape(matched_keyword)}\n"
        )

        if chat_username:
            message_text += f"\n<b>🌐 Guruh linki:</b> https://t.me/{chat_username}"

        stats_add(
            chat_id=str(event.chat_id),
            chat_title=chat_title,
            sender_name=full_name,
            keyword=matched_keyword,
            message_text=text_raw,
        )

        if bot_app is None:
            logger.warning("bot_app hali tayyor emas")
            return

        await bot_app.bot.send_message(
            chat_id=ADMIN_ID,
            text=message_text,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )

        logger.info("Xabar yuborildi | chat=%s | keyword=%s", event.chat_id, matched_keyword)

    except Exception as e:
        logger.exception("Telethon handler xatolik: %s", e)
