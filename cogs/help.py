import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional


class HelpCategorySelect(discord.ui.Select):
    """Interactive category selector for the help menu."""

    def __init__(self):
        options = [
            discord.SelectOption(
                label="Overview",
                description="General summary and quick start guide",
                emoji="🏠",
                value="overview",
                default=True,
            ),
            discord.SelectOption(
                label="Moderation & Security",
                description="/kick, /ban, /timeout, /clear, /lock, /unlock, /slowmode, /automod",
                emoji="🛡️",
                value="moderation",
            ),
            discord.SelectOption(
                label="Leveling & Economy",
                description="/rank, /leaderboard, /levelrole, /balance, /daily, /pay, /coinflip",
                emoji="📈",
                value="leveling_economy",
            ),
            discord.SelectOption(
                label="Tickets & Roles",
                description="/ticketsetup, /rolepanel, /role, /autorole",
                emoji="📩",
                value="tickets_roles",
            ),
            discord.SelectOption(
                label="Community & Utility",
                description="/suggest, /starboard, /poll, /giveaway, /sticky, /tag, /autoresponder",
                emoji="💬",
                value="community",
            ),
            discord.SelectOption(
                label="Premium & Monetization",
                description="/premium, /redeem, /license",
                emoji="💎",
                value="premium",
            ),
        ]
        super().__init__(placeholder="Select a category to view commands...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selection = self.values[0]
        for opt in self.options:
            opt.default = opt.value == selection

        embed = self.get_category_embed(selection, interaction)
        await interaction.response.edit_message(embed=embed, view=self.view)

    def get_category_embed(self, category: str, interaction: discord.Interaction) -> discord.Embed:
        if category == "moderation":
            embed = discord.Embed(
                title="🛡️ Moderation & AutoMod Commands",
                description="Keep your server secure, organized, and protected against raids.",
                color=0xED4245,
            )
            embed.add_field(
                name="Punishments & Enforcement",
                value=(
                    "• `/warn [member] [reason]` - Formally warn member with auto-escalation (timeout/kick/ban).\n"
                    "• `/warnings [member]` - View full warning & infraction log.\n"
                    "• `/delwarn [id]` & `/clearwarns [member]` - Remove or purge infractions.\n"
                    "• `/kick [member] [reason]` - Kick a member from the server.\n"
                    "• `/ban [member] [reason] [delete_days]` - Ban a user with optional message purge.\n"
                    "• `/unban [user_id] [reason]` - Unban a user using their numeric ID.\n"
                    "• `/timeout [member] [duration] [reason]` - Mute/timeout a member (up to 28 days).\n"
                    "• `/untimeout [member]` - Remove an active timeout."
                ),
                inline=False,
            )
            embed.add_field(
                name="Channel Control & Anti-Raid",
                value=(
                    "• `/clear [amount] [member]` - Bulk delete up to 100 messages.\n"
                    "• `/lock [channel] [reason]` - Lock a channel for `@everyone` during raids.\n"
                    "• `/unlock [channel]` - Restore default sending permissions.\n"
                    "• `/slowmode [seconds] [channel]` - Set channel rate limits (0 to 6 hours).\n"
                    "• `/automod status` & `/automod toggle` - Manage invite, spam & mass-mention filters."
                ),
                inline=False,
            )

        elif category == "leveling_economy":
            embed = discord.Embed(
                title="📈 Leveling & Virtual Economy",
                description="Gamify your server with chat XP, ranks, and coin mini-games.",
                color=0xFEE75C,
            )
            embed.add_field(
                name="XP & Gamification",
                value=(
                    "• `/rank [member]` - Inspect rank card with visual progress bar.\n"
                    "• `/leaderboard` - Top 10 most active community members.\n"
                    "• `/levelrole add [level] [role]` - Reward members with roles when they reach levels.\n"
                    "• `/levelrole list` - View all level milestone rewards."
                ),
                inline=False,
            )
            embed.add_field(
                name="Server Economy",
                value=(
                    "• `/balance [member]` - Check your wallet or another user's balance.\n"
                    "• `/daily` - Claim 200 free coins every 24 hours.\n"
                    "• `/pay [member] [amount]` - Send coins to another server member.\n"
                    "• `/coinflip [bet] [choice]` - Double-or-nothing coin toss game."
                ),
                inline=False,
            )

        elif category == "tickets_roles":
            embed = discord.Embed(
                title="📩 Tickets, Auto-Roles & Self-Roles",
                description="Professional onboarding and customer support tools.",
                color=0x5865F2,
            )
            embed.add_field(
                name="Support Ticket System",
                value=(
                    "• `/ticketsetup [channel]` - Deploy an interactive ticket launch panel.\n"
                    "• Creates private permission-isolated support channels.\n"
                    "• Persistent close button with automated transcripts."
                ),
                inline=False,
            )
            embed.add_field(
                name="Roles Management",
                value=(
                    "• `/rolepanel [title] [description] [roles...]` - Create button self-role panels.\n"
                    "• `/role [member] [role]` - Quickly assign or remove a role from a user.\n"
                    "• `/autorole set [member_role] [bot_role]` - Automatically assign roles upon joining.\n"
                    "• `/autorole status` - View current auto-role configuration."
                ),
                inline=False,
            )
            embed.add_field(
                name="Member Verification Gate",
                value=(
                    "• `/verifysetup [channel] [role]` - Deploy a 1-click verification panel to stop bots.\n"
                    "• `/verifystatus` - View current verification gate status.\n"
                    "• `/verifyremove` - Disable verification for this server."
                ),
                inline=False,
            )

        elif category == "community":
            embed = discord.Embed(
                title="💬 Community Engagement & Utilities",
                description="Interactive tools to boost chat activity and streamline announcements.",
                color=0x57F287,
            )
            embed.add_field(
                name="Community Features",
                value=(
                    "• `/suggest [suggestion]` - Post rich suggestions with 👍/👎 voting buttons.\n"
                    "• `/suggeststatus [id] [status] [reason]` - Approve, deny, or consider suggestions.\n"
                    "• `/starboard setup [channel] [threshold]` - Feature community starred messages.\n"
                    "• `/poll [question] [options...]` - Interactive polls with numbered reactions.\n"
                    "• `/giveaway [duration] [prize]` - Timed giveaways with automated winner selection."
                ),
                inline=False,
            )
            embed.add_field(
                name="Automation & Chat Utilities",
                value=(
                    "• `/sticky set [message]` - Pin an announcement that stays at the bottom of chat.\n"
                    "• `/tag add` / `/tag get` / `/tag list` - Custom server tags & canned FAQ responses.\n"
                    "• `/autoresponder add` - Trigger automated replies to specific keywords.\n"
                    "• `/serverstats setup` - Live voice channels showing member & bot counts.\n"
                    "• `/remindme [time] [message]` - Scheduled timers and alerts.\n"
                    "• `/afk [reason]` - Away status with mention auto-replies."
                ),
                inline=False,
            )

        elif category == "premium":
            embed = discord.Embed(
                title="💎 RookieBot Premium & Monetization",
                description="Unlock unlimited limits and priority cloud infrastructure.",
                color=0xFFD700,
            )
            embed.add_field(
                name="Subscription Commands",
                value=(
                    "• `/premium` - View active subscription tier, perks, and purchase link.\n"
                    "• `/redeem [key]` - Redeem a Premium license key (`PREM-XXXX-XXXX-XXXX`)."
                ),
                inline=False,
            )
            embed.add_field(
                name="Administrator License Commands",
                value=(
                    "• `/license generate [days] [note]` - Generate unforgeable license keys.\n"
                    "• `/license list` - View active and redeemed license keys in SQLite.\n"
                    "• `/license revoke [guild_id]` - Revoke premium perks from a guild."
                ),
                inline=False,
            )

        else:  # Overview
            embed = discord.Embed(
                title="🤖 RookieBot Command Directory",
                description=(
                    "Welcome to **RookieBot**, your enterprise-ready all-in-one Discord assistant!\n\n"
                    "Use the **dropdown menu below** to browse commands by category, or type `/` in chat to see all slash commands with autocompletion."
                ),
                color=0x5865F2,
            )
            embed.add_field(
                name="🚀 Quick Start Commands",
                value=(
                    "• `/help` - View this interactive guide.\n"
                    "• `/premium` - Check subscription tier & perks.\n"
                    "• `/ticketsetup` - Deploy a support ticket panel.\n"
                    "• `/setwelcome` - Configure greeting cards.\n"
                    "• `/rank` - Inspect your community chat XP & level."
                ),
                inline=False,
            )
            embed.add_field(
                name="📊 Bot Capabilities",
                value="🛡️ Moderation • 📈 Leveling • 🪙 Economy • 📩 Tickets • ⭐ Starboard • 🏷️ Tags • 📊 Server Stats",
                inline=False,
            )

        embed.set_footer(text="RookieBot • Built with discord.py • 99.9% Uptime")
        return embed


class HelpView(discord.ui.View):
    """View containing the help category dropdown and useful link buttons."""

    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(HelpCategorySelect())
        self.add_item(
            discord.ui.Button(
                label="GitHub Repository",
                style=discord.ButtonStyle.link,
                url="https://github.com/rk-ranjith0143/RookieBot",
                emoji="🐙",
            )
        )


class Help(commands.Cog):
    """Interactive help directory with category dropdown navigation."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="Explore RookieBot's commands, modules, and setup guides")
    async def help_command(self, interaction: discord.Interaction):
        view = HelpView()
        embed = view.children[0].get_category_embed("overview", interaction)
        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))
