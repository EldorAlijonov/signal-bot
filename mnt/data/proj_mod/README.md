# Telegram Signal Monitor Bot

Bu loyiha 2 qismdan iborat:

1. **Telethon userbot** — siz a'zo bo'lgan guruhlardan xabarlarni kuzatadi
2. **BotFather bot** — sizga tugmalar orqali boshqaruv panelini beradi

## Imkoniyatlar

- Tugmalar orqali boshqarish:
  - ON
  - OFF
  - STATUS
  - CHATS
  - KEYWORDS
  - STATS
- SQLite database
- Log yozish
- Faqat admin boshqaruvi
- Kalit so'z asosida signal topish
- Statistika saqlash
- Serverda ishlatishga tayyor tuzilma

## O'rnatish

```bash
py -m pip install -r requirements.txt
```

## Sozlash

`.env.example` faylidan nusxa olib `.env` yarating va ichini to'ldiring.

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

## Muhim

- `.session` faylni hech kimga bermang
- `.env` ichidagi token va hash'larni oshkor qilmang
- Oddiy BotFather bot barcha guruhlardan mustaqil o'qiy olmaydi; bu ishni Telethon qismi bajaradi
