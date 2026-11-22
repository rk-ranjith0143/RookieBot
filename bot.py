import os
import random
import datetime
import asyncio
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Setup Intents (Server Members Intent is required for on_member_join)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

POLL_NUMBER_EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Slash commands synced successfully!")


@bot.event
async def on_member_join(member: discord.Member):
    """Greet new members automatically when they join the server."""
    guild = member.guild

    # 1. Look for system channel
    target_channel = guild.system_channel

    # 2. If no system channel or cannot send, look for common welcome channel names
    if not target_channel or not target_channel.permissions_for(guild.me).send_messages:
        common_names = ("welcome", "welcomes", "general", "lobby", "chat")
        for channel in guild.text_channels:
            if channel.name.lower() in common_names and channel.permissions_for(guild.me).send_messages:
                target_channel = channel
                break

    # 3. Fallback to the first text channel where bot has send permission
    if not target_channel or not target_channel.permissions_for(guild.me).send_messages:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                target_channel = channel
                break

    # If no channel found where bot can send messages, exit gracefully
    if not target_channel:
        return

    # Build welcoming embed
    embed = discord.Embed(
        title=f"👋 Welcome to {guild.name}!",
        description=(
            f"Hey {member.mention}, welcome to the server! 🎉\n"
            "We're glad to have you here. Please make sure to check the rules and enjoy your stay!"
        ),
        color=discord.Color.green(),
        timestamp=discord.utils.utcnow(),
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(
        name="Account Created",
        value=f"<t:{int(member.created_at.timestamp())}:R>",
        inline=True,
    )
    embed.add_field(
        name="Member Count",
        value=f"#{guild.member_count}",
        inline=True,
    )
    embed.set_footer(text=f"User ID: {member.id}")

    try:
        await target_channel.send(content=f"Welcome {member.mention}!", embed=embed)
    except discord.HTTPException as e:
        print(f"Failed to send welcome message in {guild.name}: {e}")


# ---------------------------------------------------------------------------
# Global App Command Error Handler
# ---------------------------------------------------------------------------

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Handle slash command permission and validation errors cleanly."""
    if isinstance(error, app_commands.MissingPermissions):
        perms = ", ".join(f"`{p}`" for p in error.missing_permissions)
        msg = f"❌ You do not have the required permissions to use this command.\n**Missing:** {perms}"
    elif isinstance(error, app_commands.BotMissingPermissions):
        perms = ", ".join(f"`{p}`" for p in error.missing_permissions)
        msg = f"❌ I do not have the required permissions to execute this command.\n**Missing:** {perms}"
    else:
        msg = f"❌ An unexpected error occurred: `{error}`"

    if interaction.response.is_done():
        await interaction.followup.send(msg, ephemeral=True)
    else:
        await interaction.response.send_message(msg, ephemeral=True)


# ---------------------------------------------------------------------------
# General Commands
# ---------------------------------------------------------------------------

@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! Latency: {round(bot.latency * 1000)}ms")


@bot.tree.command(name="hello", description="Get a friendly greeting from the bot")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hey {interaction.user.mention}! Welcome to the server.")


@bot.tree.command(name="roll", description="Roll a dice (default is 6 sides)")
@app_commands.describe(sides="Number of sides on the dice (e.g., 6, 20, 100)")
async def roll(interaction: discord.Interaction, sides: int = 6):
    if sides < 2:
        await interaction.response.send_message("Please pick at least 2 sides!", ephemeral=True)
        return
    result = random.randint(1, sides)
    await interaction.response.send_message(f"🎲 You rolled a **{result}** (1–{sides})")


# ---------------------------------------------------------------------------
# Poll & Giveaway Commands
# ---------------------------------------------------------------------------

@bot.tree.command(name="poll", description="Create an interactive poll with custom options or a Yes/No vote")
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

    # If only 1 option provided
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


@bot.tree.command(name="giveaway", description="Start a quick giveaway with reactions")
@app_commands.describe(
    prize="What are you giving away?",
    duration="Duration of the giveaway in minutes",
    winners="Number of winners (default: 1)",
)
async def giveaway(
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

    # Background task to complete the giveaway after duration
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


# ---------------------------------------------------------------------------
# Moderation Commands
# ---------------------------------------------------------------------------

@bot.tree.command(name="kick", description="Kick a member from the server")
@app_commands.describe(
    member="The member to kick",
    reason="Reason for kicking the member",
)
@app_commands.checks.has_permissions(kick_members=True)
@app_commands.checks.bot_has_permissions(kick_members=True)
async def kick(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: Optional[str] = "No reason provided",
):
    guild = interaction.guild

    # Hierarchy and safety checks
    if member.id == interaction.user.id:
        await interaction.response.send_message("❌ You cannot kick yourself!", ephemeral=True)
        return
    if member.id == bot.user.id:
        await interaction.response.send_message("❌ I cannot kick myself!", ephemeral=True)
        return
    if member.id == guild.owner_id:
        await interaction.response.send_message("❌ You cannot kick the server owner!", ephemeral=True)
        return
    if interaction.user.id != guild.owner_id and interaction.user.top_role <= member.top_role:
        await interaction.response.send_message(
            "❌ You cannot kick someone with a role equal to or higher than yours!",
            ephemeral=True,
        )
        return
    if guild.me.top_role <= member.top_role:
        await interaction.response.send_message(
            "❌ I cannot kick someone with a role equal to or higher than my highest role!",
            ephemeral=True,
        )
        return

    # Attempt to notify member in DM
    try:
        await member.send(f"⚠️ You were kicked from **{guild.name}**.\n**Reason:** {reason}")
    except (discord.Forbidden, discord.HTTPException):
        pass

    audit_reason = f"Kicked by {interaction.user} (ID: {interaction.user.id}): {reason}"
    await member.kick(reason=audit_reason)

    embed = discord.Embed(
        title="👢 Member Kicked",
        color=discord.Color.orange(),
        timestamp=discord.utils.utcnow(),
    )
    embed.add_field(name="Member", value=f"{member.mention} (`{member}`)", inline=False)
    embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.set_thumbnail(url=member.display_avatar.url)

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="timeout", description="Timeout (mute) a member for a specified duration")
@app_commands.describe(
    member="The member to timeout",
    duration="Duration in minutes (1 - 40320 minutes / up to 28 days)",
    reason="Reason for the timeout",
)
@app_commands.checks.has_permissions(moderate_members=True)
@app_commands.checks.bot_has_permissions(moderate_members=True)
async def timeout(
    interaction: discord.Interaction,
    member: discord.Member,
    duration: int,
    reason: Optional[str] = "No reason provided",
):
    guild = interaction.guild

    # Validation
    if duration < 1 or duration > 40320:
        await interaction.response.send_message(
            "❌ Duration must be between 1 minute and 40,320 minutes (28 days).",
            ephemeral=True,
        )
        return

    # Hierarchy and safety checks
    if member.id == interaction.user.id:
        await interaction.response.send_message("❌ You cannot timeout yourself!", ephemeral=True)
        return
    if member.id == bot.user.id:
        await interaction.response.send_message("❌ I cannot timeout myself!", ephemeral=True)
        return
    if member.id == guild.owner_id:
        await interaction.response.send_message("❌ You cannot timeout the server owner!", ephemeral=True)
        return
    if interaction.user.id != guild.owner_id and interaction.user.top_role <= member.top_role:
        await interaction.response.send_message(
            "❌ You cannot timeout someone with a role equal to or higher than yours!",
            ephemeral=True,
        )
        return
    if guild.me.top_role <= member.top_role:
        await interaction.response.send_message(
            "❌ I cannot timeout someone with a role equal to or higher than my highest role!",
            ephemeral=True,
        )
        return

    delta = datetime.timedelta(minutes=duration)
    audit_reason = f"Timed out by {interaction.user} (ID: {interaction.user.id}) for {duration}m: {reason}"
    await member.timeout(delta, reason=audit_reason)

    # Human-friendly duration formatting
    if duration >= 1440:
        duration_str = f"{duration // 1440} day(s) {((duration % 1440) // 60)} hour(s)"
    elif duration >= 60:
        duration_str = f"{duration // 60} hour(s) {duration % 60} minute(s)"
    else:
        duration_str = f"{duration} minute(s)"

    # Attempt to notify member in DM
    try:
        await member.send(
            f"⏳ You have been timed out in **{guild.name}** for **{duration_str}**.\n**Reason:** {reason}"
        )
    except (discord.Forbidden, discord.HTTPException):
        pass

    embed = discord.Embed(
        title="⏳ Member Timed Out",
        color=discord.Color.red(),
        timestamp=discord.utils.utcnow(),
    )
    embed.add_field(name="Member", value=f"{member.mention} (`{member}`)", inline=False)
    embed.add_field(name="Duration", value=duration_str, inline=True)
    embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.set_thumbnail(url=member.display_avatar.url)

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="untimeout", description="Remove timeout from a member")
@app_commands.describe(
    member="The member to remove timeout from",
    reason="Reason for removing timeout",
)
@app_commands.checks.has_permissions(moderate_members=True)
@app_commands.checks.bot_has_permissions(moderate_members=True)
async def untimeout(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: Optional[str] = "Timeout removed by moderator",
):
    guild = interaction.guild

    if not member.is_timed_out():
        await interaction.response.send_message(
            f"❌ {member.mention} is not currently timed out.",
            ephemeral=True,
        )
        return

    if interaction.user.id != guild.owner_id and interaction.user.top_role <= member.top_role:
        await interaction.response.send_message(
            "❌ You cannot modify timeout for someone with a role equal to or higher than yours!",
            ephemeral=True,
        )
        return
    if guild.me.top_role <= member.top_role:
        await interaction.response.send_message(
            "❌ I cannot modify timeout for someone with a role equal to or higher than my highest role!",
            ephemeral=True,
        )
        return

    audit_reason = f"Untimed out by {interaction.user} (ID: {interaction.user.id}): {reason}"
    await member.timeout(None, reason=audit_reason)

    embed = discord.Embed(
        title="🔊 Timeout Removed",
        description=f"Timeout removed for {member.mention} (`{member}`).",
        color=discord.Color.green(),
        timestamp=discord.utils.utcnow(),
    )
    embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.set_thumbnail(url=member.display_avatar.url)

    await interaction.response.send_message(embed=embed)


# ---------------------------------------------------------------------------
# Run Bot
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if not TOKEN:
        raise ValueError("DISCORD_TOKEN environment variable is not set. Please check your .env file.")
    bot.run(TOKEN)
