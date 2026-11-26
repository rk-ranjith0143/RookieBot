"""Automated Test Suite for Rookie Discord Bot.

Validates all 19 Cogs, 39 Slash Commands, Database Operations,
Auto-Mod Regex, UI Modals/Buttons/Views, Gamification, and Monetization.
"""

import os
import sys
import datetime
import tempfile
import unittest
from unittest.mock import AsyncMock, MagicMock

import discord
from discord import app_commands

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database
from cogs.embeds import parse_color
from cogs.leveling import render_progress_bar
from cogs.automod import INVITE_REGEX, find_blacklisted_word
from cogs.roles import RoleButton, RoleMenuSelect
from cogs.tickets import (
    TicketLaunchView,
    CloseTicketView,
    extract_ticket_owner_id,
    generate_ticket_transcript,
)
from cogs.suggestions import SuggestionVoteView
from cogs.premium import PremiumUpgradeView
from cogs.verification import VerifyLaunchView
from cogs.reminders import parse_time_string
from cogs.afk import format_duration
from cogs.birthdays import is_valid_birthday, days_until_birthday
from cogs.applications import ApplicationLaunchView, ApplicationReviewView
from bot import RookieBot


class TestRookieBot(unittest.IsolatedAsyncioTestCase):
    """Full automated test suite for all Rookie bot subsystems."""

    async def asyncSetUp(self):
        # Use an isolated temporary database for tests
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        database.DB_DIR = self.temp_dir.name
        database.DB_PATH = os.path.join(self.temp_dir.name, "test_bot.db")
        await database.init_db()

        # Initialize mock bot instance
        os.environ["DISCORD_TOKEN"] = "test_token_for_automated_suite"
        self.bot = RookieBot()

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

    def test_all_28_cogs_loaded(self):
        """Verify all 28 Cogs are discovered and successfully loaded."""
        expected_cogs = {
            "AFK",
            "Applications",
            "AutoMod",
            "AutoResponder",
            "AutoRole",
            "Birthdays",
            "Economy",
            "Embeds",
            "Events",
            "Help",
            "Invites",
            "Leveling",
            "Logging",
            "Moderation",
            "Polls",
            "Premium",
            "Reminders",
            "Roles",
            "ServerStats",
            "Starboard",
            "Sticky",
            "Suggestions",
            "Tags",
            "TempVC",
            "Tickets",
            "Utility",
            "Verification",
            "Warns",
        }
        loaded_cogs = set(self.bot.cogs.keys())
        self.assertEqual(
            expected_cogs,
            loaded_cogs,
            f"Missing or mismatched cogs: {expected_cogs - loaded_cogs}",
        )

    def test_all_74_slash_commands_registered(self):
        """Verify all 74 application commands are present in the command tree."""
        expected_commands = {
            "8ball",
            "afk",
            "apply",
            "automod",
            "autoresponder",
            "autorole",
            "avatar",
            "balance",
            "ban",
            "birthday",
            "buy",
            "clear",
            "clearwarns",
            "coinflip",
            "daily",
            "delwarn",
            "eco",
            "embed",
            "giveaway",
            "hello",
            "help",
            "inventory",
            "invitebonus",
            "inviteleaderboard",
            "invitereset",
            "invites",
            "kick",
            "leaderboard",
            "levelrole",
            "license",
            "lock",
            "pay",
            "poll",
            "premium",
            "rank",
            "reactionrole",
            "redeem",
            "remindme",
            "richest",
            "rob",
            "role",
            "rolemenu",
            "rolepanel",
            "roll",
            "serverinfo",
            "serverstats",
            "setleave",
            "setlogs",
            "setsuggestchannel",
            "setwelcome",
            "shop",
            "slots",
            "slowmode",
            "starboard",
            "sticky",
            "suggest",
            "suggeststatus",
            "tag",
            "tempban",
            "temprole",
            "tempvc",
            "ticketsetup",
            "timeout",
            "unban",
            "unlock",
            "untimeout",
            "userinfo",
            "vc",
            "verifyremove",
            "verifysetup",
            "verifystatus",
            "warn",
            "warnings",
            "work",
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

        # Update settings
        await database.update_guild_setting(guild_id, "anti_invite", 0)
        await database.update_guild_setting(guild_id, "is_premium", 1)
        await database.update_guild_setting(guild_id, "welcome_message", "Welcome {user}!")
        await database.update_guild_setting(guild_id, "leave_message", "Goodbye {username}!")
        await database.update_guild_setting(guild_id, "suggestion_channel_id", 555666777)

        updated = await database.get_guild_settings(guild_id)
        self.assertEqual(updated["anti_invite"], 0)
        self.assertEqual(updated["is_premium"], 1)
        self.assertEqual(updated["welcome_message"], "Welcome {user}!")
        self.assertEqual(updated["leave_message"], "Goodbye {username}!")
        self.assertEqual(updated["suggestion_channel_id"], 555666777)

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

    async def test_afk_database_operations(self):
        """Verify setting, retrieving, and clearing user AFK states."""
        guild_id = 778899
        user_id = 445566

        # Initially not AFK
        self.assertIsNone(await database.get_user_afk(guild_id, user_id))

        # Set AFK
        await database.set_user_afk(guild_id, user_id, "Studying for exams")
        afk_info = await database.get_user_afk(guild_id, user_id)
        self.assertIsNotNone(afk_info)
        self.assertEqual(afk_info["reason"], "Studying for exams")

        # Clear AFK
        await database.remove_user_afk(guild_id, user_id)
        self.assertIsNone(await database.get_user_afk(guild_id, user_id))

    async def test_reminders_database_operations(self):
        """Verify adding, querying due, and deleting scheduled reminders."""
        user_id = 1234
        channel_id = 5678
        now = datetime.datetime.now().timestamp()

        # Add reminder due 10 seconds ago (already due)
        await database.add_reminder(user_id, channel_id, "Buy coffee", now - 10)
        # Add reminder due 1 hour in the future
        await database.add_reminder(user_id, channel_id, "Meeting", now + 3600)

        due = await database.get_due_reminders(now)
        self.assertEqual(len(due), 1)
        self.assertEqual(due[0]["message"], "Buy coffee")

        # Delete reminder
        await database.delete_reminder(due[0]["id"])
        due_after = await database.get_due_reminders(now)
        self.assertEqual(len(due_after), 0)

    async def test_economy_database_operations(self):
        """Verify default balance, daily claims, cooldowns, and balance updates."""
        guild_id = 333444
        user1 = 111
        user2 = 222

        # Check default balance (100 coins)
        bal1 = await database.get_user_balance(guild_id, user1)
        self.assertEqual(bal1, 100)

        # Claim daily bonus (+200 coins -> 300)
        claimed, new_bal, rem = await database.claim_daily(guild_id, user1, reward=200, cooldown_seconds=86400)
        self.assertTrue(claimed)
        self.assertEqual(new_bal, 300)

        # Second immediate claim should fail due to cooldown
        claimed2, bal_cur, rem2 = await database.claim_daily(guild_id, user1, reward=200, cooldown_seconds=86400)
        self.assertFalse(claimed2)
        self.assertEqual(bal_cur, 300)
        self.assertGreater(rem2, 86000)

        # Transfer / update balance: user1 pays user2 50 coins (-50 for user1, +50 for user2)
        await database.update_user_balance(guild_id, user1, -50)
        await database.update_user_balance(guild_id, user2, 50)
        self.assertEqual(await database.get_user_balance(guild_id, user1), 250)
        self.assertEqual(await database.get_user_balance(guild_id, user2), 150)

    async def test_sticky_messages_database_operations(self):
        """Verify configuring, updating, and removing sticky messages."""
        channel_id = 998877

        # Initially no sticky message
        self.assertIsNone(await database.get_sticky_message(channel_id))

        # Set sticky message
        await database.set_sticky_message(channel_id, "Welcome to our rules channel!")
        sticky = await database.get_sticky_message(channel_id)
        self.assertIsNotNone(sticky)
        self.assertEqual(sticky["message_content"], "Welcome to our rules channel!")
        self.assertIsNone(sticky["last_message_id"])

        # Update last message id
        await database.update_sticky_last_id(channel_id, 1234567890)
        sticky_updated = await database.get_sticky_message(channel_id)
        self.assertEqual(sticky_updated["last_message_id"], 1234567890)

        # Delete sticky message
        await database.delete_sticky_message(channel_id)
        self.assertIsNone(await database.get_sticky_message(channel_id))

    async def test_starboard_database_operations(self):
        """Verify starboard settings configuration, message tracking, and star counts."""
        guild_id = 123000
        channel_id = 456000

        # Set starboard settings
        await database.set_starboard_settings(guild_id, channel_id, threshold=3, is_enabled=1)
        settings = await database.get_starboard_settings(guild_id)
        self.assertIsNotNone(settings)
        self.assertEqual(settings["channel_id"], channel_id)
        self.assertEqual(settings["threshold"], 3)
        self.assertEqual(settings["is_enabled"], 1)

        # Save starboard message
        orig_msg_id = 11223344
        sb_msg_id = 99887766
        await database.save_starboard_message(orig_msg_id, sb_msg_id, channel_id, guild_id, 3)

        sb_entry = await database.get_starboard_message(orig_msg_id)
        self.assertIsNotNone(sb_entry)
        self.assertEqual(sb_entry["starboard_message_id"], sb_msg_id)
        self.assertEqual(sb_entry["star_count"], 3)

        # Update star count
        await database.update_starboard_count(orig_msg_id, 5)
        sb_updated = await database.get_starboard_message(orig_msg_id)
        self.assertEqual(sb_updated["star_count"], 5)

        # Disable starboard
        await database.disable_starboard(guild_id)
        self.assertEqual((await database.get_starboard_settings(guild_id))["is_enabled"], 0)

        # Delete starboard message
        await database.delete_starboard_message(orig_msg_id)
        self.assertIsNone(await database.get_starboard_message(orig_msg_id))

    async def test_suggestions_database_operations(self):
        """Verify suggestion creation, up/down voting logic, and status review."""
        guild_id = 101010
        channel_id = 202020
        msg_id = 303030
        author_id = 404040

        # Create suggestion
        sug_id = await database.create_suggestion(
            guild_id=guild_id,
            channel_id=channel_id,
            message_id=msg_id,
            author_id=author_id,
            content="Add a coding showcase channel!",
        )
        self.assertIsInstance(sug_id, int)

        sug = await database.get_suggestion(sug_id)
        self.assertIsNotNone(sug)
        self.assertEqual(sug["status"], "pending")
        self.assertEqual(sug["content"], "Add a coding showcase channel!")

        # Upvote by voter 1
        voter1 = 505050
        _, upvotes, downvotes = await database.vote_suggestion(sug_id, voter1, vote_type=1)
        self.assertEqual(upvotes, 1)
        self.assertEqual(downvotes, 0)

        # Downvote by voter 2
        voter2 = 606060
        _, upvotes, downvotes = await database.vote_suggestion(sug_id, voter2, vote_type=-1)
        self.assertEqual(upvotes, 1)
        self.assertEqual(downvotes, 1)

        # Voter 1 clicks upvote again (toggles vote off)
        _, upvotes, downvotes = await database.vote_suggestion(sug_id, voter1, vote_type=1)
        self.assertEqual(upvotes, 0)
        self.assertEqual(downvotes, 1)

        # Review status: Approved with note
        await database.update_suggestion_status(sug_id, "approved", "Great idea, created #showcase!")
        reviewed = await database.get_suggestion(sug_id)
        self.assertEqual(reviewed["status"], "approved")
        self.assertEqual(reviewed["response"], "Great idea, created #showcase!")

    async def test_tags_database_operations(self):
        """Verify creating tags, searching autocomplete, incrementing uses, and deleting."""
        guild_id = 554433
        author_id = 998811

        # Create tags
        created = await database.create_tag(guild_id, "rules", "Read our rules in #rules-and-info", author_id)
        self.assertTrue(created)
        # Duplicate should fail
        self.assertFalse(await database.create_tag(guild_id, "rules", "Duplicate", author_id))

        await database.create_tag(guild_id, "faq", "Frequently asked questions: https://example.com/faq", author_id)
        await database.create_tag(guild_id, "website", "https://discordbot.example.com", author_id)

        # Get tag and verify usage increments
        tag_info = await database.get_tag(guild_id, "rules", increment_uses=True)
        self.assertIsNotNone(tag_info)
        self.assertEqual(tag_info["content"], "Read our rules in #rules-and-info")
        self.assertEqual(tag_info["uses"], 1)

        # Search autocomplete
        results = await database.search_tags(guild_id, "ru")
        self.assertIn("rules", results)

        # List tags
        all_tags = await database.list_tags(guild_id)
        self.assertEqual(len(all_tags), 3)

        # Delete tag
        self.assertTrue(await database.delete_tag(guild_id, "rules"))
        self.assertFalse(await database.delete_tag(guild_id, "rules"))
        self.assertIsNone(await database.get_tag(guild_id, "rules"))

    async def test_serverstats_database_operations(self):
        """Verify saving, retrieving, and clearing server counter channels."""
        guild_id = 889900

        # Initially empty
        self.assertEqual(len(await database.get_server_stat_channels(guild_id)), 0)

        # Set channels
        await database.set_server_stat_channel(guild_id, "all_members", 111222, "👥 Total: {count}")
        await database.set_server_stat_channel(guild_id, "bots", 333444, "🤖 Bots: {count}")

        stats = await database.get_server_stat_channels(guild_id)
        self.assertEqual(len(stats), 2)

        # Remove channels
        await database.remove_server_stat_channels(guild_id)
        self.assertEqual(len(await database.get_server_stat_channels(guild_id)), 0)

    async def test_premium_key_generation_and_redemption(self):
        """Verify generating a license key and redeeming it for a guild."""
        guild_id = 991199
        user_id = 772277

        # Key generation
        key = await database.create_premium_key(duration_days=30, note="Stripe sub_123")
        self.assertTrue(key.startswith("PREM-"))

        # Initially guild is not premium
        self.assertFalse(await database.is_guild_premium(guild_id))

        # Redeem key
        success, msg, new_exp = await database.redeem_premium_key(key, guild_id, user_id)
        self.assertTrue(success)
        self.assertIsNotNone(new_exp)

        # Guild is now premium
        self.assertTrue(await database.is_guild_premium(guild_id))
        details = await database.get_guild_premium_details(guild_id)
        self.assertTrue(details["is_premium"])
        self.assertFalse(details["is_lifetime"])
        self.assertGreaterEqual(details["days_remaining"], 29)

        # Attempting to redeem the same key again fails
        success2, msg2, _ = await database.redeem_premium_key(key, guild_id, user_id)
        self.assertFalse(success2)
        self.assertIn("already been redeemed", msg2)

    async def test_premium_expiration_auto_downgrade(self):
        """Verify expired subscriptions are automatically downgraded."""
        guild_id = 882288
        past_timestamp = datetime.datetime.now().timestamp() - 3600  # 1 hour in the past

        await database.update_guild_setting(guild_id, "is_premium", 1)
        await database.update_guild_setting(guild_id, "premium_expires_at", str(past_timestamp))

        # is_guild_premium should detect expiration, reset to 0, and return False
        self.assertFalse(await database.is_guild_premium(guild_id))

        details = await database.get_guild_premium_details(guild_id)
        self.assertFalse(details["is_premium"])

    async def test_license_revocation(self):
        """Verify manual revocation of premium tier."""
        guild_id = 556677
        key = await database.create_premium_key(duration_days=-1, note="Lifetime client")
        await database.redeem_premium_key(key, guild_id, 12345)
        self.assertTrue(await database.is_guild_premium(guild_id))

        await database.revoke_guild_premium(guild_id)
        self.assertFalse(await database.is_guild_premium(guild_id))

    async def test_tier_limits_for_tags_and_sticky(self):
        """Verify tag count and sticky count helper queries."""
        guild_id = 445566
        # Add 3 tags
        for i in range(3):
            await database.create_tag(guild_id, f"tag_{i}", f"content_{i}", 123)
        self.assertEqual(await database.get_guild_tag_count(guild_id), 3)

        # Add 1 sticky message
        await database.set_sticky_message(channel_id=98765, content="Pinned", guild_id=guild_id)
        self.assertEqual(await database.get_guild_sticky_count(guild_id), 1)

    async def test_autoroles_database_operations(self):
        """Verify setting, fetching, and removing auto-roles."""
        guild_id = 998811
        # Initially empty
        self.assertIsNone(await database.get_autoroles(guild_id))

        # Set autoroles
        await database.set_autoroles(guild_id, member_role_id=111, bot_role_id=222)
        cfg = await database.get_autoroles(guild_id)
        self.assertIsNotNone(cfg)
        self.assertEqual(cfg["member_role_id"], 111)
        self.assertEqual(cfg["bot_role_id"], 222)

        # Remove autoroles
        await database.remove_autoroles(guild_id)
        self.assertIsNone(await database.get_autoroles(guild_id))

    async def test_autoresponder_database_operations(self):
        """Verify adding, querying, and deleting keyword auto-responders."""
        guild_id = 887722
        # Initially empty
        self.assertEqual(len(await database.get_autoresponders(guild_id)), 0)

        # Add auto-responder
        r_id = await database.add_autoresponder(guild_id, trigger="!ip", response="play.server.com", is_exact=1)
        self.assertIsInstance(r_id, int)

        responders = await database.get_autoresponders(guild_id)
        self.assertEqual(len(responders), 1)
        self.assertEqual(responders[0]["trigger_phrase"], "!ip")
        self.assertEqual(responders[0]["response_text"], "play.server.com")

        # Delete auto-responder
        self.assertTrue(await database.delete_autoresponder(guild_id, r_id))
        self.assertEqual(len(await database.get_autoresponders(guild_id)), 0)

    async def test_level_roles_database_operations(self):
        """Verify adding, listing, and removing milestone role rewards."""
        guild_id = 776633
        # Initially empty
        self.assertEqual(len(await database.get_level_roles(guild_id)), 0)

        # Add milestone roles
        await database.add_level_role(guild_id, level=5, role_id=555)
        await database.add_level_role(guild_id, level=10, role_id=1010)

        roles = await database.get_level_roles(guild_id)
        self.assertEqual(len(roles), 2)
        self.assertEqual(roles[0]["level"], 5)
        self.assertEqual(roles[0]["role_id"], 555)

        # Remove level role
        self.assertTrue(await database.remove_level_role(guild_id, level=5))
        self.assertEqual(len(await database.get_level_roles(guild_id)), 1)

    async def test_infractions_database_operations(self):
        """Verify adding, listing, counting, and clearing infractions."""
        guild_id = 992211
        user_id = 334455
        mod_id = 112233

        # Initially 0 warnings
        self.assertEqual(await database.get_user_warning_count(guild_id, user_id), 0)
        self.assertEqual(len(await database.get_user_infractions(guild_id, user_id)), 0)

        # Add warnings
        inf_id1 = await database.add_infraction(guild_id, user_id, mod_id, "warn", "Spamming in #general")
        inf_id2 = await database.add_infraction(guild_id, user_id, mod_id, "warn", "Advertising without permit")
        self.assertIsInstance(inf_id1, int)
        self.assertIsInstance(inf_id2, int)

        # Check count and list
        self.assertEqual(await database.get_user_warning_count(guild_id, user_id), 2)
        infractions = await database.get_user_infractions(guild_id, user_id)
        self.assertEqual(len(infractions), 2)
        self.assertEqual(infractions[0]["reason"], "Spamming in #general")

        # Delete single infraction
        self.assertTrue(await database.delete_infraction(guild_id, inf_id1))
        self.assertEqual(await database.get_user_warning_count(guild_id, user_id), 1)

        # Clear remaining infractions
        cleared_count = await database.clear_user_infractions(guild_id, user_id)
        self.assertEqual(cleared_count, 1)
        self.assertEqual(await database.get_user_warning_count(guild_id, user_id), 0)

    async def test_verification_database_operations(self):
        """Verify setting, fetching, and disabling verification gate settings."""
        guild_id = 883311
        channel_id = 445566
        role_id = 998877

        # Initially None
        self.assertIsNone(await database.get_verification_settings(guild_id))

        # Set settings
        await database.set_verification_settings(guild_id, channel_id, role_id, message_id=123456)
        cfg = await database.get_verification_settings(guild_id)
        self.assertIsNotNone(cfg)
        self.assertEqual(cfg["channel_id"], channel_id)
        self.assertEqual(cfg["role_id"], role_id)
        self.assertEqual(cfg["message_id"], 123456)
        self.assertEqual(cfg["is_enabled"], 1)

        # Disable verification
        self.assertTrue(await database.disable_verification(guild_id))
        cfg_disabled = await database.get_verification_settings(guild_id)
        self.assertEqual(cfg_disabled["is_enabled"], 0)

    async def test_temp_vc_database_operations(self):
        """Verify setting, fetching, and managing join-to-create voice channels."""
        guild_id = 998844
        master_id = 556677
        cat_id = 112233
        temp_vc_id = 445566
        owner_id = 778899

        # Initially None
        self.assertIsNone(await database.get_temp_vc_settings(guild_id))

        # Set settings
        await database.set_temp_vc_settings(guild_id, master_id, cat_id)
        cfg = await database.get_temp_vc_settings(guild_id)
        self.assertIsNotNone(cfg)
        self.assertEqual(cfg["master_channel_id"], master_id)
        self.assertEqual(cfg["category_id"], cat_id)
        self.assertEqual(cfg["is_enabled"], 1)

        # Track temp channel
        await database.add_temp_channel(temp_vc_id, guild_id, owner_id)
        channel_data = await database.get_temp_channel(temp_vc_id)
        self.assertIsNotNone(channel_data)
        self.assertEqual(channel_data["owner_id"], owner_id)

        # Delete temp channel
        self.assertTrue(await database.delete_temp_channel(temp_vc_id))
        self.assertIsNone(await database.get_temp_channel(temp_vc_id))

        # Disable temp VC
        self.assertTrue(await database.disable_temp_vc(guild_id))
        self.assertEqual((await database.get_temp_vc_settings(guild_id))["is_enabled"], 0)

    async def test_economy_shop_and_inventory_database_operations(self):
        """Verify shop item creation, purchasing, inventory tracking, and work rewards."""
        guild_id = 991122
        user_id = 332211
        role_id = 776655

        # Initial shop is empty
        self.assertEqual(len(await database.get_shop_items(guild_id)), 0)

        # Add shop item
        item_id = await database.add_shop_item(
            guild_id=guild_id,
            item_name="VIP Pass",
            price=50,
            description="Grants VIP role",
            role_id=role_id,
        )
        self.assertIsInstance(item_id, int)

        # Get shop items
        items = await database.get_shop_items(guild_id)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["item_name"], "VIP Pass")
        self.assertEqual(items[0]["price"], 50)

        # Ensure user has balance
        await database.update_user_balance(guild_id, user_id, 100)

        # Buy item
        success, msg, itm = await database.buy_shop_item(guild_id, user_id, item_id)
        self.assertTrue(success)
        self.assertEqual(itm["item_name"], "VIP Pass")

        # Check inventory
        inv = await database.get_user_inventory(guild_id, user_id)
        self.assertEqual(len(inv), 1)
        self.assertEqual(inv[0]["item_name"], "VIP Pass")

        # Attempt to buy without sufficient balance
        await database.update_user_balance(guild_id, user_id, -1000)  # zero/negative out
        fail_success, fail_msg, _ = await database.buy_shop_item(guild_id, user_id, item_id)
        self.assertFalse(fail_success)
        self.assertIn("Insufficient funds", fail_msg)

        # Delete shop item
        self.assertTrue(await database.delete_shop_item(guild_id, item_id))
        self.assertEqual(len(await database.get_shop_items(guild_id)), 0)

        # Test claim_work
        work_user = 443322
        worked, earned, new_bal, rem = await database.claim_work(guild_id, work_user, min_reward=50, max_reward=50)
        self.assertTrue(worked)
        self.assertEqual(earned, 50)
        self.assertEqual(new_bal, 150)  # default 100 + 50
        # Second work within cooldown fails
        worked2, _, _, rem2 = await database.claim_work(guild_id, work_user)
        self.assertFalse(worked2)
        self.assertGreater(rem2, 0)

        # Test richest leaderboard and rob heist
        await database.update_user_balance(guild_id, 556677, 1000)
        top = await database.get_top_balances(guild_id, limit=5)
        self.assertEqual(top[0]["user_id"], 556677)

        allowed, _, _, _, _, _, _ = await database.attempt_rob(guild_id, work_user, 556677)
        self.assertTrue(allowed)
        # Immediate second rob blocked by cooldown
        allowed2, _, _, _, _, rem_rob, reason = await database.attempt_rob(guild_id, work_user, 556677)
        self.assertFalse(allowed2)
        self.assertEqual(reason, "cooldown")
        self.assertGreater(rem_rob, 0)

    async def test_giveaways_database_operations(self):
        """Verify persistent giveaway creation, querying due giveaways, and marking ended."""
        import time as pytime
        guild_id = 33333
        channel_id = 44444
        msg_id = 55555111
        past_ts = pytime.time() - 5.0

        await database.create_giveaway(
            message_id=msg_id,
            guild_id=guild_id,
            channel_id=channel_id,
            host_id=10101,
            prize="Discord Nitro",
            winners_count=2,
            ends_at=past_ts,
        )

        record = await database.get_giveaway(msg_id)
        self.assertIsNotNone(record)
        self.assertEqual(record["prize"], "Discord Nitro")
        self.assertEqual(record["winners_count"], 2)
        self.assertEqual(record["is_ended"], 0)

        active = await database.get_active_giveaways(guild_id)
        self.assertEqual(len(active), 1)

        due = await database.get_due_giveaways(pytime.time())
        self.assertEqual(len(due), 1)

        ended = await database.mark_giveaway_ended(msg_id)
        self.assertTrue(ended)
        self.assertEqual(len(await database.get_active_giveaways(guild_id)), 0)
        self.assertEqual(len(await database.get_due_giveaways(pytime.time())), 0)

    async def test_birthdays_database_operations(self):
        """Verify birthday storage, validation, due queries, and celebration marking."""
        guild_id = 445566
        user_id = 778899

        self.assertTrue(is_valid_birthday(2, 29))
        self.assertFalse(is_valid_birthday(2, 30))
        self.assertEqual(days_until_birthday(11, 25, today=datetime.date(2026, 11, 25)), 0)
        self.assertEqual(days_until_birthday(11, 28, today=datetime.date(2026, 11, 25)), 3)

        await database.set_birthday_settings(guild_id, channel_id=1234, role_id=5678)
        cfg = await database.get_birthday_settings(guild_id)
        self.assertIsNotNone(cfg)
        self.assertEqual(cfg["is_enabled"], 1)

        await database.set_user_birthday(guild_id, user_id, month=11, day=25)
        entry = await database.get_user_birthday(guild_id, user_id)
        self.assertEqual(entry["month"], 11)
        self.assertEqual(entry["day"], 25)

        due = await database.get_due_birthdays(11, 25, 2026)
        self.assertEqual(len(due), 1)
        self.assertEqual(due[0]["user_id"], user_id)

        await database.mark_birthday_celebrated(guild_id, user_id, 2026)
        self.assertEqual(len(await database.get_due_birthdays(11, 25, 2026)), 0)

        self.assertTrue(await database.remove_user_birthday(guild_id, user_id))
        self.assertTrue(await database.disable_birthday_settings(guild_id))

    async def test_invites_database_operations(self):
        """Verify invite tracking, leaver deductions, bonus adjustments, leaderboard, and reset."""
        guild_id = 998877
        inviter_id = 111000

        await database.record_member_invite(guild_id, member_id=222001, inviter_id=inviter_id, invite_code="abc123")
        await database.record_member_invite(guild_id, member_id=222002, inviter_id=inviter_id, invite_code="abc123")
        stats = await database.get_user_invite_stats(guild_id, inviter_id)
        self.assertEqual(stats, {"regular": 2, "leaves": 0, "bonus": 0, "total": 2})

        left_inviter = await database.record_invited_member_leave(guild_id, member_id=222002)
        self.assertEqual(left_inviter, inviter_id)
        stats_after_leave = await database.get_user_invite_stats(guild_id, inviter_id)
        self.assertEqual(stats_after_leave, {"regular": 2, "leaves": 1, "bonus": 0, "total": 1})

        new_total = await database.adjust_bonus_invites(guild_id, inviter_id, 5)
        self.assertEqual(new_total, 6)

        board = await database.get_invite_leaderboard(guild_id, limit=5)
        self.assertEqual(len(board), 1)
        self.assertEqual(board[0]["total"], 6)

        await database.reset_guild_invites(guild_id)
        self.assertEqual(await database.get_user_invite_stats(guild_id, inviter_id), {"regular": 0, "leaves": 0, "bonus": 0, "total": 0})

    async def test_applications_database_operations(self):
        """Verify application form configs, submissions, message linking, and review status."""
        guild_id = 313131
        await database.set_application_config(
            guild_id=guild_id,
            panel_channel_id=101,
            review_channel_id=202,
            accept_role_id=303,
            title="Staff App",
            questions=["Why join?", "Timezone?"],
        )
        cfg = await database.get_application_config(guild_id)
        self.assertIsNotNone(cfg)
        self.assertEqual(cfg["questions"], ["Why join?", "Timezone?"])
        self.assertEqual(cfg["is_enabled"], 1)

        app_id = await database.create_application(
            guild_id=guild_id,
            applicant_id=9090,
            answers=[{"question": "Why join?", "answer": "To help!"}],
        )
        await database.set_application_review_message(app_id, 555777)

        by_msg = await database.get_application_by_message(555777)
        self.assertIsNotNone(by_msg)
        self.assertEqual(by_msg["id"], app_id)
        self.assertEqual(by_msg["status"], "pending")

        await database.update_application_status(app_id, "accepted", reviewer_id=4242)
        updated = await database.get_application(app_id)
        self.assertEqual(updated["status"], "accepted")
        self.assertEqual(updated["reviewed_by"], 4242)

        self.assertTrue(await database.disable_application_config(guild_id))

    async def test_timed_actions_database_operations(self):
        """Verify temporary ban and temporary role persistence, querying due, and deletion."""
        import time as pytime
        guild_id = 515151
        user_id = 616161
        past_ts = pytime.time() - 5.0

        tb_id = await database.add_timed_action(
            guild_id=guild_id,
            user_id=user_id,
            action_type="tempban",
            expires_at=past_ts,
            moderator_id=1010,
            reason="7d ban",
        )
        tr_id = await database.add_timed_action(
            guild_id=guild_id,
            user_id=user_id,
            action_type="temprole",
            expires_at=past_ts,
            role_id=777888,
            moderator_id=1010,
            reason="Temp VIP",
        )

        due_bans = await database.get_due_timed_actions(pytime.time(), action_type="tempban")
        self.assertEqual(len(due_bans), 1)
        self.assertEqual(due_bans[0]["id"], tb_id)

        due_roles = await database.get_due_timed_actions(pytime.time(), action_type="temprole")
        self.assertEqual(len(due_roles), 1)
        self.assertEqual(due_roles[0]["role_id"], 777888)

        self.assertTrue(await database.delete_timed_action(tb_id))
        self.assertTrue(await database.delete_timed_action(tr_id))
        self.assertEqual(len(await database.get_due_timed_actions(pytime.time())), 0)

    async def test_reaction_roles_database_operations(self):
        """Verify adding, querying, listing, and removing reaction role bindings."""
        guild_id = 616162
        channel_id = 717172
        message_id = 818182

        await database.add_reaction_role(guild_id, channel_id, message_id, "🎮", 9001)
        binding = await database.get_reaction_role(message_id, "🎮")
        self.assertIsNotNone(binding)
        self.assertEqual(binding["role_id"], 9001)

        all_bindings = await database.get_reaction_roles_by_guild(guild_id)
        self.assertEqual(len(all_bindings), 1)
        self.assertEqual(all_bindings[0]["emoji"], "🎮")

        removed = await database.remove_reaction_role(guild_id, message_id, "🎮")
        self.assertTrue(removed)
        self.assertIsNone(await database.get_reaction_role(message_id, "🎮"))

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

    async def test_automod_word_blacklist_and_database(self):
        """Verify blacklisted word storage and smart word-boundary matching."""
        guild_id = 777111
        self.assertTrue(await database.add_bad_word(guild_id, "scamlink", 123))
        self.assertFalse(await database.add_bad_word(guild_id, "scamlink", 123))  # duplicate
        self.assertTrue(await database.add_bad_word(guild_id, "free nitro", 123))

        words = await database.get_bad_words(guild_id)
        self.assertEqual(words, ["free nitro", "scamlink"])

        self.assertEqual(find_blacklisted_word("Click this SCAMLINK now!", words), "scamlink")
        self.assertEqual(find_blacklisted_word("claim your free nitro today", words), "free nitro")
        self.assertIsNone(find_blacklisted_word("myscamlinker is harmless", words))

        self.assertTrue(await database.remove_bad_word(guild_id, "scamlink"))
        self.assertEqual(await database.get_bad_words(guild_id), ["free nitro"])

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
        self.assertEqual(close_view.children[1].custom_id, "ticket_claim")

        role_btn = RoleButton(role_id=12345, label="Member")
        self.assertTrue(role_btn.custom_id.startswith("selfrole:role:12345"))

        role_menu = RoleMenuSelect(
            options=[discord.SelectOption(label="Red", value="111")],
            exclusive=True,
            menu_id="abc123",
        )
        self.assertEqual(role_menu.custom_id, "selfrolemenu:1:abc123")

        sug_view = SuggestionVoteView()
        self.assertEqual(sug_view.children[0].custom_id, "suggestion_btn_upvote")
        self.assertEqual(sug_view.children[1].custom_id, "suggestion_btn_downvote")

        prem_view = PremiumUpgradeView()
        self.assertEqual(prem_view.children[0].custom_id, "premium_btn_redeem")

        verify_view = VerifyLaunchView()
        self.assertEqual(verify_view.children[0].custom_id, "verify_member_btn")

        app_launch = ApplicationLaunchView()
        self.assertEqual(app_launch.children[0].custom_id, "app_launch_btn")

        app_review = ApplicationReviewView()
        self.assertEqual(app_review.children[0].custom_id, "app_btn_accept")
        self.assertEqual(app_review.children[1].custom_id, "app_btn_deny")

    def test_reminder_time_parser(self):
        """Verify time string parsing into seconds."""
        self.assertEqual(parse_time_string("30s"), 30)
        self.assertEqual(parse_time_string("10m"), 600)
        self.assertEqual(parse_time_string("2h"), 7200)
        self.assertEqual(parse_time_string("1d"), 86400)
        self.assertEqual(parse_time_string("invalid"), 0)

    def test_afk_duration_formatter(self):
        """Verify human-readable duration conversion."""
        self.assertIn("second(s)", format_duration(45))
        self.assertIn("minute(s)", format_duration(120))
        self.assertIn("hour(s)", format_duration(7200))

    # -----------------------------------------------------------------------
    # 5. End-to-End Command Callback Runtime Execution Tests
    # -----------------------------------------------------------------------

    async def test_slash_command_runtime_execution(self):
        """Execute command callback functions with simulated Discord interactions."""
        # 1. Setup mock Discord Guild
        guild = MagicMock(spec=discord.Guild)
        guild.id = 123456789
        guild.name = "Test Guild"
        guild.description = "Test Server Description"
        guild.icon = None
        guild.banner = None
        guild.created_at = datetime.datetime.now(datetime.timezone.utc)
        guild.member_count = 25
        guild.members = []
        guild.text_channels = []
        guild.voice_channels = []
        guild.stage_channels = []
        guild.categories = []
        guild.roles = []
        guild.emojis = []
        guild.stickers = []
        guild.premium_tier = 0
        guild.premium_subscription_count = 0
        guild.verification_level = discord.VerificationLevel.low
        guild.owner_id = 999999
        guild.owner = MagicMock(spec=discord.Member)
        guild.owner.mention = "@ServerOwner"
        guild.me = MagicMock(spec=discord.Member)
        guild.me.top_role = MagicMock()
        guild.me.guild_permissions = discord.Permissions.all()

        # 2. Setup mock Discord Member & User
        user = MagicMock(spec=discord.Member)
        user.id = 111111
        user.name = "TestUser"
        user.display_name = "TestUser"
        user.mention = "@TestUser"
        user.display_avatar = MagicMock()
        user.display_avatar.url = "https://example.com/avatar.png"
        user.display_avatar.with_size.return_value.url = "https://example.com/avatar1024.png"
        user.display_avatar.with_format.return_value.url = "https://example.com/avatar.png"
        user.color = discord.Color.blue()
        user.bot = False
        user.created_at = datetime.datetime.now(datetime.timezone.utc)
        user.joined_at = datetime.datetime.now(datetime.timezone.utc)
        user.top_role = MagicMock()
        user.roles = []
        user.guild_permissions = discord.Permissions.all()
        user.guild = guild

        # Target user for economy pay
        target_user = MagicMock(spec=discord.Member)
        target_user.id = 222222
        target_user.bot = False
        target_user.display_name = "Recipient"
        target_user.mention = "@Recipient"

        # 3. Setup mock Messages and Channels
        mock_msg = MagicMock(spec=discord.Message)
        mock_msg.id = 888999
        mock_msg.embeds = [discord.Embed(title="Test", color=0x5865F2)]
        mock_msg.edit = AsyncMock()
        mock_msg.delete = AsyncMock()

        mock_voice = MagicMock(spec=discord.VoiceChannel)
        mock_voice.id = 333444
        mock_voice.name = "👥 Total: 25"
        mock_voice.mention = "#voice"
        mock_voice.edit = AsyncMock()
        mock_voice.delete = AsyncMock()

        mock_category = MagicMock(spec=discord.CategoryChannel)
        mock_category.id = 444555
        mock_category.name = "📊 Server Stats"

        guild.create_voice_channel = AsyncMock(return_value=mock_voice)
        guild.create_category = AsyncMock(return_value=mock_category)

        mock_role = MagicMock(spec=discord.Role)
        mock_role.id = 555444
        mock_role.name = "Member"
        mock_role.mention = "@Member"
        mock_role.__ge__ = MagicMock(return_value=False)
        guild.roles = [mock_role]
        guild.get_role = MagicMock(return_value=mock_role)
        guild.default_role = MagicMock(spec=discord.Role)
        guild.get_member = MagicMock(return_value=guild.me)

        channel = MagicMock(spec=discord.TextChannel)
        channel.id = 222222
        channel.name = "general"
        channel.mention = "#general"
        channel.send = AsyncMock(return_value=mock_msg)
        channel.fetch_message = AsyncMock(return_value=mock_msg)
        channel.purge = AsyncMock(return_value=[mock_msg, mock_msg])
        channel.edit = AsyncMock()
        channel.overwrites_for = MagicMock(return_value=discord.PermissionOverwrite())
        channel.set_permissions = AsyncMock()
        channel.permissions_for = MagicMock(return_value=MagicMock(send_messages=True, embed_links=True))
        guild.get_channel = MagicMock(return_value=channel)

        # 4. Setup mock Interaction
        interaction = MagicMock(spec=discord.Interaction)
        interaction.guild = guild
        interaction.guild_id = guild.id
        interaction.user = user
        interaction.channel = channel
        interaction.channel_id = channel.id
        interaction.response = AsyncMock()
        interaction.followup = AsyncMock()
        interaction.entitlements = []

        # -------------------------------------------------------------
        # Utility Cog Commands
        # -------------------------------------------------------------
        util = self.bot.get_cog("Utility")
        await util.hello.callback(util, interaction)
        await util.roll.callback(util, interaction, sides=6)
        await util.eight_ball.callback(util, interaction, question="Will RookieBot scale?")
        await util.serverinfo.callback(util, interaction)
        await util.userinfo.callback(util, interaction, member=None)
        await util.avatar.callback(util, interaction, user=None)

        # -------------------------------------------------------------
        # Premium Cog Commands
        # -------------------------------------------------------------
        prem_cog = self.bot.get_cog("Premium")
        await prem_cog.premium.callback(prem_cog, interaction)
        await prem_cog.redeem_command.callback(prem_cog, interaction, key="PREM-ABCD-1234-5678")
        await prem_cog.license_generate.callback(prem_cog, interaction, duration_days=30, note="Customer A")
        await prem_cog.license_list.callback(prem_cog, interaction)
        await prem_cog.license_revoke.callback(prem_cog, interaction, guild_id=str(guild.id))

        # -------------------------------------------------------------
        # Leveling Cog Commands
        # -------------------------------------------------------------
        lvl = self.bot.get_cog("Leveling")
        await lvl.leaderboard.callback(lvl, interaction)
        await lvl.rank.callback(lvl, interaction, member=None)
        await lvl.levelrole_add.callback(lvl, interaction, level=5, role=mock_role)
        await lvl.levelrole_list.callback(lvl, interaction)
        await lvl.levelrole_remove.callback(lvl, interaction, level=5)

        # -------------------------------------------------------------
        # Embeds Cog Commands
        # -------------------------------------------------------------
        emb = self.bot.get_cog("Embeds")
        await emb.embed.callback(emb, interaction)

        # -------------------------------------------------------------
        # Moderation Cog Commands
        # -------------------------------------------------------------
        mod = self.bot.get_cog("Moderation")
        await mod.clear.callback(mod, interaction, amount=2)
        await mod.timeout.callback(mod, interaction, member=user, duration=5)
        await mod.tempban.callback(mod, interaction, user=user, duration="2h", reason="Cooldown ban")
        await mod.kick.callback(mod, interaction, member=user)
        await mod.slowmode.callback(mod, interaction, seconds=10, channel=channel)
        await mod.lock.callback(mod, interaction, channel=channel, reason="Testing lock")
        await mod.unlock.callback(mod, interaction, channel=channel)

        # -------------------------------------------------------------
        # Polls & Persistent Giveaways Cog Commands
        # -------------------------------------------------------------
        polls = self.bot.get_cog("Polls")
        msg_mock = AsyncMock()
        msg_mock.id = 987654321
        reaction_mock = MagicMock()
        reaction_mock.emoji = "🎉"

        async def mock_react_users():
            yield user

        reaction_mock.users = mock_react_users
        msg_mock.reactions = [reaction_mock]
        channel.fetch_message = AsyncMock(return_value=msg_mock)
        guild.get_channel = MagicMock(return_value=channel)

        interaction.original_response = AsyncMock(return_value=msg_mock)
        await polls.poll.callback(polls, interaction, question="Favorite Language?", option1="Python", option2="Rust")
        await polls.giveaway_start.callback(polls, interaction, prize="VIP Role", duration=30, winners=1)
        await polls.giveaway_list.callback(polls, interaction)
        await polls.giveaway_end.callback(polls, interaction, message_id="987654321")
        await polls.giveaway_reroll.callback(polls, interaction, message_id="987654321", winners=1)

        # -------------------------------------------------------------
        # Logging Cog Commands & Expanded Audit Listeners
        # -------------------------------------------------------------
        logging_cog = self.bot.get_cog("Logging")
        await logging_cog.setlogs.callback(logging_cog, interaction, channel=channel)

        # Verify SQLite WAL mode is active
        with database._get_connection() as conn:
            mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
            self.assertEqual(mode.lower(), "wal")

        # Verify expanded audit listeners (join, nickname/role update, voice transitions)
        guild.get_channel = MagicMock(return_value=channel)
        channel.permissions_for = MagicMock(return_value=discord.Permissions(send_messages=True))
        user.created_at = discord.utils.utcnow()
        user.bot = False
        user.nick = "OldNick"
        user.roles = [mock_role]

        after_user = MagicMock(spec=discord.Member)
        after_user.id = user.id
        after_user.guild = guild
        after_user.bot = False
        after_user.name = user.name
        after_user.mention = user.mention
        after_user.display_avatar = user.display_avatar
        after_user.nick = "NewNick"
        extra_role = MagicMock(spec=discord.Role)
        extra_role.id = 888777
        extra_role.mention = "@ExtraRole"
        after_user.roles = [mock_role, extra_role]

        await logging_cog.on_member_join(user)
        await logging_cog.on_member_update(user, after_user)

        vc_before = MagicMock(spec=discord.VoiceState)
        vc_before.channel = None
        vc_after = MagicMock(spec=discord.VoiceState)
        vc_after.channel = mock_voice
        await logging_cog.on_voice_state_update(user, vc_before, vc_after)
        await logging_cog.on_voice_state_update(user, vc_after, vc_before)

        # -------------------------------------------------------------
        # Tickets Cog Commands & Transcript / Claim Testing
        # -------------------------------------------------------------
        tix = self.bot.get_cog("Tickets")
        await tix.ticketsetup.callback(tix, interaction, channel=channel, transcript_channel=channel)

        self.assertEqual(extract_ticket_owner_id("Support ticket for User (ID: 123456)"), 123456)
        self.assertIsNone(extract_ticket_owner_id("Random topic"))

        ticket_ch = MagicMock(spec=discord.TextChannel)
        ticket_ch.id = 778899
        ticket_ch.name = "ticket-testuser"
        ticket_ch.guild = guild
        ticket_ch.topic = f"Support ticket for TestUser (ID: {user.id})"
        ticket_ch.send = AsyncMock()
        ticket_ch.edit = AsyncMock()
        ticket_ch.delete = AsyncMock()

        msg_entry = MagicMock()
        msg_entry.created_at = discord.utils.utcnow()
        msg_entry.author = user
        msg_entry.content = "Hello, I need help with my role."
        msg_entry.embeds = []
        att_mock = MagicMock()
        att_mock.filename = "screenshot.png"
        att_mock.url = "https://example.com/screenshot.png"
        msg_entry.attachments = [att_mock]

        async def mock_history(limit=500, oldest_first=True):
            yield msg_entry

        ticket_ch.history = mock_history
        transcript_text = await generate_ticket_transcript(ticket_ch)
        self.assertIn("ticket-testuser", transcript_text)
        self.assertIn("Hello, I need help with my role.", transcript_text)
        self.assertIn("screenshot.png", transcript_text)

        # Test Claim Ticket button
        ticket_interaction = MagicMock(spec=discord.Interaction)
        ticket_interaction.guild = guild
        ticket_interaction.channel = ticket_ch
        ticket_interaction.user = user
        user.guild_permissions = discord.Permissions(administrator=True)
        ticket_interaction.response = AsyncMock()
        ticket_interaction.response.edit_message = AsyncMock()
        ticket_interaction.response.send_message = AsyncMock()

        close_view_inst = CloseTicketView()
        await close_view_inst.claim_ticket.callback(ticket_interaction)
        self.assertTrue(close_view_inst.children[1].disabled)
        self.assertIn("Claimed by", close_view_inst.children[1].label)

        # Test Close Ticket button with fast sleep patch
        from unittest.mock import patch
        guild.get_channel = MagicMock(return_value=channel)
        guild.get_member = MagicMock(return_value=user)
        user.send = AsyncMock()
        with patch("cogs.tickets.asyncio.sleep", new=AsyncMock()):
            await close_view_inst.close_ticket.callback(ticket_interaction)
        ticket_ch.delete.assert_called_once()
        self.assertTrue(channel.send.called)

        # -------------------------------------------------------------
        # AutoMod Cog Commands & Anti-Raid Join Guard
        # -------------------------------------------------------------
        am = self.bot.get_cog("AutoMod")
        await am.automod_status.callback(am, interaction)
        choice_mock = app_commands.Choice(name="Anti-Invite Links", value="anti_invite")
        await am.automod_toggle.callback(am, interaction, filter_name=choice_mock, enabled=True)
        await am.word_add.callback(am, interaction, word="badword")
        await am.word_list.callback(am, interaction)
        await am.word_remove.callback(am, interaction, word="badword")

        # Simulate rapid join burst triggering Anti-Raid timeout
        guild.me.guild_permissions = discord.Permissions.all()
        guild.me.top_role.__gt__ = MagicMock(return_value=True)
        user.timeout = AsyncMock()
        for _ in range(5):
            await am.on_member_join(user)
        self.assertTrue(user.timeout.called)

        # -------------------------------------------------------------
        # AFK Cog Commands
        # -------------------------------------------------------------
        afk_cog = self.bot.get_cog("AFK")
        await afk_cog.afk.callback(afk_cog, interaction, reason="Lunch break")

        # -------------------------------------------------------------
        # Reminders Cog Commands
        # -------------------------------------------------------------
        rem_cog = self.bot.get_cog("Reminders")
        await rem_cog.remindme.callback(rem_cog, interaction, time="10m", message="Check oven")

        # -------------------------------------------------------------
        # Economy Cog Commands
        # -------------------------------------------------------------
        eco_cog = self.bot.get_cog("Economy")
        await eco_cog.balance.callback(eco_cog, interaction, member=None)
        await eco_cog.daily.callback(eco_cog, interaction)
        coin_choice = app_commands.Choice(name="Heads", value="heads")
        await eco_cog.coinflip.callback(eco_cog, interaction, bet=50, choice=coin_choice)
        await eco_cog.pay.callback(eco_cog, interaction, member=target_user, amount=50)
        await eco_cog.work.callback(eco_cog, interaction)
        await eco_cog.richest.callback(eco_cog, interaction)
        await eco_cog.slots.callback(eco_cog, interaction, bet=20)
        await eco_cog.rob.callback(eco_cog, interaction, member=target_user)
        await eco_cog.eco_give.callback(eco_cog, interaction, member=target_user, amount=100)
        await eco_cog.eco_take.callback(eco_cog, interaction, member=target_user, amount=50)
        await eco_cog.shop_add.callback(eco_cog, interaction, name="VIP Role", price=50, description="VIP perks", role=mock_role)
        await eco_cog.shop_view.callback(eco_cog, interaction)
        await eco_cog.buy.callback(eco_cog, interaction, item_id=1)
        await eco_cog.inventory.callback(eco_cog, interaction, member=None)
        await eco_cog.shop_remove.callback(eco_cog, interaction, item_id=1)

        # -------------------------------------------------------------
        # Events Cog Commands (Welcome & Leave configuration)
        # -------------------------------------------------------------
        events_cog = self.bot.get_cog("Events")
        await events_cog.setwelcome.callback(events_cog, interaction, channel=channel, custom_message="Welcome {user}!")
        await events_cog.setleave.callback(events_cog, interaction, channel=channel, custom_message="Bye {username}!")

        # -------------------------------------------------------------
        # Sticky Cog Commands
        # -------------------------------------------------------------
        sticky_cog = self.bot.get_cog("Sticky")
        await sticky_cog.sticky_set.callback(sticky_cog, interaction, message="Important notice!")
        await sticky_cog.sticky_remove.callback(sticky_cog, interaction)

        # -------------------------------------------------------------
        # Starboard Cog Commands
        # -------------------------------------------------------------
        sb_cog = self.bot.get_cog("Starboard")
        await sb_cog.setup_starboard.callback(sb_cog, interaction, channel=channel, threshold=3)
        await sb_cog.disable_starboard.callback(sb_cog, interaction)

        # -------------------------------------------------------------
        # Suggestions Cog Commands
        # -------------------------------------------------------------
        sug_cog = self.bot.get_cog("Suggestions")
        await sug_cog.set_suggest_channel.callback(sug_cog, interaction, channel=channel)
        await sug_cog.submit_suggestion.callback(sug_cog, interaction, suggestion="Add more voice channels")

        # -------------------------------------------------------------
        # Tags Cog Commands
        # -------------------------------------------------------------
        tag_cog = self.bot.get_cog("Tags")
        await tag_cog.add_tag.callback(tag_cog, interaction, name="rules", content="Rules here!")
        await tag_cog.get_tag_cmd.callback(tag_cog, interaction, name="rules")
        await tag_cog.list_tags_cmd.callback(tag_cog, interaction)
        await tag_cog.delete_tag_cmd.callback(tag_cog, interaction, name="rules")

        # -------------------------------------------------------------
        # ServerStats Cog Commands
        # -------------------------------------------------------------
        stats_cog = self.bot.get_cog("ServerStats")
        await stats_cog.setup_stats.callback(stats_cog, interaction)
        await stats_cog.refresh_stats.callback(stats_cog, interaction)
        await stats_cog.remove_stats.callback(stats_cog, interaction)

        # -------------------------------------------------------------
        # Help Cog Commands
        # -------------------------------------------------------------
        help_cog = self.bot.get_cog("Help")
        await help_cog.help_command.callback(help_cog, interaction)

        # -------------------------------------------------------------
        # AutoRole Cog Commands
        # -------------------------------------------------------------
        ar_cog = self.bot.get_cog("AutoRole")
        await ar_cog.autorole_set.callback(ar_cog, interaction, member_role=mock_role, bot_role=None)
        await ar_cog.autorole_status.callback(ar_cog, interaction)
        await ar_cog.autorole_remove.callback(ar_cog, interaction)

        # -------------------------------------------------------------
        # AutoResponder Cog Commands
        # -------------------------------------------------------------
        responder_cog = self.bot.get_cog("AutoResponder")
        match_choice = app_commands.Choice(name="Contains", value="contains")
        await responder_cog.ar_add.callback(responder_cog, interaction, trigger="faq", response="Check info", match_type=match_choice)
        await responder_cog.ar_list.callback(responder_cog, interaction)
        await responder_cog.ar_delete.callback(responder_cog, interaction, responder_id=1)

        # -------------------------------------------------------------
        # Warns Cog Commands
        # -------------------------------------------------------------
        warn_cog = self.bot.get_cog("Warns")
        warn_target = MagicMock(spec=discord.Member)
        warn_target.id = 889900
        warn_target.name = "WarnTarget"
        warn_target.display_name = "WarnTarget"
        warn_target.mention = "@WarnTarget"
        warn_target.top_role = MagicMock()
        warn_target.display_avatar.url = "https://example.com/avatar.png"
        warn_target.send = AsyncMock()
        warn_target.timeout = AsyncMock()
        warn_target.kick = AsyncMock()
        warn_target.ban = AsyncMock()

        user.top_role.__le__ = MagicMock(return_value=False)
        guild.me.top_role.__le__ = MagicMock(return_value=False)

        await warn_cog.warn.callback(warn_cog, interaction, member=warn_target, reason="First warning")
        await warn_cog.warnings.callback(warn_cog, interaction, member=warn_target)
        await warn_cog.delwarn.callback(warn_cog, interaction, infraction_id=1)
        await warn_cog.clearwarns.callback(warn_cog, interaction, member=warn_target)

        # -------------------------------------------------------------
        # Verification Cog Commands
        # -------------------------------------------------------------
        verify_cog = self.bot.get_cog("Verification")
        user.add_roles = AsyncMock()
        await verify_cog.verifysetup.callback(verify_cog, interaction, channel=channel, role=mock_role)
        await verify_cog.verifystatus.callback(verify_cog, interaction)
        await verify_cog.verifyremove.callback(verify_cog, interaction)

        # Test verification button click
        verify_btn_view = VerifyLaunchView()
        await verify_btn_view.children[0].callback(interaction)

        # -------------------------------------------------------------
        # TempVC Cog Commands & Voice Listeners
        # -------------------------------------------------------------
        tempvc_cog = self.bot.get_cog("TempVC")
        await tempvc_cog.tempvc_setup.callback(tempvc_cog, interaction, category=mock_category, channel_name="➕ Join to Create")
        await tempvc_cog.tempvc_status.callback(tempvc_cog, interaction)
        await tempvc_cog.tempvc_remove.callback(tempvc_cog, interaction)

        # Mock owner in temporary voice channel
        user.voice = MagicMock()
        user.voice.channel = mock_voice
        mock_voice.overwrites_for = MagicMock(return_value=discord.PermissionOverwrite())
        mock_voice.set_permissions = AsyncMock()
        await database.add_temp_channel(mock_voice.id, guild.id, user.id)

        await tempvc_cog.vc_lock.callback(tempvc_cog, interaction)
        await tempvc_cog.vc_unlock.callback(tempvc_cog, interaction)
        await tempvc_cog.vc_limit.callback(tempvc_cog, interaction, limit=5)
        await tempvc_cog.vc_name.callback(tempvc_cog, interaction, new_name="Chilling Room")

        # Voice state listener testing
        # 1. Join generator
        master_state = MagicMock(spec=discord.VoiceState)
        master_state.channel = mock_voice
        await database.set_temp_vc_settings(guild.id, mock_voice.id, mock_category.id)
        user.move_to = AsyncMock()
        guild.create_voice_channel = AsyncMock(return_value=mock_voice)

        await tempvc_cog.on_voice_state_update(user, MagicMock(channel=None), master_state)

        # 2. Leave temp channel
        leave_state = MagicMock(spec=discord.VoiceState)
        leave_state.channel = None
        mock_voice.members = []
        await tempvc_cog.on_voice_state_update(user, master_state, leave_state)

        # -------------------------------------------------------------
        # Birthdays Cog Commands
        # -------------------------------------------------------------
        bday_cog = self.bot.get_cog("Birthdays")
        month_choice = app_commands.Choice(name="November", value=11)
        await bday_cog.birthday_setup.callback(bday_cog, interaction, channel=channel, role=mock_role)
        await bday_cog.birthday_set.callback(bday_cog, interaction, month=month_choice, day=25)
        await bday_cog.birthday_view.callback(bday_cog, interaction, member=None)
        await bday_cog.birthday_upcoming.callback(bday_cog, interaction)
        await bday_cog.birthday_disable.callback(bday_cog, interaction)
        await bday_cog.birthday_remove.callback(bday_cog, interaction)

        # -------------------------------------------------------------
        # Roles Cog & Dropdown Role Menu Commands
        # -------------------------------------------------------------
        roles_cog = self.bot.get_cog("Roles")
        mock_role.is_default = MagicMock(return_value=False)
        mock_role.managed = False
        mock_role2 = MagicMock(spec=discord.Role)
        mock_role2.id = 555667
        mock_role2.name = "Blue"
        mock_role2.mention = "@Blue"
        mock_role2.is_default = MagicMock(return_value=False)
        mock_role2.managed = False

        await roles_cog.rolepanel.callback(roles_cog, interaction, title="Roles", role1=mock_role)
        await roles_cog.rolemenu.callback(roles_cog, interaction, title="Colors", role1=mock_role, role2=mock_role2, exclusive=True)
        await roles_cog.temprole.callback(roles_cog, interaction, member=user, role=mock_role2, duration="6h", reason="Event prize")

        # Simulate exclusive dropdown selection swapping mock_role -> mock_role2
        user.roles = [mock_role]
        user.remove_roles = AsyncMock()
        guild.get_role = MagicMock(side_effect=lambda rid: mock_role2 if rid == mock_role2.id else mock_role)
        select_item = discord.ui.Select(
            custom_id="selfrolemenu:1:test1",
            options=[
                discord.SelectOption(label="MockRole", value=str(mock_role.id)),
                discord.SelectOption(label="Blue", value=str(mock_role2.id)),
            ],
        )
        select_item._values = [str(mock_role2.id)]
        menu_dyn = RoleMenuSelect(options=list(select_item.options), exclusive=True, menu_id="test1", select_item=select_item)
        await menu_dyn.callback(interaction)
        user.remove_roles.assert_called()
        user.add_roles.assert_called()

        # Classic Emoji Reaction Roles flow
        mock_msg.add_reaction = AsyncMock()
        mock_msg.jump_url = "https://discord.com/channels/12345/67890/999999"
        channel.fetch_message = AsyncMock(return_value=mock_msg)
        await roles_cog.reactionrole_add.callback(
            roles_cog, interaction, message_id=str(mock_msg.id), emoji="🎮", role=mock_role2, channel=channel
        )
        await roles_cog.reactionrole_list.callback(roles_cog, interaction)

        add_payload = MagicMock(spec=discord.RawReactionActionEvent)
        add_payload.guild_id = guild.id
        add_payload.message_id = mock_msg.id
        add_payload.user_id = user.id
        add_payload.emoji = discord.PartialEmoji.from_str("🎮")
        add_payload.member = user
        user.roles = []
        user.add_roles.reset_mock()
        orig_get_guild = self.bot.get_guild
        self.bot.get_guild = MagicMock(return_value=guild)
        try:
            await roles_cog.on_raw_reaction_add(add_payload)
            user.add_roles.assert_called_with(mock_role2, reason="Reaction role added (🎮)")

            rem_payload = MagicMock(spec=discord.RawReactionActionEvent)
            rem_payload.guild_id = guild.id
            rem_payload.message_id = mock_msg.id
            rem_payload.user_id = user.id
            rem_payload.emoji = discord.PartialEmoji.from_str("🎮")
            guild.get_member = MagicMock(return_value=user)
            user.roles = [mock_role2]
            user.remove_roles.reset_mock()
            await roles_cog.on_raw_reaction_remove(rem_payload)
            user.remove_roles.assert_called_with(mock_role2, reason="Reaction role removed (🎮)")
        finally:
            self.bot.get_guild = orig_get_guild

        await roles_cog.reactionrole_remove.callback(
            roles_cog, interaction, message_id=str(mock_msg.id), emoji="🎮"
        )

        # -------------------------------------------------------------
        # Invites Cog Commands & Join/Leave Listeners
        # -------------------------------------------------------------
        inv_cog = self.bot.get_cog("Invites")
        mock_inv = MagicMock(spec=discord.Invite)
        mock_inv.code = "rookie123"
        mock_inv.uses = 1
        mock_inv.inviter = target_user
        guild.invites = AsyncMock(return_value=[mock_inv])
        inv_cog._invite_cache[guild.id] = {"rookie123": 0}

        await inv_cog.on_member_join(user)
        await inv_cog.invites.callback(inv_cog, interaction, member=target_user)
        await inv_cog.inviteleaderboard.callback(inv_cog, interaction)
        await inv_cog.invitebonus.callback(inv_cog, interaction, member=target_user, amount=3)
        await inv_cog.on_member_remove(user)
        await inv_cog.invitereset.callback(inv_cog, interaction)

        # -------------------------------------------------------------
        # Applications Cog Commands & Review Flow
        # -------------------------------------------------------------
        app_cog = self.bot.get_cog("Applications")
        await app_cog.apply_setup.callback(
            app_cog,
            interaction,
            panel_channel=channel,
            review_channel=channel,
            question1="Why do you want to be staff?",
            question2="What is your timezone?",
            accept_role=mock_role,
        )
        await app_cog.apply_status.callback(app_cog, interaction)

        created_app_id = await database.create_application(
            guild.id, user.id, [{"question": "Why?", "answer": "Active daily"}]
        )
        await database.set_application_review_message(created_app_id, mock_msg.id)
        review_interaction = MagicMock(spec=discord.Interaction)
        review_interaction.guild = guild
        review_interaction.user = user
        review_interaction.message = mock_msg
        review_interaction.response = AsyncMock()
        guild.get_member = MagicMock(return_value=user)
        guild.get_role = MagicMock(return_value=mock_role)
        user.send = AsyncMock()

        review_view = ApplicationReviewView()
        await review_view.accept_button.callback(review_interaction)
        reviewed = await database.get_application(created_app_id)
        self.assertEqual(reviewed["status"], "accepted")

        await app_cog.apply_disable.callback(app_cog, interaction)

        # Assert responses were sent without errors across all calls
        self.assertTrue(interaction.response.send_message.called or interaction.channel.send.called)


# Backward compatibility alias
TestDiscordUtilityBot = TestRookieBot


if __name__ == "__main__":
    unittest.main()
