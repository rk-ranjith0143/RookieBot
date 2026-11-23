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
                leave_channel_id INTEGER DEFAULT NULL,
                welcome_message TEXT DEFAULT NULL,
                leave_message TEXT DEFAULT NULL,
                mod_log_channel_id INTEGER DEFAULT NULL,
                ticket_category_id INTEGER DEFAULT NULL,
                ticket_support_role_id INTEGER DEFAULT NULL,
                suggestion_channel_id INTEGER DEFAULT NULL
            )
            """
        )

        # Safe schema column migrations for existing databases
        migrations = (
            "mod_log_channel_id",
            "ticket_category_id",
            "ticket_support_role_id",
            "leave_channel_id",
            "welcome_message",
            "leave_message",
            "suggestion_channel_id",
        )
        for col in migrations:
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

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_afk (
                guild_id INTEGER,
                user_id INTEGER,
                reason TEXT,
                afk_since REAL,
                PRIMARY KEY (guild_id, user_id)
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                channel_id INTEGER,
                message TEXT,
                remind_at REAL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_economy (
                guild_id INTEGER,
                user_id INTEGER,
                balance INTEGER DEFAULT 100,
                last_daily REAL DEFAULT 0,
                PRIMARY KEY (guild_id, user_id)
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sticky_messages (
                channel_id INTEGER PRIMARY KEY,
                message_content TEXT,
                last_message_id INTEGER DEFAULT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS starboard_settings (
                guild_id INTEGER PRIMARY KEY,
                channel_id INTEGER,
                threshold INTEGER DEFAULT 3,
                is_enabled INTEGER DEFAULT 1
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS starboard_messages (
                original_message_id INTEGER PRIMARY KEY,
                starboard_message_id INTEGER,
                channel_id INTEGER,
                guild_id INTEGER,
                star_count INTEGER DEFAULT 0
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                channel_id INTEGER,
                message_id INTEGER,
                author_id INTEGER,
                content TEXT,
                status TEXT DEFAULT 'pending',
                response TEXT DEFAULT NULL,
                upvotes INTEGER DEFAULT 0,
                downvotes INTEGER DEFAULT 0,
                created_at REAL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS suggestion_votes (
                suggestion_id INTEGER,
                user_id INTEGER,
                vote_type INTEGER,
                PRIMARY KEY (suggestion_id, user_id)
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS guild_tags (
                guild_id INTEGER,
                tag_name TEXT,
                content TEXT,
                author_id INTEGER,
                uses INTEGER DEFAULT 0,
                created_at REAL,
                PRIMARY KEY (guild_id, tag_name)
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS server_stats_channels (
                guild_id INTEGER,
                stat_type TEXT,
                channel_id INTEGER,
                format_string TEXT,
                PRIMARY KEY (guild_id, stat_type)
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
        "leave_channel_id",
        "welcome_message",
        "leave_message",
        "mod_log_channel_id",
        "ticket_category_id",
        "ticket_support_role_id",
        "suggestion_channel_id",
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


# ---------------------------------------------------------------------------
# AFK System Database Operations
# ---------------------------------------------------------------------------

def _set_user_afk_sync(guild_id: int, user_id: int, reason: str = "AFK"):
    now = time.time()
    with _get_connection() as conn:
        conn.execute(
            """
            INSERT INTO user_afk (guild_id, user_id, reason, afk_since)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(guild_id, user_id) DO UPDATE SET reason = excluded.reason, afk_since = excluded.afk_since
            """,
            (guild_id, user_id, reason, now),
        )
        conn.commit()


async def set_user_afk(guild_id: int, user_id: int, reason: str = "AFK"):
    await asyncio.to_thread(_set_user_afk_sync, guild_id, user_id, reason)


def _get_user_afk_sync(guild_id: int, user_id: int) -> Optional[Dict[str, Any]]:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT reason, afk_since FROM user_afk WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id),
        )
        row = cursor.fetchone()
        return dict(row) if row else None


async def get_user_afk(guild_id: int, user_id: int) -> Optional[Dict[str, Any]]:
    return await asyncio.to_thread(_get_user_afk_sync, guild_id, user_id)


def _remove_user_afk_sync(guild_id: int, user_id: int) -> Optional[Dict[str, Any]]:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT reason, afk_since FROM user_afk WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id),
        )
        row = cursor.fetchone()
        if row:
            conn.execute(
                "DELETE FROM user_afk WHERE guild_id = ? AND user_id = ?",
                (guild_id, user_id),
            )
            conn.commit()
            return dict(row)
        return None


async def remove_user_afk(guild_id: int, user_id: int) -> Optional[Dict[str, Any]]:
    return await asyncio.to_thread(_remove_user_afk_sync, guild_id, user_id)


# ---------------------------------------------------------------------------
# Reminders Database Operations
# ---------------------------------------------------------------------------

def _add_reminder_sync(user_id: int, channel_id: int, message: str, remind_at: float) -> int:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO reminders (user_id, channel_id, message, remind_at) VALUES (?, ?, ?, ?)",
            (user_id, channel_id, message, remind_at),
        )
        conn.commit()
        return cursor.lastrowid


async def add_reminder(user_id: int, channel_id: int, message: str, remind_at: float) -> int:
    return await asyncio.to_thread(_add_reminder_sync, user_id, channel_id, message, remind_at)


def _get_due_reminders_sync(now: float) -> List[Dict[str, Any]]:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, user_id, channel_id, message, remind_at FROM reminders WHERE remind_at <= ?",
            (now,),
        )
        return [dict(r) for r in cursor.fetchall()]


async def get_due_reminders(now: float) -> List[Dict[str, Any]]:
    return await asyncio.to_thread(_get_due_reminders_sync, now)


def _delete_reminder_sync(reminder_id: int):
    with _get_connection() as conn:
        conn.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
        conn.commit()


async def delete_reminder(reminder_id: int):
    await asyncio.to_thread(_delete_reminder_sync, reminder_id)


# ---------------------------------------------------------------------------
# Economy Database Operations
# ---------------------------------------------------------------------------

def _get_user_balance_sync(guild_id: int, user_id: int) -> int:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT balance FROM user_economy WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id),
        )
        row = cursor.fetchone()
        if not row:
            conn.execute(
                "INSERT INTO user_economy (guild_id, user_id, balance, last_daily) VALUES (?, ?, 100, 0)",
                (guild_id, user_id),
            )
            conn.commit()
            return 100
        return row["balance"]


async def get_user_balance(guild_id: int, user_id: int) -> int:
    return await asyncio.to_thread(_get_user_balance_sync, guild_id, user_id)


def _update_user_balance_sync(guild_id: int, user_id: int, delta: int) -> int:
    with _get_connection() as conn:
        current = _get_user_balance_sync(guild_id, user_id)
        new_balance = max(0, current + delta)
        conn.execute(
            "UPDATE user_economy SET balance = ? WHERE guild_id = ? AND user_id = ?",
            (new_balance, guild_id, user_id),
        )
        conn.commit()
        return new_balance


async def update_user_balance(guild_id: int, user_id: int, delta: int) -> int:
    return await asyncio.to_thread(_update_user_balance_sync, guild_id, user_id, delta)


def _claim_daily_sync(
    guild_id: int,
    user_id: int,
    reward: int = 200,
    cooldown_seconds: float = 86400.0,
) -> Tuple[bool, int, float]:
    now = time.time()
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT balance, last_daily FROM user_economy WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id),
        )
        row = cursor.fetchone()
        if not row:
            conn.execute(
                "INSERT INTO user_economy (guild_id, user_id, balance, last_daily) VALUES (?, ?, ?, ?)",
                (guild_id, user_id, 100 + reward, now),
            )
            conn.commit()
            return True, 100 + reward, 0.0

        balance, last_daily = row["balance"], row["last_daily"]
        time_passed = now - last_daily
        if time_passed < cooldown_seconds:
            remaining = cooldown_seconds - time_passed
            return False, balance, remaining

        new_balance = balance + reward
        conn.execute(
            "UPDATE user_economy SET balance = ?, last_daily = ? WHERE guild_id = ? AND user_id = ?",
            (new_balance, now, guild_id, user_id),
        )
        conn.commit()
        return True, new_balance, 0.0


async def claim_daily(
    guild_id: int,
    user_id: int,
    reward: int = 200,
    cooldown_seconds: float = 86400.0,
) -> Tuple[bool, int, float]:
    return await asyncio.to_thread(_claim_daily_sync, guild_id, user_id, reward, cooldown_seconds)


# ---------------------------------------------------------------------------
# Sticky Messages Database Operations
# ---------------------------------------------------------------------------

def _set_sticky_message_sync(channel_id: int, content: str):
    with _get_connection() as conn:
        conn.execute(
            """
            INSERT INTO sticky_messages (channel_id, message_content, last_message_id)
            VALUES (?, ?, NULL)
            ON CONFLICT(channel_id) DO UPDATE SET message_content = excluded.message_content
            """,
            (channel_id, content),
        )
        conn.commit()


async def set_sticky_message(channel_id: int, content: str):
    await asyncio.to_thread(_set_sticky_message_sync, channel_id, content)


def _get_sticky_message_sync(channel_id: int) -> Optional[Dict[str, Any]]:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT channel_id, message_content, last_message_id FROM sticky_messages WHERE channel_id = ?",
            (channel_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None


async def get_sticky_message(channel_id: int) -> Optional[Dict[str, Any]]:
    return await asyncio.to_thread(_get_sticky_message_sync, channel_id)


def _update_sticky_last_id_sync(channel_id: int, last_id: Optional[int]):
    with _get_connection() as conn:
        conn.execute(
            "UPDATE sticky_messages SET last_message_id = ? WHERE channel_id = ?",
            (last_id, channel_id),
        )
        conn.commit()


async def update_sticky_last_id(channel_id: int, last_id: Optional[int]):
    await asyncio.to_thread(_update_sticky_last_id_sync, channel_id, last_id)


def _delete_sticky_message_sync(channel_id: int):
    with _get_connection() as conn:
        conn.execute("DELETE FROM sticky_messages WHERE channel_id = ?", (channel_id,))
        conn.commit()


async def delete_sticky_message(channel_id: int):
    await asyncio.to_thread(_delete_sticky_message_sync, channel_id)


# ---------------------------------------------------------------------------
# Starboard Database Operations
# ---------------------------------------------------------------------------

def _set_starboard_settings_sync(guild_id: int, channel_id: int, threshold: int = 3, is_enabled: int = 1):
    with _get_connection() as conn:
        conn.execute(
            """
            INSERT INTO starboard_settings (guild_id, channel_id, threshold, is_enabled)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET
                channel_id = excluded.channel_id,
                threshold = excluded.threshold,
                is_enabled = excluded.is_enabled
            """,
            (guild_id, channel_id, threshold, is_enabled),
        )
        conn.commit()


async def set_starboard_settings(guild_id: int, channel_id: int, threshold: int = 3, is_enabled: int = 1):
    await asyncio.to_thread(_set_starboard_settings_sync, guild_id, channel_id, threshold, is_enabled)


def _get_starboard_settings_sync(guild_id: int) -> Optional[Dict[str, Any]]:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM starboard_settings WHERE guild_id = ?", (guild_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


async def get_starboard_settings(guild_id: int) -> Optional[Dict[str, Any]]:
    return await asyncio.to_thread(_get_starboard_settings_sync, guild_id)


def _disable_starboard_sync(guild_id: int):
    with _get_connection() as conn:
        conn.execute("UPDATE starboard_settings SET is_enabled = 0 WHERE guild_id = ?", (guild_id,))
        conn.commit()


async def disable_starboard(guild_id: int):
    await asyncio.to_thread(_disable_starboard_sync, guild_id)


def _get_starboard_message_sync(original_message_id: int) -> Optional[Dict[str, Any]]:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM starboard_messages WHERE original_message_id = ?", (original_message_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


async def get_starboard_message(original_message_id: int) -> Optional[Dict[str, Any]]:
    return await asyncio.to_thread(_get_starboard_message_sync, original_message_id)


def _save_starboard_message_sync(
    original_message_id: int,
    starboard_message_id: int,
    channel_id: int,
    guild_id: int,
    star_count: int,
):
    with _get_connection() as conn:
        conn.execute(
            """
            INSERT INTO starboard_messages (original_message_id, starboard_message_id, channel_id, guild_id, star_count)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(original_message_id) DO UPDATE SET
                starboard_message_id = excluded.starboard_message_id,
                star_count = excluded.star_count
            """,
            (original_message_id, starboard_message_id, channel_id, guild_id, star_count),
        )
        conn.commit()


async def save_starboard_message(
    original_message_id: int,
    starboard_message_id: int,
    channel_id: int,
    guild_id: int,
    star_count: int,
):
    await asyncio.to_thread(
        _save_starboard_message_sync,
        original_message_id,
        starboard_message_id,
        channel_id,
        guild_id,
        star_count,
    )


def _update_starboard_count_sync(original_message_id: int, star_count: int):
    with _get_connection() as conn:
        conn.execute(
            "UPDATE starboard_messages SET star_count = ? WHERE original_message_id = ?",
            (star_count, original_message_id),
        )
        conn.commit()


async def update_starboard_count(original_message_id: int, star_count: int):
    await asyncio.to_thread(_update_starboard_count_sync, original_message_id, star_count)


def _delete_starboard_message_sync(original_message_id: int):
    with _get_connection() as conn:
        conn.execute("DELETE FROM starboard_messages WHERE original_message_id = ?", (original_message_id,))
        conn.commit()


async def delete_starboard_message(original_message_id: int):
    await asyncio.to_thread(_delete_starboard_message_sync, original_message_id)


# ---------------------------------------------------------------------------
# Suggestions Database Operations
# ---------------------------------------------------------------------------

def _create_suggestion_sync(guild_id: int, channel_id: int, message_id: int, author_id: int, content: str) -> int:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO suggestions (guild_id, channel_id, message_id, author_id, content, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'pending', ?)
            """,
            (guild_id, channel_id, message_id, author_id, content, time.time()),
        )
        conn.commit()
        return cursor.lastrowid


