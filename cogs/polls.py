import random
import time
import datetime
from typing import Optional, List

import discord
from discord import app_commands
from discord.ext import commands, tasks

import database

POLL_NUMBER_EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]


class Polls(commands.Cog):
    """Interactive polls and restart-safe persistent community giveaways."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def cog_unload(self):
        if self.giveaway_loop.is_running():
            self.giveaway_loop.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.giveaway_loop.is_running():
            self.giveaway_loop.start()

    @tasks.loop(seconds=10.0)
    async def giveaway_loop(self):
        """Poll SQLite for active giveaways that have reached their end time."""
        due = await database.get_due_giveaways(time.time())
        for item in due:
            try:
                await self._finalize_giveaway(item)
            except Exception as err:
                print(f"Error resolving giveaway {item.get('message_id')}: {err}")
                await database.mark_giveaway_ended(item["message_id"])

    @giveaway_loop.before_loop
    async def before_giveaway_loop(self):
        await self.bot.wait_until_ready()

    async def _fetch_reaction_entrants(self, message: discord.Message) -> List[discord.abc.User]:
        """Collect all non-bot users who reacted with 🎉 on a giveaway message."""
        reaction = discord.utils.get(message.reactions, emoji="🎉")
        if not reaction:
            return []
        return [u async for u in reaction.users() if not u.bot]

    async def _finalize_giveaway(
        self,
        giveaway_record: dict,
        winners_override: Optional[int] = None,
        is_reroll: bool = False,
    ) -> Optional[List[discord.abc.User]]:
        """Draw winners, update the giveaway embed, and announce results."""
        message_id = giveaway_record["message_id"]
        channel_id = giveaway_record["channel_id"]
        host_id = giveaway_record["host_id"]
        prize = giveaway_record["prize"]
        winners_count = winners_override or giveaway_record.get("winners_count", 1)

        if not is_reroll:
            await database.mark_giveaway_ended(message_id)

        channel = self.bot.get_channel(channel_id)
        if not channel:
            try:
                channel = await self.bot.fetch_channel(channel_id)
            except Exception:
                return None

        try:
            refreshed_msg = await channel.fetch_message(message_id)
        except Exception:
            await channel.send(f"⚠️ Could not find giveaway message (`{message_id}`) for **{prize}**.")
            return None

        users = await self._fetch_reaction_entrants(refreshed_msg)
        if not users:
            ended_embed = discord.Embed(
                title="🎉 Giveaway Ended 🎉",
                description=f"**Prize:** {prize}\n**Winner:** No one entered the giveaway! 😢",
                color=discord.Color.dark_grey(),
                timestamp=discord.utils.utcnow(),
            )
            ended_embed.set_footer(text=f"Message ID: {message_id}")
            await refreshed_msg.edit(embed=ended_embed)
            await channel.send(f"No valid entries for the **{prize}** giveaway.")
            return []

        pick_count = min(winners_count, len(users))
        chosen = random.sample(users, pick_count)
        winner_mentions = ", ".join(u.mention for u in chosen)

        ended_embed = discord.Embed(
            title="🎉 Giveaway Ended 🎉",
            description=(
                f"**Prize:** {prize}\n"
                f"**Winner(s):** {winner_mentions}\n"
                f"**Hosted by:** <@{host_id}>"
            ),
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow(),
        )
        ended_embed.set_footer(text=f"Ended at • ID: {message_id}")
        await refreshed_msg.edit(embed=ended_embed)

        if is_reroll:
            await channel.send(f"🎲 **Giveaway Reroll!** New winner(s) for **{prize}**: {winner_mentions}! 🎁")
        else:
            await channel.send(f"Congratulations {winner_mentions}! You won the **{prize}**! 🎁")

        return chosen

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

    # -----------------------------------------------------------------------
    # Persistent Giveaways Command Group
    # -----------------------------------------------------------------------

    giveaway_group = app_commands.Group(
        name="giveaway",
        description="Start, list, end, or reroll persistent community giveaways",
    )

    @giveaway_group.command(name="start", description="Start a restart-safe timed giveaway with 🎉 reactions")
    @app_commands.describe(
        prize="What are you giving away?",
        duration="Duration of the giveaway in minutes",
        winners="Number of winners (default: 1)",
    )
    async def giveaway_start(
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

        end_ts = time.time() + (duration * 60)
        end_time = datetime.datetime.fromtimestamp(end_ts, tz=datetime.timezone.utc)
        embed = discord.Embed(
            title="🎉 GIVEAWAY! 🎉",
            description=(
                f"**Prize:** {prize}\n"
                f"**Hosted by:** {interaction.user.mention}\n"
                f"**Winners:** {winners}\n"
                f"**Ends:** <t:{int(end_ts)}:R> (<t:{int(end_ts)}:f>)\n\n"
                "React with 🎉 to enter!"
            ),
            color=discord.Color.gold(),
            timestamp=end_time,
        )
        embed.set_footer(text="Ends at")

        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        await message.add_reaction("🎉")

        embed.set_footer(text=f"Ends at • ID: {message.id}")
        try:
            await message.edit(embed=embed)
        except Exception:
            pass

        guild_id = interaction.guild.id if interaction.guild else 0
        channel_id = interaction.channel.id if interaction.channel else 0
        await database.create_giveaway(
            message_id=message.id,
            guild_id=guild_id,
            channel_id=channel_id,
            host_id=interaction.user.id,
            prize=prize.strip()[:200],
            winners_count=winners,
            ends_at=end_ts,
        )

    @giveaway_group.command(name="list", description="View all active giveaways in this server")
    async def giveaway_list(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        active = await database.get_active_giveaways(interaction.guild.id)
        if not active:
            await interaction.response.send_message("ℹ️ There are no active giveaways right now.", ephemeral=True)
            return

        lines = []
        for g in active[:15]:
            lines.append(
                f"• **{g['prize']}** ({g['winners_count']} winner(s)) — Ends <t:{int(g['ends_at'])}:R>\n"
                f"  └ Message ID: `{g['message_id']}` in <#{g['channel_id']}>"
            )

        embed = discord.Embed(
            title=f"🎉 Active Giveaways ({len(active)})",
            description="\n".join(lines),
            color=discord.Color.gold(),
        )
        embed.set_footer(text="Use /giveaway end or /giveaway reroll with the Message ID.")
        await interaction.response.send_message(embed=embed)

    def _can_manage_giveaway(self, interaction: discord.Interaction, record: dict) -> bool:
        if interaction.user.id == record.get("host_id"):
            return True
        if isinstance(interaction.user, discord.Member):
            perms = interaction.user.guild_permissions
            return perms.administrator or perms.manage_guild or perms.manage_messages
        return False

    @giveaway_group.command(name="end", description="End an active giveaway early and pick winner(s) now")
    @app_commands.describe(message_id="The giveaway message ID (see embed footer or /giveaway list)")
    async def giveaway_end(self, interaction: discord.Interaction, message_id: str):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        try:
            mid = int(message_id.strip())
        except ValueError:
            await interaction.response.send_message("❌ Invalid Message ID. Please enter numbers only.", ephemeral=True)
            return

        record = await database.get_giveaway(mid)
        if not record or record["guild_id"] != interaction.guild.id:
            await interaction.response.send_message(f"❌ Giveaway `{mid}` not found in this server.", ephemeral=True)
            return

        if record["is_ended"]:
            await interaction.response.send_message("ℹ️ That giveaway has already ended. Use `/giveaway reroll` instead.", ephemeral=True)
            return

        if not self._can_manage_giveaway(interaction, record):
            await interaction.response.send_message("❌ Only the giveaway host or a moderator can end this giveaway.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        await self._finalize_giveaway(record, is_reroll=False)
        await interaction.followup.send(f"✅ Giveaway for **{record['prize']}** ended and winners drawn!", ephemeral=True)

    @giveaway_group.command(name="reroll", description="Pick new random winner(s) for an ended giveaway")
    @app_commands.describe(
        message_id="The giveaway message ID to reroll",
        winners="Optional override for number of new winners",
    )
    async def giveaway_reroll(
        self,
        interaction: discord.Interaction,
        message_id: str,
        winners: Optional[int] = None,
    ):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        if winners is not None and winners < 1:
            await interaction.response.send_message("❌ Number of winners must be at least 1.", ephemeral=True)
            return

        try:
            mid = int(message_id.strip())
        except ValueError:
            await interaction.response.send_message("❌ Invalid Message ID. Please enter numbers only.", ephemeral=True)
            return

        record = await database.get_giveaway(mid)
        if not record or record["guild_id"] != interaction.guild.id:
            await interaction.response.send_message(f"❌ Giveaway `{mid}` not found in this server.", ephemeral=True)
            return

        if not self._can_manage_giveaway(interaction, record):
            await interaction.response.send_message("❌ Only the giveaway host or a moderator can reroll this giveaway.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        await self._finalize_giveaway(record, winners_override=winners, is_reroll=True)
        await interaction.followup.send(f"🎲 Rerolled winners for **{record['prize']}**!", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Polls(bot))
