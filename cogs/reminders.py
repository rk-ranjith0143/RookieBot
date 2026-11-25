import re
import time as time_mod

import discord
from discord import app_commands
from discord.ext import commands, tasks

from database import add_reminder, get_due_reminders, delete_reminder


def parse_time_string(time_str: str) -> int:
    """Parse strings like '10m', '2h', '1d', '30s' into total seconds."""
    time_str = time_str.lower().strip()
    match = re.fullmatch(r"(\d+)\s*([smhd])", time_str)
    if not match:
        return 0
    val, unit = int(match.group(1)), match.group(2)
    multipliers = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    return val * multipliers[unit]


class Reminders(commands.Cog):
    """Personal reminders and scheduled timer alerts."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def cog_unload(self):
        if self.reminder_loop.is_running():
            self.reminder_loop.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.reminder_loop.is_running():
            self.reminder_loop.start()

    @tasks.loop(seconds=5.0)
    async def reminder_loop(self):
        """Poll the database for reminders that are due and send them."""
        now = time_mod.time()
        due_items = await get_due_reminders(now)

        for item in due_items:
            reminder_id = item["id"]
            user_id = item["user_id"]
            channel_id = item["channel_id"]
            reminder_msg = item["message"]

            try:
                channel = self.bot.get_channel(channel_id)
                if not channel:
                    channel = await self.bot.fetch_channel(channel_id)

                if channel:
                    embed = discord.Embed(
                        title="⏰ Reminder Alert!",
                        description=f"<@{user_id}>, here is the reminder you scheduled:\n\n**{reminder_msg}**",
                        color=discord.Color.gold(),
                        timestamp=discord.utils.utcnow(),
                    )
                    await channel.send(content=f"<@{user_id}>", embed=embed)
            except Exception as e:
                print(f"Failed to deliver reminder #{reminder_id}: {e}")
            finally:
                await delete_reminder(reminder_id)

    @reminder_loop.before_loop
    async def before_reminder_loop(self):
        await self.bot.wait_until_ready()

    @app_commands.command(name="remindme", description="Set a timer that pings you with a reminder message")
    @app_commands.describe(
        time="How long to wait (e.g., 30s, 10m, 2h, 1d)",
        message="What should I remind you about?",
    )
    async def remindme(self, interaction: discord.Interaction, time: str, message: str):
        duration_sec = parse_time_string(time)
        if duration_sec <= 0:
            await interaction.response.send_message(
                "❌ Invalid time format! Please use a number followed by `s`, `m`, `h`, or `d` (e.g., `10m`, `2h`, `1d`).",
                ephemeral=True,
            )
            return

        # Maximum reminder is 30 days
        if duration_sec > 86400 * 30:
            await interaction.response.send_message(
                "❌ Reminders cannot be set for more than 30 days into the future.",
                ephemeral=True,
            )
            return

        remind_at = time_mod.time() + duration_sec

        channel_id = getattr(interaction, "channel_id", None) or (interaction.channel.id if interaction.channel else None)
        if hasattr(channel_id, "__class__") and not isinstance(channel_id, int):
            try:
                channel_id = int(channel_id)
            except Exception:
                channel_id = interaction.channel.id if interaction.channel and isinstance(interaction.channel.id, int) else 0

        await add_reminder(
            user_id=interaction.user.id,
            channel_id=channel_id,
            message=message.strip()[:500],
            remind_at=remind_at,
        )

        embed = discord.Embed(
            title="⏰ Reminder Scheduled",
            description=f"I will remind you <t:{int(remind_at)}:R> (<t:{int(remind_at)}:f>):\n\n**{message}**",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Reminders(bot))