async def create_suggestion(guild_id: int, channel_id: int, message_id: int, author_id: int, content: str) -> int:
    return await asyncio.to_thread(_create_suggestion_sync, guild_id, channel_id, message_id, author_id, content)


def _get_suggestion_sync(suggestion_id: int) -> Optional[Dict[str, Any]]:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM suggestions WHERE id = ?", (suggestion_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


async def get_suggestion(suggestion_id: int) -> Optional[Dict[str, Any]]:
    return await asyncio.to_thread(_get_suggestion_sync, suggestion_id)


def _get_suggestion_by_message_sync(message_id: int) -> Optional[Dict[str, Any]]:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM suggestions WHERE message_id = ?", (message_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


async def get_suggestion_by_message(message_id: int) -> Optional[Dict[str, Any]]:
    return await asyncio.to_thread(_get_suggestion_by_message_sync, message_id)


def _update_suggestion_status_sync(suggestion_id: int, status: str, response: Optional[str] = None):
    with _get_connection() as conn:
        conn.execute(
            "UPDATE suggestions SET status = ?, response = ? WHERE id = ?",
            (status, response, suggestion_id),
        )
        conn.commit()


async def update_suggestion_status(suggestion_id: int, status: str, response: Optional[str] = None):
    await asyncio.to_thread(_update_suggestion_status_sync, suggestion_id, status, response)


