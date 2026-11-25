from typing import Optional, Union

import discord
from discord import app_commands
from discord.ext import commands

from database import get_guild_settings, update_guild_setting


class Logging(commands.Cog):
    """Audit logging and moderation event tracking."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _get_log_channel(self, guild: discord.Guild) -> Optional[discord.TextChannel]:
        """Fetch the designated mod-log channel for this guild if configured."""
        settings = await get_guild_settings(guild.id)
        channel_id = settings.get("mod_log_channel_id")
        if not channel_id:
            return None
        channel = guild.get_channel(channel_id)
        if isinstance(channel, discord.TextChannel) and channel.permissions_for(guild.me).send_messages:
            return channel
        return None

    async def _send_log(self, guild: discord.Guild, embed: discord.Embed):
        """Send an audit embed if a writable log channel is configured."""
        log_channel = await self._get_log_channel(guild)
        if not log_channel:
            return
        try:
            await log_channel.send(embed=embed)
        except discord.HTTPException:
            pass

    @app_commands.command(name="setlogs", description="Set the channel where moderation and audit events will be logged")
    @app_commands.describe(channel="The text channel for logs (leave empty to disable)")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setlogs(
        self,
        interaction: discord.Interaction,
        channel: Optional[discord.TextChannel] = None,
    ):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        channel_id = channel.id if channel else None
        await update_guild_setting(guild.id, "mod_log_channel_id", channel_id)

        if channel:
            embed = discord.Embed(
                title="📋 Mod-Logs Configured",
                description=f"Server audit events will now be logged to {channel.mention}.",
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow(),
            )
            embed.set_footer(text=f"Configured by {interaction.user.display_name}")
            await channel.send(embed=embed)
            await interaction.response.send_message(
                f"✅ Mod-logs channel set to {channel.mention}!",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                "🛑 Mod-logs have been **disabled** for this server.",
                ephemeral=True,
            )

    # -----------------------------------------------------------------------
    # Message Audit Listeners
    # -----------------------------------------------------------------------

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        """Log deleted messages."""
        if message.author.bot or not message.guild:
            return

        embed = discord.Embed(
            title="🗑️ Message Deleted",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_author(
            name=f"{message.author} ({message.author.id})",
            icon_url=message.author.display_avatar.url,
        )
        embed.add_field(name="Channel", value=message.channel.mention, inline=True)

        content = message.content or "*[No text content]*"
        if len(content) > 1024:
            content = content[:1021] + "..."
        embed.add_field(name="Content", value=content, inline=False)

        if message.attachments:
            att_names = ", ".join(f"`{a.filename}`" for a in message.attachments)
            embed.add_field(name="Attachments", value=att_names, inline=False)

        embed.set_footer(text=f"Message ID: {message.id}")
        await self._send_log(message.guild, embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        """Log edited messages."""
        if before.author.bot or not before.guild:
            return
        if before.content == after.content:
            return

        embed = discord.Embed(
            title="✏️ Message Edited",
            color=discord.Color.orange(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_author(
            name=f"{before.author} ({before.author.id})",
            icon_url=before.author.display_avatar.url,
        )
        embed.add_field(name="Channel", value=before.channel.mention, inline=True)
        embed.add_field(name="Jump Link", value=f"[Go to Message]({after.jump_url})", inline=True)

        b_content = before.content or "*[Empty]*"
        a_content = after.content or "*[Empty]*"
        if len(b_content) > 1024:
            b_content = b_content[:1021] + "..."
        if len(a_content) > 1024:
            a_content = a_content[:1021] + "..."

        embed.add_field(name="Before", value=b_content, inline=False)
        embed.add_field(name="After", value=a_content, inline=False)
        embed.set_footer(text=f"Message ID: {before.id}")

        await self._send_log(before.guild, embed)

    # -----------------------------------------------------------------------
    # Member & Moderation Audit Listeners
    # -----------------------------------------------------------------------

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Log new member joins."""
        if not member.guild:
            return

        embed = discord.Embed(
            title="📥 Member Joined",
            description=f"{member.mention} (`{member}` - ID: `{member.id}`) joined the server.",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Account Created", value=f"<t:{int(member.created_at.timestamp())}:R>", inline=True)
        embed.add_field(name="Bot Account?", value="🤖 Yes" if member.bot else "👤 No", inline=True)
        embed.set_footer(text=f"Total Members: {member.guild.member_count}")

        await self._send_log(member.guild, embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Log member departures or kicks."""
        embed = discord.Embed(
            title="👋 Member Left",
            description=f"{member.mention} (`{member}` - ID: `{member.id}`) left the server.",
            color=discord.Color.dark_grey(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Total Members: {member.guild.member_count}")

        await self._send_log(member.guild, embed)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """Log member nickname changes and role additions/removals."""
        if not after.guild or after.bot:
            return

        if before.nick != after.nick:
            nick_embed = discord.Embed(
                title="🏷️ Nickname Changed",
                color=discord.Color.blue(),
                timestamp=discord.utils.utcnow(),
            )
            nick_embed.set_author(name=f"{after} ({after.id})", icon_url=after.display_avatar.url)
            nick_embed.add_field(name="Member", value=after.mention, inline=False)
            nick_embed.add_field(name="Before", value=before.nick or before.name, inline=True)
            nick_embed.add_field(name="After", value=after.nick or after.name, inline=True)
            await self._send_log(after.guild, nick_embed)

        added_roles = [r for r in after.roles if r not in before.roles]
        removed_roles = [r for r in before.roles if r not in after.roles]
        if added_roles or removed_roles:
            role_embed = discord.Embed(
                title="🎭 Member Roles Updated",
                color=discord.Color.green() if added_roles else discord.Color.orange(),
                timestamp=discord.utils.utcnow(),
            )
            role_embed.set_author(name=f"{after} ({after.id})", icon_url=after.display_avatar.url)
            role_embed.add_field(name="Member", value=after.mention, inline=False)
            if added_roles:
                role_embed.add_field(
                    name="➕ Added",
                    value=", ".join(r.mention for r in added_roles),
                    inline=False,
                )
            if removed_roles:
                role_embed.add_field(
                    name="➖ Removed",
                    value=", ".join(r.mention for r in removed_roles),
                    inline=False,
                )
            await self._send_log(after.guild, role_embed)

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        """Log voice channel joins, leaves, and switches."""
        if member.bot or not member.guild or before.channel == after.channel:
            return

        if before.channel is None and after.channel is not None:
            embed = discord.Embed(
                title="🔊 Joined Voice Channel",
                description=f"{member.mention} joined **{after.channel.name}** ({after.channel.mention}).",
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow(),
            )
        elif before.channel is not None and after.channel is None:
            embed = discord.Embed(
                title="🔇 Left Voice Channel",
                description=f"{member.mention} left **{before.channel.name}** ({before.channel.mention}).",
                color=discord.Color.dark_grey(),
                timestamp=discord.utils.utcnow(),
            )
        else:
            embed = discord.Embed(
                title="🔀 Switched Voice Channel",
                description=(
                    f"{member.mention} moved from **{before.channel.name}** "
                    f"to **{after.channel.name}**."
                ),
                color=discord.Color.blurple(),
                timestamp=discord.utils.utcnow(),
            )

        embed.set_author(name=f"{member} ({member.id})", icon_url=member.display_avatar.url)
        await self._send_log(member.guild, embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: Union[discord.User, discord.Member]):
        """Log member bans."""
        embed = discord.Embed(
            title="🔨 Member Banned",
            description=f"{user.mention} (`{user}` - ID: `{user.id}`) was banned from the server.",
            color=discord.Color.dark_red(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_thumbnail(url=user.display_avatar.url)

        await self._send_log(guild, embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        """Log member unbans."""
        embed = discord.Embed(
            title="🕊️ Member Unbanned",
            description=f"{user.mention} (`{user}` - ID: `{user.id}`) had their ban revoked.",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_thumbnail(url=user.display_avatar.url)

        await self._send_log(guild, embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Logging(bot))
