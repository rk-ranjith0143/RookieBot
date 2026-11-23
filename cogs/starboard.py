import discord
from discord import app_commands
from discord.ext import commands
import database


class Starboard(commands.Cog):
    """Starboard system: highlights community favorite messages when they receive stars."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    starboard_group = app_commands.Group(
        name="starboard",
        description="Configure and manage the Starboard system",
        default_permissions=discord.Permissions(manage_guild=True),
    )

    @starboard_group.command(name="setup", description="Configure the starboard channel and star threshold")
    @app_commands.describe(
        channel="The channel where starred messages will be posted",
        threshold="Minimum stars required to appear on the starboard (default: 3)",
    )
    async def setup_starboard(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        threshold: app_commands.Range[int, 1, 50] = 3,
    ):
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        bot_member = interaction.guild.get_member(self.bot.user.id) if self.bot.user else None
        if bot_member:
            perms = channel.permissions_for(bot_member)
            if not perms.send_messages or not perms.embed_links:
                await interaction.response.send_message(
                    f"⚠️ I don't have permission to send messages or embeds in {channel.mention}.",
                    ephemeral=True,
                )
                return

        await database.set_starboard_settings(interaction.guild.id, channel.id, threshold, 1)

        embed = discord.Embed(
            title="⭐ Starboard Configured",
            description=(
                f"• **Channel:** {channel.mention}\n"
                f"• **Star Threshold:** `{threshold}` ⭐\n"
                f"• **Status:** Active\n\n"
                f"React to messages with ⭐ to feature them!"
            ),
            color=0xFFAC33,
        )
        await interaction.response.send_message(embed=embed)

    @starboard_group.command(name="disable", description="Disable the starboard system in this server")
    async def disable_starboard(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        await database.disable_starboard(interaction.guild.id)
        embed = discord.Embed(
            title="⭐ Starboard Disabled",
            description="Starboard has been turned off for this server. You can re-enable it anytime with `/starboard setup`.",
            color=discord.Color.red(),
        )
        await interaction.response.send_message(embed=embed)

    # -----------------------------------------------------------------------
    # Starboard Event Listeners
    # -----------------------------------------------------------------------

    def _build_starboard_embed(self, message: discord.Message) -> discord.Embed:
        embed = discord.Embed(
            description=message.content or "*[No text content]*",
            color=0xFFAC33,
            timestamp=message.created_at,
        )
        embed.set_author(
            name=message.author.display_name,
            icon_url=message.author.display_avatar.url,
        )
        embed.add_field(
            name="Source",
            value=f"[Jump to message]({message.jump_url})",
            inline=False,
        )

        if message.attachments:
            for att in message.attachments:
                if att.content_type and att.content_type.startswith("image/"):
                    embed.set_image(url=att.url)
                    break

        embed.set_footer(text=f"ID: {message.id}")
        return embed

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if str(payload.emoji) != "⭐" or not payload.guild_id:
            return

        settings = await database.get_starboard_settings(payload.guild_id)
        if not settings or not settings.get("is_enabled"):
            return

        starboard_channel_id = settings["channel_id"]
        threshold = settings["threshold"]

        if payload.channel_id == starboard_channel_id:
            return  # Avoid starring messages in the starboard channel itself

        channel = self.bot.get_channel(payload.channel_id)
        if not isinstance(channel, discord.TextChannel):
            try:
                channel = await self.bot.fetch_channel(payload.channel_id)
            except Exception:
                return

        try:
            message = await channel.fetch_message(payload.message_id)
        except Exception:
            return

        if message.author.id == payload.user_id:
            # Optional: prevent self-starring or let it count
            pass

        # Calculate total stars
        star_reaction = discord.utils.get(message.reactions, emoji="⭐")
        star_count = star_reaction.count if star_reaction else 0

        starboard_channel = self.bot.get_channel(starboard_channel_id)
        if not isinstance(starboard_channel, discord.TextChannel):
            try:
                starboard_channel = await self.bot.fetch_channel(starboard_channel_id)
            except Exception:
                return

        star_entry = await database.get_starboard_message(message.id)

        if star_count >= threshold:
            embed = self._build_starboard_embed(message)
            content_text = f"⭐ **{star_count}** <#{message.channel.id}>"

            if star_entry:
                try:
                    sb_msg = await starboard_channel.fetch_message(star_entry["starboard_message_id"])
                    await sb_msg.edit(content=content_text, embed=embed)
                    await database.update_starboard_count(message.id, star_count)
                except discord.NotFound:
                    # Message was deleted manually, repost
                    new_sb_msg = await starboard_channel.send(content=content_text, embed=embed)
                    await database.save_starboard_message(
                        message.id, new_sb_msg.id, message.channel.id, payload.guild_id, star_count
                    )
            else:
                new_sb_msg = await starboard_channel.send(content=content_text, embed=embed)
                await database.save_starboard_message(
                    message.id, new_sb_msg.id, message.channel.id, payload.guild_id, star_count
                )

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if str(payload.emoji) != "⭐" or not payload.guild_id:
            return

        settings = await database.get_starboard_settings(payload.guild_id)
        if not settings or not settings.get("is_enabled"):
            return

        star_entry = await database.get_starboard_message(payload.message_id)
        if not star_entry:
            return

        channel = self.bot.get_channel(payload.channel_id)
        if not isinstance(channel, discord.TextChannel):
            try:
                channel = await self.bot.fetch_channel(payload.channel_id)
            except Exception:
                return

        try:
            message = await channel.fetch_message(payload.message_id)
            star_reaction = discord.utils.get(message.reactions, emoji="⭐")
            star_count = star_reaction.count if star_reaction else 0
        except Exception:
            star_count = 0

        starboard_channel = self.bot.get_channel(settings["channel_id"])
        if not isinstance(starboard_channel, discord.TextChannel):
            try:
                starboard_channel = await self.bot.fetch_channel(settings["channel_id"])
            except Exception:
                return

        if star_count < settings["threshold"]:
            # Star dropped below threshold: delete starboard message
            try:
                sb_msg = await starboard_channel.fetch_message(star_entry["starboard_message_id"])
                await sb_msg.delete()
            except Exception:
                pass
            await database.delete_starboard_message(payload.message_id)
        else:
            # Update star count
            try:
                sb_msg = await starboard_channel.fetch_message(star_entry["starboard_message_id"])
                content_text = f"⭐ **{star_count}** <#{payload.channel_id}>"
                await sb_msg.edit(content=content_text)
                await database.update_starboard_count(payload.message_id, star_count)
            except Exception:
                pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Starboard(bot))
