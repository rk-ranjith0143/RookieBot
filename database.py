import os
import time
import sqlite3
import asyncio
import secrets
from typing import Dict, Any, Optional, Tuple, List

DB_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(DB_DIR, "bot.db")


def _get_connection() -> sqlite3.Connection:
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=20.0)
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
                ticket_transcript_channel_id INTEGER DEFAULT NULL,
                suggestion_channel_id INTEGER DEFAULT NULL
            )
            """
        )

        # Safe schema column migrations for existing databases
        migrations = (
            "mod_log_channel_id",
            "ticket_category_id",
            "ticket_support_role_id",
            "ticket_transcript_channel_id",
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

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS premium_keys (
                key_code TEXT PRIMARY KEY,
                duration_days INTEGER,
                created_at REAL,
                is_redeemed INTEGER DEFAULT 0,
                redeemed_by_guild_id INTEGER DEFAULT NULL,
                redeemed_by_user_id INTEGER DEFAULT NULL,
                redeemed_at REAL DEFAULT NULL,
                note TEXT DEFAULT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS autoroles (
                guild_id INTEGER PRIMARY KEY,
                member_role_id INTEGER DEFAULT NULL,
                bot_role_id INTEGER DEFAULT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS autoresponders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                trigger_phrase TEXT,
                response_text TEXT,
                is_exact INTEGER DEFAULT 0
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS level_roles (
                guild_id INTEGER,
                level INTEGER,
                role_id INTEGER,
                PRIMARY KEY (guild_id, level)
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS infractions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                user_id INTEGER,
                moderator_id INTEGER,
                action_type TEXT DEFAULT 'warn',
                reason TEXT,
                created_at REAL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS verification_settings (
                guild_id INTEGER PRIMARY KEY,
                channel_id INTEGER,
                role_id INTEGER,
                message_id INTEGER DEFAULT NULL,
                is_enabled INTEGER DEFAULT 1
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS temp_vc_settings (
                guild_id INTEGER PRIMARY KEY,
                master_channel_id INTEGER,
                category_id INTEGER DEFAULT NULL,
                is_enabled INTEGER DEFAULT 1
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS temp_vc_channels (
                channel_id INTEGER PRIMARY KEY,
                guild_id INTEGER,
                owner_id INTEGER,
                created_at REAL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS economy_shop (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                item_name TEXT,
                description TEXT,
                price INTEGER,
                role_id INTEGER DEFAULT NULL,
                created_at REAL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                user_id INTEGER,
                item_id INTEGER,
                item_name TEXT,
                role_id INTEGER DEFAULT NULL,
                purchased_at REAL
            )
            """
        )

        try:
            conn.execute("ALTER TABLE user_economy ADD COLUMN last_work REAL DEFAULT 0")
        except sqlite3.OperationalError:
            pass

        try:
            conn.execute("ALTER TABLE sticky_messages ADD COLUMN guild_id INTEGER DEFAULT NULL")
        except sqlite3.OperationalError:
            pass

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
        "ticket_transcript_channel_id",
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


def _is_guild_premium_sync(guild_id: int) -> bool:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT is_premium, premium_expires_at FROM guild_settings WHERE guild_id = ?", (guild_id,))
        row = cursor.fetchone()
        if not row or not row["is_premium"]:
            return False

        expires_at = row["premium_expires_at"]
        if expires_at is not None:
            try:
                exp_ts = float(expires_at)
                if time.time() > exp_ts:
                    conn.execute("UPDATE guild_settings SET is_premium = 0 WHERE guild_id = ?", (guild_id,))
                    conn.commit()
                    return False
            except ValueError:
                pass
        return True


async def is_guild_premium(guild_id: int) -> bool:
    """Check if a guild currently has active premium tier."""
    return await asyncio.to_thread(_is_guild_premium_sync, guild_id)


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

def _set_sticky_message_sync(channel_id: int, content: str, guild_id: Optional[int] = None):
    with _get_connection() as conn:
        conn.execute(
            """
            INSERT INTO sticky_messages (channel_id, guild_id, message_content, last_message_id)
            VALUES (?, ?, ?, NULL)
            ON CONFLICT(channel_id) DO UPDATE SET
                message_content = excluded.message_content,
                guild_id = COALESCE(excluded.guild_id, sticky_messages.guild_id)
            """,
            (channel_id, guild_id, content),
        )
        conn.commit()


