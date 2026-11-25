import asyncio
from typing import Dict

import discord
from discord import app_commands
from discord.ext import commands

import database
from database import (
    set_sticky_message,
    get_sticky_message,
    update_sticky_last_id,
    delete_sticky_message,
)


class Sticky(commands.Cog):
    """Sticky message manager that automatically keeps important notices at the bottom of active chats."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._locks: Dict[int, asyncio.Lock] = {}

    sticky_group = app_commands.Group(
        name="sticky",
        description="Configure sticky messages pinned to the bottom of the chat",
    )

    @sticky_group.command(name="set", description="Set or update a sticky message for this channel")
    @app_commands.describe(message="The message to keep pinned at the bottom of the channel")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def sticky_set(self, interaction: discord.Interaction, message: str):
        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message("❌ This command must be used in a text channel.", ephemeral=True)
            return

        guild = interaction.guild
        if guild:
            existing = await get_sticky_message(channel.id)
            if not existing:
                sticky_count = await database.get_guild_sticky_count(guild.id)
                if sticky_count >= 1:
                    is_premium = await database.is_guild_premium(guild.id)
                    if not is_premium:
                        await interaction.response.send_message(
                            "⚠️ **Free Tier Limit Reached (1 Sticky Message)!**\n"
                            "Free servers can only have 1 active sticky notice at a time.\n"
                            "Upgrade to **⭐ Premium** with `/premium` to enable sticky messages across unlimited channels!",
                            ephemeral=True,
                        )
                        return

        clean_text = message.strip()[:2000]
        await set_sticky_message(channel.id, clean_text, guild_id=guild.id if guild else None)

        embed = discord.Embed(
            title="📌 Pinned Notice",
            description=clean_text,
            color=discord.Color.gold(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_footer(text="Sticky Notice • Stays at the bottom of the channel")

        posted = await channel.send(embed=embed)
        await update_sticky_last_id(channel.id, posted.id)

        await interaction.response.send_message(
            "✅ Sticky message active! It will automatically re-pin to the bottom as members chat.",
            ephemeral=True,
        )

    @sticky_group.command(name="remove", description="Remove the sticky message from this channel")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def sticky_remove(self, interaction: discord.Interaction):
        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message("❌ This command must be used in a text channel.", ephemeral=True)
            return

        sticky_info = await get_sticky_message(channel.id)
        if not sticky_info:
            await interaction.response.send_message("❌ No active sticky message in this channel.", ephemeral=True)
            return

        last_id = sticky_info.get("last_message_id")
        if last_id:
            try:
                old_msg = await channel.fetch_message(last_id)
                await old_msg.delete()
            except (discord.NotFound, discord.HTTPException):
                pass

        await delete_sticky_message(channel.id)
        await interaction.response.send_message("🗑️ Sticky message removed from this channel.", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Re-send sticky message at the bottom of the channel when new messages arrive."""
        if message.author.id == self.bot.user.id or not message.guild:
            return

        channel_id = message.channel.id
        sticky_info = await get_sticky_message(channel_id)
        if not sticky_info:
            return

        if channel_id not in self._locks:
            self._locks[channel_id] = asyncio.Lock()

        async with self._locks[channel_id]:
            # Delete previous sticky message if present
            last_msg_id = sticky_info.get("last_message_id")
            if last_msg_id and last_msg_id != message.id:
                try:
                    prev_msg = await message.channel.fetch_message(last_msg_id)
                    await prev_msg.delete()
                except (discord.NotFound, discord.HTTPException):
                    pass

            embed = discord.Embed(
                title="📌 Pinned Notice",
                description=sticky_info["message_content"],
                color=discord.Color.gold(),
                timestamp=discord.utils.utcnow(),
            )
            embed.set_footer(text="Sticky Notice • Stays at the bottom of the channel")

            try:
                new_msg = await message.channel.send(embed=embed)
                await update_sticky_last_id(channel_id, new_msg.id)
            except discord.HTTPException:
                pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Sticky(bot))
