"""Automated Test Suite for Discord Utility Bot.

Validates all 10 Cogs, 22 Slash Commands, Database Operations,
Auto-Mod Regex, UI Modals/Buttons, and Gamification logic.
"""

import os
import sys
import asyncio
import tempfile
import unittest

import discord
from discord.ext import commands

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database
from cogs.embeds import parse_color
from cogs.leveling import render_progress_bar
from cogs.automod import INVITE_REGEX
from cogs.roles import RoleButton
from cogs.tickets import TicketLaunchView, CloseTicketView
from bot import UtilityBot


class TestDiscordUtilityBot(unittest.IsolatedAsyncioTestCase):
    """Full automated test suite for all bot subsystems."""

    async def asyncSetUp(self):
        # Use an isolated temporary database for tests
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        database.DB_DIR = self.temp_dir.name
        database.DB_PATH = os.path.join(self.temp_dir.name, "test_bot.db")
        await database.init_db()

        # Initialize mock bot instance
        os.environ["DISCORD_TOKEN"] = "test_token_for_automated_suite"
        self.bot = UtilityBot()

        # Load all cogs
        cogs_dir = os.path.join(os.path.dirname(__file__), "cogs")
        for filename in sorted(os.listdir(cogs_dir)):
            if filename.endswith(".py") and not filename.startswith("__"):
                await self.bot.load_extension(f"cogs.{filename[:-3]}")

    async def asyncTearDown(self):
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    # -----------------------------------------------------------------------
    # 1. Cogs & Command Registration Tests
    # -----------------------------------------------------------------------

    def test_all_10_cogs_loaded(self):
        """Verify all 10 Cogs are discovered and successfully loaded."""
        expected_cogs = {
            "AutoMod",
            "Embeds",
            "Events",
            "Leveling",
            "Logging",
            "Moderation",
            "Polls",
            "Roles",
            "Tickets",
            "Utility",
        }
        loaded_cogs = set(self.bot.cogs.keys())
        self.assertEqual(
            expected_cogs,
            loaded_cogs,
            f"Missing or mismatched cogs: {expected_cogs - loaded_cogs}",
        )

    def test_all_22_slash_commands_registered(self):
        """Verify all 22 application commands are present in the command tree."""
        expected_commands = {
            "automod",
            "avatar",
            "ban",
            "clear",
            "embed",
            "giveaway",
            "hello",
            "kick",
            "leaderboard",
            "poll",
            "premium",
            "rank",
            "role",
            "rolepanel",
            "roll",
            "serverinfo",
            "setlogs",
            "ticketsetup",
            "timeout",
            "unban",
            "untimeout",
            "userinfo",
        }
        registered_commands = {cmd.name for cmd in self.bot.tree.get_commands()}
        self.assertEqual(
            expected_commands,
            registered_commands,
            f"Missing commands: {expected_commands - registered_commands}",
        )

    def test_prefix_commands_registered(self):
        """Verify classic prefix commands (!ping, !sync)."""
        registered = {cmd.name for cmd in self.bot.commands}
        self.assertIn("ping", registered)
        self.assertIn("sync", registered)

    # -----------------------------------------------------------------------
    # 2. Database Multi-Tenant Operations Tests
    # -----------------------------------------------------------------------

    async def test_guild_settings_defaults_and_updates(self):
        """Verify guild settings creation, default values, and persistent updates."""
        guild_id = 987654321
        settings = await database.get_guild_settings(guild_id)

        self.assertEqual(settings["guild_id"], guild_id)
        self.assertEqual(settings["is_premium"], 0)
        self.assertEqual(settings["anti_invite"], 1)

        # Update setting
        await database.update_guild_setting(guild_id, "anti_invite", 0)
        await database.update_guild_setting(guild_id, "is_premium", 1)

        updated = await database.get_guild_settings(guild_id)
        self.assertEqual(updated["anti_invite"], 0)
        self.assertEqual(updated["is_premium"], 1)

        # Premium helper check
        self.assertTrue(await database.is_guild_premium(guild_id))

    async def test_leveling_system_xp_and_leaderboard(self):
        """Verify XP additions, level-up threshold calculation, and leaderboard rank."""
        guild_id = 112233
        user1 = 1001
        user2 = 1002

        # User 1 gains 150 XP (Level 1 -> Level 2 with 50 XP remainder)
        leveled_up, level, xp = await database.add_user_xp(
            guild_id=guild_id,
            user_id=user1,
            amount=150,
            cooldown_seconds=0.0,
        )
        self.assertTrue(leveled_up)
        self.assertEqual(level, 2)
        self.assertEqual(xp, 50)

        # User 2 gains 30 XP (stays Level 1)
        leveled_up2, level2, xp2 = await database.add_user_xp(
            guild_id=guild_id,
            user_id=user2,
            amount=30,
            cooldown_seconds=0.0,
        )
        self.assertFalse(leveled_up2)
        self.assertEqual(level2, 1)
        self.assertEqual(xp2, 30)

        # Verify Rank calculation
        rank1, lvl1, cur_xp1, needed1 = await database.get_user_level_data(guild_id, user1)
        self.assertEqual(rank1, 1)  # User 1 is Rank #1
        self.assertEqual(lvl1, 2)
        self.assertEqual(cur_xp1, 50)
        self.assertEqual(needed1, 200)

        rank2, lvl2, cur_xp2, needed2 = await database.get_user_level_data(guild_id, user2)
        self.assertEqual(rank2, 2)  # User 2 is Rank #2

        # Leaderboard query
        board = await database.get_top_leaderboard(guild_id, limit=5)
        self.assertEqual(len(board), 2)
        self.assertEqual(board[0]["user_id"], user1)
        self.assertEqual(board[1]["user_id"], user2)

    # -----------------------------------------------------------------------
    # 3. Auto-Mod Regular Expression Tests
    # -----------------------------------------------------------------------

    def test_automod_invite_detection(self):
        """Verify regex accurately intercepts Discord invite links."""
        positive_samples = [
            "join https://discord.gg/coolserver",
            "check out discord.gg/test123",
            "http://discord.com/invite/gaming",
            "DISCORD.GG/SHOUTING",
            "discord.me/community",
        ]
        negative_samples = [
            "hello everyone, how are you?",
            "check out my website https://google.com",
            "discord is a great app",
            "github.com/rk-ranjith0143",
        ]

        for text in positive_samples:
            self.assertIsNotNone(
                INVITE_REGEX.search(text),
                f"Invite regex failed to catch: {text}",
            )

        for text in negative_samples:
            self.assertIsNone(
                INVITE_REGEX.search(text),
                f"Invite regex incorrectly flagged: {text}",
            )

    # -----------------------------------------------------------------------
    # 4. UI Components, Colors, and Views
    # -----------------------------------------------------------------------

    def test_custom_embed_color_parser(self):
        """Verify parsing of hex strings and named colors."""
        self.assertEqual(parse_color("#FF0000"), discord.Color(0xFF0000))
        self.assertEqual(parse_color("blue"), discord.Color.blue())
        self.assertEqual(parse_color("gold"), discord.Color.gold())
        self.assertEqual(parse_color("invalid_color_fallback"), discord.Color.blurple())

    def test_ascii_progress_bar(self):
        """Verify visual progress bar rendering."""
        bar_50 = render_progress_bar(50, 100, length=10)
        self.assertEqual(bar_50, "[▓▓▓▓▓░░░░░] 50%")

        bar_100 = render_progress_bar(100, 100, length=10)
        self.assertEqual(bar_100, "[▓▓▓▓▓▓▓▓▓▓] 100%")

    def test_persistent_views_custom_ids(self):
        """Ensure persistent views have fixed custom_ids for reboot survival."""
        ticket_view = TicketLaunchView()
        self.assertEqual(ticket_view.children[0].custom_id, "ticket_create")

        close_view = CloseTicketView()
        self.assertEqual(close_view.children[0].custom_id, "ticket_close")

        role_btn = RoleButton(role_id=12345, label="Member")
        self.assertTrue(role_btn.custom_id.startswith("selfrole:role:12345"))


if __name__ == "__main__":
    unittest.main()