def _vote_suggestion_sync(suggestion_id: int, user_id: int, vote_type: int) -> Tuple[bool, int, int]:
    """Record or toggle an upvote (+1) or downvote (-1). Returns (has_voted, upvotes, downvotes)."""
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT vote_type FROM suggestion_votes WHERE suggestion_id = ? AND user_id = ?",
            (suggestion_id, user_id),
        )
        existing = cursor.fetchone()
        if existing and existing["vote_type"] == vote_type:
            # User clicked the same vote again: remove it (toggle off)
            conn.execute(
                "DELETE FROM suggestion_votes WHERE suggestion_id = ? AND user_id = ?",
                (suggestion_id, user_id),
            )
        else:
            # Insert or replace user vote
            conn.execute(
                """
                INSERT INTO suggestion_votes (suggestion_id, user_id, vote_type)
                VALUES (?, ?, ?)
                ON CONFLICT(suggestion_id, user_id) DO UPDATE SET vote_type = excluded.vote_type
                """,
                (suggestion_id, user_id, vote_type),
            )

        # Recalculate upvotes and downvotes
        cursor.execute("SELECT COUNT(*) FROM suggestion_votes WHERE suggestion_id = ? AND vote_type = 1", (suggestion_id,))
        upvotes = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM suggestion_votes WHERE suggestion_id = ? AND vote_type = -1", (suggestion_id,))
        downvotes = cursor.fetchone()[0]

        conn.execute(
            "UPDATE suggestions SET upvotes = ?, downvotes = ? WHERE id = ?",
            (upvotes, downvotes, suggestion_id),
        )
        conn.commit()
        return True, upvotes, downvotes


