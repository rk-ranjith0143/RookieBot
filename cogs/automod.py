import re
import time
import datetime
import asyncio
from collections import defaultdict

import discord
from discord import app_commands
from discord.ext import commands

from database import get_guild_settings, update_guild_setting

INVITE_REGEX = re.compile(
    r"(?:https?://)?(?:www\.)?(?:discord\.(?:gg|io|me|li)|discord(?:app)?\.com/invite)/[a-zA-Z0-9]+",
    re.IGNORECASE,
)

SPAM_TRACKER = defaultdict(list)
MAX_MENTIONS = 5


def is_automod_exempt(member: discord.Member) -> bool:
    """Check if a member is exempt from automated moderation rules."""
    if member.bot:
        return True
    if member.id == member.guild.owner_id:
        return True
    perms = member.guild_permissions
    return perms.administrator or perms.manage_guild or perms.manage_messages


class AutoMod(commands.Cog):
    """Automated content filtering and server protection."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    automod_group = app_commands.Group(
        name="automod",
        description="View and configure automated moderation settings and filters",
    )

    @automod_group.command(name="status", description="View current auto-moderation filters and rules")
    async def automod_status(self, interaction: discord.Interaction):
        """Displays auto-moderation status and active protections."""
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        settings = await get_guild_settings(interaction.guild_id)

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
            name="🛡️ Exemptions",
            value="Server Owner, Administrators, and Members with `Manage Messages` / `Manage Server`.",
            inline=False,
        )
        embed.set_footer(text="Use /automod toggle to configure individual protections.")
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

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Monitor messages for invite links, mass mentions, and spam flooding."""
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

            # 2. Anti-Mass Mentions
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

            # 3. Anti-Spam / Flood Detection
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
