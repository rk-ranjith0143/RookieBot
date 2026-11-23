import os
import time
import sqlite3
import asyncio
from typing import Dict, Any, Optional, Tuple, List

DB_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(DB_DIR, "bot.db")


def _get_connection() -> sqlite3.Connection:
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db_sync():
    """Create necessary database tables and perform migrations."""
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
                welcome_channel_id INTEGER DEFAULT NULL,
                mod_log_channel_id INTEGER DEFAULT NULL,
                ticket_category_id INTEGER DEFAULT NULL,
                ticket_support_role_id INTEGER DEFAULT NULL
            )
            """
        )

        # Safe schema column migrations for existing databases
        for col in ("mod_log_channel_id", "ticket_category_id", "ticket_support_role_id"):
            try:
                conn.execute(f"ALTER TABLE guild_settings ADD COLUMN {col} INTEGER DEFAULT NULL")
            except sqlite3.OperationalError:
                pass

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_levels (
                guild_id INTEGER,
                user_id INTEGER,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                last_xp_time REAL DEFAULT 0,
                PRIMARY KEY (guild_id, user_id)
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
        "mod_log_channel_id",
        "ticket_category_id",
        "ticket_support_role_id",
    }
    if key not in allowed_keys:
        raise ValueError(f"Invalid setting key: {key}")

    with _get_connection() as conn:
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


# ---------------------------------------------------------------------------
# Leveling / XP System Database Operations
# ---------------------------------------------------------------------------

def _add_user_xp_sync(
    guild_id: int,
    user_id: int,
    amount: int,
    cooldown_seconds: float = 60.0,
) -> Tuple[bool, int, int]:
    """
    Adds XP with cooldown check.
    Returns: (leveled_up: bool, new_level: int, current_xp: int)
    """
    now = time.time()
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT xp, level, last_xp_time FROM user_levels WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id),
        )
        row = cursor.fetchone()

        if not row:
            xp = amount
            level = 1
            leveled_up = False
            while xp >= level * 100:
                xp -= level * 100
                level += 1
                leveled_up = True
            cursor.execute(
                "INSERT INTO user_levels (guild_id, user_id, xp, level, last_xp_time) VALUES (?, ?, ?, ?, ?)",
                (guild_id, user_id, xp, level, now),
            )
            conn.commit()
            return leveled_up, level, xp

        xp, level, last_time = row["xp"], row["level"], row["last_xp_time"]

        # Check rate-limit cooldown
        if now - last_time < cooldown_seconds:
            return False, level, xp

        xp += amount
        leveled_up = False
        while xp >= level * 100:
            xp -= level * 100
            level += 1
            leveled_up = True

        cursor.execute(
            "UPDATE user_levels SET xp = ?, level = ?, last_xp_time = ? WHERE guild_id = ? AND user_id = ?",
            (xp, level, now, guild_id, user_id),
        )
        conn.commit()
        return leveled_up, level, xp


async def add_user_xp(
    guild_id: int,
    user_id: int,
    amount: int,
    cooldown_seconds: float = 60.0,
) -> Tuple[bool, int, int]:
    return await asyncio.to_thread(_add_user_xp_sync, guild_id, user_id, amount, cooldown_seconds)


def _get_user_level_data_sync(guild_id: int, user_id: int) -> Tuple[int, int, int, int]:
    """Returns (rank, level, xp, xp_needed_for_next_level)."""
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT xp, level FROM user_levels WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id),
        )
        row = cursor.fetchone()
        if not row:
            return 1, 1, 0, 100

        user_xp = row["xp"]
        user_level = row["level"]

        # Calculate rank
        cursor.execute(
            """
            SELECT COUNT(*) + 1 AS rank FROM user_levels
            WHERE guild_id = ? AND (level > ? OR (level = ? AND xp > ?))
            """,
            (guild_id, user_level, user_level, user_xp),
        )
        rank = cursor.fetchone()["rank"]
        xp_needed = user_level * 100
        return rank, user_level, user_xp, xp_needed


async def get_user_level_data(guild_id: int, user_id: int) -> Tuple[int, int, int, int]:
    return await asyncio.to_thread(_get_user_level_data_sync, guild_id, user_id)


def _get_top_leaderboard_sync(guild_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT user_id, level, xp FROM user_levels
            WHERE guild_id = ?
            ORDER BY level DESC, xp DESC
            LIMIT ?
            """,
            (guild_id, limit),
        )
        return [dict(r) for r in cursor.fetchall()]


async def get_top_leaderboard(guild_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    return await asyncio.to_thread(_get_top_leaderboard_sync, guild_id, limit)
