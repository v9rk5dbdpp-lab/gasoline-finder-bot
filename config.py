import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
CHANNEL_ID: int | None = int(os.getenv("CHANNEL_ID")) if os.getenv("CHANNEL_ID") else None
ADMIN_IDS: list[int] = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
DB_PATH: str = os.getenv("DB_PATH", "./data/reports.db")
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

# Параметры бонусной системы
REPORTS_FOR_PREMIUM: int = 20
PREMIUM_DAYS_REWARD: int = 7

# Создаём папку для БД
Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env файле!")