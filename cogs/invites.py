from typing import Dict, Optional

import discord
from discord import app_commands
from discord.ext import commands

import database


class Invites(commands.Cog):
    """Invite & referral tracker counting regular, left, and bonus invites per member."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._invite_cache: Dict[int, Dict[str, int]] = {}

    async def _cache_guild_invites(self, guild: discord.Guild):
        """Snapshot current invite link use counts for a guild."""
        if not guild.me or not guild.me.guild_permissions.manage_guild:
            return
        try:
            invites = await guild.invites()
            self._invite_cache[guild.id] = {inv.code: (inv.uses or 0) for inv in invites}
        except (discord.Forbidden, discord.HTTPException):
            pass

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            await self._cache_guild_invites(guild)

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite):
        if invite.guild:
            self._invite_cache.setdefault(invite.guild.id, {})[invite.code] = invite.uses or 0

    @commands.Cog.listener()
    async def on_invite_delete(self, invite: discord.Invite):
        if invite.guild and invite.guild.id in self._invite_cache:
            self._invite_cache[invite.guild.id].pop(invite.code, None)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Detect which invite link was used when a new member joins."""
        if member.bot or not member.guild:
            return

        guild = member.guild
        if not guild.me or not guild.me.guild_permissions.manage_guild:
            return

        cached = self._invite_cache.get(guild.id, {})
        try:
            current_invites = await guild.invites()
        except (discord.Forbidden, discord.HTTPException):
            return

        used_invite: Optional[discord.Invite] = None
        new_cache: Dict[str, int] = {}
        for inv in current_invites:
            uses = inv.uses or 0
            new_cache[inv.code] = uses
            if uses > cached.get(inv.code, 0):
                used_invite = inv

        self._invite_cache[guild.id] = new_cache

        if used_invite and used_invite.inviter and used_invite.inviter.id != member.id:
            await database.record_member_invite(
                guild_id=guild.id,
                member_id=member.id,
                inviter_id=used_invite.inviter.id,
                invite_code=used_invite.code,
            )

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Increment leave count on the original inviter if an invited member leaves."""
        if member.bot or not member.guild:
            return
        await database.record_invited_member_leave(member.guild.id, member.id)

    @app_commands.command(name="invites", description="Check how many members you or another user has invited")
    @app_commands.describe(member="Member whose invite count you want to inspect (defaults to you)")
    async def invites(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        target = member or interaction.user
        stats = await database.get_user_invite_stats(interaction.guild.id, target.id)

        embed = discord.Embed(
            title=f"📨 Invite Stats — {target.display_name}",
            description=f"{target.mention} currently has **{stats['total']}** active invite(s)!",
            color=0x5865F2,
            timestamp=discord.utils.utcnow(),
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="👥 Regular", value=f"**{stats['regular']}**", inline=True)
        embed.add_field(name="🚪 Left", value=f"**{stats['leaves']}**", inline=True)
        embed.add_field(name="🎁 Bonus", value=f"**{stats['bonus']}**", inline=True)
        embed.set_footer(text="Use /inviteleaderboard to see the top server inviters!")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="inviteleaderboard", description="View the Top 10 server inviters")
    async def inviteleaderboard(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        top = await database.get_invite_leaderboard(interaction.guild.id, limit=10)
        if not top:
            await interaction.response.send_message(
                "📨 No invites tracked yet! Invite friends to claim the #1 spot.",
                ephemeral=True,
            )
            return

        medals = ["🥇", "🥈", "🥉"]
        lines = []
        for idx, row in enumerate(top, start=1):
            uid = row["inviter_id"]
            member = interaction.guild.get_member(uid)
            display = member.mention if member else f"User ID `{uid}`"
            badge = medals[idx - 1] if idx <= 3 else f"`#{idx}`"
            lines.append(
                f"{badge} **{display}** — **{row['total']} Invites** "
                f"(`{row['regular_count']}` regular • `{row['leaves_count']}` left • `{row['bonus_count']}` bonus)"
            )

        embed = discord.Embed(
            title=f"🏆 {interaction.guild.name} — Invite Leaderboard",
            description="\n\n".join(lines),
            color=discord.Color.gold(),
            timestamp=discord.utils.utcnow(),
        )
        if interaction.guild.icon:
            embed.set_thumbnail(url=interaction.guild.icon.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="invitebonus", description="Add or subtract bonus invites for a member")
    @app_commands.describe(
        member="Member to adjust bonus invites for",
        amount="Number of bonus invites (positive to add, negative to subtract)",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def invitebonus(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        if amount == 0:
            await interaction.response.send_message("❌ Bonus amount cannot be 0.", ephemeral=True)
            return

        new_total = await database.adjust_bonus_invites(interaction.guild.id, member.id, amount)
        sign = "+" if amount > 0 else ""
        embed = discord.Embed(
            title="🎁 Bonus Invites Updated",
            description=f"Adjusted {member.mention}'s invites by **{sign}{amount}**.\nNew Total: **{new_total} Invite(s)**",
            color=discord.Color.green() if amount > 0 else discord.Color.orange(),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="invitereset", description="Reset all tracked invite counts for this server")
    @app_commands.checks.has_permissions(administrator=True)
    async def invitereset(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        await database.reset_guild_invites(interaction.guild.id)
        await interaction.response.send_message("🧹 All tracked invite statistics for this server have been reset.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Invites(bot))
