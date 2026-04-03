# Telegram Signal Monitor Bot

Bu loyiha 2 qismdan iborat:

1. **Telethon userbot** — siz a'zo bo'lgan guruhlardan xabarlarni kuzatadi
2. **BotFather bot** — interaktiv menyu orqali boshqaruv beradi

## Yangilangan imkoniyatlar

- Interaktiv Telegram menyu bari (`ReplyKeyboardMarkup`)
- Tugma bosilganda foydalanuvchiga alohida xabar yuboriladi
- Keyword qo'shish
- Keyword tahrirlash
- Keyword o'chirish
- Keywordlar ro'yxatini ko'rish
- SQLite database
- Log yozish
- Faqat admin boshqaruvi
- Kalit so'z asosida signal topish
- Anti-duplicate himoya
- BLACKLIST va ALLOWED_CHATS qo'llovi
- Statistika saqlash

## Avvalgi loyiha kamchiliklari

- Boshqaruv tugmalari inline callback ko'rinishida edi, menyu barida emas edi
- Tugma amallari ko'pincha bitta xabarni tahrirlash orqali ishlardi; alohida javob xabari yo'q edi
- Keywordlarni faqat ko'rish mumkin edi, qo'shish/tahrirlash/o'chirish yo'q edi
- Arxiv ichiga `.env`, `.session`, `bot_data.db` qo'shilgan edi — bu xavfsizlik jihatdan noto'g'ri

## O'rnatish

```bash
py -m pip install -r requirements.txt
```

## Sozlash

`.env.example` dan nusxa olib `.env` yarating.

Windows:
```bash
copy .env.example .env
```

Linux:
```bash
cp .env.example .env
```

## Ishga tushirish

```bash
py main.py
```

Birinchi marta Telethon sizdan telefon raqam, login kodi, ehtimol 2-step password so'raydi.

## Menyu tugmalari

- ✅ ON
- ⛔ OFF
- 📊 STATUS
- 👥 CHATS
- 🔑 KEYWORDS
- 📈 STATS
- 🔄 REFRESH

### KEYWORDS bo'limi ichida
- ➕ KEYWORD QO'SHISH
- ✏️ KEYWORD TAHRIRLASH
- 🗑 KEYWORD O'CHIRISH
- 📋 KEYWORDS RO'YXATI
- ⬅️ ORQAGA

## Muhim xavfsizlik

- `.session` faylni hech kimga bermang
- `.env` ichidagi token va hash'larni oshkor qilmang
- Token yoki session oshkor bo'lgan bo'lsa, yangisini oling
- Git yoki zip yuborishda quyidagilarni qo'shmang:
  - `.env`
  - `*.session`
  - `bot_data.db`
  - `__pycache__/`
