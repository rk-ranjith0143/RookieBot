import random
import datetime
import asyncio
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

POLL_NUMBER_EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]


class Polls(commands.Cog):
    """Interactive polls and community giveaways."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="poll", description="Create an interactive poll with custom options or a Yes/No vote")
    @app_commands.describe(
        question="The question to ask in the poll",
        option1="Option 1 (leave blank for Yes/No poll)",
        option2="Option 2 (leave blank for Yes/No poll)",
        option3="Option 3 (optional)",
        option4="Option 4 (optional)",
        option5="Option 5 (optional)",
        option6="Option 6 (optional)",
        option7="Option 7 (optional)",
        option8="Option 8 (optional)",
        option9="Option 9 (optional)",
        option10="Option 10 (optional)",
    )
    async def poll(
        self,
        interaction: discord.Interaction,
        question: str,
        option1: Optional[str] = None,
        option2: Optional[str] = None,
        option3: Optional[str] = None,
        option4: Optional[str] = None,
        option5: Optional[str] = None,
        option6: Optional[str] = None,
        option7: Optional[str] = None,
        option8: Optional[str] = None,
        option9: Optional[str] = None,
        option10: Optional[str] = None,
    ):
        raw_options = [option1, option2, option3, option4, option5, option6, option7, option8, option9, option10]
        options = [opt.strip() for opt in raw_options if opt and opt.strip()]

        if len(options) == 1:
            await interaction.response.send_message(
                "❌ A poll needs at least 2 options! Leave options blank if you want a Yes/No poll.",
                ephemeral=True,
            )
            return

        is_yes_no = len(options) == 0

        embed = discord.Embed(
            title=f"📊 {question}",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.display_avatar.url,
        )

        if is_yes_no:
            embed.description = "React with 👍 for **Yes** or 👎 for **No**."
            reactions = ["👍", "👎"]
        else:
            reactions = POLL_NUMBER_EMOJIS[: len(options)]
            lines = [f"{emoji} **{opt}**" for emoji, opt in zip(reactions, options)]
            embed.description = "\n\n".join(lines)

        embed.set_footer(text="Click a reaction below to cast your vote!")

        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()

        for emoji in reactions:
            await message.add_reaction(emoji)

    @app_commands.command(name="giveaway", description="Start a quick giveaway with reactions")
    @app_commands.describe(
        prize="What are you giving away?",
        duration="Duration of the giveaway in minutes",
        winners="Number of winners (default: 1)",
    )
    async def giveaway(
        self,
        interaction: discord.Interaction,
        prize: str,
        duration: int,
        winners: int = 1,
    ):
        if duration <= 0:
            await interaction.response.send_message("❌ Duration must be at least 1 minute!", ephemeral=True)
            return
        if winners < 1:
            await interaction.response.send_message("❌ There must be at least 1 winner!", ephemeral=True)
            return

        end_time = discord.utils.utcnow() + datetime.timedelta(minutes=duration)
        embed = discord.Embed(
            title="🎉 GIVEAWAY! 🎉",
            description=(
                f"**Prize:** {prize}\n"
                f"**Hosted by:** {interaction.user.mention}\n"
                f"**Winners:** {winners}\n"
                f"**Ends:** <t:{int(end_time.timestamp())}:R> (<t:{int(end_time.timestamp())}:f>)\n\n"
                "React with 🎉 to enter!"
            ),
            color=discord.Color.gold(),
            timestamp=end_time,
        )
        embed.set_footer(text="Ends at")

        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        await message.add_reaction("🎉")

        async def finish_giveaway():
            await asyncio.sleep(duration * 60)
            try:
                refreshed_msg = await interaction.channel.fetch_message(message.id)
                reaction = discord.utils.get(refreshed_msg.reactions, emoji="🎉")
                if not reaction:
                    await interaction.channel.send(f"⚠️ Could not find giveaway message reactions for **{prize}**.")
                    return

                users = [u async for u in reaction.users() if not u.bot]
                if not users:
                    ended_embed = discord.Embed(
                        title="🎉 Giveaway Ended 🎉",
                        description=f"**Prize:** {prize}\n**Winner:** No one entered the giveaway! 😢",
                        color=discord.Color.dark_grey(),
                    )
                    await refreshed_msg.edit(embed=ended_embed)
                    await interaction.channel.send(f"No valid entries for the **{prize}** giveaway.")
                    return

                winner_count = min(winners, len(users))
                chosen = random.sample(users, winner_count)
                winner_mentions = ", ".join(u.mention for u in chosen)

                ended_embed = discord.Embed(
                    title="🎉 Giveaway Ended 🎉",
                    description=(
                        f"**Prize:** {prize}\n"
                        f"**Winner(s):** {winner_mentions}\n"
                        f"**Hosted by:** {interaction.user.mention}"
                    ),
                    color=discord.Color.green(),
                    timestamp=discord.utils.utcnow(),
                )
                ended_embed.set_footer(text="Ended at")
                await refreshed_msg.edit(embed=ended_embed)
                await interaction.channel.send(f"Congratulations {winner_mentions}! You won the **{prize}**! 🎁")
            except Exception as err:
                print(f"Error resolving giveaway: {err}")

        asyncio.create_task(finish_giveaway())


async def setup(bot: commands.Bot):
    await bot.add_cog(Polls(bot))