async def set_sticky_message(channel_id: int, content: str, guild_id: Optional[int] = None):
    await asyncio.to_thread(_set_sticky_message_sync, channel_id, content, guild_id)


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


# ---------------------------------------------------------------------------
# Premium Licensing & Monetization Database Operations
# ---------------------------------------------------------------------------

def _generate_key_string() -> str:
    parts = [secrets.token_hex(2).upper() for _ in range(3)]
    return f"PREM-{parts[0]}-{parts[1]}-{parts[2]}"


def _create_premium_key_sync(duration_days: int = 30, note: Optional[str] = None) -> str:
    key_code = _generate_key_string()
    with _get_connection() as conn:
        conn.execute(
            """
            INSERT INTO premium_keys (key_code, duration_days, created_at, is_redeemed, note)
            VALUES (?, ?, ?, 0, ?)
            """,
            (key_code, duration_days, time.time(), note),
        )
        conn.commit()
    return key_code


async def create_premium_key(duration_days: int = 30, note: Optional[str] = None) -> str:
    return await asyncio.to_thread(_create_premium_key_sync, duration_days, note)


def _redeem_premium_key_sync(key_code: str, guild_id: int, user_id: int) -> Tuple[bool, str, Optional[float]]:
    key_code = key_code.strip().upper()
    now = time.time()
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM premium_keys WHERE key_code = ?", (key_code,))
        row = cursor.fetchone()
        if not row:
            return False, "❌ Invalid license key. Please check the key and try again.", None
        if row["is_redeemed"]:
            return False, "❌ This license key has already been redeemed.", None

        duration_days = row["duration_days"]

        # Check existing guild subscription
        cursor.execute("SELECT is_premium, premium_expires_at FROM guild_settings WHERE guild_id = ?", (guild_id,))
        guild_row = cursor.fetchone()

        base_time = now
        if guild_row and guild_row["is_premium"] and guild_row["premium_expires_at"]:
            try:
                current_exp = float(guild_row["premium_expires_at"])
                if current_exp > now:
                    base_time = current_exp  # Extend existing active subscription
            except ValueError:
                pass

        if duration_days == -1:
            new_expiry = None
            expiry_str = None
        else:
            new_expiry = base_time + (duration_days * 86400)
            expiry_str = str(new_expiry)

        # Mark key redeemed
        conn.execute(
            """
            UPDATE premium_keys
            SET is_redeemed = 1, redeemed_by_guild_id = ?, redeemed_by_user_id = ?, redeemed_at = ?
            WHERE key_code = ?
            """,
            (guild_id, user_id, now, key_code),
        )

        # Ensure guild settings exist and update
        cursor.execute("SELECT guild_id FROM guild_settings WHERE guild_id = ?", (guild_id,))
        if not cursor.fetchone():
            conn.execute(
                """
                INSERT INTO guild_settings (guild_id, is_premium, premium_expires_at, anti_invite, anti_spam, anti_mass_mention)
                VALUES (?, 1, ?, 1, 1, 1)
                """,
                (guild_id, expiry_str),
            )
        else:
            conn.execute(
                "UPDATE guild_settings SET is_premium = 1, premium_expires_at = ? WHERE guild_id = ?",
                (expiry_str, guild_id),
            )
        conn.commit()
        return True, "✅ License redeemed successfully! Premium perks unlocked.", new_expiry


async def redeem_premium_key(key_code: str, guild_id: int, user_id: int) -> Tuple[bool, str, Optional[float]]:
    return await asyncio.to_thread(_redeem_premium_key_sync, key_code, guild_id, user_id)


def _revoke_guild_premium_sync(guild_id: int):
    with _get_connection() as conn:
        conn.execute(
            "UPDATE guild_settings SET is_premium = 0, premium_expires_at = NULL WHERE guild_id = ?",
            (guild_id,),
        )
        conn.commit()


async def revoke_guild_premium(guild_id: int):
    await asyncio.to_thread(_revoke_guild_premium_sync, guild_id)


