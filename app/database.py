from __future__ import annotations

import sqlite3
from datetime import datetime

from .config import DEFAULT_KEYWORDS, BASE_DIR

DB_PATH = BASE_DIR / "bot_data.db"

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """
)

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id TEXT,
        chat_title TEXT,
        sender_name TEXT,
        keyword TEXT,
        message_text TEXT,
        created_at TEXT
    )
    """
)

conn.commit()


def db_get(key: str, default: str = "") -> str:
    row = cur.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else default


def db_set(key: str, value: str) -> None:
    cur.execute(
        """
        INSERT INTO settings(key, value) VALUES(?, ?)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value
        """,
        (key, value),
    )
    conn.commit()


def init_db() -> None:
    if db_get("bot_enabled", "") == "":
        db_set("bot_enabled", "1")

    if db_get("keywords", "") == "":
        db_set("keywords", "||".join(DEFAULT_KEYWORDS))


def get_bot_enabled() -> bool:
    return db_get("bot_enabled", "1") == "1"


def set_bot_enabled(value: bool) -> None:
    db_set("bot_enabled", "1" if value else "0")


def get_keywords() -> list[str]:
    raw = db_get("keywords", "")
    if not raw.strip():
        return []
    return [x.strip() for x in raw.split("||") if x.strip()]


def _save_keywords(words: list[str]) -> None:
    cleaned: list[str] = []
    seen: set[str] = set()
    for word in words:
        item = word.strip()
        if not item:
            continue
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        cleaned.append(item)
    db_set("keywords", "||".join(cleaned))


def add_keyword(new_word: str) -> bool:
    new_word = new_word.strip()
    if not new_word:
        return False

    words = get_keywords()
    if any(item.lower() == new_word.lower() for item in words):
        return False

    words.append(new_word)
    _save_keywords(words)
    return True


def remove_keyword(word: str) -> bool:
    words = get_keywords()
    for item in words:
        if item.lower() == word.strip().lower():
            words.remove(item)
            _save_keywords(words)
            return True
    return False


def update_keyword(old_word: str, new_word: str) -> bool:
    old_word = old_word.strip()
    new_word = new_word.strip()
    if not old_word or not new_word:
        return False

    words = get_keywords()
    for idx, item in enumerate(words):
        if item.lower() == old_word.lower():
            if any(existing.lower() == new_word.lower() for existing in words if existing.lower() != old_word.lower()):
                return False
            words[idx] = new_word
            _save_keywords(words)
            return True
    return False


def stats_add(chat_id: str, chat_title: str, sender_name: str, keyword: str, message_text: str) -> None:
    cur.execute(
        """
        INSERT INTO stats(chat_id, chat_title, sender_name, keyword, message_text, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            str(chat_id),
            chat_title,
            sender_name,
            keyword,
            message_text,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    conn.commit()


def stats_count() -> int:
    row = cur.execute("SELECT COUNT(*) AS cnt FROM stats").fetchone()
    return int(row["cnt"]) if row else 0


def stats_last(limit: int = 5) -> list[sqlite3.Row]:
    return list(
        cur.execute(
            """
            SELECT chat_title, sender_name, keyword, message_text, created_at
            FROM stats
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    )
