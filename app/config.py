from pathlib import Path
from .utils import load_env_file, parse_int_set, parse_keywords

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

env = load_env_file(ENV_PATH)

API_ID = int(env.get("API_ID", "0"))
API_HASH = env.get("API_HASH", "")
BOT_TOKEN = env.get("BOT_TOKEN", "")
ADMIN_ID = int(env.get("ADMIN_ID", "0"))
SESSION_NAME = env.get("SESSION_NAME", "eldor")

ALLOWED_CHATS = parse_int_set(env.get("ALLOWED_CHATS", ""))
BLACKLIST = parse_int_set(env.get("BLACKLIST", ""))
MAX_STATS_ROWS = int(env.get("MAX_STATS_ROWS", "5"))
DEBUG = env.get("DEBUG", "0") == "1"

DEFAULT_KEYWORDS = parse_keywords(
    env.get(
        "DEFAULT_KEYWORDS",
        "pochta bor|почта бор|poshta bor|пошта бор|odam bor|одам бор|poʻchta bor|po'chta bor|ketishimiz kerak|borishimiz kerak|кетишимиз керак|боришимиз керак",
    )
)

if not API_ID or not API_HASH or not BOT_TOKEN or not ADMIN_ID:
    raise RuntimeError(
        "Sozlamalar to'liq emas. .env fayl yarating va API_ID, API_HASH, BOT_TOKEN, ADMIN_ID ni to'ldiring."
    )
