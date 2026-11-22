import os
import sqlite3
import asyncio
from typing import Dict, Any, Optional

DB_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(DB_DIR, "bot.db")


def _get_connection() -> sqlite3.Connection:
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db_sync():
    """Create necessary database tables if they do not exist."""
    with _get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id INTEGER PRIMARY KEY,
                is_premium INTEGER DEFAULT 0,
                premium_expires_at TEXT DEFAULT NULL,
                anti_invite INTEGER DEFAULT 1,
                anti_spam INTEGER DEFAULT 1,
                anti_mass_mention INTEGER DEFAULT 1,
                welcome_channel_id INTEGER DEFAULT NULL
            )
            """
        )
        conn.commit()


async def init_db():
    """Async wrapper for initializing the database."""
    await asyncio.to_thread(init_db_sync)


def _get_guild_settings_sync(guild_id: int) -> Dict[str, Any]:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM guild_settings WHERE guild_id = ?", (guild_id,))
        row = cursor.fetchone()
        if not row:
            cursor.execute(
                """
                INSERT INTO guild_settings (guild_id, is_premium, anti_invite, anti_spam, anti_mass_mention)
                VALUES (?, 0, 1, 1, 1)
                """,
                (guild_id,),
            )
            conn.commit()
            cursor.execute("SELECT * FROM guild_settings WHERE guild_id = ?", (guild_id,))
            row = cursor.fetchone()
        return dict(row)


async def get_guild_settings(guild_id: int) -> Dict[str, Any]:
    """Retrieve settings for a specific guild, inserting default row if missing."""
    return await asyncio.to_thread(_get_guild_settings_sync, guild_id)


def _update_guild_setting_sync(guild_id: int, key: str, value: Any):
    allowed_keys = {
        "is_premium",
        "premium_expires_at",
        "anti_invite",
        "anti_spam",
        "anti_mass_mention",
        "welcome_channel_id",
    }
    if key not in allowed_keys:
        raise ValueError(f"Invalid setting key: {key}")

    with _get_connection() as conn:
        # Ensure row exists
        _get_guild_settings_sync(guild_id)
        conn.execute(f"UPDATE guild_settings SET {key} = ? WHERE guild_id = ?", (value, guild_id))
        conn.commit()


async def update_guild_setting(guild_id: int, key: str, value: Any):
    """Update a specific setting for a guild."""
    await asyncio.to_thread(_update_guild_setting_sync, guild_id, key, value)


async def is_guild_premium(guild_id: int) -> bool:
    """Check if a guild currently has active premium tier."""
    settings = await get_guild_settings(guild_id)
    return bool(settings.get("is_premium", 0))
