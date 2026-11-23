import discord
from discord import app_commands
from discord.ext import commands
import database


class ServerStats(commands.Cog):
    """Dynamic server statistics channels displaying live member and bot counts."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    serverstats_group = app_commands.Group(
        name="serverstats",
        description="Configure live server statistics counter channels",
        default_permissions=discord.Permissions(administrator=True),
    )

    async def _update_counters_for_guild(self, guild: discord.Guild):
        """Helper to refresh all counter channels for a given guild."""
        channels_info = await database.get_server_stat_channels(guild.id)
        if not channels_info:
            return

        total_members = guild.member_count or len(guild.members)
        bot_count = sum(1 for m in guild.members if m.bot)
        human_count = total_members - bot_count

        stat_map = {
            "all_members": total_members,
            "humans": human_count,
            "bots": bot_count,
        }

        for item in channels_info:
            stat_type = item["stat_type"]
            channel_id = item["channel_id"]
            fmt = item["format_string"]

            channel = guild.get_channel(channel_id)
            if channel and stat_type in stat_map:
                new_name = fmt.format(count=stat_map[stat_type])
                if channel.name != new_name:
                    try:
                        await channel.edit(name=new_name)
                    except Exception:
                        pass

    @serverstats_group.command(
        name="setup",
        description="Create locked voice channels displaying live member stats",
    )
    async def setup_stats(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        guild = interaction.guild
        await interaction.response.defer(ephemeral=True)

        # Create category for stats
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(connect=False, view_channel=True),
        }

        try:
            category = await guild.create_category(name="📊 Server Stats", overwrites=overwrites)
        except discord.Forbidden:
            await interaction.followup.send(
                "❌ Missing permissions to create categories or manage channels.",
                ephemeral=True,
            )
            return

        total_members = guild.member_count or len(guild.members)
        bot_count = sum(1 for m in guild.members if m.bot)
        human_count = total_members - bot_count

        # Create 3 voice channels
        ch_total = await guild.create_voice_channel(
            name=f"👥 Total: {total_members}",
            category=category,
            overwrites=overwrites,
        )
        ch_humans = await guild.create_voice_channel(
            name=f"👤 Members: {human_count}",
            category=category,
            overwrites=overwrites,
        )
        ch_bots = await guild.create_voice_channel(
            name=f"🤖 Bots: {bot_count}",
            category=category,
            overwrites=overwrites,
        )

        # Save to database
        await database.set_server_stat_channel(guild.id, "all_members", ch_total.id, "👥 Total: {count}")
        await database.set_server_stat_channel(guild.id, "humans", ch_humans.id, "👤 Members: {count}")
        await database.set_server_stat_channel(guild.id, "bots", ch_bots.id, "🤖 Bots: {count}")

        embed = discord.Embed(
            title="📊 Server Stats Setup Complete",
            description=(
                f"Created stats category **{category.name}** with live counters:\n"
                f"• {ch_total.mention} (`👥 Total: {total_members}`)\n"
                f"• {ch_humans.mention} (`👤 Members: {human_count}`)\n"
                f"• {ch_bots.mention} (`🤖 Bots: {bot_count}`)\n\n"
                f"*These channels are locked and will auto-update whenever members join or leave!*"
            ),
            color=0x5865F2,
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

    @serverstats_group.command(name="refresh", description="Force refresh the server stats channels now")
    async def refresh_stats(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        await self._update_counters_for_guild(interaction.guild)
        await interaction.response.send_message("✅ Server stats channels have been refreshed!", ephemeral=True)

    @serverstats_group.command(
        name="remove",
        description="Delete stats channels and disable live tracking",
    )
    async def remove_stats(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        channels_info = await database.get_server_stat_channels(interaction.guild.id)
        if not channels_info:
            await interaction.response.send_message("ℹ️ No stats channels are currently configured.", ephemeral=True)
            return

        for item in channels_info:
            ch = interaction.guild.get_channel(item["channel_id"])
            if ch:
                try:
                    await ch.delete()
                except Exception:
                    pass

        await database.remove_server_stat_channels(interaction.guild.id)
        await interaction.response.send_message("✅ Server stats tracking has been removed.", ephemeral=True)

    # -----------------------------------------------------------------------
    # Listeners for Auto-Updates
    # -----------------------------------------------------------------------

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.guild:
            await self._update_counters_for_guild(member.guild)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        if member.guild:
            await self._update_counters_for_guild(member.guild)


async def setup(bot: commands.Bot):
    await bot.add_cog(ServerStats(bot))
