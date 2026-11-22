import random
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands


class Utility(commands.Cog):
    """General utility and informational commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context):
        """Check bot response latency."""
        latency_ms = round(self.bot.latency * 1000)
        await ctx.send(f"🏓 Pong! Latency: **{latency_ms}ms**")

    @app_commands.command(name="hello", description="Get a friendly greeting from the bot")
    async def hello(self, interaction: discord.Interaction):
        """Friendly greeting command."""
        await interaction.response.send_message(f"Hey {interaction.user.mention}! Welcome to the server. 👋")

    @app_commands.command(name="roll", description="Roll a dice (default is 6 sides)")
    @app_commands.describe(sides="Number of sides on the dice (e.g., 6, 20, 100)")
    async def roll(self, interaction: discord.Interaction, sides: int = 6):
        """Roll a dice with specified number of sides."""
        if sides < 2:
            await interaction.response.send_message("❌ Please pick at least 2 sides!", ephemeral=True)
            return
        result = random.randint(1, sides)
        await interaction.response.send_message(f"🎲 You rolled a **{result}** (1–{sides})")

    @app_commands.command(name="serverinfo", description="Display detailed information and statistics about this server")
    async def serverinfo(self, interaction: discord.Interaction):
        """Detailed server overview."""
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ This command can only be used inside a server.", ephemeral=True)
            return

        humans = sum(1 for m in guild.members if not m.bot)
        bots = sum(1 for m in guild.members if m.bot)

        text_count = len(guild.text_channels)
        voice_count = len(guild.voice_channels)
        stage_count = len(guild.stage_channels)
        category_count = len(guild.categories)

        verification_level = str(guild.verification_level).title()

        embed = discord.Embed(
            title=f"🏰 {guild.name}",
            description=guild.description or "No server description set.",
            color=discord.Color.blurple(),
            timestamp=discord.utils.utcnow(),
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        if guild.banner:
            embed.set_image(url=guild.banner.url)

        embed.add_field(name="👑 Server Owner", value=f"{guild.owner.mention if guild.owner else 'Unknown'}", inline=True)
        embed.add_field(name="🆔 Server ID", value=f"`{guild.id}`", inline=True)
        embed.add_field(
            name="📅 Created On",
            value=f"<t:{int(guild.created_at.timestamp())}:D>\n(<t:{int(guild.created_at.timestamp())}:R>)",
            inline=True,
        )

        member_desc = f"**Total:** {guild.member_count}\n👤 **Humans:** {humans} | 🤖 **Bots:** {bots}"
        embed.add_field(name="👥 Members", value=member_desc, inline=True)

        channel_desc = f"💬 **Text:** {text_count} | 🔊 **Voice:** {voice_count}\n🎙️ **Stage:** {stage_count} | 📁 **Categories:** {category_count}"
        embed.add_field(name="📺 Channels", value=channel_desc, inline=True)

        boost_tier = f"Level {guild.premium_tier}" if guild.premium_tier > 0 else "None"
        boost_desc = f"**Tier:** {boost_tier}\n**Boosts:** {guild.premium_subscription_count}"
        embed.add_field(name="🚀 Boost Status", value=boost_desc, inline=True)

        embed.add_field(name="🛡️ Roles", value=f"{len(guild.roles)} roles", inline=True)
        embed.add_field(name="😀 Emojis / Stickers", value=f"{len(guild.emojis)} emojis | {len(guild.stickers)} stickers", inline=True)
        embed.add_field(name="🔒 Verification", value=verification_level, inline=True)

        embed.set_footer(text=f"Requested by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo", description="Display detailed information about a member or yourself")
    @app_commands.describe(member="The member to inspect (defaults to you)")
    async def userinfo(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        """User profile inspection."""
        target = member or interaction.user
        guild = interaction.guild

        if guild and not isinstance(target, discord.Member):
            resolved = guild.get_member(target.id)
            if resolved:
                target = resolved

        embed = discord.Embed(
            title=f"👤 {target.display_name}'s Profile",
            color=target.color if hasattr(target, "color") and target.color != discord.Color.default() else discord.Color.blue(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_thumbnail(url=target.display_avatar.url)

        embed.add_field(name="Username", value=f"{target} (`{target.id}`)", inline=True)
        embed.add_field(name="Bot Account?", value="🤖 Yes" if target.bot else "👤 No", inline=True)
        embed.add_field(name="Top Role", value=target.top_role.mention if hasattr(target, "top_role") else "None", inline=True)

        embed.add_field(
            name="Created Account",
            value=f"<t:{int(target.created_at.timestamp())}:D>\n(<t:{int(target.created_at.timestamp())}:R>)",
            inline=True,
        )
        if hasattr(target, "joined_at") and target.joined_at:
            embed.add_field(
                name="Joined Server",
                value=f"<t:{int(target.joined_at.timestamp())}:D>\n(<t:{int(target.joined_at.timestamp())}:R>)",
                inline=True,
            )

        if hasattr(target, "roles"):
            roles = [r.mention for r in reversed(target.roles) if r.name != "@everyone"]
            if roles:
                roles_str = ", ".join(roles[:15])
                if len(roles) > 15:
                    roles_str += f" ...and {len(roles) - 15} more"
            else:
                roles_str = "No custom roles"
            embed.add_field(name=f"Roles ({len(roles)})", value=roles_str, inline=False)

        if hasattr(target, "guild_permissions"):
            key_perms = []
            gp = target.guild_permissions
            if gp.administrator:
                key_perms.append("Administrator")
            if gp.manage_guild:
                key_perms.append("Manage Server")
            if gp.manage_channels:
                key_perms.append("Manage Channels")
            if gp.manage_roles:
                key_perms.append("Manage Roles")
            if gp.ban_members:
                key_perms.append("Ban Members")
            if gp.kick_members:
                key_perms.append("Kick Members")
            if gp.moderate_members:
                key_perms.append("Timeout Members")
            if gp.manage_messages:
                key_perms.append("Manage Messages")
            if gp.mention_everyone:
                key_perms.append("Mention @everyone")

            if key_perms:
                embed.add_field(name="Key Permissions", value=", ".join(key_perms), inline=False)

        embed.set_footer(text=f"Requested by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="avatar", description="View and download a user's avatar in high resolution")
    @app_commands.describe(user="The user whose avatar you want to view (defaults to you)")
    async def avatar(self, interaction: discord.Interaction, user: Optional[discord.User] = None):
        """Display avatar preview and direct download links."""
        target = user or interaction.user
        avatar_url = target.display_avatar.with_size(1024).url

        embed = discord.Embed(
            title=f"🖼️ {target.display_name}'s Avatar",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_image(url=avatar_url)

        png_url = target.display_avatar.with_format("png").url
        jpg_url = target.display_avatar.with_format("jpg").url
        webp_url = target.display_avatar.with_format("webp").url

        embed.description = f"**Download:** [PNG]({png_url}) | [JPG]({jpg_url}) | [WEBP]({webp_url})"
        embed.set_footer(text=f"Requested by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Utility(bot))
