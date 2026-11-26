from collections import deque
import random
from typing import Dict, Optional

import discord
from discord import app_commands
from discord.ext import commands


class Utility(commands.Cog):
    """General utility and informational commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._deleted_cache: Dict[int, deque] = {}
        self._edited_cache: Dict[int, deque] = {}

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if not message.guild or message.author.bot:
            return
        if not message.content and not message.attachments:
            return

        bucket = self._deleted_cache.setdefault(message.channel.id, deque(maxlen=10))
        bucket.appendleft(
            {
                "author_name": str(message.author),
                "author_avatar": message.author.display_avatar.url,
                "content": message.content or "*[No text content]*",
                "attachments": [att.url for att in message.attachments[:3]],
                "timestamp": discord.utils.utcnow(),
            }
        )

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if not before.guild or before.author.bot:
            return
        if before.content == after.content:
            return
        if not before.content and not after.content:
            return

        bucket = self._edited_cache.setdefault(before.channel.id, deque(maxlen=10))
        bucket.appendleft(
            {
                "author_name": str(before.author),
                "author_avatar": before.author.display_avatar.url,
                "before": before.content or "*[Empty]*",
                "after": after.content or "*[Empty]*",
                "jump_url": after.jump_url,
                "timestamp": discord.utils.utcnow(),
            }
        )

    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context):
        """Check bot response latency."""
        latency_ms = round(self.bot.latency * 1000)
        await ctx.send(f"🏓 Pong! Latency: **{latency_ms}ms**")

    @commands.command(name="sync")
    @commands.has_permissions(administrator=True)
    async def sync(self, ctx: commands.Context):
        """Instantly sync all slash commands directly to this server."""
        if not ctx.guild:
            await ctx.send("❌ This command can only be used in a server.")
            return

        status_msg = await ctx.send("🔄 Syncing slash commands directly to this server...")
        try:
            self.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await self.bot.tree.sync(guild=ctx.guild)
            await status_msg.edit(
                content=(
                    f"✅ Successfully synced **{len(synced)}** slash command(s) to **{ctx.guild.name}**!\n"
                    "*(Tip: If they don't appear in your `/` menu immediately, press **Ctrl + R** to reload Discord!)*"
                )
            )
        except Exception as e:
            await status_msg.edit(content=f"❌ Failed to sync slash commands: `{e}`")

    @app_commands.command(name="hello", description="Get a friendly greeting from Rookie")
    async def hello(self, interaction: discord.Interaction):
        """Friendly greeting command."""
        await interaction.response.send_message(
            f"Hey {interaction.user.mention}! I'm **Rookie**, your all-in-one server utility and community assistant. Type `/` to see my commands! 👋"
        )

    @app_commands.command(name="roll", description="Roll a dice (default is 6 sides)")
    @app_commands.describe(sides="Number of sides on the dice (e.g., 6, 20, 100)")
    async def roll(self, interaction: discord.Interaction, sides: int = 6):
        """Roll a dice with specified number of sides."""
        if sides < 2:
            await interaction.response.send_message("❌ Please pick at least 2 sides!", ephemeral=True)
            return
        result = random.randint(1, sides)
        await interaction.response.send_message(f"🎲 You rolled a **{result}** (1–{sides})")

    @app_commands.command(name="8ball", description="Ask the Magic 8-Ball a yes/no question")
    @app_commands.describe(question="What do you want to ask the Magic 8-Ball?")
    async def eight_ball(self, interaction: discord.Interaction, question: str):
        """Classic Magic 8-Ball utility."""
        responses = [
            "It is certain. ✨",
            "Without a doubt! ✅",
            "Yes, definitely! 💯",
            "You may rely on it. 👍",
            "Most likely. 🎯",
            "Outlook good! 🌟",
            "Reply hazy, try again. 🌫️",
            "Ask again later. ⏳",
            "Better not tell you now... 🤫",
            "Cannot predict now. 🔮",
            "Don't count on it. ❌",
            "My sources say no. 📉",
            "Outlook not so good. 😬",
            "Very doubtful. 🚫",
        ]
        answer = random.choice(responses)
        embed = discord.Embed(
            title="🎱 Magic 8-Ball",
            color=discord.Color.purple(),
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(name="Question", value=question.strip()[:256], inline=False)
        embed.add_field(name="Answer", value=f"**{answer}**", inline=False)
        embed.set_footer(text=f"Asked by {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

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

    @app_commands.command(name="snipe", description="View the most recently deleted message in this channel")
    @app_commands.guild_only()
    @app_commands.describe(index="Which recent deleted message to view (1 = most recent, up to 10)")
    async def snipe(self, interaction: discord.Interaction, index: int = 1):
        """Show cached recently deleted message in the current channel."""
        bucket = self._deleted_cache.get(interaction.channel.id)
        if not bucket:
            await interaction.response.send_message("ℹ️ Nothing recently deleted in this channel to snipe.", ephemeral=True)
            return
        if index < 1 or index > len(bucket):
            await interaction.response.send_message(
                f"❌ Please pick an index between `1` and `{len(bucket)}`.",
                ephemeral=True,
            )
            return

        entry = bucket[index - 1]
        embed = discord.Embed(
            description=entry["content"][:4000],
            color=discord.Color.red(),
            timestamp=entry["timestamp"],
        )
        embed.set_author(name=entry["author_name"], icon_url=entry["author_avatar"])
        if entry["attachments"]:
            embed.add_field(
                name="Attachments",
                value="\n".join(entry["attachments"]),
                inline=False,
            )
        embed.set_footer(text=f"Sniped {index}/{len(bucket)} • Deleted")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="editsnipe", description="View the most recently edited message (before & after) in this channel")
    @app_commands.guild_only()
    @app_commands.describe(index="Which recent edited message to view (1 = most recent, up to 10)")
    async def editsnipe(self, interaction: discord.Interaction, index: int = 1):
        """Show cached recently edited message before/after diff in the current channel."""
        bucket = self._edited_cache.get(interaction.channel.id)
        if not bucket:
            await interaction.response.send_message("ℹ️ Nothing recently edited in this channel to snipe.", ephemeral=True)
            return
        if index < 1 or index > len(bucket):
            await interaction.response.send_message(
                f"❌ Please pick an index between `1` and `{len(bucket)}`.",
                ephemeral=True,
            )
            return

        entry = bucket[index - 1]
        embed = discord.Embed(
            description=f"[Jump to Message]({entry['jump_url']})",
            color=discord.Color.orange(),
            timestamp=entry["timestamp"],
        )
        embed.set_author(name=entry["author_name"], icon_url=entry["author_avatar"])
        embed.add_field(name="Before", value=entry["before"][:1024], inline=False)
        embed.add_field(name="After", value=entry["after"][:1024], inline=False)
        embed.set_footer(text=f"Edit Snipe {index}/{len(bucket)} • Edited")
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Utility(bot))
