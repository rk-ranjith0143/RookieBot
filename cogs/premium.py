import os
import datetime
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands, tasks

import database

# Configurable Checkout / Payment store URL & pricing label
DEFAULT_STORE_URL = "https://discord.com/application-directory"
STORE_URL = os.getenv("PREMIUM_STORE_URL", DEFAULT_STORE_URL)
PREMIUM_PRICE_LABEL = os.getenv("PREMIUM_PRICE_LABEL", "$1/mo")


class RedeemKeyModal(discord.ui.Modal, title="Redeem Premium License Key"):
    """Interactive modal allowing server owners to paste their license key."""

    key_input = discord.ui.TextInput(
        label="License Key",
        placeholder="PREM-XXXX-XXXX-XXXX",
        min_length=10,
        max_length=32,
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        success, msg, new_exp = await database.redeem_premium_key(
            key_code=self.key_input.value,
            guild_id=interaction.guild.id,
            user_id=interaction.user.id,
        )

        if not success:
            await interaction.response.send_message(msg, ephemeral=True)
            return

        if new_exp:
            exp_date = datetime.datetime.fromtimestamp(new_exp, tz=datetime.timezone.utc)
            exp_str = exp_date.strftime("%B %d, %Y (%H:%M UTC)")
        else:
            exp_str = "Lifetime / Never Expires"

        embed = discord.Embed(
            title="🎉 Premium Activated!",
            description=(
                f"**{interaction.guild.name}** now has full access to all **⭐ Premium Perks**!\n\n"
                f"• **Expiration Date:** `{exp_str}`\n"
                f"• **Redeemed By:** {interaction.user.mention}\n\n"
                f"Thank you for supporting the bot! Use `/premium` anytime to check your perks."
            ),
            color=0xFFD700,
            timestamp=discord.utils.utcnow(),
        )
        await interaction.response.send_message(embed=embed)


class PremiumUpgradeView(discord.ui.View):
    """Interactive buttons for purchasing subscription or redeeming license keys."""

    def __init__(self, store_url: str = STORE_URL):
        super().__init__(timeout=None)
        # Add dynamic link button for direct checkout
        self.add_item(
            discord.ui.Button(
                label="💳 Buy Subscription",
                style=discord.ButtonStyle.link,
                url=store_url,
                emoji="🛒",
            )
        )

    @discord.ui.button(
        label="🔑 Redeem License Key",
        style=discord.ButtonStyle.success,
        custom_id="premium_btn_redeem",
    )
    async def redeem_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RedeemKeyModal())


