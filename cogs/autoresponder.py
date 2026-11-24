import discord
from discord import app_commands
from discord.ext import commands
import database


class AutoResponder(commands.Cog):
    """Custom keyword triggers that automatically reply with canned text, links, or guides."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    ar_group = app_commands.Group(
        name="autoresponder",
        description="Configure automatic keyword trigger responses",
        default_permissions=discord.Permissions(manage_guild=True),
    )

    @ar_group.command(name="add", description="Add an automated keyword trigger response")
    @app_commands.describe(
        trigger="Word or phrase that triggers the response",
        response="Message content the bot will automatically reply with",
        match_type="Whether the message must match exactly or simply contain the trigger",
    )
    @app_commands.choices(
        match_type=[
            app_commands.Choice(name="Contains (Substring)", value="contains"),
            app_commands.Choice(name="Exact Match Only", value="exact"),
        ]
    )
    async def ar_add(
        self,
        interaction: discord.Interaction,
        trigger: str,
        response: str,
        match_type: app_commands.Choice[str],
    ):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        clean_trigger = trigger.strip().lower()
        if len(clean_trigger) < 2 or len(clean_trigger) > 64:
            await interaction.response.send_message("Trigger must be between 2 and 64 characters.", ephemeral=True)
            return

        is_exact = 1 if match_type.value == "exact" else 0
        responder_id = await database.add_autoresponder(
            guild_id=interaction.guild.id,
            trigger=clean_trigger,
            response=response.strip()[:1000],
            is_exact=is_exact,
        )

        embed = discord.Embed(
            title="⚡ Auto-Responder Created",
            description=(
                f"• **ID:** `#{responder_id}`\n"
                f"• **Trigger:** `{clean_trigger}`\n"
                f"• **Match Type:** `{match_type.name}`\n"
                f"• **Response:** {response.strip()[:150]}"
            ),
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed)

    @ar_group.command(name="list", description="List all active auto-responders in this server")
    async def ar_list(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        responders = await database.get_autoresponders(interaction.guild.id)
        if not responders:
            await interaction.response.send_message("ℹ️ No auto-responders created yet. Use `/autoresponder add`.", ephemeral=True)
            return

        lines = []
        for r in responders[:25]:
            m_type = "Exact" if r["is_exact"] else "Contains"
            lines.append(f"• **#{r['id']}** `[{m_type}]` Trigger: `{r['trigger_phrase']}` ➔ *{r['response_text'][:40]}...*")

        embed = discord.Embed(
            title=f"⚡ Server Auto-Responders ({len(responders)})",
            description="\n".join(lines),
            color=0x5865F2,
        )
        await interaction.response.send_message(embed=embed)

    @ar_group.command(name="delete", description="Delete an auto-responder by its ID")
    @app_commands.describe(responder_id="The numeric ID of the auto-responder to delete")
    async def ar_delete(self, interaction: discord.Interaction, responder_id: int):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        deleted = await database.delete_autoresponder(interaction.guild.id, responder_id)
        if deleted:
            await interaction.response.send_message(f"✅ Auto-responder `#{responder_id}` has been deleted.", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Auto-responder `#{responder_id}` was not found in this server.", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild or not message.content:
            return

        content_lower = message.content.strip().lower()
        responders = await database.get_autoresponders(message.guild.id)
        if not responders:
            return

        for r in responders:
            trigger = r["trigger_phrase"]
            is_match = (content_lower == trigger) if r["is_exact"] else (trigger in content_lower)
            if is_match:
                try:
                    await message.channel.send(r["response_text"])
                except discord.Forbidden:
                    pass
                break


async def setup(bot: commands.Bot):
    await bot.add_cog(AutoResponder(bot))
