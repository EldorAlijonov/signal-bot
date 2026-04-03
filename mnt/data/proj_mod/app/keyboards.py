from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("✅ ON", callback_data="bot_on"),
            InlineKeyboardButton("⛔ OFF", callback_data="bot_off"),
        ],
        [
            InlineKeyboardButton("📊 STATUS", callback_data="bot_status"),
            InlineKeyboardButton("👥 CHATS", callback_data="bot_chats"),
        ],
        [
            InlineKeyboardButton("🔑 KEYWORDS", callback_data="bot_keywords"),
            InlineKeyboardButton("📈 STATS", callback_data="bot_stats"),
        ],
        [
            InlineKeyboardButton("🔄 REFRESH", callback_data="bot_menu"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
