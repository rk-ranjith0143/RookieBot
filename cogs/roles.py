import re
import secrets
import time
from typing import List, Optional

import discord
from discord import app_commands, ui
from discord.ext import commands, tasks

import database
from cogs.reminders import parse_time_string


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

        if not (guild.me.guild_permissions.manage_roles or guild.me.guild_permissions.administrator):
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


class RoleMenuSelect(ui.DynamicItem[ui.Select], template=r"selfrolemenu:(?P<exclusive>[01]):(?P<menu_id>[a-zA-Z0-9]+)"):
    """Persistent dropdown select menu supporting multi-toggle or exclusive single-choice roles."""

    def __init__(
        self,
        options: List[discord.SelectOption],
        exclusive: bool = False,
        menu_id: Optional[str] = None,
        select_item: Optional[ui.Select] = None,
    ):
        self.exclusive = exclusive
        self.menu_id = menu_id or secrets.token_hex(4)

        if select_item is not None:
            super().__init__(select_item)
        else:
            max_vals = 1 if exclusive else max(1, len(options))
            placeholder = "Choose 1 role (Exclusive)..." if exclusive else "Select role(s) to add or remove..."
            super().__init__(
                ui.Select(
                    placeholder=placeholder,
                    min_values=1,
                    max_values=max_vals,
                    options=options,
                    custom_id=f"selfrolemenu:{1 if exclusive else 0}:{self.menu_id}",
                )
            )

    @classmethod
    async def from_custom_id(
        cls,
        interaction: discord.Interaction,
        item: ui.Select,
        match: re.Match[str],
    ):
        exclusive = match.group("exclusive") == "1"
        menu_id = match.group("menu_id")
        return cls(options=list(item.options), exclusive=exclusive, menu_id=menu_id, select_item=item)

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ This action can only be performed inside a server.", ephemeral=True)
            return

        member = interaction.user
        if not isinstance(member, discord.Member):
            member = guild.get_member(member.id)

        if not (guild.me.guild_permissions.manage_roles or guild.me.guild_permissions.administrator):
            await interaction.response.send_message("❌ I do not have `Manage Roles` permission to assign roles.", ephemeral=True)
            return

        selected_ids = [int(v) for v in self.item.values if v.isdigit()]
        menu_role_ids = [int(opt.value) for opt in self.item.options if opt.value.isdigit()]

        if self.exclusive and selected_ids:
            chosen_role = guild.get_role(selected_ids[0])
            if not chosen_role:
                await interaction.response.send_message("❌ That role no longer exists.", ephemeral=True)
                return
            if guild.me.top_role <= chosen_role:
                await interaction.response.send_message(
                    f"❌ I cannot assign {chosen_role.mention} because it is equal to or higher than my highest role.",
                    ephemeral=True,
                )
                return

            other_roles = [
                r for r in member.roles
                if r.id in menu_role_ids and r.id != chosen_role.id and guild.me.top_role > r
            ]
            try:
                if chosen_role in member.roles and not other_roles:
                    await member.remove_roles(chosen_role, reason="Exclusive self-role dropdown toggle")
                    await interaction.response.send_message(f"➖ Removed {chosen_role.mention} from your roles.", ephemeral=True)
                else:
                    if other_roles:
                        await member.remove_roles(*other_roles, reason="Exclusive self-role dropdown switch")
                    if chosen_role not in member.roles:
                        await member.add_roles(chosen_role, reason="Exclusive self-role dropdown selection")
                    swapped = f" (removed {', '.join(r.mention for r in other_roles)})" if other_roles else ""
                    await interaction.response.send_message(
                        f"🎨 Updated! You now have {chosen_role.mention}{swapped}.",
                        ephemeral=True,
                    )
            except discord.HTTPException as e:
                await interaction.response.send_message(f"❌ Failed to update roles: `{e}`", ephemeral=True)
            return

        # Multi-select toggle mode
        added: List[discord.Role] = []
        removed: List[discord.Role] = []
        skipped: List[str] = []

        for rid in selected_ids:
            role = guild.get_role(rid)
            if not role:
                continue
            if guild.me.top_role <= role:
                skipped.append(role.name)
                continue
            if role in member.roles:
                removed.append(role)
            else:
                added.append(role)

        try:
            if added:
                await member.add_roles(*added, reason="Self-role dropdown toggle (added)")
            if removed:
                await member.remove_roles(*removed, reason="Self-role dropdown toggle (removed)")
        except discord.HTTPException as e:
            await interaction.response.send_message(f"❌ Failed to update roles: `{e}`", ephemeral=True)
            return

        parts = []
        if added:
            parts.append(f"➕ **Added:** {', '.join(r.mention for r in added)}")
        if removed:
            parts.append(f"➖ **Removed:** {', '.join(r.mention for r in removed)}")
        if skipped:
            parts.append(f"⚠️ **Skipped (hierarchy):** {', '.join(skipped)}")

        await interaction.response.send_message("\n".join(parts) or "ℹ️ No roles changed.", ephemeral=True)


