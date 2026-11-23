import random
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from database import get_user_balance, update_user_balance, claim_daily


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


async def setup(bot: commands.Bot):
    await bot.add_cog(Economy(bot))