def _get_guild_premium_details_sync(guild_id: int) -> Dict[str, Any]:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT is_premium, premium_expires_at FROM guild_settings WHERE guild_id = ?", (guild_id,))
        row = cursor.fetchone()
        if not row or not row["is_premium"]:
            return {"is_premium": False, "expires_at": None, "days_remaining": 0, "is_lifetime": False}

        expires_at = row["premium_expires_at"]
        if expires_at is None:
            return {"is_premium": True, "expires_at": None, "days_remaining": None, "is_lifetime": True}

        try:
            exp_ts = float(expires_at)
            now = time.time()
            if now > exp_ts:
                conn.execute("UPDATE guild_settings SET is_premium = 0 WHERE guild_id = ?", (guild_id,))
                conn.commit()
                return {"is_premium": False, "expires_at": None, "days_remaining": 0, "is_lifetime": False}
            days_left = max(0, int((exp_ts - now) // 86400))
            return {"is_premium": True, "expires_at": exp_ts, "days_remaining": days_left, "is_lifetime": False}
        except ValueError:
            return {"is_premium": True, "expires_at": None, "days_remaining": None, "is_lifetime": True}


async def get_guild_premium_details(guild_id: int) -> Dict[str, Any]:
    return await asyncio.to_thread(_get_guild_premium_details_sync, guild_id)


def _list_premium_keys_sync(limit: int = 50) -> List[Dict[str, Any]]:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT key_code, duration_days, created_at, is_redeemed, redeemed_by_guild_id, note
            FROM premium_keys
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        )
        return [dict(row) for row in cursor.fetchall()]


async def list_premium_keys(limit: int = 50) -> List[Dict[str, Any]]:
    return await asyncio.to_thread(_list_premium_keys_sync, limit)


def _check_and_expire_premium_guilds_sync() -> List[int]:
    now = time.time()
    expired_guild_ids = []
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT guild_id, premium_expires_at FROM guild_settings WHERE is_premium = 1 AND premium_expires_at IS NOT NULL")
        for row in cursor.fetchall():
            try:
                exp_ts = float(row["premium_expires_at"])
                if now > exp_ts:
                    expired_guild_ids.append(row["guild_id"])
            except ValueError:
                pass

        if expired_guild_ids:
            placeholders = ",".join("?" for _ in expired_guild_ids)
            conn.execute(
                f"UPDATE guild_settings SET is_premium = 0 WHERE guild_id IN ({placeholders})",
                expired_guild_ids,
            )
            conn.commit()
    return expired_guild_ids


async def check_and_expire_premium_guilds() -> List[int]:
    return await asyncio.to_thread(_check_and_expire_premium_guilds_sync)


def _get_guild_tag_count_sync(guild_id: int) -> int:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM guild_tags WHERE guild_id = ?", (guild_id,))
        return cursor.fetchone()[0]


async def get_guild_tag_count(guild_id: int) -> int:
    return await asyncio.to_thread(_get_guild_tag_count_sync, guild_id)


def _get_guild_sticky_count_sync(guild_id: int) -> int:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sticky_messages WHERE guild_id = ?", (guild_id,))
        return cursor.fetchone()[0]


async def get_guild_sticky_count(guild_id: int) -> int:
    return await asyncio.to_thread(_get_guild_sticky_count_sync, guild_id)


# ---------------------------------------------------------------------------
# Auto-Role Database Operations
# ---------------------------------------------------------------------------

def _set_autoroles_sync(guild_id: int, member_role_id: Optional[int], bot_role_id: Optional[int]):
    with _get_connection() as conn:
        conn.execute(
            """
            INSERT INTO autoroles (guild_id, member_role_id, bot_role_id)
            VALUES (?, ?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET
                member_role_id = COALESCE(excluded.member_role_id, autoroles.member_role_id),
                bot_role_id = COALESCE(excluded.bot_role_id, autoroles.bot_role_id)
            """,
            (guild_id, member_role_id, bot_role_id),
        )
        conn.commit()


async def set_autoroles(guild_id: int, member_role_id: Optional[int] = None, bot_role_id: Optional[int] = None):
    await asyncio.to_thread(_set_autoroles_sync, guild_id, member_role_id, bot_role_id)


def _get_autoroles_sync(guild_id: int) -> Optional[Dict[str, Any]]:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM autoroles WHERE guild_id = ?", (guild_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


async def get_autoroles(guild_id: int) -> Optional[Dict[str, Any]]:
    return await asyncio.to_thread(_get_autoroles_sync, guild_id)


def _remove_autoroles_sync(guild_id: int):
    with _get_connection() as conn:
        conn.execute("DELETE FROM autoroles WHERE guild_id = ?", (guild_id,))
        conn.commit()


async def remove_autoroles(guild_id: int):
    await asyncio.to_thread(_remove_autoroles_sync, guild_id)


# ---------------------------------------------------------------------------
# Auto-Responder Database Operations
# ---------------------------------------------------------------------------

def _add_autoresponder_sync(guild_id: int, trigger: str, response: str, is_exact: int = 0) -> int:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO autoresponders (guild_id, trigger_phrase, response_text, is_exact)
            VALUES (?, ?, ?, ?)
            """,
            (guild_id, trigger.strip().lower(), response.strip(), is_exact),
        )
        conn.commit()
        return cursor.lastrowid


async def add_autoresponder(guild_id: int, trigger: str, response: str, is_exact: int = 0) -> int:
    return await asyncio.to_thread(_add_autoresponder_sync, guild_id, trigger, response, is_exact)


def _get_autoresponders_sync(guild_id: int) -> List[Dict[str, Any]]:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM autoresponders WHERE guild_id = ? ORDER BY id ASC",
            (guild_id,),
        )
        return [dict(row) for row in cursor.fetchall()]


async def get_autoresponders(guild_id: int) -> List[Dict[str, Any]]:
    return await asyncio.to_thread(_get_autoresponders_sync, guild_id)


def _delete_autoresponder_sync(guild_id: int, responder_id: int) -> bool:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM autoresponders WHERE guild_id = ? AND id = ?",
            (guild_id, responder_id),
        )
        conn.commit()
        return cursor.rowcount > 0


async def delete_autoresponder(guild_id: int, responder_id: int) -> bool:
    return await asyncio.to_thread(_delete_autoresponder_sync, guild_id, responder_id)


# ---------------------------------------------------------------------------
# Level-Up Role Rewards Database Operations
# ---------------------------------------------------------------------------

def _add_level_role_sync(guild_id: int, level: int, role_id: int):
    with _get_connection() as conn:
        conn.execute(
            """
            INSERT INTO level_roles (guild_id, level, role_id)
            VALUES (?, ?, ?)
            ON CONFLICT(guild_id, level) DO UPDATE SET role_id = excluded.role_id
            """,
            (guild_id, level, role_id),
        )
        conn.commit()


async def add_level_role(guild_id: int, level: int, role_id: int):
    await asyncio.to_thread(_add_level_role_sync, guild_id, level, role_id)


def _get_level_roles_sync(guild_id: int) -> List[Dict[str, Any]]:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT level, role_id FROM level_roles WHERE guild_id = ? ORDER BY level ASC",
            (guild_id,),
        )
        return [dict(row) for row in cursor.fetchall()]


async def get_level_roles(guild_id: int) -> List[Dict[str, Any]]:
    return await asyncio.to_thread(_get_level_roles_sync, guild_id)


def _remove_level_role_sync(guild_id: int, level: int) -> bool:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM level_roles WHERE guild_id = ? AND level = ?",
            (guild_id, level),
        )
        conn.commit()
        return cursor.rowcount > 0


async def remove_level_role(guild_id: int, level: int) -> bool:
    return await asyncio.to_thread(_remove_level_role_sync, guild_id, level)


# ---------------------------------------------------------------------------
# Infractions & Warnings Database Operations
# ---------------------------------------------------------------------------

def _add_infraction_sync(
    guild_id: int,
    user_id: int,
    moderator_id: int,
    action_type: str = "warn",
    reason: str = "No reason provided",
) -> int:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO infractions (guild_id, user_id, moderator_id, action_type, reason, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (guild_id, user_id, moderator_id, action_type, reason, time.time()),
        )
        conn.commit()
        return cursor.lastrowid


async def add_infraction(
    guild_id: int,
    user_id: int,
    moderator_id: int,
    action_type: str = "warn",
    reason: str = "No reason provided",
) -> int:
    return await asyncio.to_thread(
        _add_infraction_sync, guild_id, user_id, moderator_id, action_type, reason
    )


def _get_user_infractions_sync(guild_id: int, user_id: int) -> List[Dict[str, Any]]:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, guild_id, user_id, moderator_id, action_type, reason, created_at
            FROM infractions
            WHERE guild_id = ? AND user_id = ?
            ORDER BY id ASC
            """,
            (guild_id, user_id),
        )
        return [dict(row) for row in cursor.fetchall()]


