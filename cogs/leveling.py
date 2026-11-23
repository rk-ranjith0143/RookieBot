import random
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from database import add_user_xp, get_user_level_data, get_top_leaderboard


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

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Grant random XP for chatting (with 60-second cooldown)."""
        if message.author.bot or not message.guild:
            return

        # Give random 15-25 XP
        xp_gain = random.randint(15, 25)
        leveled_up, new_level, _ = await add_user_xp(
            guild_id=message.guild.id,
            user_id=message.author.id,
            amount=xp_gain,
            cooldown_seconds=60.0,
        )

        if leveled_up:
            embed = discord.Embed(
                title="🎉 Level Up!",
                description=f"Congratulations {message.author.mention}! You advanced to **Level {new_level}**! 🚀",
                color=discord.Color.gold(),
            )
            embed.set_thumbnail(url=message.author.display_avatar.url)
            try:
                await message.channel.send(embed=embed)
            except discord.HTTPException:
                pass

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


async def setup(bot: commands.Bot):
    await bot.add_cog(Leveling(bot))
