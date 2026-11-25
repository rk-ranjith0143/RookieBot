import calendar
import datetime
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands, tasks

import database

MONTH_CHOICES = [
    app_commands.Choice(name=calendar.month_name[m], value=m)
    for m in range(1, 13)
]


def is_valid_birthday(month: int, day: int) -> bool:
    """Validate calendar month/day pair (allowing Feb 29 for leap-year birthdays)."""
    try:
        datetime.date(2024, month, day)
        return True
    except ValueError:
        return False


def days_until_birthday(month: int, day: int, today: Optional[datetime.date] = None) -> int:
    """Calculate days until next occurrence of month/day from today."""
    ref = today or datetime.datetime.now(datetime.timezone.utc).date()
    year = ref.year
    while True:
        try:
            target = datetime.date(year, month, day)
            if target >= ref:
                return (target - ref).days
        except ValueError:
            # Handle Feb 29 on non-leap years by checking next leap year
            pass
        year += 1


class Birthdays(commands.Cog):
    """Server birthday tracker with upcoming calendar and automated daily celebrations."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def cog_unload(self):
        if self.birthday_loop.is_running():
            self.birthday_loop.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.birthday_loop.is_running():
            self.birthday_loop.start()

    @tasks.loop(minutes=30.0)
    async def birthday_loop(self):
        """Check UTC date and celebrate any due member birthdays."""
        now = datetime.datetime.now(datetime.timezone.utc)
        due = await database.get_due_birthdays(now.month, now.day, now.year)
        for item in due:
            guild = self.bot.get_guild(item["guild_id"])
            if not guild:
                continue

            member = guild.get_member(item["user_id"])
            if not member:
                continue

            await database.mark_birthday_celebrated(guild.id, member.id, now.year)

            channel = guild.get_channel(item["channel_id"])
            if isinstance(channel, discord.TextChannel):
                embed = discord.Embed(
                    title="🎂 Happy Birthday! 🎉",
                    description=(
                        f"Join us in wishing {member.mention} a very **Happy Birthday** today! 🥳🎈\n\n"
                        "Hope you have an awesome day!"
                    ),
                    color=discord.Color.magenta(),
                    timestamp=discord.utils.utcnow(),
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                try:
                    await channel.send(content=f"🎉 Happy Birthday {member.mention}!", embed=embed)
                except (discord.Forbidden, discord.HTTPException):
                    pass

            role_id = item.get("role_id")
            if role_id:
                role = guild.get_role(role_id)
                if role and guild.me and guild.me.top_role > role:
                    try:
                        await member.add_roles(role, reason="RookieBot Happy Birthday celebration")
                    except (discord.Forbidden, discord.HTTPException):
                        pass

    @birthday_loop.before_loop
    async def before_birthday_loop(self):
        await self.bot.wait_until_ready()

    birthday_group = app_commands.Group(
        name="birthday",
        description="Set, view, and manage server birthday celebrations",
    )

    @birthday_group.command(name="set", description="Save your birthday in this server")
    @app_commands.describe(
        month="Birth month (January - December)",
        day="Day of the month (1 - 31)",
    )
    @app_commands.choices(month=MONTH_CHOICES)
    async def birthday_set(
        self,
        interaction: discord.Interaction,
        month: app_commands.Choice[int],
        day: app_commands.Range[int, 1, 31],
    ):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        if not is_valid_birthday(month.value, day):
            await interaction.response.send_message(
                f"❌ `{month.name} {day}` is not a valid calendar date!",
                ephemeral=True,
            )
            return

        await database.set_user_birthday(interaction.guild.id, interaction.user.id, month.value, day)

        embed = discord.Embed(
            title="🎂 Birthday Saved!",
            description=f"{interaction.user.mention}'s birthday is set to **{month.name} {day}**! 🎉",
            color=discord.Color.green(),
        )
        embed.set_footer(text="Use /birthday upcoming to see upcoming server birthdays.")
        await interaction.response.send_message(embed=embed)

    @birthday_group.command(name="remove", description="Remove your saved birthday from this server")
    async def birthday_remove(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        removed = await database.remove_user_birthday(interaction.guild.id, interaction.user.id)
        if removed:
            await interaction.response.send_message("✅ Your birthday has been removed from this server.", ephemeral=True)
        else:
            await interaction.response.send_message("ℹ️ You do not have a saved birthday in this server.", ephemeral=True)

    @birthday_group.command(name="view", description="Check your or another member's saved birthday")
    @app_commands.describe(member="Member to check (defaults to yourself)")
    async def birthday_view(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        target = member or interaction.user
        entry = await database.get_user_birthday(interaction.guild.id, target.id)
        if not entry:
            await interaction.response.send_message(
                f"ℹ️ {target.mention} has not set their birthday yet. Use `/birthday set`!",
                ephemeral=True,
            )
            return

        month_name = calendar.month_name[entry["month"]]
        days_left = days_until_birthday(entry["month"], entry["day"])
        countdown = "🎉 **Today!**" if days_left == 0 else f"in **{days_left} day(s)**"

        embed = discord.Embed(
            title=f"🎂 {target.display_name}'s Birthday",
            description=f"**Date:** {month_name} {entry['day']}\n**Next Celebration:** {countdown}",
            color=discord.Color.magenta(),
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @birthday_group.command(name="upcoming", description="View the next 10 upcoming birthdays in this server")
    async def birthday_upcoming(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        rows = await database.get_guild_birthdays(interaction.guild.id)
        if not rows:
            await interaction.response.send_message(
                "ℹ️ No birthdays saved yet! Be the first with `/birthday set`.",
                ephemeral=True,
            )
            return

        enriched = []
        for r in rows:
            d = days_until_birthday(r["month"], r["day"])
            enriched.append((d, r))
        enriched.sort(key=lambda x: x[0])

        lines = []
        for d, r in enriched[:10]:
            member = interaction.guild.get_member(r["user_id"])
            display = member.mention if member else f"User ID `{r['user_id']}`"
            m_name = calendar.month_name[r["month"]]
            when = "🎉 **Today!**" if d == 0 else f"in {d} day(s)"
            lines.append(f"• {display} — **{m_name} {r['day']}** ({when})")

        embed = discord.Embed(
            title=f"🎈 Upcoming Birthdays ({len(rows)} saved)",
            description="\n".join(lines),
            color=discord.Color.magenta(),
            timestamp=discord.utils.utcnow(),
        )
        await interaction.response.send_message(embed=embed)

    @birthday_group.command(name="setup", description="Configure automated daily birthday announcements")
    @app_commands.describe(
        channel="Channel where birthday celebration cards will be posted",
        role="Optional Birthday role granted on a member's birthday",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def birthday_setup(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        role: Optional[discord.Role] = None,
    ):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        bot_member = interaction.guild.get_member(self.bot.user.id) if self.bot.user else interaction.guild.me
        if role and bot_member and role >= bot_member.top_role:
            await interaction.response.send_message(
                f"❌ I cannot assign {role.mention} because it is equal to or higher than my highest role.",
                ephemeral=True,
            )
            return

        role_id = role.id if role else None
        await database.set_birthday_settings(interaction.guild.id, channel.id, role_id)

        embed = discord.Embed(
            title="🎂 Birthday System Configured",
            description=(
                f"• **Announcement Channel:** {channel.mention}\n"
                f"• **Birthday Role:** {role.mention if role else '*(None)*'}\n\n"
                "Members can save their birthdays anytime using `/birthday set`!"
            ),
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed)

    @birthday_group.command(name="disable", description="Disable automated birthday announcements in this server")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def birthday_disable(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        disabled = await database.disable_birthday_settings(interaction.guild.id)
        if disabled:
            await interaction.response.send_message("✅ Automated birthday announcements have been disabled.", ephemeral=True)
        else:
            await interaction.response.send_message("ℹ️ Birthday announcements were not configured.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Birthdays(bot))