class Roles(commands.Cog):
    """Self-assignable role panels, dropdown menus, and role administration."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def cog_unload(self):
        if self.temprole_loop.is_running():
            self.temprole_loop.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.temprole_loop.is_running():
            self.temprole_loop.start()

    @tasks.loop(seconds=30.0)
    async def temprole_loop(self):
        """Poll SQLite for expired temporary role grants and remove them automatically."""
        due = await database.get_due_timed_actions(time.time(), action_type="temprole")
        for item in due:
            guild = self.bot.get_guild(item["guild_id"])
            await database.delete_timed_action(item["id"])
            if not guild or not item.get("role_id"):
                continue
            member = guild.get_member(item["user_id"])
            role = guild.get_role(item["role_id"])
            if member and role and role in member.roles and guild.me and guild.me.top_role > role:
                try:
                    await member.remove_roles(role, reason="Temporary role expired automatically")
                except (discord.Forbidden, discord.HTTPException):
                    pass

    @temprole_loop.before_loop
    async def before_temprole_loop(self):
        await self.bot.wait_until_ready()

    async def _validate_self_roles(
        self,
        interaction: discord.Interaction,
        raw_roles: List[Optional[discord.Role]],
    ) -> Optional[List[discord.Role]]:
        """Deduplicate and verify self-assignable roles against bot permissions & hierarchy."""
        guild = interaction.guild
        seen_ids = set()
        cleaned_roles: List[discord.Role] = []

        for r in raw_roles:
            if r is None or r.id in seen_ids:
                continue
            seen_ids.add(r.id)
            if r.is_default():
                await interaction.response.send_message("❌ You cannot include `@everyone` in a self-role panel.", ephemeral=True)
                return None
            if r.managed:
                await interaction.response.send_message(f"❌ `{r.name}` is a bot-managed role and cannot be assigned manually.", ephemeral=True)
                return None
            if guild.me.top_role <= r:
                await interaction.response.send_message(
                    f"❌ `{r.name}` is higher than or equal to my highest role. Move my bot role above `{r.name}` in Server Settings > Roles.",
                    ephemeral=True,
                )
                return None
            cleaned_roles.append(r)

        return cleaned_roles

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
        cleaned_roles = await self._validate_self_roles(interaction, [role1, role2, role3, role4, role5])
        if cleaned_roles is None:
            return

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

    @app_commands.command(name="rolemenu", description="Create a persistent dropdown role menu (up to 10 roles, optional exclusive mode)")
    @app_commands.describe(
        title="Title of the dropdown role menu",
        role1="First role option",
        description="Instructions shown on the role menu card",
        exclusive="If True, picking 1 role removes the others (ideal for color or team roles)",
        role2="Second role option (optional)",
        role3="Third role option (optional)",
        role4="Fourth role option (optional)",
        role5="Fifth role option (optional)",
        role6="Sixth role option (optional)",
        role7="Seventh role option (optional)",
        role8="Eighth role option (optional)",
        role9="Ninth role option (optional)",
        role10="Tenth role option (optional)",
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    async def rolemenu(
        self,
        interaction: discord.Interaction,
        title: str,
        role1: discord.Role,
        description: Optional[str] = "Select a role from the dropdown menu below!",
        exclusive: bool = False,
        role2: Optional[discord.Role] = None,
        role3: Optional[discord.Role] = None,
        role4: Optional[discord.Role] = None,
        role5: Optional[discord.Role] = None,
        role6: Optional[discord.Role] = None,
        role7: Optional[discord.Role] = None,
        role8: Optional[discord.Role] = None,
        role9: Optional[discord.Role] = None,
        role10: Optional[discord.Role] = None,
    ):
        cleaned_roles = await self._validate_self_roles(
            interaction,
            [role1, role2, role3, role4, role5, role6, role7, role8, role9, role10],
        )
        if cleaned_roles is None:
            return

        options = [
            discord.SelectOption(
                label=r.name[:100],
                value=str(r.id),
                emoji="🎨" if exclusive else "🏷️",
            )
            for r in cleaned_roles
        ]

        view = ui.View(timeout=None)
        view.add_item(RoleMenuSelect(options=options, exclusive=exclusive))

        mode_text = "Single Choice (Exclusive)" if exclusive else "Multi-Select Toggle"
        embed = discord.Embed(
            title=f"🎨 {title}" if exclusive else f"🎭 {title}",
            description=description,
            color=discord.Color.purple() if exclusive else discord.Color.blue(),
            timestamp=discord.utils.utcnow(),
        )
        role_list = "\n".join(f"• {r.mention}" for r in cleaned_roles)
        embed.add_field(name="Available Roles", value=role_list, inline=False)
        embed.set_footer(text=f"Mode: {mode_text} • Select from the menu below")

        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("✅ Dropdown role menu created successfully!", ephemeral=True)

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

    @app_commands.command(name="temprole", description="Temporarily assign a role to a member that auto-removes when expired")
    @app_commands.describe(
        member="The member to assign the temporary role to",
        role="The role to assign temporarily",
        duration="Duration before automatic removal (e.g. 30m, 6h, 7d)",
        reason="Reason for temporary role assignment",
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    async def temprole(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        role: discord.Role,
        duration: str,
        reason: Optional[str] = "Temporary role assignment",
    ):
        guild = interaction.guild
        duration_sec = parse_time_string(duration)
        if duration_sec <= 0 or duration_sec > 86400 * 365:
            await interaction.response.send_message(
                "❌ Invalid duration! Use a number followed by `s`, `m`, `h`, or `d` (max `365d`, e.g., `6h`, `7d`).",
                ephemeral=True,
            )
            return

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

        expires_at = time.time() + duration_sec
        await member.add_roles(role, reason=f"Temp-role by {interaction.user} for {duration}: {reason}")
        await database.add_timed_action(
            guild_id=guild.id,
            user_id=member.id,
            action_type="temprole",
            expires_at=expires_at,
            role_id=role.id,
            moderator_id=interaction.user.id,
            reason=reason or "Temporary role assignment",
        )

        embed = discord.Embed(
            title="⏳ Temporary Role Assigned",
            description=f"Granted {role.mention} to {member.mention} for `{duration}`.",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(name="Expires", value=f"<t:{int(expires_at)}:R> (<t:{int(expires_at)}:f>)", inline=True)
        embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    bot.add_dynamic_items(RoleButton, RoleMenuSelect)
    await bot.add_cog(Roles(bot))
