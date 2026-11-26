import asyncio
from typing import Optional

import discord
from discord import app_commands, ui
from discord.ext import commands

import database


_AUTOMOD_SHIELD_LABELS = {
    "anti_invite": "Anti-Invite Links",
    "anti_spam": "Anti-Spam / Flood",
    "anti_mass_mention": "Anti-Mass Mention",
    "anti_word_filter": "Word Blacklist Filter",
    "anti_raid": "Auto Anti-Raid Guard",
}


def _status_badge(enabled: bool) -> str:
    return "🟢 On" if enabled else "🔴 Off"


def _channel_badge(channel_id: Optional[int]) -> str:
    return f"<#{channel_id}>" if channel_id else "`Not Set`"


async def build_settings_dashboard_embed(guild: discord.Guild) -> discord.Embed:
    """Build the unified Server Configuration & Status Dashboard embed from SQLite."""
    (
        gs,
        autoroles,
        starboard,
        verification,
        temp_vc,
        birthdays,
        apps,
        counting,
        bad_words,
        level_roles,
        reaction_roles,
        schedules,
    ) = await asyncio.gather(
        database.get_guild_settings(guild.id),
        database.get_autoroles(guild.id),
        database.get_starboard_settings(guild.id),
        database.get_verification_settings(guild.id),
        database.get_temp_vc_settings(guild.id),
        database.get_birthday_settings(guild.id),
        database.get_application_config(guild.id),
        database.get_counting_settings(guild.id),
        database.get_bad_words(guild.id),
        database.get_level_roles(guild.id),
        database.get_reaction_roles_by_guild(guild.id),
        database.get_guild_scheduled_messages(guild.id),
    )

    shields_text = "\n".join(
        [
            f"• **Anti-Invite:** {_status_badge(bool(gs.get('anti_invite', 1)))}",
            f"• **Anti-Spam:** {_status_badge(bool(gs.get('anti_spam', 1)))}",
            f"• **Mass Mention:** {_status_badge(bool(gs.get('anti_mass_mention', 1)))}",
            f"• **Word Blacklist:** {_status_badge(bool(gs.get('anti_word_filter', 1)))} ({len(bad_words)} words)",
            f"• **Anti-Raid Guard:** {_status_badge(bool(gs.get('anti_raid', 1)))}",
        ]
    )

    starboard_txt = (
        f"<#{starboard['channel_id']}> (⭐ {starboard['threshold']}+)"
        if starboard and starboard.get("is_enabled")
        else "`Disabled`"
    )
    counting_txt = (
        f"<#{counting['channel_id']}> (Streak: **{counting['current_count']}**)"
        if counting
        else "`Disabled`"
    )

    channels_text = "\n".join(
        [
            f"• **Mod Logs:** {_channel_badge(gs.get('mod_log_channel_id'))}",
            f"• **Welcome:** {_channel_badge(gs.get('welcome_channel_id'))}",
            f"• **Leave:** {_channel_badge(gs.get('leave_channel_id'))}",
            f"• **Suggestions:** {_channel_badge(gs.get('suggestion_channel_id'))}",
            f"• **Starboard:** {starboard_txt}",
            f"• **Counting:** {counting_txt}",
        ]
    )

    verify_txt = (
        f"<#{verification['channel_id']}> → <@&{verification['role_id']}>"
        if verification and verification.get("is_enabled")
        else "`Disabled`"
    )
    auto_human = f"<@&{autoroles['member_role_id']}>" if autoroles and autoroles.get("member_role_id") else "`None`"
    auto_bot = f"<@&{autoroles['bot_role_id']}>" if autoroles and autoroles.get("bot_role_id") else "`None`"

    roles_text = "\n".join(
        [
            f"• **Verification Gate:** {verify_txt}",
            f"• **Auto-Role:** Human {auto_human} • Bot {auto_bot}",
            f"• **Level Rewards:** **{len(level_roles)}** milestone(s)",
            f"• **Reaction Roles:** **{len(reaction_roles)}** binding(s)",
        ]
    )

    tickets_txt = "🟢 Configured" if gs.get("ticket_category_id") else "`Not Set`"
    apps_txt = "🟢 Enabled" if apps and apps.get("is_enabled") else "`Disabled`"
    tempvc_txt = f"<#{temp_vc['master_channel_id']}>" if temp_vc and temp_vc.get("is_enabled") else "`Disabled`"
    bday_txt = f"<#{birthdays['channel_id']}>" if birthdays and birthdays.get("is_enabled") else "`Disabled`"
    prem_txt = "💎 **Premium Active**" if gs.get("is_premium") else "🆓 Free Tier"

    modules_text = "\n".join(
        [
            f"• **Support Tickets:** {tickets_txt}",
            f"• **Staff Applications:** {apps_txt}",
            f"• **Temp Voice Channels:** {tempvc_txt}",
            f"• **Birthday Celebrations:** {bday_txt}",
            f"• **Scheduled Announcements:** **{len(schedules)}** active/paused",
            f"• **Subscription:** {prem_txt}",
        ]
    )

    embed = discord.Embed(
        title=f"⚙️ {guild.name} — Server Setup Dashboard",
        description="Use the dropdowns below to toggle AutoMod shields or bind key channels in 1 click.",
        color=0x5865F2,
        timestamp=discord.utils.utcnow(),
    )
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="🛡️ AutoMod Shields", value=shields_text, inline=True)
    embed.add_field(name="📺 Key Channels", value=channels_text, inline=True)
    embed.add_field(name="🎭 Roles & Onboarding", value=roles_text, inline=False)
    embed.add_field(name="🧩 Server Modules & Plan", value=modules_text, inline=False)
    embed.set_footer(text="RookieBot All-in-One Control Panel • Changes save immediately to SQLite")
    return embed


