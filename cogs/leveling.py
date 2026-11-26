import random
from typing import List, Optional

import discord
from discord import app_commands
from discord.ext import commands, tasks

from database import (
    add_user_xp,
    get_user_level_data,
    get_top_leaderboard,
    add_level_role,
    get_level_roles,
    remove_level_role,
)


def render_progress_bar(current: int, total: int, length: int = 10) -> str:
    """Generate a clean ASCII progress bar with percentage."""
    if total <= 0:
        total = 1
    pct = min(max(current / total, 0.0), 1.0)
    filled = int(round(length * pct))
    bar = "▓" * filled + "░" * (length - filled)
    return f"[{bar}] {int(pct * 100)}%"


class Leveling(commands.Cog):
    """Gamification, user activity tracking, rank cards, and server leaderboards."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def cog_unload(self):
        if self.voice_xp_loop.is_running():
            self.voice_xp_loop.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.voice_xp_loop.is_running():
            self.voice_xp_loop.start()

    async def _grant_level_rewards_and_announce(
        self,
        guild: discord.Guild,
        member: discord.Member,
        new_level: int,
        channel: Optional[discord.abc.Messageable] = None,
    ):
        """Unlock level milestone roles and send a Level Up embed if a channel is writable."""
        unlocked_roles_text = ""
        rewards = await get_level_roles(guild.id)
        for r in rewards:
            if r["level"] == new_level:
                role = guild.get_role(r["role_id"])
                if role and isinstance(member, discord.Member):
                    try:
                        await member.add_roles(role, reason=f"Level {new_level} milestone reached")
                        unlocked_roles_text += f"\n🎁 **Role Reward Unlocked:** {role.mention}!"
                    except discord.Forbidden:
                        pass

        target_ch = channel or guild.system_channel
        if not target_ch:
            return

        embed = discord.Embed(
            title="🎉 Level Up!",
            description=f"Congratulations {member.mention}! You advanced to **Level {new_level}**! 🚀{unlocked_roles_text}",
            color=discord.Color.gold(),
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        try:
            await target_ch.send(embed=embed)
        except (discord.Forbidden, discord.HTTPException):
            pass

    async def _award_voice_xp_tick(self):
        """Award 10-20 XP per minute to active non-AFK humans in populated voice channels."""
        for guild in self.bot.guilds:
            afk_id = guild.afk_channel.id if guild.afk_channel else None
            for vc in guild.voice_channels:
                if afk_id and vc.id == afk_id:
                    continue

                eligible: List[discord.Member] = []
                for m in vc.members:
                    if m.bot or not m.voice:
                        continue
                    if m.voice.deaf or m.voice.self_deaf or m.voice.afk:
                        continue
                    eligible.append(m)

                # Anti-AFK farming guard: require at least 2 active non-deafened humans
                if len(eligible) < 2:
                    continue

                for member in eligible:
                    xp_gain = random.randint(10, 20)
                    leveled_up, new_level, _ = await add_user_xp(
                        guild_id=guild.id,
                        user_id=member.id,
                        amount=xp_gain,
                        cooldown_seconds=55.0,
                    )
                    if leveled_up:
                        await self._grant_level_rewards_and_announce(guild, member, new_level, channel=vc)

    @tasks.loop(seconds=60.0)
    async def voice_xp_loop(self):
        """Periodically award XP to members actively conversing in voice channels."""
        await self._award_voice_xp_tick()

    @voice_xp_loop.before_loop
    async def before_voice_xp_loop(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Grant random XP for chatting (with 60-second cooldown)."""
        if message.author.bot or not message.guild:
            return

        xp_gain = random.randint(15, 25)
        leveled_up, new_level, _ = await add_user_xp(
            guild_id=message.guild.id,
            user_id=message.author.id,
            amount=xp_gain,
            cooldown_seconds=60.0,
        )

        if leveled_up and isinstance(message.author, discord.Member):
            await self._grant_level_rewards_and_announce(
                message.guild,
                message.author,
                new_level,
                channel=message.channel,
            )

    @app_commands.command(name="rank", description="Check your current level, XP, and server rank")
    @app_commands.describe(member="Member whose rank you want to inspect (defaults to you)")
    async def rank(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        """Display a member's level card."""
        target = member or interaction.user
        guild = interaction.guild

        if not guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        rank_pos, level, current_xp, xp_needed = await get_user_level_data(guild.id, target.id)
        progress_bar = render_progress_bar(current_xp, xp_needed)

        embed = discord.Embed(
            title=f"📊 Rank Card — {target.display_name}",
            color=target.color if target.color != discord.Color.default() else discord.Color.blue(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_thumbnail(url=target.display_avatar.url)

        embed.add_field(name="🏆 Server Rank", value=f"#{rank_pos}", inline=True)
        embed.add_field(name="⭐ Level", value=f"Level {level}", inline=True)
        embed.add_field(name="✨ XP Progress", value=f"{current_xp} / {xp_needed} XP", inline=True)
        embed.add_field(name="📈 Progress to Next Level", value=f"`{progress_bar}`", inline=False)

        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard", description="View the top 10 most active members by Level and XP")
    async def leaderboard(self, interaction: discord.Interaction):
        """Display the server XP leaderboard."""
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        top_users = await get_top_leaderboard(guild.id, limit=10)
        if not top_users:
            await interaction.response.send_message(
                "📜 No activity recorded yet! Start chatting to earn XP and claim the top spot.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title=f"🏆 {guild.name} — XP Leaderboard",
            color=discord.Color.gold(),
            timestamp=discord.utils.utcnow(),
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        medals = ["🥇", "🥈", "🥉"]
        lines = []

        for idx, row in enumerate(top_users, start=1):
            user_id = row["user_id"]
            user = guild.get_member(user_id)
            user_display = user.mention if user else f"User ID `{user_id}`"
            badge = medals[idx - 1] if idx <= 3 else f"`#{idx}`"
            lines.append(
                f"{badge} **{user_display}** — **Level {row['level']}** ({row['xp']} XP)"
            )

        embed.description = "\n\n".join(lines)
        embed.set_footer(text="Earn XP by chatting in the server!")
        await interaction.response.send_message(embed=embed)

    # -----------------------------------------------------------------------
    # Level Milestone Roles
    # -----------------------------------------------------------------------

    levelrole_group = app_commands.Group(
        name="levelrole",
        description="Configure automatic role rewards for reaching level milestones",
        default_permissions=discord.Permissions(manage_roles=True),
    )

    @levelrole_group.command(name="add", description="Set a role reward for reaching a specific level")
    @app_commands.describe(
        level="The level required to unlock this role (e.g. 5, 10, 20)",
        role="The role to grant to members who reach this level",
    )
    async def levelrole_add(
        self,
        interaction: discord.Interaction,
        level: app_commands.Range[int, 1, 100],
        role: discord.Role,
    ):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        bot_member = interaction.guild.get_member(self.bot.user.id) if self.bot.user else None
        if bot_member and role >= bot_member.top_role:
            await interaction.response.send_message(
                f"❌ I cannot assign {role.mention} because it is equal to or higher than my highest role.",
                ephemeral=True,
            )
            return

        await add_level_role(interaction.guild.id, level, role.id)
        embed = discord.Embed(
            title="🎁 Level Reward Configured",
            description=f"Members will automatically receive {role.mention} when they reach **Level {level}**!",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed)

    @levelrole_group.command(name="list", description="List all configured level role rewards")
    async def levelrole_list(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        rewards = await get_level_roles(interaction.guild.id)
        if not rewards:
            await interaction.response.send_message("ℹ️ No level roles configured yet. Use `/levelrole add`.", ephemeral=True)
            return

        lines = []
        for r in rewards:
            role = interaction.guild.get_role(r["role_id"])
            role_text = role.mention if role else f"Unknown Role (`{r['role_id']}`)"
            lines.append(f"• **Level {r['level']}** ➔ {role_text}")

        embed = discord.Embed(
            title=f"🎁 Level Role Rewards ({len(rewards)})",
            description="\n".join(lines),
            color=0xFEE75C,
        )
        await interaction.response.send_message(embed=embed)

    @levelrole_group.command(name="remove", description="Remove a role reward for a level milestone")
    @app_commands.describe(level="The level whose reward you want to remove")
    async def levelrole_remove(self, interaction: discord.Interaction, level: int):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        removed = await remove_level_role(interaction.guild.id, level)
        if removed:
            await interaction.response.send_message(f"✅ Removed role reward for **Level {level}**.", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ No role reward was found for **Level {level}**.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Leveling(bot))
