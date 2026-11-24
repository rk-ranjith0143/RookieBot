import discord
from discord import app_commands
from discord.ext import commands
import datetime
from typing import Optional
import database


class Warns(commands.Cog):
    """Formal warning and infraction tracking system with automated punishment escalation."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="warn", description="Issue a formal warning to a member with auto-escalation")
    @app_commands.describe(
        member="The member to warn",
        reason="Reason for the warning",
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.checks.bot_has_permissions(moderate_members=True)
    async def warn(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: Optional[str] = "No reason provided",
    ):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        guild = interaction.guild

        # Hierarchy validations
        if member.id == interaction.user.id:
            await interaction.response.send_message("❌ You cannot warn yourself!", ephemeral=True)
            return
        if self.bot.user and member.id == self.bot.user.id:
            await interaction.response.send_message("❌ You cannot warn the bot!", ephemeral=True)
            return
        if member.id == guild.owner_id:
            await interaction.response.send_message("❌ You cannot warn the server owner!", ephemeral=True)
            return
        if interaction.user.id != guild.owner_id and interaction.user.top_role <= member.top_role:
            await interaction.response.send_message(
                "❌ You cannot warn someone with a role equal to or higher than yours!",
                ephemeral=True,
            )
            return
        if guild.me.top_role <= member.top_role:
            await interaction.response.send_message(
                "❌ I cannot moderate someone with a role equal to or higher than my highest role!",
                ephemeral=True,
            )
            return

        # Store warning in database
        infraction_id = await database.add_infraction(
            guild_id=guild.id,
            user_id=member.id,
            moderator_id=interaction.user.id,
            action_type="warn",
            reason=reason,
        )
        total_warns = await database.get_user_warning_count(guild.id, member.id)

        # Notify member via direct message
        try:
            dm_embed = discord.Embed(
                title=f"⚠️ Warning Received in {guild.name}",
                description=f"You have been formally warned by staff.\n**Reason:** {reason}\n**Total Warnings:** {total_warns}",
                color=discord.Color.yellow(),
                timestamp=discord.utils.utcnow(),
            )
            await member.send(embed=dm_embed)
        except (discord.Forbidden, discord.HTTPException):
            pass

        # Check automated punishment escalation:
        # 3 warns -> 1 hour timeout
        # 5 warns -> kick
        # 7+ warns -> ban
        escalation_notice = None
        try:
            if total_warns >= 7:
                await member.ban(reason=f"Auto-escalation: reached {total_warns} warnings.")
                escalation_notice = "🔨 **Auto-Escalation:** Reached 7 warnings ➔ Member **Banned**!"
            elif total_warns >= 5:
                await member.kick(reason=f"Auto-escalation: reached {total_warns} warnings.")
                escalation_notice = "👢 **Auto-Escalation:** Reached 5 warnings ➔ Member **Kicked**!"
            elif total_warns >= 3:
                delta = datetime.timedelta(hours=1)
                await member.timeout(delta, reason=f"Auto-escalation: reached {total_warns} warnings.")
                escalation_notice = "⏳ **Auto-Escalation:** Reached 3 warnings ➔ Member **Timed Out for 1 hour**!"
        except (discord.Forbidden, discord.HTTPException) as e:
            escalation_notice = f"⚠️ Escalation triggered but failed: `{e}`"

        embed = discord.Embed(
            title="⚠️ Member Warned",
            color=discord.Color.gold(),
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(name="Member", value=f"{member.mention} (`{member}` - `{member.id}`)", inline=False)
        embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
        embed.add_field(name="Total Warnings", value=f"**{total_warns}**", inline=True)
        embed.add_field(name="Infraction ID", value=f"`#{infraction_id}`", inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)

        if escalation_notice:
            embed.add_field(name="Punishment Escalation", value=escalation_notice, inline=False)

        embed.set_thumbnail(url=member.display_avatar.url)
        await interaction.response.send_message(embed=embed)

        # Log to mod log channel if configured
        settings = await database.get_guild_settings(guild.id)
        if settings and settings.get("mod_log_channel_id"):
            log_chan = guild.get_channel(settings["mod_log_channel_id"])
            if isinstance(log_chan, discord.TextChannel):
                try:
                    await log_chan.send(embed=embed)
                except (discord.Forbidden, discord.HTTPException):
                    pass

    @app_commands.command(name="warnings", description="View warning and infraction history for a member")
    @app_commands.describe(member="Member to view infractions for (defaults to yourself)")
    async def warnings(
        self,
        interaction: discord.Interaction,
        member: Optional[discord.Member] = None,
    ):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        target = member or interaction.user
        infractions = await database.get_user_infractions(interaction.guild.id, target.id)

        if not infractions:
            await interaction.response.send_message(
                f"✅ {target.mention} has no recorded warnings or infractions.",
                ephemeral=True,
            )
            return

        lines = []
        for inf in infractions[-15:]:  # Show recent 15
            mod = f"<@{inf['moderator_id']}>"
            time_str = f"<t:{int(inf['created_at'])}:R>" if inf.get("created_at") else "Unknown"
            lines.append(f"• **`#{inf['id']}`** [{inf['action_type'].upper()}] - {time_str} by {mod}\n  └ *Reason:* {inf['reason']}")

        embed = discord.Embed(
            title=f"📋 Infraction History for {target.display_name}",
            description="\n".join(lines),
            color=0x5865F2,
            timestamp=discord.utils.utcnow(),
        )
        embed.set_footer(text=f"Total Infractions: {len(infractions)}")
        embed.set_thumbnail(url=target.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="delwarn", description="Delete an infraction by its numeric ID")
    @app_commands.describe(infraction_id="The numeric ID of the warning to remove")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def delwarn(self, interaction: discord.Interaction, infraction_id: int):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        deleted = await database.delete_infraction(interaction.guild.id, infraction_id)
        if deleted:
            await interaction.response.send_message(f"✅ Infraction `#{infraction_id}` has been deleted.")
        else:
            await interaction.response.send_message(f"❌ Infraction `#{infraction_id}` not found for this server.", ephemeral=True)

    @app_commands.command(name="clearwarns", description="Clear all warnings and infractions for a member")
    @app_commands.describe(member="Member whose warnings should be purged")
    @app_commands.checks.has_permissions(administrator=True)
    async def clearwarns(self, interaction: discord.Interaction, member: discord.Member):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        count = await database.clear_user_infractions(interaction.guild.id, member.id)
        await interaction.response.send_message(f"🧹 Cleared **{count}** warning(s) for {member.mention}.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Warns(bot))