async def get_user_infractions(guild_id: int, user_id: int) -> List[Dict[str, Any]]:
    return await asyncio.to_thread(_get_user_infractions_sync, guild_id, user_id)


def _get_user_warning_count_sync(guild_id: int, user_id: int) -> int:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM infractions WHERE guild_id = ? AND user_id = ? AND action_type = 'warn'",
            (guild_id, user_id),
        )
        row = cursor.fetchone()
        return row[0] if row else 0


async def get_user_warning_count(guild_id: int, user_id: int) -> int:
    return await asyncio.to_thread(_get_user_warning_count_sync, guild_id, user_id)


def _delete_infraction_sync(guild_id: int, infraction_id: int) -> bool:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM infractions WHERE guild_id = ? AND id = ?",
            (guild_id, infraction_id),
        )
        conn.commit()
        return cursor.rowcount > 0


async def delete_infraction(guild_id: int, infraction_id: int) -> bool:
    return await asyncio.to_thread(_delete_infraction_sync, guild_id, infraction_id)


def _clear_user_infractions_sync(guild_id: int, user_id: int) -> int:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM infractions WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id),
        )
        conn.commit()
        return cursor.rowcount


async def clear_user_infractions(guild_id: int, user_id: int) -> int:
    return await asyncio.to_thread(_clear_user_infractions_sync, guild_id, user_id)


