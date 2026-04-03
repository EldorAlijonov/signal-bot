from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        ["✅ ON", "⛔ OFF"],
        ["📊 STATUS", "👥 CHATS"],
        ["🔑 KEYWORDS", "📈 STATS"],
        ["🔄 REFRESH"],
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        selective=False,
        input_field_placeholder="Bo'limni tanlang...",
    )


def keywords_menu_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        ["➕ KEYWORD QO'SHISH", "✏️ KEYWORD TAHRIRLASH"],
        ["🗑 KEYWORD O'CHIRISH", "📋 KEYWORDS RO'YXATI"],
        ["⬅️ ORQAGA"],
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        selective=False,
        input_field_placeholder="Keyword bo'limidan tanlang...",
    )


def remove_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()
