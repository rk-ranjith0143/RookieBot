import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError(
        "Error: 'DISCORD_TOKEN' environment variable is missing or empty. "
        "Please check your .env file."
    )

intents = discord.Intents.default()
intents.message_content = True  # Required to read messages

bot = commands.Bot(
    command_prefix="!",
    description="Discord Utility Bot",
    intents=intents,
)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! Latency: {round(bot.latency * 1000)}ms")

bot.run(TOKEN)