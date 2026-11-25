import re

import discord
from discord import app_commands, ui
from discord.ext import commands


def parse_color(color_str: str) -> discord.Color:
    """Parse hex code or named color with fallback to blurple."""
    color_str = color_str.strip().lower().lstrip("#")
    named_colors = {
        "blue": discord.Color.blue(),
        "red": discord.Color.red(),
        "green": discord.Color.green(),
        "gold": discord.Color.gold(),
        "orange": discord.Color.orange(),
        "purple": discord.Color.purple(),
        "blurple": discord.Color.blurple(),
        "dark": discord.Color.dark_theme(),
    }
    if color_str in named_colors:
        return named_colors[color_str]

    if re.fullmatch(r"[0-9a-f]{6}", color_str):
        try:
            return discord.Color(int(color_str, 16))
        except ValueError:
            pass

    return discord.Color.blurple()


class CustomEmbedModal(ui.Modal, title="Create Custom Announcement Embed"):
    """Interactive modal popup for crafting custom server announcement embeds."""

    embed_title = ui.TextInput(
        label="Title",
        placeholder="Announcement Header...",
        max_length=256,
        required=True,
    )

    embed_description = ui.TextInput(
        label="Description",
        placeholder="Write your announcement or rules message here...",
        style=discord.TextStyle.paragraph,
        max_length=4000,
        required=True,
    )

    embed_color = ui.TextInput(
        label="Color (Hex code or name e.g. #5865F2, gold)",
        placeholder="#5865F2",
        default="#5865F2",
        max_length=20,
        required=False,
    )

    embed_image = ui.TextInput(
        label="Image URL (optional banner image)",
        placeholder="https://example.com/banner.png",
        required=False,
    )

    embed_footer = ui.TextInput(
        label="Footer Text (optional)",
        placeholder="Server Announcements • 2026",
        max_length=128,
        required=False,
    )

    async def on_submit(self, interaction: discord.Interaction):
        color = parse_color(str(self.embed_color))
        embed = discord.Embed(
            title=str(self.embed_title),
            description=str(self.embed_description),
            color=color,
            timestamp=discord.utils.utcnow(),
        )

        image_url = str(self.embed_image).strip()
        if image_url.startswith("http://") or image_url.startswith("https://"):
            embed.set_image(url=image_url)

        footer_text = str(self.embed_footer).strip()
        if footer_text:
            embed.set_footer(
                text=footer_text,
                icon_url=interaction.guild.icon.url if interaction.guild and interaction.guild.icon else None,
            )

        # Send embed directly to the channel
        await interaction.channel.send(embed=embed)
        await interaction.response.send_message("✅ Embed successfully published to this channel!", ephemeral=True)


class Embeds(commands.Cog):
    """Custom embed announcement builder with interactive popups."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="embed", description="Open an interactive modal to craft and publish a custom embed")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.bot_has_permissions(send_messages=True, embed_links=True)
    async def embed(self, interaction: discord.Interaction):
        """Triggers the custom embed builder modal."""
        await interaction.response.send_modal(CustomEmbedModal())


async def setup(bot: commands.Bot):
    await bot.add_cog(Embeds(bot))
