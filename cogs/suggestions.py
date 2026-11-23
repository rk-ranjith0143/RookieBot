import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
import database


class SuggestionVoteView(discord.ui.View):
    """Persistent voting view for community suggestions."""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Upvote (0)",
        style=discord.ButtonStyle.success,
        emoji="👍",
        custom_id="suggestion_btn_upvote",
    )
    async def upvote_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_vote(interaction, 1)

    @discord.ui.button(
        label="Downvote (0)",
        style=discord.ButtonStyle.danger,
        emoji="👎",
        custom_id="suggestion_btn_downvote",
    )
    async def downvote_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_vote(interaction, -1)

    async def _handle_vote(self, interaction: discord.Interaction, vote_type: int):
        if not interaction.message:
            await interaction.response.send_message("Unable to identify suggestion message.", ephemeral=True)
            return

        sug = await database.get_suggestion_by_message(interaction.message.id)
        if not sug:
            await interaction.response.send_message("Suggestion not found in database.", ephemeral=True)
            return

        if sug["status"] != "pending":
            await interaction.response.send_message(
                f"Voting is closed because this suggestion is already **{sug['status'].upper()}**.",
                ephemeral=True,
            )
            return

        has_voted, upvotes, downvotes = await database.vote_suggestion(
            sug["id"], interaction.user.id, vote_type
        )

        # Update button labels on the message
        self.children[0].label = f"Upvote ({upvotes})"
        self.children[1].label = f"Downvote ({downvotes})"

        # Also update the embed votes field
        embeds = interaction.message.embeds
        if embeds:
            embed = embeds[0]
            # Replace votes field if present
            for idx, field in enumerate(embed.fields):
                if field.name == "Votes":
                    embed.set_field_at(
                        idx,
                        name="Votes",
                        value=f"👍 **{upvotes}** • 👎 **{downvotes}** (Score: {upvotes - downvotes})",
                        inline=True,
                    )
                    break
            await interaction.message.edit(embed=embed, view=self)

        action_name = "upvoted" if vote_type == 1 else "downvoted"
        await interaction.response.send_message(
            f"Your vote has been updated! (Current: 👍 {upvotes} | 👎 {downvotes})",
            ephemeral=True,
        )


class Suggestions(commands.Cog):
    """Interactive suggestions system with community upvotes and admin status reviews."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        # Register persistent view so button callbacks survive bot restarts
        self.bot.add_view(SuggestionVoteView())

    @app_commands.command(
        name="setsuggestchannel",
        description="Set the channel where user suggestions will be posted",
    )
    @app_commands.describe(channel="The channel for community suggestions")
    @app_commands.default_permissions(manage_guild=True)
    async def set_suggest_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        await database.update_guild_setting(interaction.guild.id, "suggestion_channel_id", channel.id)
        embed = discord.Embed(
            title="💡 Suggestions Channel Updated",
            description=f"Community suggestions will now be submitted to {channel.mention}.",
            color=0x5865F2,
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="suggest",
        description="Submit a suggestion for the server to review and vote on",
    )
    @app_commands.describe(suggestion="Your idea or proposal for the server")
    async def submit_suggestion(self, interaction: discord.Interaction, suggestion: str):
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        settings = await database.get_guild_settings(interaction.guild.id)
        channel_id = settings.get("suggestion_channel_id")
        if not channel_id:
            await interaction.response.send_message(
                "⚠️ A suggestion channel has not been configured yet. Ask an admin to run `/setsuggestchannel`.",
                ephemeral=True,
            )
            return

        target_channel = interaction.guild.get_channel(channel_id)
        if not isinstance(target_channel, discord.TextChannel):
            await interaction.response.send_message(
                "⚠️ Configured suggestion channel could not be found. Please contact an admin.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title="💡 New Suggestion",
            description=suggestion,
            color=0x5865F2,
            timestamp=discord.utils.utcnow(),
        )
        embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.display_avatar.url,
        )
        embed.add_field(name="Status", value="⏳ **Pending Review**", inline=True)
        embed.add_field(name="Votes", value="👍 **0** • 👎 **0** (Score: 0)", inline=True)
        embed.set_footer(text=f"Submitted by {interaction.user}")

        view = SuggestionVoteView()
        sent_message = await target_channel.send(embed=embed, view=view)

        sug_id = await database.create_suggestion(
            guild_id=interaction.guild.id,
            channel_id=target_channel.id,
            message_id=sent_message.id,
            author_id=interaction.user.id,
            content=suggestion,
        )

        embed.set_footer(text=f"Suggestion #{sug_id} • Submitted by {interaction.user}")
        await sent_message.edit(embed=embed)

        await interaction.response.send_message(
            f"✅ Your suggestion (#{sug_id}) has been submitted to {target_channel.mention}!",
            ephemeral=True,
        )

    @app_commands.command(
        name="suggeststatus",
        description="Approve, deny, or consider a user suggestion",
    )
    @app_commands.describe(
        suggestion_id="The ID of the suggestion to review",
        status="New review status for this suggestion",
        reason="Optional explanation or response note from management",
    )
    @app_commands.choices(
        status=[
            app_commands.Choice(name="Approved", value="approved"),
            app_commands.Choice(name="Denied", value="denied"),
            app_commands.Choice(name="Considered", value="considered"),
        ]
    )
    @app_commands.default_permissions(manage_guild=True)
    async def manage_suggestion(
        self,
        interaction: discord.Interaction,
        suggestion_id: int,
        status: app_commands.Choice[str],
        reason: Optional[str] = None,
    ):
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        sug = await database.get_suggestion(suggestion_id)
        if not sug or sug["guild_id"] != interaction.guild.id:
            await interaction.response.send_message(
                f"❌ Suggestion #{suggestion_id} was not found in this server.",
                ephemeral=True,
            )
            return

        status_value = status.value
        await database.update_suggestion_status(suggestion_id, status_value, reason)

        # Attempt to edit the original message in the suggestion channel
        channel = interaction.guild.get_channel(sug["channel_id"])
        if isinstance(channel, discord.TextChannel):
            try:
                msg = await channel.fetch_message(sug["message_id"])
                if msg.embeds:
                    embed = msg.embeds[0]
                    if status_value == "approved":
                        embed.color = discord.Color.green()
                        status_text = "✅ **Approved**"
                    elif status_value == "denied":
                        embed.color = discord.Color.red()
                        status_text = "❌ **Denied**"
                    else:
                        embed.color = discord.Color.gold()
                        status_text = "🤔 **Under Consideration**"

                    for idx, field in enumerate(embed.fields):
                        if field.name == "Status":
                            embed.set_field_at(idx, name="Status", value=status_text, inline=True)
                            break

                    if reason:
                        embed.add_field(
                            name=f"Admin Note ({interaction.user.display_name})",
                            value=reason,
                            inline=False,
                        )

                    # Disable vote buttons once finalized
                    final_view = None
                    if status_value in ("approved", "denied"):
                        view = SuggestionVoteView()
                        for item in view.children:
                            item.disabled = True
                        final_view = view
                    else:
                        final_view = SuggestionVoteView()

                    await msg.edit(embed=embed, view=final_view)
            except Exception:
                pass

        await interaction.response.send_message(
            f"✅ Suggestion #{suggestion_id} status updated to **{status.name}**.",
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Suggestions(bot))
