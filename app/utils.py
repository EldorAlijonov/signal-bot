from __future__ import annotations

from pathlib import Path


def load_env_file(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    if not path.exists():
        return result

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key.strip()] = value.strip()
    return result


def parse_int_set(value: str) -> set[int]:
    if not value.strip():
        return set()

    items: set[int] = set()
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        items.add(int(part))
    return items


def parse_keywords(value: str) -> list[str]:
    if not value.strip():
        return []
    return [item.strip() for item in value.split("|") if item.strip()]


def is_admin_user_id(user_id: int, admin_id: int) -> bool:
    return user_id == admin_id


def normalize_text(text: str) -> str:
    return " ".join(text.lower().strip().split())
