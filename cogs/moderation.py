import datetime
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands


class Moderation(commands.Cog):
    """Server moderation and administrative enforcement commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="kick", description="Kick a member from the server")
    @app_commands.describe(
        member="The member to kick",
        reason="Reason for kicking the member",
    )
    @app_commands.checks.has_permissions(kick_members=True)
    @app_commands.checks.bot_has_permissions(kick_members=True)
    async def kick(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: Optional[str] = "No reason provided",
    ):
        guild = interaction.guild

        if member.id == interaction.user.id:
            await interaction.response.send_message("❌ You cannot kick yourself!", ephemeral=True)
            return
        if member.id == self.bot.user.id:
            await interaction.response.send_message("❌ I cannot kick myself!", ephemeral=True)
            return
        if member.id == guild.owner_id:
            await interaction.response.send_message("❌ You cannot kick the server owner!", ephemeral=True)
            return
        if interaction.user.id != guild.owner_id and interaction.user.top_role <= member.top_role:
            await interaction.response.send_message(
                "❌ You cannot kick someone with a role equal to or higher than yours!",
                ephemeral=True,
            )
            return
        if guild.me.top_role <= member.top_role:
            await interaction.response.send_message(
                "❌ I cannot kick someone with a role equal to or higher than my highest role!",
                ephemeral=True,
            )
            return

        try:
            await member.send(f"⚠️ You were kicked from **{guild.name}**.\n**Reason:** {reason}")
        except (discord.Forbidden, discord.HTTPException):
            pass

        audit_reason = f"Kicked by {interaction.user} (ID: {interaction.user.id}): {reason}"
        await member.kick(reason=audit_reason)

        embed = discord.Embed(
            title="👢 Member Kicked",
            color=discord.Color.orange(),
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(name="Member", value=f"{member.mention} (`{member}`)", inline=False)
        embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ban", description="Ban a user from the server with optional message deletion")
    @app_commands.describe(
        user="The user or member to ban",
        delete_message_days="Days of message history to delete (0 to 7 days)",
        reason="Reason for banning the user",
    )
    @app_commands.choices(
        delete_message_days=[
            app_commands.Choice(name="Don't delete any messages", value=0),
            app_commands.Choice(name="Previous 24 Hours (1 day)", value=1),
            app_commands.Choice(name="Previous 7 Days", value=7),
        ]
    )
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.checks.bot_has_permissions(ban_members=True)
    async def ban(
        self,
        interaction: discord.Interaction,
        user: discord.User,
        delete_message_days: Optional[app_commands.Choice[int]] = None,
        reason: Optional[str] = "No reason provided",
    ):
        guild = interaction.guild
        delete_days = delete_message_days.value if delete_message_days else 0

        if user.id == interaction.user.id:
            await interaction.response.send_message("❌ You cannot ban yourself!", ephemeral=True)
            return
        if user.id == self.bot.user.id:
            await interaction.response.send_message("❌ I cannot ban myself!", ephemeral=True)
            return
        if user.id == guild.owner_id:
            await interaction.response.send_message("❌ You cannot ban the server owner!", ephemeral=True)
            return

        member = guild.get_member(user.id)
        if member:
            if interaction.user.id != guild.owner_id and interaction.user.top_role <= member.top_role:
                await interaction.response.send_message(
                    "❌ You cannot ban someone with a role equal to or higher than yours!",
                    ephemeral=True,
                )
                return
            if guild.me.top_role <= member.top_role:
                await interaction.response.send_message(
                    "❌ I cannot ban someone with a role equal to or higher than my highest role!",
                    ephemeral=True,
                )
                return

            try:
                await member.send(f"🔨 You were banned from **{guild.name}**.\n**Reason:** {reason}")
            except (discord.Forbidden, discord.HTTPException):
                pass

        audit_reason = f"Banned by {interaction.user} (ID: {interaction.user.id}): {reason}"
        await guild.ban(user, reason=audit_reason, delete_message_days=delete_days)

        embed = discord.Embed(
            title="🔨 Member Banned",
            color=discord.Color.dark_red(),
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(name="User", value=f"{user.mention} (`{user}` - `{user.id}`)", inline=False)
        embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
        embed.add_field(name="Deleted Messages", value=f"{delete_days} day(s)", inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_thumbnail(url=user.display_avatar.url)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="unban", description="Unban a user from the server using their User ID")
    @app_commands.describe(
        user_id="The 17-20 digit Discord User ID to unban",
        reason="Reason for unbanning",
    )
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.checks.bot_has_permissions(ban_members=True)
    async def unban(
        self,
        interaction: discord.Interaction,
        user_id: str,
        reason: Optional[str] = "Unbanned by moderator",
    ):
        guild = interaction.guild

        try:
            uid = int(user_id.strip())
        except ValueError:
            await interaction.response.send_message(
                "❌ Invalid User ID. Please provide a numeric Discord User ID (e.g., `123456789012345678`).",
                ephemeral=True,
            )
            return

        try:
            ban_entry = await guild.fetch_ban(discord.Object(id=uid))
        except discord.NotFound:
            await interaction.response.send_message(
                f"❌ No ban found for User ID `{uid}` in this server.",
                ephemeral=True,
            )
            return
        except discord.HTTPException as e:
            await interaction.response.send_message(
                f"❌ Failed to fetch ban information: `{e}`",
                ephemeral=True,
            )
            return

        banned_user = ban_entry.user
        audit_reason = f"Unbanned by {interaction.user} (ID: {interaction.user.id}): {reason}"
        await guild.unban(banned_user, reason=audit_reason)

        embed = discord.Embed(
            title="🕊️ User Unbanned",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(name="User", value=f"{banned_user.mention} (`{banned_user}` - `{banned_user.id}`)", inline=False)
        embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_thumbnail(url=banned_user.display_avatar.url)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="timeout", description="Timeout (mute) a member for a specified duration")
    @app_commands.describe(
        member="The member to timeout",
        duration="Duration in minutes (1 - 40320 minutes / up to 28 days)",
        reason="Reason for the timeout",
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.checks.bot_has_permissions(moderate_members=True)
    async def timeout(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        duration: int,
        reason: Optional[str] = "No reason provided",
    ):
        guild = interaction.guild

        if duration < 1 or duration > 40320:
            await interaction.response.send_message(
                "❌ Duration must be between 1 minute and 40,320 minutes (28 days).",
                ephemeral=True,
            )
            return

        if member.id == interaction.user.id:
            await interaction.response.send_message("❌ You cannot timeout yourself!", ephemeral=True)
            return
        if member.id == self.bot.user.id:
            await interaction.response.send_message("❌ I cannot timeout myself!", ephemeral=True)
            return
        if member.id == guild.owner_id:
            await interaction.response.send_message("❌ You cannot timeout the server owner!", ephemeral=True)
            return
        if interaction.user.id != guild.owner_id and interaction.user.top_role <= member.top_role:
            await interaction.response.send_message(
                "❌ You cannot timeout someone with a role equal to or higher than yours!",
                ephemeral=True,
            )
            return
        if guild.me.top_role <= member.top_role:
            await interaction.response.send_message(
                "❌ I cannot timeout someone with a role equal to or higher than my highest role!",
                ephemeral=True,
            )
            return

        delta = datetime.timedelta(minutes=duration)
        audit_reason = f"Timed out by {interaction.user} (ID: {interaction.user.id}) for {duration}m: {reason}"
        await member.timeout(delta, reason=audit_reason)

        if duration >= 1440:
            duration_str = f"{duration // 1440} day(s) {((duration % 1440) // 60)} hour(s)"
        elif duration >= 60:
            duration_str = f"{duration // 60} hour(s) {duration % 60} minute(s)"
        else:
            duration_str = f"{duration} minute(s)"

        try:
            await member.send(
                f"⏳ You have been timed out in **{guild.name}** for **{duration_str}**.\n**Reason:** {reason}"
            )
        except (discord.Forbidden, discord.HTTPException):
            pass

        embed = discord.Embed(
            title="⏳ Member Timed Out",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(name="Member", value=f"{member.mention} (`{member}`)", inline=False)
        embed.add_field(name="Duration", value=duration_str, inline=True)
        embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="untimeout", description="Remove timeout from a member")
    @app_commands.describe(
        member="The member to remove timeout from",
        reason="Reason for removing timeout",
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.checks.bot_has_permissions(moderate_members=True)
    async def untimeout(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: Optional[str] = "Timeout removed by moderator",
    ):
        guild = interaction.guild

        if not member.is_timed_out():
            await interaction.response.send_message(
                f"❌ {member.mention} is not currently timed out.",
                ephemeral=True,
            )
            return

        if interaction.user.id != guild.owner_id and interaction.user.top_role <= member.top_role:
            await interaction.response.send_message(
                "❌ You cannot modify timeout for someone with a role equal to or higher than yours!",
                ephemeral=True,
            )
            return
        if guild.me.top_role <= member.top_role:
            await interaction.response.send_message(
                "❌ I cannot modify timeout for someone with a role equal to or higher than my highest role!",
                ephemeral=True,
            )
            return

        audit_reason = f"Untimed out by {interaction.user} (ID: {interaction.user.id}): {reason}"
        await member.timeout(None, reason=audit_reason)

        embed = discord.Embed(
            title="🔊 Timeout Removed",
            description=f"Timeout removed for {member.mention} (`{member}`).",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_thumbnail(url=member.display_avatar.url)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="clear", description="Bulk delete messages from this channel (purge)")
    @app_commands.describe(
        amount="Number of messages to delete (1 - 100)",
        member="Optionally delete messages from only this member",
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.bot_has_permissions(manage_messages=True)
    async def clear(
        self,
        interaction: discord.Interaction,
        amount: int,
        member: Optional[discord.Member] = None,
    ):
        if amount < 1 or amount > 100:
            await interaction.response.send_message(
                "❌ Please specify an amount between 1 and 100.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        check = (lambda m: m.author.id == member.id) if member else None

        try:
            deleted = await interaction.channel.purge(limit=amount, check=check)
            filter_text = f" from {member.mention}" if member else ""
            await interaction.followup.send(
                f"🧹 Successfully cleared **{len(deleted)}** message(s){filter_text}!",
                ephemeral=True,
            )
        except discord.HTTPException as e:
            await interaction.followup.send(
                f"❌ Failed to delete messages: `{e}` (Discord does not permit bulk deleting messages older than 14 days).",
                ephemeral=True,
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
