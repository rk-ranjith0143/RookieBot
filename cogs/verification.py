import discord
from discord import app_commands, ui
from discord.ext import commands
from typing import Optional
import database


class VerifyLaunchView(ui.View):
    """Persistent button view for member verification."""

    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(
        label="Verify",
        emoji="✅",
        style=discord.ButtonStyle.success,
        custom_id="verify_member_btn",
    )
    async def verify_button_click(self, interaction: discord.Interaction, button: ui.Button):
        if not interaction.guild:
            await interaction.response.send_message("❌ This button can only be used in a server.", ephemeral=True)
            return

        settings = await database.get_verification_settings(interaction.guild.id)
        if not settings or not settings.get("is_enabled"):
            await interaction.response.send_message(
                "❌ Verification is currently disabled or not configured on this server.",
                ephemeral=True,
            )
            return

        role = interaction.guild.get_role(settings["role_id"])
        if not role:
            await interaction.response.send_message(
                "❌ The verified role is missing or was deleted. Please contact staff.",
                ephemeral=True,
            )
            return

        if role in interaction.user.roles:
            await interaction.response.send_message(
                "ℹ️ You are already verified on this server!",
                ephemeral=True,
            )
            return

        # Hierarchy check
        bot_member = interaction.guild.get_member(interaction.client.user.id) if interaction.client.user else None
        if bot_member and role >= bot_member.top_role:
            await interaction.response.send_message(
                "❌ I cannot assign the verified role because it is equal to or higher than my highest role.",
                ephemeral=True,
            )
            return

        try:
            await interaction.user.add_roles(role, reason="Verification gate button click")
            await interaction.response.send_message(
                f"🎉 **You have been successfully verified!** Welcome to **{interaction.guild.name}**!",
                ephemeral=True,
            )
        except (discord.Forbidden, discord.HTTPException) as e:
            await interaction.response.send_message(
                f"⚠️ Failed to assign role: `{e}`. Please ensure I have `Manage Roles` permission.",
                ephemeral=True,
            )


class Verification(commands.Cog):
    """Verification gate system to protect servers from bots and raids with a 1-click button."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="verifysetup", description="Deploy a persistent 1-click verification panel")
    @app_commands.describe(
        channel="Channel where the verification embed should be sent",
        role="The role granted to members when they click Verify",
        title="Custom title for the verification card",
        description="Custom rules or instructions for the verification card",
    )
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    async def verifysetup(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        role: discord.Role,
        title: Optional[str] = "Server Member Verification",
        description: Optional[str] = "Click the button below to verify your account and unlock access to the server.",
    ):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        bot_member = interaction.guild.get_member(self.bot.user.id) if self.bot.user else None
        if bot_member and role >= bot_member.top_role:
            await interaction.response.send_message(
                f"❌ I cannot assign {role.mention} because it is equal to or higher than my highest role.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title=f"🛡️ {title}",
            description=description,
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(
            name="📜 Community Rules",
            value="By clicking **Verify**, you agree to abide by our server rules and Discord's Terms of Service.",
            inline=False,
        )
        embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon.url if interaction.guild.icon else None)

        view = VerifyLaunchView()
        sent_msg = await channel.send(embed=embed, view=view)

        await database.set_verification_settings(
            guild_id=interaction.guild.id,
            channel_id=channel.id,
            role_id=role.id,
            message_id=sent_msg.id,
        )

        await interaction.response.send_message(
            f"✅ Verification gate successfully deployed to {channel.mention} using role {role.mention}!",
            ephemeral=True,
        )

    @app_commands.command(name="verifystatus", description="View current verification gate configuration")
    async def verifystatus(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        cfg = await database.get_verification_settings(interaction.guild.id)
        if not cfg or not cfg.get("is_enabled"):
            await interaction.response.send_message(
                "ℹ️ Verification is currently **disabled** or not set up. Use `/verifysetup`.",
                ephemeral=True,
            )
            return

        channel = interaction.guild.get_channel(cfg["channel_id"])
        role = interaction.guild.get_role(cfg["role_id"])

        embed = discord.Embed(
            title="🛡️ Verification Gate Status",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(name="Status", value="🟢 **Active**", inline=True)
        embed.add_field(name="Channel", value=channel.mention if channel else f"`{cfg['channel_id']}`", inline=True)
        embed.add_field(name="Role Granted", value=role.mention if role else f"`{cfg['role_id']}`", inline=True)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="verifyremove", description="Disable the verification gate for this server")
    @app_commands.checks.has_permissions(administrator=True)
    async def verifyremove(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        disabled = await database.disable_verification(interaction.guild.id)
        if disabled:
            await interaction.response.send_message("✅ Verification gate has been disabled.", ephemeral=True)
        else:
            await interaction.response.send_message("ℹ️ Verification was not configured.", ephemeral=True)


async def setup(bot: commands.Bot):
    bot.add_view(VerifyLaunchView())
    await bot.add_cog(Verification(bot))