class Premium(commands.Cog):
    """Monetization engine, subscription tier management, and license key validation."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def cog_unload(self):
        if self.check_expirations_loop.is_running():
            self.check_expirations_loop.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.check_expirations_loop.is_running():
            self.check_expirations_loop.start()

    @tasks.loop(hours=6.0)
    async def check_expirations_loop(self):
        """Periodically audit active subscriptions and expire overdue guilds."""
        expired = await database.check_and_expire_premium_guilds()
        if expired:
            print(f"ℹ️ Automatically expired {len(expired)} guild subscription(s).")

    @check_expirations_loop.before_loop
    async def before_check_expirations(self):
        await self.bot.wait_until_ready()

    # -----------------------------------------------------------------------
    # Public Commands
    # -----------------------------------------------------------------------

    @app_commands.command(
        name="premium",
        description="View this server's subscription tier, perks, and upgrade options",
    )
    async def premium(self, interaction: discord.Interaction):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        has_discord_sub = any(not e.is_expired() for e in interaction.entitlements)
        details = await database.get_guild_premium_details(guild.id)
        is_sub = has_discord_sub or details["is_premium"]

        if is_sub:
            if details["is_lifetime"]:
                duration_text = "♾️ **Lifetime Subscription**"
            elif details["expires_at"]:
                exp_date = datetime.datetime.fromtimestamp(details["expires_at"], tz=datetime.timezone.utc)
                duration_text = f"📅 Expires on **{exp_date.strftime('%B %d, %Y')}** ({details['days_remaining']} days left)"
            else:
                duration_text = "⭐ Active Discord In-App Subscription"

            embed = discord.Embed(
                title=f"💎 Server Subscription: ⭐ Premium Server",
                description=(
                    f"**{guild.name}** is enjoying all **⭐ Premium Perks**!\n"
                    f"• **Status:** Active\n"
                    f"• **Duration:** {duration_text}\n\n"
                    f"Thank you for supporting continuous development and cloud infrastructure."
                ),
                color=0xFFD700,
                timestamp=discord.utils.utcnow(),
            )
        else:
            embed = discord.Embed(
                title="💎 Server Subscription: Free Tier",
                description=(
                    f"**{guild.name}** is currently on the **Free Tier**.\n"
                    f"Upgrade for just **{PREMIUM_PRICE_LABEL}** *(available for all servers)* to unlock unlimited tags, unlimited sticky notices, all live stats channels, and priority uptime!"
                ),
                color=0x5865F2,
                timestamp=discord.utils.utcnow(),
            )

        embed.add_field(
            name="🆓 Free Tier Limits",
            value=(
                "• All standard Moderation tools (`/kick`, `/ban`, `/timeout`, `/clear`)\n"
                "• Up to **5 Custom Tags** (`/tag`)\n"
                "• **1 Sticky Message** per server (`/sticky`)\n"
                "• **1 Live Stats Channel** (`👥 Total Members`)\n"
                "• Community Suggestions, Polls & Giveaways"
            ),
            inline=False,
        )

        embed.add_field(
            name=f"⭐ Premium Perks ({PREMIUM_PRICE_LABEL})",
            value=(
                "• **Unlimited Custom Tags & Auto-FAQs**\n"
                "• **Unlimited Sticky Notices** across multiple channels\n"
                "• **Full Live Stats Suite** (Total, Humans, Bots, Boosts)\n"
                "• **Priority 99.9% Cloud Uptime & Instant Response**\n"
                "• **Direct Developer Support & White-Label Retainer Access**"
            ),
            inline=False,
        )

        view = PremiumUpgradeView(STORE_URL)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(
        name="redeem",
        description="Redeem a Premium License Key to upgrade this server",
    )
    @app_commands.describe(key="Your license key in format PREM-XXXX-XXXX-XXXX")
    async def redeem_command(self, interaction: discord.Interaction, key: str):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        success, msg, new_exp = await database.redeem_premium_key(
            key_code=key,
            guild_id=interaction.guild.id,
            user_id=interaction.user.id,
        )

        if not success:
            await interaction.response.send_message(msg, ephemeral=True)
            return

        if new_exp:
            exp_date = datetime.datetime.fromtimestamp(new_exp, tz=datetime.timezone.utc)
            exp_str = exp_date.strftime("%B %d, %Y (%H:%M UTC)")
        else:
            exp_str = "Lifetime / Never Expires"

        embed = discord.Embed(
            title="🎉 License Redeemed Successfully!",
            description=(
                f"**{interaction.guild.name}** has been upgraded to **⭐ Premium**!\n\n"
                f"• **Expiration:** `{exp_str}`\n"
                f"• **Redeemed By:** {interaction.user.mention}\n\n"
                f"All feature limits have been lifted. Use `/premium` to view your active status."
            ),
            color=0xFFD700,
            timestamp=discord.utils.utcnow(),
        )
        await interaction.response.send_message(embed=embed)

    # -----------------------------------------------------------------------
    # Owner & Admin License Management Commands
    # -----------------------------------------------------------------------

    license_group = app_commands.Group(
        name="license",
        description="Generate, inspect, and revoke Premium license keys",
        default_permissions=discord.Permissions(administrator=True),
    )

    def _is_authorized_owner(self, interaction: discord.Interaction) -> bool:
        """Check if caller is the bot application owner or matching BOT_OWNER_ID."""
        owner_id_env = os.getenv("BOT_OWNER_ID")
        if owner_id_env and str(interaction.user.id) == owner_id_env.strip():
            return True
        if self.bot.owner_id and interaction.user.id == self.bot.owner_id:
            return True
        if self.bot.owner_ids and interaction.user.id in self.bot.owner_ids:
            return True
        # Allow guild administrator in local testing if no owner configured
        return interaction.user.guild_permissions.administrator

    @license_group.command(name="generate", description="Generate a new Premium license key to sell or assign")
    @app_commands.describe(
        duration_days="Duration in days (e.g. 30, 90, 365, or -1 for lifetime)",
        note="Optional note (e.g. customer name, Stripe payment ID, retainer)",
    )
    async def license_generate(
        self,
        interaction: discord.Interaction,
        duration_days: int = 30,
        note: Optional[str] = None,
    ):
        if not self._is_authorized_owner(interaction):
            await interaction.response.send_message("❌ Only bot administrators can generate license keys.", ephemeral=True)
            return

        key_code = await database.create_premium_key(duration_days=duration_days, note=note)

        duration_label = "Lifetime" if duration_days == -1 else f"{duration_days} Days"
        embed = discord.Embed(
            title="🔑 Premium License Key Generated",
            description=(
                f"A new license key has been generated and is ready to deliver to your client or customer:\n\n"
                f"```text\n{key_code}\n```\n"
                f"• **Duration:** `{duration_label}`\n"
                f"• **Note:** `{note or 'None'}`\n\n"
                f"*The recipient can activate it using `/redeem {key_code}` in their server.*"
            ),
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @license_group.command(name="revoke", description="Revoke Premium tier from a specific server")
    @app_commands.describe(guild_id="The numeric Discord Server ID to downgrade")
    async def license_revoke(self, interaction: discord.Interaction, guild_id: str):
        if not self._is_authorized_owner(interaction):
            await interaction.response.send_message("❌ Only bot administrators can revoke licenses.", ephemeral=True)
            return

        try:
            target_guild_id = int(guild_id.strip())
        except ValueError:
            await interaction.response.send_message("❌ Invalid Server ID format. Must be numeric.", ephemeral=True)
            return

        await database.revoke_guild_premium(target_guild_id)
        await interaction.response.send_message(
            f"✅ Premium tier revoked for Server ID `{target_guild_id}`.",
            ephemeral=True,
        )

    @license_group.command(name="list", description="List recently created license keys and redemption status")
    async def license_list(self, interaction: discord.Interaction):
        if not self._is_authorized_owner(interaction):
            await interaction.response.send_message("❌ Only bot administrators can view license keys.", ephemeral=True)
            return

        keys = await database.list_premium_keys(limit=20)
        if not keys:
            await interaction.response.send_message("ℹ️ No license keys found in database.", ephemeral=True)
            return

        lines = []
        for k in keys:
            status = "🔴 Redeemed" if k["is_redeemed"] else "🟢 Available"
            dur = "Lifetime" if k["duration_days"] == -1 else f"{k['duration_days']}d"
            note_str = f" ({k['note']})" if k.get("note") else ""
            lines.append(f"• `{k['key_code']}` | **{dur}** | {status}{note_str}")

        embed = discord.Embed(
            title=f"🔑 License Keys ({len(keys)})",
            description="\n".join(lines),
            color=0x5865F2,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Premium(bot))
