from typing import List, Optional

import discord
from discord import app_commands, ui
from discord.ext import commands

import database


class ApplicationReviewView(ui.View):
    """Persistent review buttons attached to submitted staff applications."""

    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(
        label="Accept",
        emoji="✅",
        style=discord.ButtonStyle.success,
        custom_id="app_btn_accept",
    )
    async def accept_button(self, interaction: discord.Interaction, button: ui.Button):
        await self._handle_decision(interaction, "accepted")

    @ui.button(
        label="Deny",
        emoji="❌",
        style=discord.ButtonStyle.danger,
        custom_id="app_btn_deny",
    )
    async def deny_button(self, interaction: discord.Interaction, button: ui.Button):
        await self._handle_decision(interaction, "denied")

    async def _handle_decision(self, interaction: discord.Interaction, decision: str):
        guild = interaction.guild
        if not guild or not interaction.message:
            await interaction.response.send_message("❌ This action can only be used inside a server.", ephemeral=True)
            return

        reviewer = interaction.user
        if isinstance(reviewer, discord.Member):
            perms = reviewer.guild_permissions
            if not (perms.administrator or perms.manage_guild or perms.manage_roles):
                await interaction.response.send_message(
                    "❌ Only administrators or staff managers can review applications.",
                    ephemeral=True,
                )
                return

        app_record = await database.get_application_by_message(interaction.message.id)
        if not app_record:
            await interaction.response.send_message("❌ Application record not found.", ephemeral=True)
            return

        if app_record["status"] != "pending":
            await interaction.response.send_message(
                f"ℹ️ This application was already **{app_record['status'].upper()}**.",
                ephemeral=True,
            )
            return

        app_id = app_record["id"]
        applicant_id = app_record["applicant_id"]
        await database.update_application_status(app_id, decision, reviewer.id)

        config = await database.get_application_config(guild.id)
        role_note = ""
        applicant = guild.get_member(applicant_id)

        if decision == "accepted" and config and config.get("accept_role_id") and applicant:
            role = guild.get_role(config["accept_role_id"])
            if role and guild.me and guild.me.top_role > role:
                try:
                    await applicant.add_roles(role, reason=f"Application #{app_id} accepted by {reviewer}")
                    role_note = f"\n🎁 Granted role: {role.mention}"
                except (discord.Forbidden, discord.HTTPException):
                    role_note = f"\n⚠️ Could not assign {role.mention} automatically."

        for child in self.children:
            child.disabled = True

        if interaction.message.embeds:
            embed = interaction.message.embeds[0]
            if decision == "accepted":
                embed.color = discord.Color.green()
                status_val = f"✅ **Accepted** by {reviewer.mention}{role_note}"
            else:
                embed.color = discord.Color.red()
                status_val = f"❌ **Denied** by {reviewer.mention}"

            replaced = False
            for idx, field in enumerate(embed.fields):
                if field.name == "Status":
                    embed.set_field_at(idx, name="Status", value=status_val, inline=False)
                    replaced = True
                    break
            if not replaced:
                embed.add_field(name="Status", value=status_val, inline=False)

            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.edit_message(view=self)

        # Notify applicant via DM
        if applicant:
            try:
                if decision == "accepted":
                    await applicant.send(
                        f"🎉 Congratulations! Your application (`#{app_id}`) in **{guild.name}** has been **Accepted**!"
                    )
                else:
                    await applicant.send(
                        f"❌ Thank you for applying to **{guild.name}**. Unfortunately, your application (`#{app_id}`) was **Denied** at this time."
                    )
            except (discord.Forbidden, discord.HTTPException):
                pass