# ---------------------------------------------------------------------------
# Verification Gate Database Operations
# ---------------------------------------------------------------------------

def _set_verification_settings_sync(
    guild_id: int, channel_id: int, role_id: int, message_id: Optional[int] = None
):
    with _get_connection() as conn:
        conn.execute(
            """
            INSERT INTO verification_settings (guild_id, channel_id, role_id, message_id, is_enabled)
            VALUES (?, ?, ?, ?, 1)
            ON CONFLICT(guild_id) DO UPDATE SET
                channel_id = excluded.channel_id,
                role_id = excluded.role_id,
                message_id = excluded.message_id,
                is_enabled = 1
            """,
            (guild_id, channel_id, role_id, message_id),
        )
        conn.commit()


async def set_verification_settings(
    guild_id: int, channel_id: int, role_id: int, message_id: Optional[int] = None
):
    await asyncio.to_thread(
        _set_verification_settings_sync, guild_id, channel_id, role_id, message_id
    )


def _get_verification_settings_sync(guild_id: int) -> Optional[Dict[str, Any]]:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT guild_id, channel_id, role_id, message_id, is_enabled FROM verification_settings WHERE guild_id = ?",
            (guild_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None


async def get_verification_settings(guild_id: int) -> Optional[Dict[str, Any]]:
    return await asyncio.to_thread(_get_verification_settings_sync, guild_id)


def _disable_verification_sync(guild_id: int) -> bool:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE verification_settings SET is_enabled = 0 WHERE guild_id = ?",
            (guild_id,),
        )
        conn.commit()
        return cursor.rowcount > 0


async def disable_verification(guild_id: int) -> bool:
    return await asyncio.to_thread(_disable_verification_sync, guild_id)


# ---------------------------------------------------------------------------
# Join-to-Create Temporary Voice Channels Database Operations
# ---------------------------------------------------------------------------

