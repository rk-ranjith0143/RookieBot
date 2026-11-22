import re
from typing import Optional

import discord
from discord import app_commands, ui
from discord.ext import commands


class RoleButton(ui.DynamicItem[ui.Button], template=r"selfrole:role:(?P<role_id>[0-9]+)"):
    """Persistent button that toggles a specific server role on click across bot reboots."""

    def __init__(
        self,
        role_id: int,
        label: str = "Role",
        style: discord.ButtonStyle = discord.ButtonStyle.primary,
    ):
        super().__init__(
            ui.Button(
                label=label,
                style=style,
                custom_id=f"selfrole:role:{role_id}",
            )
        )
        self.role_id = role_id

    @classmethod
    async def from_custom_id(
        cls,
        interaction: discord.Interaction,
        item: ui.Button,
        match: re.Match[str],
    ):
        role_id = int(match.group("role_id"))
        return cls(role_id=role_id, label=item.label or "Role", style=item.style)

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ This action can only be performed inside a server.", ephemeral=True)
            return

        role = guild.get_role(self.role_id)
        if not role:
            await interaction.response.send_message("❌ This role no longer exists in this server.", ephemeral=True)
            return

        member = interaction.user
        if not isinstance(member, discord.Member):
            member = guild.get_member(member.id)

        if not guild.me.guild_permissions.manage_roles:
            await interaction.response.send_message("❌ I do not have `Manage Roles` permission to assign roles.", ephemeral=True)
            return

        if guild.me.top_role <= role:
            await interaction.response.send_message(
                f"❌ I cannot assign {role.mention} because it is equal to or higher than my highest role.",
                ephemeral=True,
            )
            return

        if role in member.roles:
            try:
                await member.remove_roles(role, reason="Self-role button toggle (removed)")
                await interaction.response.send_message(f"➖ Removed {role.mention} from your roles.", ephemeral=True)
            except discord.HTTPException as e:
                await interaction.response.send_message(f"❌ Failed to remove role: `{e}`", ephemeral=True)
        else:
            try:
                await member.add_roles(role, reason="Self-role button toggle (added)")
                await interaction.response.send_message(f"➕ Added {role.mention} to your roles!", ephemeral=True)
            except discord.HTTPException as e:
                await interaction.response.send_message(f"❌ Failed to add role: `{e}`", ephemeral=True)


class Roles(commands.Cog):
    """Self-assignable role panels and role administration."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="rolepanel", description="Create a persistent interactive self-role panel with buttons")
    @app_commands.describe(
        title="Title of the role panel",
        description="Instructions or description for the role panel",
        role1="First self-assignable role",
        role2="Second self-assignable role (optional)",
        role3="Third self-assignable role (optional)",
        role4="Fourth self-assignable role (optional)",
        role5="Fifth self-assignable role (optional)",
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    async def rolepanel(
        self,
        interaction: discord.Interaction,
        title: str,
        role1: discord.Role,
        description: Optional[str] = "Click a button below to get or remove a role!",
        role2: Optional[discord.Role] = None,
        role3: Optional[discord.Role] = None,
        role4: Optional[discord.Role] = None,
        role5: Optional[discord.Role] = None,
    ):
        guild = interaction.guild
        raw_roles = [role1, role2, role3, role4, role5]
        roles = [r for r in raw_roles if r is not None]

        seen_ids = set()
        cleaned_roles = []
        for r in roles:
            if r.id in seen_ids:
                continue
            seen_ids.add(r.id)
            if r.is_default():
                await interaction.response.send_message("❌ You cannot include `@everyone` in a self-role panel.", ephemeral=True)
                return
            if r.managed:
                await interaction.response.send_message(f"❌ `{r.name}` is a bot-managed role and cannot be assigned manually.", ephemeral=True)
                return
            if guild.me.top_role <= r:
                await interaction.response.send_message(
                    f"❌ `{r.name}` is higher than or equal to my highest role. Move my bot role above `{r.name}` in Server Settings > Roles.",
                    ephemeral=True,
                )
                return
            cleaned_roles.append(r)

        view = ui.View(timeout=None)
        button_styles = [
            discord.ButtonStyle.primary,
            discord.ButtonStyle.success,
            discord.ButtonStyle.secondary,
            discord.ButtonStyle.primary,
            discord.ButtonStyle.success,
        ]

        for idx, r in enumerate(cleaned_roles):
            style = button_styles[idx % len(button_styles)]
            view.add_item(RoleButton(role_id=r.id, label=r.name, style=style))

        embed = discord.Embed(
            title=f"🎭 {title}",
            description=description,
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow(),
        )
        role_list = "\n".join(f"• {r.mention}" for r in cleaned_roles)
        embed.add_field(name="Available Roles", value=role_list, inline=False)
        embed.set_footer(text="Click a button to toggle your role!")

        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("✅ Self-role panel created successfully!", ephemeral=True)

    @app_commands.command(name="role", description="Give or remove a role from a member")
    @app_commands.describe(
        member="The member to update",
        role="The role to toggle/assign/remove",
        reason="Reason for updating role",
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    async def role(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        role: discord.Role,
        reason: Optional[str] = "Updated by moderator",
    ):
        guild = interaction.guild

        if role.is_default():
            await interaction.response.send_message("❌ Cannot assign `@everyone`.", ephemeral=True)
            return
        if role.managed:
            await interaction.response.send_message(f"❌ `{role.name}` is managed by an integration/bot and cannot be assigned manually.", ephemeral=True)
            return

        if interaction.user.id != guild.owner_id and interaction.user.top_role <= role:
            await interaction.response.send_message("❌ You cannot manage a role equal to or higher than your highest role!", ephemeral=True)
            return
        if guild.me.top_role <= role:
            await interaction.response.send_message("❌ I cannot manage a role equal to or higher than my highest role!", ephemeral=True)
            return

        audit_reason = f"{interaction.user} (ID: {interaction.user.id}): {reason}"

        if role in member.roles:
            await member.remove_roles(role, reason=audit_reason)
            action_str = f"Removed {role.mention} from {member.mention}."
            color = discord.Color.orange()
        else:
            await member.add_roles(role, reason=audit_reason)
            action_str = f"Added {role.mention} to {member.mention}."
            color = discord.Color.green()

        embed = discord.Embed(
            title="🛡️ Role Updated",
            description=action_str,
            color=color,
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    bot.add_dynamic_items(RoleButton)
    await bot.add_cog(Roles(bot))