class ApplicationFormModal(ui.Modal):
    """Dynamic popup modal displaying up to 5 configured server application questions."""

    def __init__(self, title: str, questions: List[str], guild_id: int):
        super().__init__(title=title[:45])
        self.questions = questions[:5]
        self.guild_id = guild_id
        self.inputs: List[ui.TextInput] = []

        for idx, q in enumerate(self.questions, start=1):
            inp = ui.TextInput(
                label=q[:45],
                placeholder=f"Answer question {idx} here...",
                style=discord.TextStyle.paragraph,
                max_length=1000,
                required=True,
            )
            self.inputs.append(inp)
            self.add_item(inp)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ This form must be submitted inside a server.", ephemeral=True)
            return

        config = await database.get_application_config(guild.id)
        if not config or not config.get("is_enabled"):
            await interaction.response.send_message("❌ Applications are currently closed.", ephemeral=True)
            return

        answers = [
            {"question": q, "answer": str(inp.value).strip()}
            for q, inp in zip(self.questions, self.inputs)
        ]

        app_id = await database.create_application(guild.id, interaction.user.id, answers)

        review_channel = guild.get_channel(config["review_channel_id"])
        if not isinstance(review_channel, discord.TextChannel):
            await interaction.response.send_message(
                "⚠️ Application saved, but the staff review channel could not be found. Please notify an admin.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title=f"📝 New Application (#{app_id})",
            description=f"**Applicant:** {interaction.user.mention} (`{interaction.user}` - `{interaction.user.id}`)",
            color=0x5865F2,
            timestamp=discord.utils.utcnow(),
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.add_field(
            name="Account Created",
            value=f"<t:{int(interaction.user.created_at.timestamp())}:R>",
            inline=True,
        )
        embed.add_field(name="Status", value="⏳ **Pending Review**", inline=False)

        for idx, qa in enumerate(answers, start=1):
            embed.add_field(
                name=f"Q{idx}. {qa['question'][:200]}",
                value=qa["answer"][:1024] or "*No response*",
                inline=False,
            )

        embed.set_footer(text=f"Application #{app_id} • User ID: {interaction.user.id}")

        sent = await review_channel.send(embed=embed, view=ApplicationReviewView())
        await database.set_application_review_message(app_id, sent.id)

        await interaction.response.send_message(
            f"✅ Your application (`#{app_id}`) has been submitted to the staff team! You will receive a DM once it is reviewed.",
            ephemeral=True,
        )


class ApplicationLaunchView(ui.View):
    """Persistent panel button allowing members to open the application modal."""

    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(
        label="Apply Now",
        emoji="📝",
        style=discord.ButtonStyle.primary,
        custom_id="app_launch_btn",
    )
    async def launch_application(self, interaction: discord.Interaction, button: ui.Button):
        if not interaction.guild:
            await interaction.response.send_message("❌ This button can only be used in a server.", ephemeral=True)
            return

        config = await database.get_application_config(interaction.guild.id)
        if not config or not config.get("is_enabled") or not config.get("questions"):
            await interaction.response.send_message(
                "❌ Applications are currently closed or not configured on this server.",
                ephemeral=True,
            )
            return

        modal = ApplicationFormModal(
            title=config.get("title") or "Server Application",
            questions=config["questions"],
            guild_id=interaction.guild.id,
        )
        await interaction.response.send_modal(modal)


class Applications(commands.Cog):
    """Custom staff & team application forms with modal prompts and persistent review buttons."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    apply_group = app_commands.Group(
        name="apply",
        description="Configure and manage server application forms",
    )

    @apply_group.command(name="setup", description="Deploy a persistent application form panel with up to 5 custom questions")
    @app_commands.describe(
        panel_channel="Channel where the 'Apply Now' panel will be posted",
        review_channel="Private staff channel where submitted applications are reviewed",
        question1="First application question (Required, max 45 chars for modal label)",
        question2="Second application question (optional)",
        question3="Third application question (optional)",
        question4="Fourth application question (optional)",
        question5="Fifth application question (optional)",
        accept_role="Optional role automatically granted when an application is accepted",
        title="Title shown on the application panel and popup modal",
        description="Instructions shown on the application panel",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def apply_setup(
        self,
        interaction: discord.Interaction,
        panel_channel: discord.TextChannel,
        review_channel: discord.TextChannel,
        question1: str,
        question2: Optional[str] = None,
        question3: Optional[str] = None,
        question4: Optional[str] = None,
        question5: Optional[str] = None,
        accept_role: Optional[discord.Role] = None,
        title: str = "Staff & Team Application",
        description: str = "Interested in joining our team? Click **Apply Now** below to submit your application!",
    ):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        bot_member = guild.get_member(self.bot.user.id) if self.bot.user else guild.me
        if accept_role and bot_member and accept_role >= bot_member.top_role:
            await interaction.response.send_message(
                f"❌ I cannot assign {accept_role.mention} because it is equal to or higher than my highest role.",
                ephemeral=True,
            )
            return

        raw_questions = [question1, question2, question3, question4, question5]
        questions = [q.strip()[:100] for q in raw_questions if q and q.strip()]

        await database.set_application_config(
            guild_id=guild.id,
            panel_channel_id=panel_channel.id,
            review_channel_id=review_channel.id,
            accept_role_id=accept_role.id if accept_role else None,
            title=title.strip()[:100],
            questions=questions,
        )

        embed = discord.Embed(
            title=f"📝 {title.strip()[:100]}",
            description=description,
            color=0x5865F2,
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(
            name="📋 Form Details",
            value=f"• **Questions:** {len(questions)}\n• **Privacy:** Reviewed privately by staff.",
            inline=False,
        )
        embed.set_footer(text=guild.name, icon_url=guild.icon.url if guild.icon else None)

        await panel_channel.send(embed=embed, view=ApplicationLaunchView())
        await interaction.response.send_message(
            f"✅ Application panel deployed to {panel_channel.mention}! Submissions will go to {review_channel.mention}.",
            ephemeral=True,
        )

    @apply_group.command(name="status", description="Inspect current application form settings and questions")
    async def apply_status(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        cfg = await database.get_application_config(interaction.guild.id)
        if not cfg or not cfg.get("is_enabled"):
            await interaction.response.send_message(
                "ℹ️ Applications are currently **closed** or not configured. Admins can use `/apply setup`.",
                ephemeral=True,
            )
            return

        panel_ch = interaction.guild.get_channel(cfg["panel_channel_id"])
        review_ch = interaction.guild.get_channel(cfg["review_channel_id"])
        role = interaction.guild.get_role(cfg["accept_role_id"]) if cfg.get("accept_role_id") else None
        q_lines = "\n".join(f"**{i}.** {q}" for i, q in enumerate(cfg["questions"], start=1))

        embed = discord.Embed(
            title=f"📝 Application Status — {cfg['title']}",
            color=discord.Color.green(),
        )
        embed.add_field(name="Status", value="🟢 **Open**", inline=True)
        embed.add_field(name="Panel Channel", value=panel_ch.mention if panel_ch else f"`{cfg['panel_channel_id']}`", inline=True)
        embed.add_field(name="Review Channel", value=review_ch.mention if review_ch else f"`{cfg['review_channel_id']}`", inline=True)
        embed.add_field(name="Accepted Role", value=role.mention if role else "*(None)*", inline=True)
        embed.add_field(name="Configured Questions", value=q_lines or "*(None)*", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @apply_group.command(name="disable", description="Close and disable the application form for this server")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def apply_disable(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("❌ This command must be used in a server.", ephemeral=True)
            return

        disabled = await database.disable_application_config(interaction.guild.id)
        if disabled:
            await interaction.response.send_message("✅ Applications are now **closed** for this server.", ephemeral=True)
        else:
            await interaction.response.send_message("ℹ️ Applications were not configured on this server.", ephemeral=True)


async def setup(bot: commands.Bot):
    bot.add_view(ApplicationLaunchView())
    bot.add_view(ApplicationReviewView())
    await bot.add_cog(Applications(bot))
