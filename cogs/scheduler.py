import time
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands, tasks

import database
from cogs.reminders import parse_time_string


def format_interval_human(seconds: int) -> str:
    """Convert an interval in seconds into a readable unit string."""
    if seconds % 86400 == 0:
        return f"{seconds // 86400}d"
    if seconds % 3600 == 0:
        return f"{seconds // 3600}h"
    if seconds % 60 == 0:
        return f"{seconds // 60}m"
    return f"{seconds}s"


class Scheduler(commands.Cog):
    """Recurring scheduled server announcements stored in SQLite."""

    schedule_group = app_commands.Group(
        name="schedule",
        description="Manage recurring scheduled channel announcements",
        guild_only=True,
    )

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def cog_unload(self):
        if self.scheduler_loop.is_running():
            self.scheduler_loop.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.scheduler_loop.is_running():
            self.scheduler_loop.start()

    @tasks.loop(seconds=30.0)
    async def scheduler_loop(self):
        """Poll SQLite for due recurring announcements and post them."""
        now = time.time()
        due_items = await database.get_due_scheduled_messages(now)
        for item in due_items:
            interval = max(60, int(item["interval_seconds"]))
            next_run = item["next_run_at"] + interval
            if next_run <= now:
                next_run = now + interval
            await database.advance_scheduled_message(item["id"], next_run)

            channel = self.bot.get_channel(item["channel_id"])
            if not channel:
                try:
                    channel = await self.bot.fetch_channel(item["channel_id"])
                except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                    continue

            if not channel:
                continue

            embed = discord.Embed(
                title=item.get("title") or "📢 Scheduled Announcement",
                description=item["message"],
                color=discord.Color.blue(),
                timestamp=discord.utils.utcnow(),
            )
            embed.set_footer(text=f"Schedule #{item['id']} • Repeats every {format_interval_human(interval)}")
            try:
                await channel.send(embed=embed)
            except (discord.Forbidden, discord.HTTPException):
                pass

    @scheduler_loop.before_loop
    async def before_scheduler_loop(self):
        await self.bot.wait_until_ready()

    @schedule_group.command(name="add", description="Create a recurring announcement posted automatically on an interval")
    @app_commands.describe(
        channel="Target text channel to post the announcement in",
        interval="How often to repeat (e.g. 30m, 6h, 1d, 7d — min 1m, max 30d)",
        message="Announcement text content",
        title="Optional embed title (defaults to 📢 Scheduled Announcement)",
        start_delay="Optional delay before the first post (e.g. 5m, 1h). Defaults to repeating after 1 interval",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def schedule_add(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        interval: str,
        message: str,
        title: Optional[str] = "📢 Scheduled Announcement",
        start_delay: Optional[str] = None,
    ):
        interval_sec = parse_time_string(interval)
        if interval_sec < 60 or interval_sec > 86400 * 30:
            await interaction.response.send_message(
                "❌ Invalid interval! Please use a duration between `1m` and `30d` (e.g., `30m`, `6h`, `1d`, `7d`).",
                ephemeral=True,
            )
            return

        if start_delay:
            delay_sec = parse_time_string(start_delay)
            if delay_sec < 10 or delay_sec > 86400 * 30:
                await interaction.response.send_message(
                    "❌ Invalid `start_delay`! Use a duration between `10s` and `30d` (e.g., `5m`, `1h`).",
                    ephemeral=True,
                )
                return
        else:
            delay_sec = interval_sec

        perms = channel.permissions_for(interaction.guild.me)
        if not perms.send_messages or not perms.embed_links:
            await interaction.response.send_message(
                f"❌ I need `Send Messages` and `Embed Links` permissions in {channel.mention}!",
                ephemeral=True,
            )
            return

        next_run_at = time.time() + delay_sec
        clean_title = (title or "📢 Scheduled Announcement").strip()[:200]
        clean_msg = message.strip()[:2000]

        schedule_id = await database.add_scheduled_message(
            guild_id=interaction.guild.id,
            channel_id=channel.id,
            author_id=interaction.user.id,
            title=clean_title,
            message=clean_msg,
            interval_seconds=interval_sec,
            next_run_at=next_run_at,
        )

        embed = discord.Embed(
            title="🗓️ Scheduled Announcement Created",
            description=f"Schedule **#{schedule_id}** will post automatically in {channel.mention}.",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(name="Repeat Interval", value=f"`{format_interval_human(interval_sec)}`", inline=True)
        embed.add_field(name="First Post", value=f"<t:{int(next_run_at)}:R>", inline=True)
        embed.add_field(name="Title", value=clean_title, inline=False)
        embed.add_field(name="Preview", value=clean_msg[:300], inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @schedule_group.command(name="list", description="View all recurring scheduled announcements in this server")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def schedule_list(self, interaction: discord.Interaction):
        rows = await database.get_guild_scheduled_messages(interaction.guild.id)
        if not rows:
            await interaction.response.send_message("ℹ️ No scheduled announcements are configured in this server.", ephemeral=True)
            return

        embed = discord.Embed(
            title="🗓️ Recurring Scheduled Announcements",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow(),
        )
        for row in rows[:15]:
            status_icon = "🟢 Active" if row["is_enabled"] else "⏸️ Paused"
            interval_str = format_interval_human(row["interval_seconds"])
            preview = row["message"][:100] + ("..." if len(row["message"]) > 100 else "")
            embed.add_field(
                name=f"#{row['id']} • {row['title'][:60]} ({status_icon})",
                value=(
                    f"Channel: <#{row['channel_id']}> • Every `{interval_str}` • Next: <t:{int(row['next_run_at'])}:R>\n"
                    f"> {preview}"
                ),
                inline=False,
            )
        if len(rows) > 15:
            embed.set_footer(text=f"Showing 15 of {len(rows)} scheduled announcements")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @schedule_group.command(name="toggle", description="Pause or resume a recurring scheduled announcement")
    @app_commands.describe(
        schedule_id="ID number of the scheduled announcement (from /schedule list)",
        enabled="True to resume, False to pause",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def schedule_toggle(self, interaction: discord.Interaction, schedule_id: int, enabled: bool):
        updated = await database.toggle_scheduled_message(interaction.guild.id, schedule_id, enabled)
        if not updated:
            await interaction.response.send_message(f"❌ Schedule `#{schedule_id}` was not found in this server.", ephemeral=True)
            return
        state_text = "🟢 Resumed" if enabled else "⏸️ Paused"
        await interaction.response.send_message(f"{state_text} scheduled announcement **#{schedule_id}**.", ephemeral=True)

    @schedule_group.command(name="remove", description="Delete a recurring scheduled announcement by its ID")
    @app_commands.describe(schedule_id="ID number of the scheduled announcement to delete")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def schedule_remove(self, interaction: discord.Interaction, schedule_id: int):
        removed = await database.delete_scheduled_message(interaction.guild.id, schedule_id)
        if not removed:
            await interaction.response.send_message(f"❌ Schedule `#{schedule_id}` was not found in this server.", ephemeral=True)
            return
        await interaction.response.send_message(f"🗑️ Deleted scheduled announcement **#{schedule_id}**.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Scheduler(bot))