class ShieldToggleSelect(ui.Select):
    """Dropdown allowing admins to toggle any AutoMod shield directly from /settings."""

    def __init__(self):
        options = [
            discord.SelectOption(label=label, value=key, emoji="🛡️")
            for key, label in _AUTOMOD_SHIELD_LABELS.items()
        ]
        super().__init__(
            placeholder="Toggle an AutoMod shield On/Off...",
            min_values=1,
            max_values=1,
            options=options,
            row=0,
        )

    async def callback(self, interaction: discord.Interaction):
        key = self.values[0]
        gs = await database.get_guild_settings(interaction.guild.id)
        new_val = 0 if gs.get(key, 1) else 1
        await database.update_guild_setting(interaction.guild.id, key, new_val)
        embed = await build_settings_dashboard_embed(interaction.guild)
        await interaction.response.edit_message(embed=embed, view=self.view)


class QuickChannelSelect(ui.ChannelSelect):
    """Channel picker that binds a specific guild_settings channel column in 1 click."""

    def __init__(self, setting_key: str, placeholder: str, row: int):
        self.setting_key = setting_key
        super().__init__(
            placeholder=placeholder,
            channel_types=[discord.ChannelType.text],
            min_values=1,
            max_values=1,
            row=row,
        )

    async def callback(self, interaction: discord.Interaction):
        chosen = self.values[0]
        await database.update_guild_setting(interaction.guild.id, self.setting_key, chosen.id)
        embed = await build_settings_dashboard_embed(interaction.guild)
        await interaction.response.edit_message(embed=embed, view=self.view)


class SettingsDashboardView(ui.View):
    """Interactive control panel view for /settings."""

    def __init__(self, author_id: int):
        super().__init__(timeout=300)
        self.author_id = author_id
        self.add_item(ShieldToggleSelect())
        self.add_item(QuickChannelSelect("mod_log_channel_id", "Set Mod-Log Channel...", row=1))
        self.add_item(QuickChannelSelect("welcome_channel_id", "Set Welcome Channel...", row=2))
        self.add_item(QuickChannelSelect("suggestion_channel_id", "Set Suggestions Channel...", row=3))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        perms = getattr(interaction.user, "guild_permissions", None)
        if interaction.user.id != self.author_id and not (perms and (perms.administrator or perms.manage_guild)):
            await interaction.response.send_message(
                "❌ Only administrators with `Manage Server` permission can use this dashboard.",
                ephemeral=True,
            )
            return False
        return True

    @ui.button(label="Enable All AutoMod", style=discord.ButtonStyle.success, emoji="✨", row=4)
    async def enable_all_automod(self, interaction: discord.Interaction, button: ui.Button):
        for key in _AUTOMOD_SHIELD_LABELS:
            await database.update_guild_setting(interaction.guild.id, key, 1)
        embed = await build_settings_dashboard_embed(interaction.guild)
        await interaction.response.edit_message(embed=embed, view=self)

    @ui.button(label="Refresh", style=discord.ButtonStyle.secondary, emoji="🔄", row=4)
    async def refresh_dashboard(self, interaction: discord.Interaction, button: ui.Button):
        embed = await build_settings_dashboard_embed(interaction.guild)
        await interaction.response.edit_message(embed=embed, view=self)


class Settings(commands.Cog):
    """All-in-one interactive server configuration dashboard."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="settings", description="Open the interactive all-in-one server setup dashboard")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_guild=True)
    async def settings(self, interaction: discord.Interaction):
        embed = await build_settings_dashboard_embed(interaction.guild)
        view = SettingsDashboardView(author_id=interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Settings(bot))
