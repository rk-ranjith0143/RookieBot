import random
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from database import (
    get_user_balance,
    update_user_balance,
    claim_daily,
    add_shop_item,
    get_shop_items,
    get_shop_item,
    delete_shop_item,
    buy_shop_item,
    get_user_inventory,
    claim_work,
)


class Economy(commands.Cog):
    """Server virtual economy, daily coin rewards, transactions, and mini-games."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="balance", description="Check your coin balance or view another member's wallet")
    @app_commands.describe(member="Member whose balance you want to view (defaults to you)")
    async def balance(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        target = member or interaction.user
        guild = interaction.guild

        if not guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        bal = await get_user_balance(guild.id, target.id)

        embed = discord.Embed(
            title=f"🪙 {target.display_name}'s Wallet",
            color=discord.Color.gold(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="Current Balance", value=f"**{bal:,} Coins**", inline=True)
        embed.set_footer(text="Use /daily to earn free coins every 24 hours!")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="daily", description="Claim your daily coin reward (200 Coins)")
    async def daily(self, interaction: discord.Interaction):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        claimed, new_balance, remaining_sec = await claim_daily(guild.id, interaction.user.id, reward=200)

        if not claimed:
            hours = int(remaining_sec // 3600)
            minutes = int((remaining_sec % 3600) // 60)
            await interaction.response.send_message(
                f"⏳ You have already claimed your daily reward! Please wait **{hours}h {minutes}m** before claiming again.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title="🎁 Daily Reward Claimed!",
            description=(
                f"You claimed your daily reward of **+200 Coins**! 🎉\n\n"
                f"New Balance: **{new_balance:,} Coins**"
            ),
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_footer(text="Come back in 24 hours for your next reward!")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="pay", description="Transfer coins from your wallet to another member")
    @app_commands.describe(
        member="The member you want to send coins to",
        amount="Number of coins to transfer",
    )
    async def pay(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        if amount <= 0:
            await interaction.response.send_message("❌ Amount must be at least 1 Coin.", ephemeral=True)
            return
        if member.id == interaction.user.id:
            await interaction.response.send_message("❌ You cannot send coins to yourself!", ephemeral=True)
            return
        if member.bot:
            await interaction.response.send_message("❌ You cannot transfer coins to a bot.", ephemeral=True)
            return

        sender_balance = await get_user_balance(guild.id, interaction.user.id)
        if sender_balance < amount:
            await interaction.response.send_message(
                f"❌ Insufficient funds! You only have **{sender_balance:,} Coins**.",
                ephemeral=True,
            )
            return

        # Execute transaction
        await update_user_balance(guild.id, interaction.user.id, -amount)
        receiver_new = await update_user_balance(guild.id, member.id, amount)

        embed = discord.Embed(
            title="💸 Payment Successful",
            description=(
                f"{interaction.user.mention} sent **{amount:,} Coins** to {member.mention}!\n\n"
                f"Your New Balance: **{sender_balance - amount:,} Coins**"
            ),
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow(),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="coinflip", description="Gamble coins on a double-or-nothing coin flip")
    @app_commands.describe(
        bet="Amount of coins to wager",
        choice="Heads or Tails",
    )
    @app_commands.choices(
        choice=[
            app_commands.Choice(name="Heads 🪙", value="heads"),
            app_commands.Choice(name="Tails 🪙", value="tails"),
        ]
    )
    async def coinflip(
        self,
        interaction: discord.Interaction,
        bet: int,
        choice: app_commands.Choice[str],
    ):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        if bet <= 0:
            await interaction.response.send_message("❌ Bet must be at least 1 Coin.", ephemeral=True)
            return

        balance = await get_user_balance(guild.id, interaction.user.id)
        if balance < bet:
            await interaction.response.send_message(
                f"❌ You cannot bet more than your balance! You have **{balance:,} Coins**.",
                ephemeral=True,
            )
            return

        flip_result = random.choice(["heads", "tails"])
        won = flip_result == choice.value

        if won:
            new_bal = await update_user_balance(guild.id, interaction.user.id, bet)
            embed = discord.Embed(
                title=f"🪙 Coin Flip — You Won (+{bet:,} Coins)!",
                description=(
                    f"The coin landed on **{flip_result.capitalize()}**! 🎉\n"
                    f"New Balance: **{new_bal:,} Coins**"
                ),
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow(),
            )
        else:
            new_bal = await update_user_balance(guild.id, interaction.user.id, -bet)
            embed = discord.Embed(
                title=f"🪙 Coin Flip — You Lost (-{bet:,} Coins)",
                description=(
                    f"The coin landed on **{flip_result.capitalize()}**. Better luck next time! 😢\n"
                    f"New Balance: **{new_bal:,} Coins**"
                ),
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow(),
            )

        embed.set_footer(text=f"Player: {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

    shop_group = app_commands.Group(
        name="shop",
        description="Browse and manage the server economy item and role shop",
    )

    @shop_group.command(name="view", description="Browse all items available in the server shop")
    async def shop_view(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        items = await get_shop_items(interaction.guild.id)
        if not items:
            await interaction.response.send_message(
                "🏪 The server shop is currently empty! Server admins can add items with `/shop add`.",
                ephemeral=True,
            )
            return

        lines = []
        for itm in items:
            role_text = f" [Grants Role: <@&{itm['role_id']}>]" if itm.get("role_id") else ""
            desc = f" - *{itm['description']}*" if itm.get("description") else ""
            lines.append(f"• **`#{itm['id']}` {itm['item_name']}** — **{itm['price']:,} Coins**{role_text}{desc}")

        embed = discord.Embed(
            title=f"🏪 {interaction.guild.name} Server Shop",
            description="\n".join(lines),
            color=discord.Color.gold(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_footer(text="Use /buy [item_id] to purchase an item!")
        await interaction.response.send_message(embed=embed)

    @shop_group.command(name="add", description="Add an item or role reward to the server shop")
    @app_commands.describe(
        name="Name of the item or role",
        price="Cost in coins (must be greater than 0)",
        description="Optional description or perk details",
        role="Optional Discord role granted to buyers",
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def shop_add(
        self,
        interaction: discord.Interaction,
        name: str,
        price: int,
        description: Optional[str] = "",
        role: Optional[discord.Role] = None,
    ):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        if price <= 0:
            await interaction.response.send_message("❌ Price must be at least 1 Coin.", ephemeral=True)
            return

        bot_member = interaction.guild.get_member(self.bot.user.id) if self.bot.user else interaction.guild.me
        if role and bot_member and role >= bot_member.top_role:
            await interaction.response.send_message(
                f"❌ I cannot list {role.mention} because it is equal to or higher than my highest role.",
                ephemeral=True,
            )
            return

        role_id = role.id if role else None
        item_id = await add_shop_item(
            guild_id=interaction.guild.id,
            item_name=name.strip()[:64],
            price=price,
            description=description.strip()[:200] if description else "",
            role_id=role_id,
        )

        embed = discord.Embed(
            title="🏪 Item Added to Shop",
            description=(
                f"• **Item ID:** `#{item_id}`\n"
                f"• **Name:** {name.strip()[:64]}\n"
                f"• **Price:** **{price:,} Coins**\n"
                f"• **Role Granted:** {role.mention if role else '*(None)*'}\n"
                f"• **Description:** {description or '*(None)*'}"
            ),
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed)

    @shop_group.command(name="remove", description="Remove an item from the server shop")
    @app_commands.describe(item_id="The numeric ID of the item to delete")
    @app_commands.checks.has_permissions(administrator=True)
    async def shop_remove(self, interaction: discord.Interaction, item_id: int):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        deleted = await delete_shop_item(interaction.guild.id, item_id)
        if deleted:
            await interaction.response.send_message(f"✅ Shop item `#{item_id}` has been removed.", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Shop item `#{item_id}` not found.", ephemeral=True)

    @app_commands.command(name="buy", description="Purchase an item from the server shop using your coins")
    @app_commands.describe(item_id="The numeric ID of the item you want to buy")
    async def buy(self, interaction: discord.Interaction, item_id: int):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        success, msg, item = await buy_shop_item(interaction.guild.id, interaction.user.id, item_id)
        if not success:
            await interaction.response.send_message(msg, ephemeral=True)
            return

        role_awarded_text = ""
        if item.get("role_id"):
            role = interaction.guild.get_role(item["role_id"])
            if role:
                try:
                    await interaction.user.add_roles(role, reason=f"Purchased from server shop (ID #{item_id})")
                    role_awarded_text = f"\n🎉 You have been granted the {role.mention} role!"
                except (discord.Forbidden, discord.HTTPException):
                    role_awarded_text = f"\n⚠️ Could not automatically grant {role.mention}. Please contact staff."

        embed = discord.Embed(
            title="🛍️ Purchase Successful!",
            description=f"{msg}{role_awarded_text}",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_footer(text="Check your items anytime with /inventory")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="inventory", description="View your purchased items and perks")
    @app_commands.describe(member="Member whose inventory you want to view (defaults to you)")
    async def inventory(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        target = member or interaction.user
        inv = await get_user_inventory(interaction.guild.id, target.id)

        if not inv:
            await interaction.response.send_message(
                f"🎒 {target.mention}'s inventory is empty. Browse items in `/shop view`!",
                ephemeral=True,
            )
            return

        lines = []
        for entry in inv[:25]:
            time_str = f"<t:{int(entry['purchased_at'])}:d>" if entry.get("purchased_at") else "Unknown"
            role_text = f" [Role: <@&{entry['role_id']}>]" if entry.get("role_id") else ""
            lines.append(f"• **{entry['item_name']}**{role_text} — Purchased {time_str}")

        embed = discord.Embed(
            title=f"🎒 {target.display_name}'s Inventory ({len(inv)} items)",
            description="\n".join(lines),
            color=discord.Color.gold(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="work", description="Work a job shift to earn coins (50 - 150 Coins)")
    async def work(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        claimed, earned, new_balance, remaining_sec = await claim_work(interaction.guild.id, interaction.user.id)
        if not claimed:
            mins = int(remaining_sec // 60)
            secs = int(remaining_sec % 60)
            await interaction.response.send_message(
                f"⏳ You are tired from your shift! Please rest for **{mins}m {secs}s** before working again.",
                ephemeral=True,
            )
            return

        jobs = [
            ("☕ Barista", "You brewed gourmet espresso at the downtown coffee shop"),
            ("💻 Software Developer", "You patched critical bugs in a client application"),
            ("🎮 Streamer", "You entertained viewers on a 4-hour gaming stream"),
            ("🔧 Mechanic", "You tuned up an exotic sports car at the garage"),
            ("🍔 Chef", "You prepared delicious burgers during the lunch rush"),
            ("📦 Courier", "You delivered packages safely across the city"),
        ]
        job_title, job_desc = random.choice(jobs)

        embed = discord.Embed(
            title=f"💼 Job Shift Completed — {job_title}",
            description=(
                f"{job_desc} and earned **+{earned:,} Coins**! 💰\n\n"
                f"New Balance: **{new_balance:,} Coins**"
            ),
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_footer(text="Work again in 1 hour or claim your /daily reward!")
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Economy(bot))
