import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")


class UtilityBot(commands.Bot):
    """Modular Discord Utility Bot using Cog architecture."""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        """Asynchronous initialization hook called before the bot connects."""
        cogs_dir = os.path.join(os.path.dirname(__file__), "cogs")
        for filename in sorted(os.listdir(cogs_dir)):
            if filename.endswith(".py") and not filename.startswith("__"):
                extension = f"cogs.{filename[:-3]}"
                try:
                    await self.load_extension(extension)
                    print(f"Loaded extension: {extension}")
                except Exception as e:
                    print(f"Failed to load extension {extension}: {e}")

        # Global slash command error handler
        @self.tree.error
        async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
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

        await self.tree.sync()
        print("Slash commands synced successfully!")


def main():
    if not TOKEN:
        raise ValueError("DISCORD_TOKEN environment variable is not set. Please check your .env file.")

    bot = UtilityBot()
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
