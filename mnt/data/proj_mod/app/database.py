from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from .config import DEFAULT_KEYWORDS, BASE_DIR

DB_PATH = BASE_DIR / "bot_data.db"

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    '''
)

cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id TEXT,
        chat_title TEXT,
        sender_name TEXT,
        keyword TEXT,
        message_text TEXT,
        created_at TEXT
    )
    '''
)

conn.commit()


def db_get(key: str, default: str = "") -> str:
    row = cur.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else default


def db_set(key: str, value: str) -> None:
    cur.execute(
        '''
        INSERT INTO settings(key, value) VALUES(?, ?)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value
        ''',
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


def stats_add(chat_id: str, chat_title: str, sender_name: str, keyword: str, message_text: str) -> None:
    cur.execute(
        '''
        INSERT INTO stats(chat_id, chat_title, sender_name, keyword, message_text, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ''',
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
            '''
            SELECT chat_title, sender_name, keyword, created_at
            FROM stats
            ORDER BY id DESC
            LIMIT ?
            ''',
            (limit,),
        ).fetchall()
    )
