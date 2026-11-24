from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from database import get_guild_settings, update_guild_setting


class Events(commands.Cog):
    """Global event listeners, customizable welcome & leave cards, and member greetings."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """Fires when bot is connected and ready."""
        print(f"Logged in as {self.bot.user} (ID: {self.bot.user.id})")

        # Automatically sync commands to all connected guilds for instant availability
        for guild in self.bot.guilds:
            try:
                self.bot.tree.copy_global_to(guild=guild)
                synced = await self.bot.tree.sync(guild=guild)
                print(f"✅ Instantly synced {len(synced)} slash commands to guild: {guild.name} ({guild.id})")
            except Exception as e:
                print(f"⚠️ Could not guild-sync to {guild.name}: {e}")

        print("Rookie is ready and operational!")

    @app_commands.command(name="setwelcome", description="Configure automated welcome greetings and custom channel")
    @app_commands.describe(
        channel="Text channel to send welcome cards (leave blank to disable)",
        custom_message="Custom template (use {user}, {username}, {server}, {count})",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setwelcome(
        self,
        interaction: discord.Interaction,
        channel: Optional[discord.TextChannel] = None,
        custom_message: Optional[str] = None,
    ):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        channel_id = channel.id if channel else None
        await update_guild_setting(guild.id, "welcome_channel_id", channel_id)
        if custom_message is not None:
            await update_guild_setting(guild.id, "welcome_message", custom_message.strip())

        if channel:
            msg_preview = custom_message or "Default Embed Welcome Card"
            embed = discord.Embed(
                title="👋 Welcome System Configured",
                description=(
                    f"New member greetings will be sent to {channel.mention}.\n\n"
                    f"**Template:** `{msg_preview}`"
                ),
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow(),
            )
            embed.set_footer(text="Tags supported: {user}, {username}, {server}, {count}")
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("🛑 Welcome greetings have been **disabled**.", ephemeral=True)

    @app_commands.command(name="setleave", description="Configure automated departure/goodbye messages")
    @app_commands.describe(
        channel="Text channel to send leave cards (leave blank to disable)",
        custom_message="Custom template (use {username}, {server}, {count})",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setleave(
        self,
        interaction: discord.Interaction,
        channel: Optional[discord.TextChannel] = None,
        custom_message: Optional[str] = None,
    ):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        channel_id = channel.id if channel else None
        await update_guild_setting(guild.id, "leave_channel_id", channel_id)
        if custom_message is not None:
            await update_guild_setting(guild.id, "leave_message", custom_message.strip())

        if channel:
            msg_preview = custom_message or "Default Goodbye Embed"
            embed = discord.Embed(
                title="👋 Leave Messages Configured",
                description=(
                    f"Departure notices will be sent to {channel.mention}.\n\n"
                    f"**Template:** `{msg_preview}`"
                ),
                color=discord.Color.orange(),
                timestamp=discord.utils.utcnow(),
            )
            embed.set_footer(text="Tags supported: {username}, {server}, {count}")
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("🛑 Leave notices have been **disabled**.", ephemeral=True)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Greet new members automatically when they join the server."""
        guild = member.guild
        settings = await get_guild_settings(guild.id)

        target_channel = None
        custom_cid = settings.get("welcome_channel_id")
        if custom_cid:
            target_channel = guild.get_channel(custom_cid)

        # Fallback channel selection if no custom channel is set
        if not target_channel or not target_channel.permissions_for(guild.me).send_messages:
            target_channel = guild.system_channel

        if not target_channel or not target_channel.permissions_for(guild.me).send_messages:
            common_names = ("welcome", "welcomes", "general", "lobby", "chat")
            for channel in guild.text_channels:
                if channel.name.lower() in common_names and channel.permissions_for(guild.me).send_messages:
                    target_channel = channel
                    break

        if not target_channel:
            return

        custom_tpl = settings.get("welcome_message")
        if custom_tpl:
            rendered_text = (
                custom_tpl.replace("{user}", member.mention)
                .replace("{username}", member.name)
                .replace("{server}", guild.name)
                .replace("{count}", str(guild.member_count))
            )
            try:
                await target_channel.send(rendered_text)
                return
            except discord.HTTPException:
                pass

        # Default rich card embed
        embed = discord.Embed(
            title=f"👋 Welcome to {guild.name}!",
            description=(
                f"Hey {member.mention}, welcome to the server! 🎉\n"
                "We're glad to have you here. Please make sure to check the rules and enjoy your stay!"
            ),
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(
            name="Account Created",
            value=f"<t:{int(member.created_at.timestamp())}:R>",
            inline=True,
        )
        embed.add_field(
            name="Member Count",
            value=f"#{guild.member_count}",
            inline=True,
        )
        embed.set_footer(text=f"User ID: {member.id}")

        try:
            await target_channel.send(content=f"Welcome {member.mention}!", embed=embed)
        except discord.HTTPException as e:
            print(f"Failed to send welcome message in {guild.name}: {e}")

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Send farewell notices when a member leaves."""
        guild = member.guild
        settings = await get_guild_settings(guild.id)

        leave_cid = settings.get("leave_channel_id")
        if not leave_cid:
            return

        target_channel = guild.get_channel(leave_cid)
        if not target_channel or not target_channel.permissions_for(guild.me).send_messages:
            return

        custom_tpl = settings.get("leave_message")
        if custom_tpl:
            rendered_text = (
                custom_tpl.replace("{username}", member.name)
                .replace("{server}", guild.name)
                .replace("{count}", str(guild.member_count))
            )
            try:
                await target_channel.send(rendered_text)
                return
            except discord.HTTPException:
                pass

        embed = discord.Embed(
            title="👋 Goodbye!",
            description=f"**{member}** has left the server. We now have **{guild.member_count}** members.",
            color=discord.Color.dark_grey(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        try:
            await target_channel.send(embed=embed)
        except discord.HTTPException:
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))
