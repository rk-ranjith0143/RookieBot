import discord
from discord.ext import commands


class Events(commands.Cog):
    """Global event listeners and member greetings."""

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

        print("Bot is ready and operational!")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Greet new members automatically when they join the server."""
        guild = member.guild

        # 1. Look for system channel
        target_channel = guild.system_channel

        # 2. If no system channel or cannot send, look for common welcome channel names
        if not target_channel or not target_channel.permissions_for(guild.me).send_messages:
            common_names = ("welcome", "welcomes", "general", "lobby", "chat")
            for channel in guild.text_channels:
                if channel.name.lower() in common_names and channel.permissions_for(guild.me).send_messages:
                    target_channel = channel
                    break

        # 3. Fallback to the first text channel where bot has send permission
        if not target_channel or not target_channel.permissions_for(guild.me).send_messages:
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    target_channel = channel
                    break

        if not target_channel:
            return

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


async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))