async def vote_suggestion(suggestion_id: int, user_id: int, vote_type: int) -> Tuple[bool, int, int]:
    return await asyncio.to_thread(_vote_suggestion_sync, suggestion_id, user_id, vote_type)


# ---------------------------------------------------------------------------
# Custom Tags / Auto-FAQ Database Operations
# ---------------------------------------------------------------------------

def _create_tag_sync(guild_id: int, tag_name: str, content: str, author_id: int) -> bool:
    tag_name = tag_name.lower().strip()
    with _get_connection() as conn:
        try:
            conn.execute(
                """
                INSERT INTO guild_tags (guild_id, tag_name, content, author_id, uses, created_at)
                VALUES (?, ?, ?, ?, 0, ?)
                """,
                (guild_id, tag_name, content, author_id, time.time()),
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False


async def create_tag(guild_id: int, tag_name: str, content: str, author_id: int) -> bool:
    return await asyncio.to_thread(_create_tag_sync, guild_id, tag_name, content, author_id)


def _get_tag_sync(guild_id: int, tag_name: str, increment_uses: bool = True) -> Optional[Dict[str, Any]]:
    tag_name = tag_name.lower().strip()
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM guild_tags WHERE guild_id = ? AND tag_name = ?",
            (guild_id, tag_name),
        )
        row = cursor.fetchone()
        if not row:
            return None
        res = dict(row)
        if increment_uses:
            conn.execute(
                "UPDATE guild_tags SET uses = uses + 1 WHERE guild_id = ? AND tag_name = ?",
                (guild_id, tag_name),
            )
            conn.commit()
            res["uses"] += 1
        return res