def _set_temp_vc_settings_sync(
    guild_id: int, master_channel_id: int, category_id: Optional[int] = None
):
    with _get_connection() as conn:
        conn.execute(
            """
            INSERT INTO temp_vc_settings (guild_id, master_channel_id, category_id, is_enabled)
            VALUES (?, ?, ?, 1)
            ON CONFLICT(guild_id) DO UPDATE SET
                master_channel_id = excluded.master_channel_id,
                category_id = excluded.category_id,
                is_enabled = 1
            """,
            (guild_id, master_channel_id, category_id),
        )
        conn.commit()


async def set_temp_vc_settings(
    guild_id: int, master_channel_id: int, category_id: Optional[int] = None
):
    await asyncio.to_thread(
        _set_temp_vc_settings_sync, guild_id, master_channel_id, category_id
    )


def _get_temp_vc_settings_sync(guild_id: int) -> Optional[Dict[str, Any]]:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT guild_id, master_channel_id, category_id, is_enabled FROM temp_vc_settings WHERE guild_id = ?",
            (guild_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None


async def get_temp_vc_settings(guild_id: int) -> Optional[Dict[str, Any]]:
    return await asyncio.to_thread(_get_temp_vc_settings_sync, guild_id)


def _disable_temp_vc_sync(guild_id: int) -> bool:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE temp_vc_settings SET is_enabled = 0 WHERE guild_id = ?",
            (guild_id,),
        )
        conn.commit()
        return cursor.rowcount > 0


async def disable_temp_vc(guild_id: int) -> bool:
    return await asyncio.to_thread(_disable_temp_vc_sync, guild_id)


def _add_temp_channel_sync(channel_id: int, guild_id: int, owner_id: int):
    with _get_connection() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO temp_vc_channels (channel_id, guild_id, owner_id, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (channel_id, guild_id, owner_id, time.time()),
        )
        conn.commit()


async def add_temp_channel(channel_id: int, guild_id: int, owner_id: int):
    await asyncio.to_thread(_add_temp_channel_sync, channel_id, guild_id, owner_id)


def _get_temp_channel_sync(channel_id: int) -> Optional[Dict[str, Any]]:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT channel_id, guild_id, owner_id, created_at FROM temp_vc_channels WHERE channel_id = ?",
            (channel_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None


async def get_temp_channel(channel_id: int) -> Optional[Dict[str, Any]]:
    return await asyncio.to_thread(_get_temp_channel_sync, channel_id)


def _delete_temp_channel_sync(channel_id: int) -> bool:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM temp_vc_channels WHERE channel_id = ?", (channel_id,))
        conn.commit()
        return cursor.rowcount > 0


async def delete_temp_channel(channel_id: int) -> bool:
    return await asyncio.to_thread(_delete_temp_channel_sync, channel_id)


# ---------------------------------------------------------------------------
# Economy Shop, Inventory & Work Database Operations
# ---------------------------------------------------------------------------

def _add_shop_item_sync(
    guild_id: int, item_name: str, price: int, description: str = "", role_id: Optional[int] = None
) -> int:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO economy_shop (guild_id, item_name, description, price, role_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (guild_id, item_name, description, price, role_id, time.time()),
        )
        conn.commit()
        return cursor.lastrowid


async def add_shop_item(
    guild_id: int, item_name: str, price: int, description: str = "", role_id: Optional[int] = None
) -> int:
    return await asyncio.to_thread(
        _add_shop_item_sync, guild_id, item_name, price, description, role_id
    )


def _get_shop_items_sync(guild_id: int) -> List[Dict[str, Any]]:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, guild_id, item_name, description, price, role_id, created_at FROM economy_shop WHERE guild_id = ? ORDER BY price ASC",
            (guild_id,),
        )
        return [dict(row) for row in cursor.fetchall()]


async def get_shop_items(guild_id: int) -> List[Dict[str, Any]]:
    return await asyncio.to_thread(_get_shop_items_sync, guild_id)


def _get_shop_item_sync(guild_id: int, item_id: int) -> Optional[Dict[str, Any]]:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, guild_id, item_name, description, price, role_id, created_at FROM economy_shop WHERE guild_id = ? AND id = ?",
            (guild_id, item_id),
        )
        row = cursor.fetchone()
        return dict(row) if row else None


async def get_shop_item(guild_id: int, item_id: int) -> Optional[Dict[str, Any]]:
    return await asyncio.to_thread(_get_shop_item_sync, guild_id, item_id)


