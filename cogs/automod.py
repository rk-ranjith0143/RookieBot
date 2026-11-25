import re
import time
import datetime
import asyncio
from collections import defaultdict
from typing import List, Optional

import discord
from discord import app_commands
from discord.ext import commands

from database import (
    get_guild_settings,
    update_guild_setting,
    add_bad_word,
    remove_bad_word,
    get_bad_words,
)

INVITE_REGEX = re.compile(
    r"(?:https?://)?(?:www\.)?(?:discord\.(?:gg|io|me|li)|discord(?:app)?\.com/invite)/[a-zA-Z0-9]+",
    re.IGNORECASE,
)

SPAM_TRACKER = defaultdict(list)
JOIN_TRACKER = defaultdict(list)
RAID_ALERT_COOLDOWNS = {}
MAX_MENTIONS = 5
RAID_JOIN_THRESHOLD = 5
RAID_WINDOW_SECONDS = 10.0


def find_blacklisted_word(content: str, words: List[str]) -> Optional[str]:
    """Return the first matched blacklisted word/phrase in content, or None."""
    if not content or not words:
        return None
    text_lower = content.lower()
    for word in words:
        if not word:
            continue
        # Use whole-word boundary matching for single alphanumeric words to avoid false positives
        if re.fullmatch(r"[a-z0-9_]+", word):
            if re.search(rf"\b{re.escape(word)}\b", text_lower):
                return word
        elif word in text_lower:
            return word
    return None


def is_automod_exempt(member: discord.Member) -> bool:
    """Check if a member is exempt from automated moderation rules."""
    if member.bot:
        return True
    if member.id == member.guild.owner_id:
        return True
    perms = member.guild_permissions
    return perms.administrator or perms.manage_guild or perms.manage_messages


