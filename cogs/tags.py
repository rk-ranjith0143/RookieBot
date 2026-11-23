import discord
from discord import app_commands
from discord.ext import commands
from typing import List
import database


class Tags(commands.Cog):
    """Custom tags and auto-FAQ canned responses system with instant search autocomplete."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    tag_group = app_commands.Group(
        name="tag",
        description="Create, view, and manage custom server tags and FAQ responses",
    )

    async def _tag_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> List[app_commands.Choice[str]]:
        if not interaction.guild:
            return []
        matches = await database.search_tags(interaction.guild.id, current, limit=25)
        return [app_commands.Choice(name=name, value=name) for name in matches]

    @tag_group.command(name="add", description="Create a new custom tag or canned response")
    @app_commands.describe(
        name="Unique short name for the tag (e.g. rules, website, faq)",
        content="The message content or links that the tag will output",
    )
    @app_commands.default_permissions(manage_messages=True)
    async def add_tag(self, interaction: discord.Interaction, name: str, content: str):
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        clean_name = name.lower().strip()
        if len(clean_name) > 32:
            await interaction.response.send_message("Tag name cannot exceed 32 characters.", ephemeral=True)
            return

        success = await database.create_tag(
            guild_id=interaction.guild.id,
            tag_name=clean_name,
            content=content,
            author_id=interaction.user.id,
        )

        if not success:
            await interaction.response.send_message(
                f"❌ A tag named `{clean_name}` already exists. Use `/tag delete` first if you want to replace it.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title="🏷️ Tag Created",
            description=f"Tag `{clean_name}` has been saved!\nUse `/tag get {clean_name}` to call it.",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed)

    @tag_group.command(name="get", description="Send the content of a saved tag")
    @app_commands.describe(name="The name of the tag to display")
    @app_commands.autocomplete(name=_tag_autocomplete)
    async def get_tag_cmd(self, interaction: discord.Interaction, name: str):
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        clean_name = name.lower().strip()
        tag = await database.get_tag(interaction.guild.id, clean_name, increment_uses=True)
        if not tag:
            await interaction.response.send_message(
                f"❌ Tag `{clean_name}` not found in this server.",
                ephemeral=True,
            )
            return

        # Output the tag content cleanly
        await interaction.response.send_message(tag["content"])

    @tag_group.command(name="delete", description="Delete an existing custom tag")
    @app_commands.describe(name="The name of the tag to delete")
    @app_commands.autocomplete(name=_tag_autocomplete)
    @app_commands.default_permissions(manage_messages=True)
    async def delete_tag_cmd(self, interaction: discord.Interaction, name: str):
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        clean_name = name.lower().strip()
        deleted = await database.delete_tag(interaction.guild.id, clean_name)
        if deleted:
            await interaction.response.send_message(
                f"✅ Tag `{clean_name}` was successfully deleted.",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                f"❌ Tag `{clean_name}` does not exist.",
                ephemeral=True,
            )

    @tag_group.command(name="list", description="List all custom tags available in this server")
    async def list_tags_cmd(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        tags = await database.list_tags(interaction.guild.id)
        if not tags:
            await interaction.response.send_message(
                "ℹ️ No custom tags have been created yet. Admins can create one using `/tag add`.",
                ephemeral=True,
            )
            return

        tag_list_str = "\n".join(
            f"• `{t['tag_name']}` — *{t['uses']} uses*" for t in tags[:30]
        )
        if len(tags) > 30:
            tag_list_str += f"\n*...and {len(tags) - 30} more*"

        embed = discord.Embed(
            title=f"🏷️ Server Tags ({len(tags)})",
            description=tag_list_str,
            color=0x5865F2,
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Tags(bot))
