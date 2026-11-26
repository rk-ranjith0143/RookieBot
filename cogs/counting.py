import ast
import operator
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

import database


_SAFE_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
}

_SAFE_UNARYOPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def evaluate_counting_expression(content: str, allow_math: bool = True) -> Optional[int]:
    """Parse an integer or safe arithmetic expression for counting channels."""
    text = content.strip()
    if not text or len(text) > 50:
        return None

    # Allow clean signed/unsigned integers even when math mode is off
    if text.isdigit() or (text.startswith("-") and text[1:].isdigit()):
        return int(text)

    if not allow_math:
        return None

    try:
        tree = ast.parse(text, mode="eval")
    except SyntaxError:
        return None

    def _eval(node: ast.AST) -> Optional[float]:
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return node.value
        if isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_UNARYOPS:
            val = _eval(node.operand)
            return _SAFE_UNARYOPS[type(node.op)](val) if val is not None else None
        if isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            if left is None or right is None:
                return None
            if isinstance(node.op, ast.Div):
                if right == 0:
                    return None
                res = left / right
                return int(res) if res == int(res) else None
            if type(node.op) in _SAFE_BINOPS:
                if isinstance(node.op, (ast.FloorDiv, ast.Mod)) and right == 0:
                    return None
                res = _SAFE_BINOPS[type(node.op)](left, right)
                if abs(res) > 10**9:
                    return None
                return res
        return None

    result = _eval(tree)
    if result is None or isinstance(result, bool):
        return None
    if isinstance(result, float):
        if result != int(result):
            return None
        result = int(result)
    return result if isinstance(result, int) else None


class Counting(commands.Cog):
    """Collaborative counting channel minigame with streaks, safe math, and leaderboards."""

    counting_group = app_commands.Group(
        name="counting",
        description="Configure and inspect the server counting minigame",
        guild_only=True,
    )

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        settings = await database.get_counting_settings(message.guild.id)
        if not settings or settings["channel_id"] != message.channel.id:
            return

        guess = evaluate_counting_expression(
            message.content,
            allow_math=bool(settings.get("allow_math", 1)),
        )
        if guess is None:
            return

        expected = settings["current_count"] + 1
        last_user_id = settings.get("last_user_id")

        if last_user_id == message.author.id:
            await database.reset_counting_streak(message.guild.id, message.author.id)
            try:
                await message.add_reaction("❌")
            except (discord.Forbidden, discord.HTTPException):
                pass
            await message.channel.send(
                f"❌ {message.author.mention} ruined the count at **{settings['current_count']}**! You cannot count two numbers in a row.\nNext number: **1**."
            )
            return

        if guess != expected:
            await database.reset_counting_streak(message.guild.id, message.author.id)
            try:
                await message.add_reaction("❌")
            except (discord.Forbidden, discord.HTTPException):
                pass
            await message.channel.send(
                f"❌ {message.author.mention} ruined the count at **{settings['current_count']}**! Wrong number (`{guess}` instead of **{expected}**).\nNext number: **1**."
            )
            return

        prev_high = settings.get("high_score", 0)
        new_high = await database.record_counting_turn(message.guild.id, message.author.id, expected)

        reaction_emoji = "🏆" if (expected > prev_high and expected > 1) else ("💯" if expected % 100 == 0 else "✅")
        try:
            await message.add_reaction(reaction_emoji)
        except (discord.Forbidden, discord.HTTPException):
            pass

    @counting_group.command(name="setup", description="Set up the server counting minigame channel")
    @app_commands.describe(
        channel="Text channel dedicated to the counting minigame",
        allow_math="Allow simple arithmetic expressions like 40+2 (defaults to True)",
    )
    @app_commands.checks.has_permissions(manage_channels=True)
    async def counting_setup(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        allow_math: bool = True,
    ):
        await database.set_counting_channel(interaction.guild.id, channel.id, allow_math=allow_math)
        settings = await database.get_counting_settings(interaction.guild.id)
        next_num = (settings["current_count"] + 1) if settings else 1

        embed = discord.Embed(
            title="🔢 Counting Channel Configured",
            description=f"The counting minigame is now active in {channel.mention}!",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(name="Next Number", value=f"**{next_num}**", inline=True)
        embed.add_field(name="Math Expressions", value="Allowed ✅" if allow_math else "Numbers Only", inline=True)
        embed.set_footer(text="Rules: Count +1 in order. No counting twice in a row!")
        await interaction.response.send_message(embed=embed)

    @counting_group.command(name="stats", description="View server counting streak, high score, and player stats")
    @app_commands.describe(member="Optional member to inspect individual counting stats for")
    async def counting_stats(
        self,
        interaction: discord.Interaction,
        member: Optional[discord.Member] = None,
    ):
        settings = await database.get_counting_settings(interaction.guild.id)
        if not settings:
            await interaction.response.send_message(
                "ℹ️ Counting is not enabled in this server. Ask an admin to run `/counting setup`.",
                ephemeral=True,
            )
            return

        target = member or interaction.user
        user_stats = await database.get_counting_user_stats(interaction.guild.id, target.id)

        embed = discord.Embed(
            title="🔢 Server Counting Stats",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(name="Channel", value=f"<#{settings['channel_id']}>", inline=True)
        embed.add_field(name="Current Count", value=f"**{settings['current_count']}** (Next: **{settings['current_count'] + 1}**)", inline=True)
        embed.add_field(name="All-Time High Score", value=f"🏆 **{settings['high_score']}**", inline=True)
        embed.add_field(
            name=f"{target.display_name}'s Stats",
            value=f"✅ Correct: **{user_stats['correct_counts']}** • ❌ Ruined: **{user_stats['ruined_counts']}**",
            inline=False,
        )
        await interaction.response.send_message(embed=embed)

    @counting_group.command(name="leaderboard", description="View the Top 10 counters in this server")
    async def counting_leaderboard(self, interaction: discord.Interaction):
        rows = await database.get_counting_leaderboard(interaction.guild.id, limit=10)
        if not rows:
            await interaction.response.send_message("ℹ️ Nobody has scored in counting yet!", ephemeral=True)
            return

        lines = []
        medals = ["🥇", "🥈", "🥉"]
        for idx, row in enumerate(rows):
            prefix = medals[idx] if idx < 3 else f"**#{idx + 1}**"
            lines.append(
                f"{prefix} <@{row['user_id']}> — **{row['correct_counts']}** correct *(ruined: {row['ruined_counts']})*"
            )

        embed = discord.Embed(
            title="🏆 Top Server Counters",
            description="\n".join(lines),
            color=discord.Color.gold(),
            timestamp=discord.utils.utcnow(),
        )
        await interaction.response.send_message(embed=embed)

    @counting_group.command(name="disable", description="Disable the counting channel minigame")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def counting_disable(self, interaction: discord.Interaction):
        removed = await database.disable_counting_channel(interaction.guild.id)
        if not removed:
            await interaction.response.send_message("ℹ️ Counting is not currently enabled in this server.", ephemeral=True)
            return
        await interaction.response.send_message("🛑 Counting minigame disabled for this server.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Counting(bot))