class AutoMod(commands.Cog):
    """Automated content filtering, word blacklists, and anti-raid server protection."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    automod_group = app_commands.Group(
        name="automod",
        description="View and configure automated moderation settings and filters",
    )

    word_group = app_commands.Group(
        name="word",
        description="Manage custom blacklisted words and phrases",
        parent=automod_group,
        default_permissions=discord.Permissions(manage_guild=True),
    )

    @automod_group.command(name="status", description="View current auto-moderation filters and rules")
    async def automod_status(self, interaction: discord.Interaction):
        """Displays auto-moderation status and active protections."""
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        settings = await get_guild_settings(interaction.guild_id)
        bad_words = await get_bad_words(interaction.guild_id)

        embed = discord.Embed(
            title="🛡️ Auto-Moderation System Status",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(
            name="🔗 Anti-Invite Links",
            value="🟢 **Enabled**" if settings.get("anti_invite", 1) else "🔴 **Disabled**",
            inline=False,
        )
        embed.add_field(
            name="📢 Anti-Mass Mention",
            value=f"🟢 **Enabled** (Blocks {MAX_MENTIONS}+ users)" if settings.get("anti_mass_mention", 1) else "🔴 **Disabled**",
            inline=False,
        )
        embed.add_field(
            name="⚡ Anti-Spam / Flood",
            value="🟢 **Enabled** (Deletes rapid flood > 5 msgs/5s)" if settings.get("anti_spam", 1) else "🔴 **Disabled**",
            inline=False,
        )
        embed.add_field(
            name="🚫 Custom Word Blacklist",
            value=f"🟢 **Enabled** ({len(bad_words)} word(s))" if settings.get("anti_word_filter", 1) else "🔴 **Disabled**",
            inline=False,
        )
        embed.add_field(
            name="🚨 Auto Anti-Raid Join Guard",
            value=f"🟢 **Enabled** (Flags {RAID_JOIN_THRESHOLD}+ joins/{int(RAID_WINDOW_SECONDS)}s)" if settings.get("anti_raid", 1) else "🔴 **Disabled**",
            inline=False,
        )
        embed.add_field(
            name="🛡️ Exemptions",
            value="Server Owner, Administrators, and Members with `Manage Messages` / `Manage Server`.",
            inline=False,
        )
        embed.set_footer(text="Use /automod toggle or /automod word to configure protections.")
        await interaction.response.send_message(embed=embed)

    @automod_group.command(name="toggle", description="Enable or disable a specific auto-mod protection")
    @app_commands.describe(
        filter_name="The auto-mod filter to toggle",
        enabled="Whether to enable (True) or disable (False) the filter",
    )
    @app_commands.choices(
        filter_name=[
            app_commands.Choice(name="Anti-Invite Links", value="anti_invite"),
            app_commands.Choice(name="Anti-Mass Mention", value="anti_mass_mention"),
            app_commands.Choice(name="Anti-Spam / Flood", value="anti_spam"),
            app_commands.Choice(name="Custom Word Blacklist", value="anti_word_filter"),
            app_commands.Choice(name="Auto Anti-Raid Join Guard", value="anti_raid"),
        ]
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def automod_toggle(
        self,
        interaction: discord.Interaction,
        filter_name: app_commands.Choice[str],
        enabled: bool,
    ):
        """Toggles a specific auto-mod protection."""
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        key = filter_name.value
        await update_guild_setting(interaction.guild_id, key, 1 if enabled else 0)
        state_str = "🟢 **Enabled**" if enabled else "🔴 **Disabled**"

        embed = discord.Embed(
            title="🛡️ Auto-Mod Setting Updated",
            description=f"{filter_name.name} is now {state_str}.",
            color=discord.Color.green() if enabled else discord.Color.orange(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_footer(text=f"Updated by {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

    # -----------------------------------------------------------------------
    # Custom Word Blacklist Commands
    # -----------------------------------------------------------------------

    @word_group.command(name="add", description="Add a banned word or phrase to AutoMod")
    @app_commands.describe(word="Word or phrase to block (2-50 characters, case-insensitive)")
    async def word_add(self, interaction: discord.Interaction, word: str):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        clean_word = word.strip().lower()
        if len(clean_word) < 2 or len(clean_word) > 50:
            await interaction.response.send_message("❌ Word/phrase must be between 2 and 50 characters.", ephemeral=True)
            return

        existing = await get_bad_words(interaction.guild.id)
        if len(existing) >= 100:
            await interaction.response.send_message("❌ Blacklist limit reached (100 words max per server).", ephemeral=True)
            return

        added = await add_bad_word(interaction.guild.id, clean_word, interaction.user.id)
        if not added:
            await interaction.response.send_message(f"ℹ️ `{clean_word}` is already in the blacklist.", ephemeral=True)
            return

        embed = discord.Embed(
            title="🚫 Blacklisted Word Added",
            description=f"`{clean_word}` will now be automatically blocked by AutoMod.",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @word_group.command(name="remove", description="Remove a word or phrase from the AutoMod blacklist")
    @app_commands.describe(word="The blacklisted word or phrase to remove")
    async def word_remove(self, interaction: discord.Interaction, word: str):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        clean_word = word.strip().lower()
        removed = await remove_bad_word(interaction.guild.id, clean_word)
        if removed:
            await interaction.response.send_message(f"✅ Removed `{clean_word}` from the blacklist.", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ `{clean_word}` was not found in the blacklist.", ephemeral=True)

    @word_group.command(name="list", description="View all blacklisted words configured on this server")
    async def word_list(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        words = await get_bad_words(interaction.guild.id)
        if not words:
            await interaction.response.send_message("ℹ️ No blacklisted words configured yet. Use `/automod word add`.", ephemeral=True)
            return

        formatted = ", ".join(f"`{w}`" for w in words[:50])
        if len(words) > 50:
            formatted += f" ...and {len(words) - 50} more"

        embed = discord.Embed(
            title=f"🚫 AutoMod Blacklisted Words ({len(words)})",
            description=formatted,
            color=discord.Color.red(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # -----------------------------------------------------------------------
    # Listeners
    # -----------------------------------------------------------------------

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Detect rapid join raids and temporarily contain raid accounts."""
        if member.bot or not member.guild:
            return

        guild = member.guild
        settings = await get_guild_settings(guild.id)
        if not settings.get("anti_raid", 1):
            return

        now = time.time()
        recent_joins = [t for t in JOIN_TRACKER[guild.id] if now - t < RAID_WINDOW_SECONDS]
        recent_joins.append(now)
        JOIN_TRACKER[guild.id] = recent_joins

        if len(recent_joins) >= RAID_JOIN_THRESHOLD:
            if guild.me and guild.me.guild_permissions.moderate_members and guild.me.top_role > member.top_role:
                try:
                    await member.timeout(
                        datetime.timedelta(minutes=10),
                        reason="Auto-Mod: Anti-Raid sudden join burst protection",
                    )
                except (discord.Forbidden, discord.HTTPException):
                    pass

            last_alert = RAID_ALERT_COOLDOWNS.get(guild.id, 0.0)
            if now - last_alert > 30.0:
                RAID_ALERT_COOLDOWNS[guild.id] = now
                log_cid = settings.get("mod_log_channel_id")
                if log_cid:
                    log_chan = guild.get_channel(log_cid)
                    if isinstance(log_chan, discord.TextChannel):
                        embed = discord.Embed(
                            title="🚨 Anti-Raid Alert Triggered",
                            description=(
                                f"Detected **{len(recent_joins)} joins within {int(RAID_WINDOW_SECONDS)} seconds**!\n"
                                f"Incoming join {member.mention} (`{member.id}`) has been placed on a **10-minute containment timeout**."
                            ),
                            color=discord.Color.dark_red(),
                            timestamp=discord.utils.utcnow(),
                        )
                        try:
                            await log_chan.send(embed=embed)
                        except (discord.Forbidden, discord.HTTPException):
                            pass

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Monitor messages for invite links, mass mentions, blacklisted words, and spam flooding."""
        if message.author.bot or not message.guild:
            return

        author = message.author

        if isinstance(author, discord.Member) and not is_automod_exempt(author):
            settings = await get_guild_settings(message.guild.id)

            # 1. Anti-Invite Links
            if settings.get("anti_invite", 1) and INVITE_REGEX.search(message.content):
                try:
                    await message.delete()
                    warn = await message.channel.send(
                        f"⚠️ {author.mention}, posting external Discord invite links is not allowed!",
                    )
                    await asyncio.sleep(5)
                    await warn.delete()
                except (discord.Forbidden, discord.NotFound, discord.HTTPException):
                    pass
                return

            # 2. Custom Word Blacklist Filter
            if settings.get("anti_word_filter", 1):
                bad_words = await get_bad_words(message.guild.id)
                matched = find_blacklisted_word(message.content, bad_words)
                if matched:
                    try:
                        await message.delete()
                        warn = await message.channel.send(
                            f"⚠️ {author.mention}, your message contained a restricted word or phrase.",
                        )
                        await asyncio.sleep(5)
                        await warn.delete()
                    except (discord.Forbidden, discord.NotFound, discord.HTTPException):
                        pass
                    return

            # 3. Anti-Mass Mentions
            if settings.get("anti_mass_mention", 1):
                mention_count = len(message.mentions)
                has_unauthorized_everyone = (
                    message.mention_everyone and not author.guild_permissions.mention_everyone
                )
                if mention_count >= MAX_MENTIONS or has_unauthorized_everyone:
                    try:
                        await message.delete()
                        warn = await message.channel.send(
                            f"⚠️ {author.mention}, mass mentions and spam pings are prohibited!",
                        )
                        await asyncio.sleep(5)
                        await warn.delete()
                    except (discord.Forbidden, discord.NotFound, discord.HTTPException):
                        pass
                    return

            # 4. Anti-Spam / Flood Detection
            if settings.get("anti_spam", 1):
                now = time.time()
                user_times = SPAM_TRACKER[author.id]
                valid_times = [t for t in user_times if now - t < 5.0]
                valid_times.append(now)
                SPAM_TRACKER[author.id] = valid_times
                msg_count = len(valid_times)

                if msg_count > 5:
                    try:
                        await message.delete()
                    except (discord.Forbidden, discord.NotFound, discord.HTTPException):
                        pass

                    guild = message.guild
                    if (
                        msg_count >= 8
                        and guild.me.guild_permissions.moderate_members
                        and guild.me.top_role > author.top_role
                    ):
                        try:
                            await author.timeout(
                                datetime.timedelta(minutes=1),
                                reason="Auto-Mod: Automated message spam / flood protection",
                            )
                            warn = await message.channel.send(
                                f"⏳ {author.mention} was placed on a 1-minute timeout for spamming.",
                            )
                        except (discord.Forbidden, discord.HTTPException):
                            warn = await message.channel.send(
                                f"⚠️ {author.mention}, please slow down! You are sending messages too quickly.",
                            )
                    else:
                        warn = await message.channel.send(
                            f"⚠️ {author.mention}, please slow down! You are sending messages too quickly.",
                        )

                    await asyncio.sleep(5)
                    try:
                        await warn.delete()
                    except (discord.Forbidden, discord.NotFound, discord.HTTPException):
                        pass
                    return


async def setup(bot: commands.Bot):
    await bot.add_cog(AutoMod(bot))
