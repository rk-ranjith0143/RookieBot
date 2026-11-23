import time
import asyncio
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from database import set_user_afk, get_user_afk, remove_user_afk


def format_duration(seconds: float) -> str:
    """Format duration into human-readable string."""
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds} second(s)"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} minute(s)"
    hours = minutes // 60
    rem_mins = minutes % 60
    return f"{hours} hour(s) {rem_mins} minute(s)"


class AFK(commands.Cog):
    """AFK status management with mention auto-replies and return notifications."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._mention_cooldowns = {}  # (channel_id, target_user_id): last_notified_timestamp

    @app_commands.command(name="afk", description="Set an AFK status that notifies members when they mention you")
    @app_commands.describe(reason="Reason for being away (e.g., studying, sleeping, eating)")
    async def afk(self, interaction: discord.Interaction, reason: Optional[str] = "AFK"):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        clean_reason = reason.strip()[:150]
        await set_user_afk(guild.id, interaction.user.id, clean_reason)

        await interaction.response.send_message(
            f"💤 {interaction.user.mention}, I set your AFK: **{clean_reason}**.",
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Handle returning AFK members and notify users who ping AFK members."""
        if message.author.bot or not message.guild:
            return

        now = time.time()
        guild_id = message.guild.id
        author = message.author

        # 1. Did the author return from AFK?
        afk_info = await remove_user_afk(guild_id, author.id)
        if afk_info:
            time_away = format_duration(now - afk_info["afk_since"])
            welcome_msg = await message.channel.send(
                f"👋 Welcome back {author.mention}! I removed your AFK (You were away for {time_away})."
            )
            # Self-delete notice after 6 seconds to keep chat clean
            await asyncio.sleep(6)
            try:
                await welcome_msg.delete()
            except (discord.NotFound, discord.HTTPException):
                pass

        # 2. Did the message mention any currently AFK members?
        if message.mentions:
            for member in message.mentions:
                if member.id == author.id or member.bot:
                    continue

                target_afk = await get_user_afk(guild_id, member.id)
                if target_afk:
                    # Cooldown check: don't spam multiple notices in the same channel within 10s
                    cooldown_key = (message.channel.id, member.id)
                    last_alert = self._mention_cooldowns.get(cooldown_key, 0)
                    if now - last_alert > 10.0:
                        self._mention_cooldowns[cooldown_key] = now
                        since_ts = int(target_afk["afk_since"])
                        await message.reply(
                            f"💤 **{member.display_name}** is currently AFK: **{target_afk['reason']}** (<t:{since_ts}:R>).",
                            mention_author=False,
                        )


async def setup(bot: commands.Bot):
    await bot.add_cog(AFK(bot))
