import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
import database


class AutoRole(commands.Cog):
    """Automatically assigns configured roles to members or bots upon joining the server."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    autorole_group = app_commands.Group(
        name="autorole",
        description="Configure automatic role assignment for incoming members and bots",
        default_permissions=discord.Permissions(manage_roles=True),
    )

    @autorole_group.command(name="set", description="Set default auto-roles for new members and bots")
    @app_commands.describe(
        member_role="Role to automatically assign to new human members",
        bot_role="Role to automatically assign to new bots",
    )
    async def autorole_set(
        self,
        interaction: discord.Interaction,
        member_role: Optional[discord.Role] = None,
        bot_role: Optional[discord.Role] = None,
    ):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        if not member_role and not bot_role:
            await interaction.response.send_message(
                "⚠️ Please specify at least one role (`member_role` or `bot_role`).",
                ephemeral=True,
            )
            return

        # Hierarchy validation
        bot_member = interaction.guild.get_member(self.bot.user.id) if self.bot.user else None
        if bot_member:
            for r in (member_role, bot_role):
                if r and r >= bot_member.top_role:
                    await interaction.response.send_message(
                        f"❌ I cannot assign {r.mention} because it is equal to or higher than my highest role.",
                        ephemeral=True,
                    )
                    return

        mem_id = member_role.id if member_role else None
        b_id = bot_role.id if bot_role else None
        await database.set_autoroles(interaction.guild.id, member_role_id=mem_id, bot_role_id=b_id)

        embed = discord.Embed(
            title="🎭 Auto-Roles Configured",
            description=(
                f"• **Human Members:** {member_role.mention if member_role else '*(Unchanged / None)*'}\n"
                f"• **Bots:** {bot_role.mention if bot_role else '*(Unchanged / None)*'}\n\n"
                f"New joins will automatically receive their assigned role."
            ),
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed)

    @autorole_group.command(name="status", description="View current auto-role configuration for this server")
    async def autorole_status(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        cfg = await database.get_autoroles(interaction.guild.id)
        if not cfg or (not cfg.get("member_role_id") and not cfg.get("bot_role_id")):
            await interaction.response.send_message("ℹ️ No auto-roles are currently configured. Use `/autorole set`.", ephemeral=True)
            return

        mem_role = interaction.guild.get_role(cfg["member_role_id"]) if cfg.get("member_role_id") else None
        bot_role = interaction.guild.get_role(cfg["bot_role_id"]) if cfg.get("bot_role_id") else None

        embed = discord.Embed(
            title="🎭 Auto-Role Status",
            description=(
                f"• **Human Member Role:** {mem_role.mention if mem_role else '`None`'}\n"
                f"• **Bot Role:** {bot_role.mention if bot_role else '`None`'}"
            ),
            color=0x5865F2,
        )
        await interaction.response.send_message(embed=embed)

    @autorole_group.command(name="remove", description="Disable auto-roles for this server")
    async def autorole_remove(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        await database.remove_autoroles(interaction.guild.id)
        await interaction.response.send_message("✅ Auto-roles have been disabled for this server.", ephemeral=True)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if not member.guild:
            return

        cfg = await database.get_autoroles(member.guild.id)
        if not cfg:
            return

        target_role_id = cfg.get("bot_role_id") if member.bot else cfg.get("member_role_id")
        if not target_role_id:
            return

        role = member.guild.get_role(target_role_id)
        if role:
            try:
                await member.add_roles(role, reason="RookieBot Auto-Role on Join")
            except discord.Forbidden:
                pass


async def setup(bot: commands.Bot):
    await bot.add_cog(AutoRole(bot))
