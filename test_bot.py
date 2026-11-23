"""Automated Test Suite for Discord Utility Bot.

Validates all 18 Cogs, 37 Slash Commands, Database Operations,
Auto-Mod Regex, UI Modals/Buttons/Views, and Gamification logic.
"""

import os
import sys
import asyncio
import datetime
import tempfile
import unittest
from unittest.mock import AsyncMock, MagicMock

import discord
from discord import app_commands
from discord.ext import commands

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database
from cogs.embeds import parse_color
from cogs.leveling import render_progress_bar
from cogs.automod import INVITE_REGEX
from cogs.roles import RoleButton
from cogs.tickets import TicketLaunchView, CloseTicketView
from cogs.suggestions import SuggestionVoteView
from cogs.premium import PremiumUpgradeView, RedeemKeyModal
from cogs.reminders import parse_time_string
from cogs.afk import format_duration
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

    def test_all_19_cogs_loaded(self):
        """Verify all 19 Cogs are discovered and successfully loaded."""
        expected_cogs = {
            "AFK",
            "AutoMod",
            "Economy",
            "Embeds",
            "Events",
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
            "Tickets",
            "Utility",
        }
        loaded_cogs = set(self.bot.cogs.keys())
        self.assertEqual(
            expected_cogs,
            loaded_cogs,
            f"Missing or mismatched cogs: {expected_cogs - loaded_cogs}",
        )

    def test_all_39_slash_commands_registered(self):
        """Verify all 39 application commands are present in the command tree."""
        expected_commands = {
            "afk",
            "automod",
            "avatar",
            "balance",
            "ban",
            "clear",
            "coinflip",
            "daily",
            "embed",
            "giveaway",
            "hello",
            "kick",
            "leaderboard",
            "license",
            "pay",
            "poll",
            "premium",
            "rank",
            "redeem",
            "remindme",
            "role",
            "rolepanel",
            "roll",
            "serverinfo",
            "serverstats",
            "setleave",
            "setlogs",
            "setsuggestchannel",
            "setwelcome",
            "starboard",
            "sticky",
            "suggest",
            "suggeststatus",
            "tag",
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

        sug_view = SuggestionVoteView()
        self.assertEqual(sug_view.children[0].custom_id, "suggestion_btn_upvote")
        self.assertEqual(sug_view.children[1].custom_id, "suggestion_btn_downvote")

        prem_view = PremiumUpgradeView()
        self.assertEqual(prem_view.children[0].custom_id, "premium_btn_redeem")

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

        channel = MagicMock(spec=discord.TextChannel)
        channel.id = 222222
        channel.name = "general"
        channel.mention = "#general"
        channel.send = AsyncMock(return_value=mock_msg)
        channel.fetch_message = AsyncMock(return_value=mock_msg)
        channel.purge = AsyncMock(return_value=[mock_msg, mock_msg])
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
        await mod.kick.callback(mod, interaction, member=user)

        # -------------------------------------------------------------
        # Polls Cog Commands
        # -------------------------------------------------------------
        polls = self.bot.get_cog("Polls")
        msg_mock = AsyncMock()
        interaction.original_response = AsyncMock(return_value=msg_mock)
        await polls.poll.callback(polls, interaction, question="Favorite Language?", option1="Python", option2="Rust")

        # -------------------------------------------------------------
        # Logging Cog Commands
        # -------------------------------------------------------------
        logging_cog = self.bot.get_cog("Logging")
        await logging_cog.setlogs.callback(logging_cog, interaction, channel=channel)

        # -------------------------------------------------------------
        # Tickets Cog Commands
        # -------------------------------------------------------------
        tix = self.bot.get_cog("Tickets")
        await tix.ticketsetup.callback(tix, interaction, channel=channel)

        # -------------------------------------------------------------
        # AutoMod Cog Commands
        # -------------------------------------------------------------
        am = self.bot.get_cog("AutoMod")
        await am.automod_status.callback(am, interaction)
        choice_mock = app_commands.Choice(name="Anti-Invite Links", value="anti_invite")
        await am.automod_toggle.callback(am, interaction, filter_name=choice_mock, enabled=True)

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

        # Assert responses were sent without errors across all calls
        self.assertTrue(interaction.response.send_message.called or interaction.channel.send.called)


if __name__ == "__main__":
    unittest.main()
