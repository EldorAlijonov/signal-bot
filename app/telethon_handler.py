from __future__ import annotations

import html
import logging

from telethon import TelegramClient, events

from .config import API_ID, API_HASH, SESSION_NAME, ALLOWED_CHATS, BLACKLIST, ADMIN_ID
from .database import get_bot_enabled, get_keywords, stats_add
from .utils import normalize_text

logger = logging.getLogger(__name__)

user_client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
bot_app = None
recent_messages: set[tuple[int, int]] = set()


def set_bot_app(app) -> None:
    global bot_app
    bot_app = app


def build_user_text(sender, sender_id: int) -> tuple[str, str]:
    first_name = getattr(sender, "first_name", "") or ""
    last_name = getattr(sender, "last_name", "") or ""
    full_name = f"{first_name} {last_name}".strip() or "Noma'lum foydalanuvchi"

    safe_name = html.escape(full_name)
    sender_username = getattr(sender, "username", None)

    if sender_username:
        profile_link = f"https://t.me/{sender_username}"
        clickable_name = f"<a href='{profile_link}'>{safe_name}</a>"
        return clickable_name, profile_link

    profile_link = f"tg://user?id={sender_id}"
    clickable_name = f"<a href='{profile_link}'>{safe_name}</a>"
    return clickable_name, profile_link


def build_message_link(chat, chat_id: int, message_id: int) -> str | None:
    chat_username = getattr(chat, "username", None)

    # Public group/channel
    if chat_username:
        return f"https://t.me/{chat_username}/{message_id}"

    # Private supergroup
    if str(chat_id).startswith("-100"):
        internal_id = str(chat_id)[4:]
        return f"https://t.me/c/{internal_id}/{message_id}"

    return None


@user_client.on(events.NewMessage)
async def handle_new_message(event):
    try:
        if not get_bot_enabled():
            return

        if not event.message:
            return

        if event.chat_id in BLACKLIST:
            return

        message_key = (event.chat_id, event.message.id)
        if message_key in recent_messages:
            return

        recent_messages.add(message_key)
        if len(recent_messages) > 1000:
            recent_messages.clear()

        text_raw = (event.message.message or "").strip()
        if not text_raw:
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

        sender_id = getattr(sender, "id", event.sender_id)
        user_text, profile_link = build_user_text(sender, sender_id)

        sender_username = getattr(sender, "username", None)
        username_text = f"@{sender_username}" if sender_username else "Username yo'q"

        phone_number = getattr(sender, "phone", None)
        if phone_number:
            if phone_number.startswith("998"):
                phone_number = "+" + phone_number
        else:
            phone_number = "Telefon yo'q"

        chat_title = getattr(chat, "title", None) or "Noma'lum guruh"
        chat_username = getattr(chat, "username", None)

        if chat_username:
            group_text = f"<b>👥 Guruh:</b> <a href='https://t.me/{chat_username}'>{html.escape(chat_title)}</a>\n\n"
        else:
            group_text = f"<b>👥 Guruh:</b> {html.escape(chat_title)}\n\n"

        message_link = build_message_link(chat, event.chat_id, event.message.id)
        if message_link:
            message_link_text = f"<b>🔗 Xabar havolasi:</b> <a href='{message_link}'>Ochish</a>\n"
        else:
            message_link_text = "<b>🔗 Xabar havolasi:</b> Mavjud emas\n"

        message_text = (
            f"<b>💬 Yangi signal topildi</b>\n\n\n"
            f"<blockquote>{html.escape(text_raw)}</blockquote>\n\n\n"
            f"<b>👤 Yozgan:</b> {user_text}\n\n"
            f"<b>🔗 Profil:</b> <a href='{profile_link}'>Ochish</a>\n\n"
            f"<b>📞 Telefon:</b> {html.escape(phone_number)}\n\n"
            f"<b>🔗 Username:</b> {html.escape(username_text)}\n\n"
            f"{group_text}"
            f"{message_link_text}"
            f"<b>🔑 Topilgan kalit so'z:</b> {html.escape(matched_keyword)}\n\n"
        )

        stats_add(
            chat_id=str(event.chat_id),
            chat_title=chat_title,
            sender_name=getattr(sender, "first_name", "") or "Noma'lum",
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
        if bot_app is not None:
            try:
                await bot_app.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=f"⚠️ Telethon handler xatolik:\n<code>{html.escape(str(e))}</code>",
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                )
            except Exception:
                pass