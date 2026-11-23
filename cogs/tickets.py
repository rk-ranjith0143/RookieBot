import asyncio
from typing import Optional

import discord
from discord import app_commands, ui
from discord.ext import commands

from database import get_guild_settings, update_guild_setting


class CloseTicketView(ui.View):
    """Persistent view with a button to close/delete a ticket channel."""

    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(
        label="Close Ticket",
        emoji="🔒",
        style=discord.ButtonStyle.danger,
        custom_id="ticket_close",
    )
    async def close_ticket(self, interaction: discord.Interaction, button: ui.Button):
        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel) or not channel.name.startswith("ticket-"):
            await interaction.response.send_message(
                "❌ This command can only be used inside a ticket channel.",
                ephemeral=True,
            )
            return

        button.disabled = True
        await interaction.response.edit_message(view=self)

        embed = discord.Embed(
            title="🔒 Ticket Closed",
            description=f"Ticket closed by {interaction.user.mention}.\nThis channel will be deleted in **5 seconds**...",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow(),
        )
        await channel.send(embed=embed)
        await asyncio.sleep(5)

        try:
            await channel.delete(reason=f"Ticket closed by {interaction.user}")
        except discord.HTTPException as e:
            await channel.send(f"⚠️ Failed to delete channel: `{e}`")


class TicketLaunchView(ui.View):
    """Persistent view attached to the ticket panel allowing members to create tickets."""

    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(
        label="Open Ticket",
        emoji="📩",
        style=discord.ButtonStyle.primary,
        custom_id="ticket_create",
    )
    async def create_ticket(self, interaction: discord.Interaction, button: ui.Button):
        guild = interaction.guild
        user = interaction.user

        if not guild:
            await interaction.response.send_message("❌ This action can only be performed in a server.", ephemeral=True)
            return

        clean_username = user.name.lower().replace(" ", "-")[:15]
        expected_channel_name = f"ticket-{clean_username}"

        # Prevent duplicate tickets from the same user
        existing = discord.utils.get(guild.text_channels, name=expected_channel_name)
        if existing:
            await interaction.response.send_message(
                f"⚠️ You already have an open ticket in {existing.mention}!",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        settings = await get_guild_settings(guild.id)
        cat_id = settings.get("ticket_category_id")
        category = guild.get_channel(cat_id) if cat_id else None

        # Fallback: find or create a 'Tickets' category
        if not category or not isinstance(category, discord.CategoryChannel):
            category = discord.utils.get(guild.categories, name="Tickets")
            if not category and guild.me.guild_permissions.manage_channels:
                try:
                    category = await guild.create_category("Tickets")
                    await update_guild_setting(guild.id, "ticket_category_id", category.id)
                except discord.HTTPException:
                    category = None

        # Permission overwrites for private ticket channel
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                attach_files=True,
                embed_links=True,
            ),
            guild.me: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                manage_channels=True,
                manage_messages=True,
            ),
        }

        # Grant access to staff/support role if configured
        role_id = settings.get("ticket_support_role_id")
        if role_id:
            support_role = guild.get_role(role_id)
            if support_role:
                overwrites[support_role] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    attach_files=True,
                )

        try:
            ticket_channel = await guild.create_text_channel(
                name=expected_channel_name,
                category=category,
                overwrites=overwrites,
                topic=f"Support ticket for {user} (ID: {user.id})",
                reason=f"Ticket opened by {user}",
            )
        except discord.HTTPException as e:
            await interaction.followup.send(
                f"❌ Failed to create ticket channel: `{e}`. Make sure my bot role has `Manage Channels` permission.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title="📩 Support Ticket Opened",
            description=(
                f"Welcome {user.mention}!\n\n"
                "Please describe your question or issue in detail. A staff member will be with you shortly.\n\n"
                "When you are finished, click the **Close Ticket** button below."
            ),
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f"Ticket ID: #{ticket_channel.id}")

        await ticket_channel.send(
            content=f"{user.mention} Support staff has been notified.",
            embed=embed,
            view=CloseTicketView(),
        )

        await interaction.followup.send(
            f"✅ Ticket created! Head over to {ticket_channel.mention}.",
            ephemeral=True,
        )


class Tickets(commands.Cog):
    """Interactive ticket creation and support management."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ticketsetup", description="Deploy an interactive support ticket panel")
    @app_commands.describe(
        channel="Channel to post the ticket panel in (defaults to current)",
        category="Category channel to organize new tickets under",
        support_role="Staff/Support role that should receive access to all tickets",
        title="Title of the ticket embed",
        description="Description explaining how to open a ticket",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.checks.bot_has_permissions(manage_channels=True)
    async def ticketsetup(
        self,
        interaction: discord.Interaction,
        channel: Optional[discord.TextChannel] = None,
        category: Optional[discord.CategoryChannel] = None,
        support_role: Optional[discord.Role] = None,
        title: str = "Need Help? Open a Support Ticket",
        description: str = "Click the button below to start a private conversation with our support team.",
    ):
        target_channel = channel or interaction.channel
        guild = interaction.guild

        if not guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        # Save settings
        if category:
            await update_guild_setting(guild.id, "ticket_category_id", category.id)
        if support_role:
            await update_guild_setting(guild.id, "ticket_support_role_id", support_role.id)

        embed = discord.Embed(
            title=f"📩 {title}",
            description=description,
            color=discord.Color.blurple(),
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(
            name="🔒 Privacy Guaranteed",
            value="Each ticket creates a private text channel accessible only to you and staff members.",
            inline=False,
        )
        embed.set_footer(text=guild.name, icon_url=guild.icon.url if guild.icon else None)

        view = TicketLaunchView()
        await target_channel.send(embed=embed, view=view)
        await interaction.response.send_message(
            f"✅ Ticket panel successfully deployed to {target_channel.mention}!",
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    bot.add_view(TicketLaunchView())
    bot.add_view(CloseTicketView())
    await bot.add_cog(Tickets(bot))