async def get_tag(guild_id: int, tag_name: str, increment_uses: bool = True) -> Optional[Dict[str, Any]]:
    return await asyncio.to_thread(_get_tag_sync, guild_id, tag_name, increment_uses)


def _delete_tag_sync(guild_id: int, tag_name: str) -> bool:
    tag_name = tag_name.lower().strip()
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM guild_tags WHERE guild_id = ? AND tag_name = ?",
            (guild_id, tag_name),
        )
        conn.commit()
        return cursor.rowcount > 0


async def delete_tag(guild_id: int, tag_name: str) -> bool:
    return await asyncio.to_thread(_delete_tag_sync, guild_id, tag_name)


def _list_tags_sync(guild_id: int) -> List[Dict[str, Any]]:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT tag_name, author_id, uses, created_at FROM guild_tags WHERE guild_id = ? ORDER BY tag_name ASC",
            (guild_id,),
        )
        return [dict(row) for row in cursor.fetchall()]


async def list_tags(guild_id: int) -> List[Dict[str, Any]]:
    return await asyncio.to_thread(_list_tags_sync, guild_id)


def _search_tags_sync(guild_id: int, query: str, limit: int = 25) -> List[str]:
    query = f"%{query.lower().strip()}%"
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT tag_name FROM guild_tags WHERE guild_id = ? AND tag_name LIKE ? ORDER BY uses DESC LIMIT ?",
            (guild_id, query, limit),
        )
        return [row["tag_name"] for row in cursor.fetchall()]


async def search_tags(guild_id: int, query: str, limit: int = 25) -> List[str]:
    return await asyncio.to_thread(_search_tags_sync, guild_id, query, limit)


# ---------------------------------------------------------------------------
# Server Stats Channels Database Operations
# ---------------------------------------------------------------------------

def _set_server_stat_channel_sync(guild_id: int, stat_type: str, channel_id: int, format_string: str):
    with _get_connection() as conn:
        conn.execute(
            """
            INSERT INTO server_stats_channels (guild_id, stat_type, channel_id, format_string)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(guild_id, stat_type) DO UPDATE SET
                channel_id = excluded.channel_id,
                format_string = excluded.format_string
            """,
            (guild_id, stat_type, channel_id, format_string),
        )
        conn.commit()


async def set_server_stat_channel(guild_id: int, stat_type: str, channel_id: int, format_string: str):
    await asyncio.to_thread(_set_server_stat_channel_sync, guild_id, stat_type, channel_id, format_string)


def _get_server_stat_channels_sync(guild_id: int) -> List[Dict[str, Any]]:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM server_stats_channels WHERE guild_id = ?", (guild_id,))
        return [dict(row) for row in cursor.fetchall()]


async def get_server_stat_channels(guild_id: int) -> List[Dict[str, Any]]:
    return await asyncio.to_thread(_get_server_stat_channels_sync, guild_id)


def _remove_server_stat_channels_sync(guild_id: int):
    with _get_connection() as conn:
        conn.execute("DELETE FROM server_stats_channels WHERE guild_id = ?", (guild_id,))
        conn.commit()


async def remove_server_stat_channels(guild_id: int):
    await asyncio.to_thread(_remove_server_stat_channels_sync, guild_id)

