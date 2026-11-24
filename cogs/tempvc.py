import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
import database


class TempVC(commands.Cog):
    """Dynamic Join-to-Create temporary voice channels with member management controls."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    tempvc_group = app_commands.Group(
        name="tempvc",
        description="Configure join-to-create temporary voice channels",
        default_permissions=discord.Permissions(manage_channels=True),
    )

    vc_group = app_commands.Group(
        name="vc",
        description="Manage your active temporary voice channel",
    )

    # -----------------------------------------------------------------------
    # Admin Setup Commands
    # -----------------------------------------------------------------------

    @tempvc_group.command(name="setup", description="Deploy a master join-to-create voice channel")
    @app_commands.describe(
        category="Category to place the master voice channel and generated channels",
        channel_name="Name for the generator channel (defaults to '➕ Join to Create')",
    )
    async def tempvc_setup(
        self,
        interaction: discord.Interaction,
        category: Optional[discord.CategoryChannel] = None,
        channel_name: Optional[str] = "➕ Join to Create",
    ):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        guild = interaction.guild
        bot_member = guild.get_member(self.bot.user.id) if self.bot.user else guild.me
        if not bot_member.guild_permissions.manage_channels:
            await interaction.response.send_message(
                "❌ I need the `Manage Channels` permission to create and delete temporary voice channels.",
                ephemeral=True,
            )
            return

        master_vc = await guild.create_voice_channel(
            name=channel_name or "➕ Join to Create",
            category=category,
            user_limit=1,
            reason=f"Temp VC generator channel created by {interaction.user}",
        )

        cat_id = category.id if category else None
        await database.set_temp_vc_settings(guild.id, master_vc.id, cat_id)

        embed = discord.Embed(
            title="🔊 Temp VC Generator Configured",
            description=(
                f"• **Generator Channel:** {master_vc.mention}\n"
                f"• **Category:** {category.name if category else '*(None)*'}\n\n"
                f"When members connect to {master_vc.mention}, a private temporary voice channel will automatically be generated for them!"
            ),
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed)

    @tempvc_group.command(name="status", description="Inspect current Temp VC settings for this server")
    async def tempvc_status(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        cfg = await database.get_temp_vc_settings(interaction.guild.id)
        if not cfg or not cfg.get("is_enabled"):
            await interaction.response.send_message(
                "ℹ️ Join-to-Create voice channels are currently **disabled** or not configured. Use `/tempvc setup`.",
                ephemeral=True,
            )
            return

        channel = interaction.guild.get_channel(cfg["master_channel_id"])
        category = interaction.guild.get_channel(cfg["category_id"]) if cfg.get("category_id") else None

        embed = discord.Embed(
            title="🔊 Join-to-Create Status",
            color=0x5865F2,
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(name="Status", value="🟢 **Active**", inline=True)
        embed.add_field(name="Generator Channel", value=channel.mention if channel else f"`{cfg['master_channel_id']}`", inline=True)
        embed.add_field(name="Category", value=category.name if category else "*(Default)*", inline=True)

        await interaction.response.send_message(embed=embed)

    @tempvc_group.command(name="remove", description="Disable join-to-create temporary voice channels")
    async def tempvc_remove(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        disabled = await database.disable_temp_vc(interaction.guild.id)
        if disabled:
            await interaction.response.send_message("✅ Join-to-create Temp VCs have been disabled for this server.", ephemeral=True)
        else:
            await interaction.response.send_message("ℹ️ Temp VCs were not configured.", ephemeral=True)

    # -----------------------------------------------------------------------
    # Channel Owner Controls
    # -----------------------------------------------------------------------

    async def _verify_vc_owner(self, interaction: discord.Interaction) -> Optional[discord.VoiceChannel]:
        """Helper to ensure the caller is currently in a temporary voice channel they own."""
        if not interaction.user or not getattr(interaction.user, "voice", None) or not interaction.user.voice.channel:
            await interaction.response.send_message("❌ You must be connected to your voice channel to use this command.", ephemeral=True)
            return None

        vc = interaction.user.voice.channel
        temp_data = await database.get_temp_channel(vc.id)
        if not temp_data or temp_data.get("owner_id") != interaction.user.id:
            await interaction.response.send_message("❌ You are not the owner of this temporary voice channel.", ephemeral=True)
            return None

        return vc

    @vc_group.command(name="lock", description="Lock your temporary voice channel to prevent new members from joining")
    async def vc_lock(self, interaction: discord.Interaction):
        vc = await self._verify_vc_owner(interaction)
        if not vc:
            return

        overwrites = vc.overwrites_for(interaction.guild.default_role)
        overwrites.connect = False
        await vc.set_permissions(interaction.guild.default_role, overwrite=overwrites, reason=f"Channel locked by owner {interaction.user}")

        await interaction.response.send_message("🔒 Your voice channel has been **locked**. Regular members cannot connect.", ephemeral=True)

    @vc_group.command(name="unlock", description="Unlock your temporary voice channel to allow members to join")
    async def vc_unlock(self, interaction: discord.Interaction):
        vc = await self._verify_vc_owner(interaction)
        if not vc:
            return

        overwrites = vc.overwrites_for(interaction.guild.default_role)
        overwrites.connect = None
        await vc.set_permissions(interaction.guild.default_role, overwrite=overwrites, reason=f"Channel unlocked by owner {interaction.user}")

        await interaction.response.send_message("🔓 Your voice channel has been **unlocked**. Members can now connect.", ephemeral=True)

    @vc_group.command(name="limit", description="Set a member limit for your temporary voice channel")
    @app_commands.describe(limit="Maximum number of users allowed in the channel (0 for unlimited)")
    async def vc_limit(self, interaction: discord.Interaction, limit: app_commands.Range[int, 0, 99]):
        vc = await self._verify_vc_owner(interaction)
        if not vc:
            return

        await vc.edit(user_limit=limit)
        limit_str = "Unlimited" if limit == 0 else str(limit)
        await interaction.response.send_message(f"👥 Voice channel capacity set to **{limit_str}**.", ephemeral=True)

    @vc_group.command(name="name", description="Rename your temporary voice channel")
    @app_commands.describe(new_name="New name for your voice channel (max 32 characters)")
    async def vc_name(self, interaction: discord.Interaction, new_name: str):
        vc = await self._verify_vc_owner(interaction)
        if not vc:
            return

        clean_name = new_name.strip()[:32]
        if not clean_name:
            await interaction.response.send_message("❌ Channel name cannot be empty.", ephemeral=True)
            return

        await vc.edit(name=clean_name)
        await interaction.response.send_message(f"📝 Voice channel renamed to **{clean_name}**.", ephemeral=True)

    # -----------------------------------------------------------------------
    # Voice State Listener
    # -----------------------------------------------------------------------

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if member.bot or not member.guild:
            return

        guild = member.guild

        # 1. User joins generator channel -> create private channel and move member
        if after.channel is not None and (before.channel is None or before.channel.id != after.channel.id):
            cfg = await database.get_temp_vc_settings(guild.id)
            if cfg and cfg.get("is_enabled") and after.channel.id == cfg.get("master_channel_id"):
                category = after.channel.category
                target_category = category if category else (guild.get_channel(cfg.get("category_id")) if cfg.get("category_id") else None)

                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(connect=True),
                    member: discord.PermissionOverwrite(manage_channels=True, move_members=True, connect=True),
                }

                try:
                    new_vc = await guild.create_voice_channel(
                        name=f"🔊 {member.display_name}'s VC",
                        category=target_category,
                        overwrites=overwrites,
                        reason=f"Join-to-Create temp VC generated for {member}",
                    )
                    await database.add_temp_channel(new_vc.id, guild.id, member.id)
                    await member.move_to(new_vc, reason="Moved to new Temp VC")
                except (discord.Forbidden, discord.HTTPException):
                    pass

        # 2. User leaves a temporary channel -> if empty, delete channel
        if before.channel is not None and (after.channel is None or before.channel.id != after.channel.id):
            temp_record = await database.get_temp_channel(before.channel.id)
            if temp_record:
                # If channel is empty
                if len(before.channel.members) == 0:
                    await database.delete_temp_channel(before.channel.id)
                    try:
                        await before.channel.delete(reason="Temporary voice channel empty")
                    except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                        pass


async def setup(bot: commands.Bot):
    await bot.add_cog(TempVC(bot))