def _delete_shop_item_sync(guild_id: int, item_id: int) -> bool:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM economy_shop WHERE guild_id = ? AND id = ?",
            (guild_id, item_id),
        )
        conn.commit()
        return cursor.rowcount > 0


async def delete_shop_item(guild_id: int, item_id: int) -> bool:
    return await asyncio.to_thread(_delete_shop_item_sync, guild_id, item_id)


def _buy_shop_item_sync(
    guild_id: int, user_id: int, item_id: int
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, guild_id, item_name, description, price, role_id FROM economy_shop WHERE guild_id = ? AND id = ?",
            (guild_id, item_id),
        )
        item_row = cursor.fetchone()
        if not item_row:
            return False, "❌ Item not found in this server's shop.", None

        item = dict(item_row)
        price = item["price"]

        cursor.execute(
            "SELECT balance FROM user_economy WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id),
        )
        bal_row = cursor.fetchone()
        current_balance = bal_row[0] if bal_row else 100

        if current_balance < price:
            return (
                False,
                f"❌ Insufficient funds! You need **{price:,} Coins**, but only have **{current_balance:,} Coins**.",
                None,
            )

        # Deduct balance
        conn.execute(
            """
            INSERT INTO user_economy (guild_id, user_id, balance, last_daily)
            VALUES (?, ?, ?, 0)
            ON CONFLICT(guild_id, user_id) DO UPDATE SET balance = balance - excluded.balance
            """,
            (guild_id, user_id, price),
        )

        # Insert into inventory
        cursor.execute(
            """
            INSERT INTO user_inventory (guild_id, user_id, item_id, item_name, role_id, purchased_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (guild_id, user_id, item["id"], item["item_name"], item.get("role_id"), time.time()),
        )
        conn.commit()
        return True, f"✅ Successfully purchased **{item['item_name']}** for **{price:,} Coins**!", item


async def buy_shop_item(
    guild_id: int, user_id: int, item_id: int
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    return await asyncio.to_thread(_buy_shop_item_sync, guild_id, user_id, item_id)


def _get_user_inventory_sync(guild_id: int, user_id: int) -> List[Dict[str, Any]]:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, guild_id, user_id, item_id, item_name, role_id, purchased_at
            FROM user_inventory
            WHERE guild_id = ? AND user_id = ?
            ORDER BY id DESC
            """,
            (guild_id, user_id),
        )
        return [dict(row) for row in cursor.fetchall()]


async def get_user_inventory(guild_id: int, user_id: int) -> List[Dict[str, Any]]:
    return await asyncio.to_thread(_get_user_inventory_sync, guild_id, user_id)


def _claim_work_sync(
    guild_id: int,
    user_id: int,
    min_reward: int = 50,
    max_reward: int = 150,
    cooldown_seconds: float = 3600.0,
) -> Tuple[bool, int, int, float]:
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT balance, last_work FROM user_economy WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id),
        )
        row = cursor.fetchone()
        now = time.time()

        if row:
            balance = row["balance"]
            last_work = row["last_work"] if "last_work" in row.keys() and row["last_work"] is not None else 0.0
            elapsed = now - last_work
            if elapsed < cooldown_seconds:
                return False, 0, balance, cooldown_seconds - elapsed
        else:
            balance = 100

        import random
        earned = random.randint(min_reward, max_reward)
        new_balance = balance + earned

        conn.execute(
            """
            INSERT INTO user_economy (guild_id, user_id, balance, last_daily, last_work)
            VALUES (?, ?, ?, 0, ?)
            ON CONFLICT(guild_id, user_id) DO UPDATE SET balance = balance + excluded.balance, last_work = excluded.last_work
            """,
            (guild_id, user_id, earned, now),
        )
        conn.commit()
        return True, earned, new_balance, 0.0


async def claim_work(
    guild_id: int,
    user_id: int,
    min_reward: int = 50,
    max_reward: int = 150,
    cooldown_seconds: float = 3600.0,
) -> Tuple[bool, int, int, float]:
    return await asyncio.to_thread(
        _claim_work_sync, guild_id, user_id, min_reward, max_reward, cooldown_seconds
    )






