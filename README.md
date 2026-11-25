# RookieBot 🚀

An enterprise-ready, modular, multi-tenant Discord community management and utility bot built with Python 3.12 and [discord.py 2.x](https://discordpy.readthedocs.io/).

Engineered for 24/7 uptime, server monetization, community engagement, and multi-guild administration with SQLite async persistence and automated unit testing.

> **📚 Official Command Wiki & Step-by-Step Discord Tutorials:**
> View the complete text-based tutorials with exact Discord previews for all 84 commands & workflows in **[wiki/README.md](wiki/README.md)**.

---

## 🌟 Key Features & Cogs

### 1. 📩 Support Ticket System (`cogs/tickets.py`)
- `/ticketsetup [channel]`: Deploy an interactive persistent ticket launcher panel.
- Clicking **"Open Ticket"** instantly creates a private, permission-isolated support channel for the member and staff.
- Includes a persistent **"Close Ticket"** button with confirmation prompts and automated ticket transcripts.

### 2. 📋 Audit & Moderation Logs (`cogs/logging.py`)
- `/setlogs [channel]`: Designate an audit log channel.
- Automatically tracks and logs:
  - Deleted messages with author, channel, and content.
  - Edited messages with side-by-side before/after diffs.
  - Member bans, unbans, and server departures.

### 3. 📈 Leveling & Milestone Roles (`cogs/leveling.py`)
- Automated chat activity XP system with 60s cooldowns to prevent spam abuse.
- `/rank [member]`: View dynamic rank cards with ASCII progress bars, level, current XP, and XP required for next level.
- `/leaderboard`: Display the top 10 most active community members.
- `/levelrole add [level] [role]`: Automatically reward members with custom vanity or perks roles upon hitting level milestones (e.g. Level 5, 10, 20).
- `/levelrole list`: View all configured level rewards in the server.
- `/levelrole remove [level]`: Unbind a level reward.

### 4. 🎨 Custom Embed Builder (`cogs/embeds.py`)
- `/embed`: Opens an interactive Discord modal to build and publish rich announcement embeds with custom hex colors, titles, descriptions, and footers.

### 5. 👋 Customizable Welcome & Leave Greetings (`cogs/events.py`)
- `/setwelcome [channel] [custom_message]`: Configure automated welcome cards. Supports variables `{user}`, `{username}`, `{server}`, and `{count}`.
- `/setleave [channel] [custom_message]`: Configure departure notices.
- Automatic guild command sync on startup for instant availability.

### 6. 📊 Polls & Giveaways (`cogs/polls.py`)
- `/poll [question] [options...]`: Create multi-choice polls (up to 10 options) with automatic numbered reaction buttons, or simple Yes/No questions.
- `/giveaway [duration] [prize]`: Host timed giveaways with reaction entry and automated random winner selection.

### 7. 🎭 Interactive Self-Roles (`cogs/roles.py`)
- `/rolepanel [title] [description] [roles...]`: Deploy persistent button self-role panels (up to 5 roles per view) that survive bot restarts.
- `/role [member] [role]`: Quick moderator command to toggle or assign/remove any role.

### 8. 🛡️ Auto-Moderation & Protection (`cogs/automod.py`)
- **Anti-Invite Links**: Intercepts and purges unauthorized `discord.gg` / `discord.com/invite` links with temporary warnings.
- **Anti-Mass Mention**: Blocks messages tagging 5+ users or unauthorized `@everyone` / `@here` pings.
- **Anti-Spam / Flood Protection**: Detects rapid message bursts (> 5 msgs in 5s) and issues automatic 60-second timeouts.
- `/automod status`: Inspect server filter configurations.
- `/automod toggle [filter] [enabled]`: Administrators can toggle individual protections.

### 9. 🔨 Comprehensive Moderation Suite (`cogs/moderation.py`)
- `/kick [member] [reason]`: Kick members with role hierarchy validation and DM notifications.
- `/ban [member] [reason] [delete_days]`: Ban users with optional chat purge (up to 7 days).
- `/unban [user_id] [reason]`: Unban members via their User ID.
- `/timeout [member] [duration] [reason]`: Timeout disruptive members for up to 28 days.
- `/untimeout [member]`: Remove an active timeout.
- `/clear [amount] [member]`: Purge up to 100 messages from the channel, with optional user filtering.
- `/slowmode [seconds] [channel]`: Adjust channel rate limits from 0s up to 6 hours to calm fast-moving chats.
- `/lock [channel] [reason]`: Instantly lock channel sending permissions for `@everyone` during raids.
- `/unlock [channel]`: Restore normal channel permissions with confirmation embeds.

### 10. 💤 AFK Status System (`cogs/afk.py`)
- `/afk [reason]`: Set an AFK status.
- When mentioned in chat, the bot automatically notifies callers of your AFK status with cooldown prevention.
- Automatically removes AFK status and greets you upon your next message.

### 11. ⏰ Reminders & Timers (`cogs/reminders.py`)
- `/remindme [time] [message]`: Schedule timers and reminders (e.g. `30s`, `10m`, `2h`, `1d`).
- High-efficiency background task polls SQLite and pings you when your reminder is due.

### 12. 🪙 Virtual Server Economy & Shop (`cogs/economy.py`)
- `/balance [member]`: Inspect personal wallet or check another member's coin balance.
- `/daily`: Claim 200 free coins every 24 hours with strict cooldown enforcement.
- `/work`: Work randomized career shifts (barista, coder, streamer, chef) to earn 50–150 coins (1-hour cooldown).
- `/pay [member] [amount]`: Transfer coins securely between server members.
- `/coinflip [bet] [choice]`: Double-or-nothing coin toss mini-game against the house.
- `/shop view`: Browse server shop items and role rewards with prices.
- `/shop add [name] [price] [description] [role]`: Server administrators can list custom items or unlockable roles.
- `/shop remove [item_id]`: Delete an item from the server shop.
- `/buy [item_id]`: Purchase items using virtual coins — automatically assigns linked roles to your profile!
- `/inventory [member]`: Inspect all purchased items, perks, and roles with purchase timestamps.

### 13. 📌 Sticky Messages (`cogs/sticky.py`)
- `/sticky set [message]`: Pins an important announcement to the bottom of the chat.
- Automatically removes old notices and reposts at the bottom whenever members send new messages.
- `/sticky remove`: Safely disable the sticky notice.

### 14. ⭐ Community Starboard (`cogs/starboard.py`)
- `/starboard setup [channel] [threshold]`: Configure a starboard showcase channel (default threshold: 3 ⭐).
- Dynamically updates star counts (`⭐ 5 #general`) and removes messages if stars drop below threshold.
- `/starboard disable`: Turn off starboard tracking.

### 15. 💡 Suggestions with Persistent Voting (`cogs/suggestions.py`)
- `/setsuggestchannel [channel]`: Designate the suggestion submission channel.
- `/suggest [suggestion]`: Post rich proposal cards with interactive **👍 Upvote** and **👎 Downvote** buttons.
- Duplicate vote prevention & vote toggling.
- `/suggeststatus [suggestion_id] [status] [reason]`: Administrators can approve, deny, or consider suggestions, dynamically changing card colors and locking votes once finalized.

### 16. 🏷️ Custom Tags & Auto-FAQ (`cogs/tags.py`)
- `/tag add [name] [content]`: Create reusable server tags or canned FAQ responses.
- `/tag get [name]`: Instant retrieval with real-time slash command autocomplete!
- `/tag list`: View all server tags with usage counters.
- `/tag delete [name]`: Delete an existing tag.

### 17. 📊 Live Server Statistics Channels (`cogs/serverstats.py`)
- `/serverstats setup`: Automatically creates locked voice channels displaying live statistics:
  - `👥 Total: {count}`
  - `👤 Members: {count}`
  - `🤖 Bots: {count}`
- Automatically updates counters on member join and leave events.
- `/serverstats refresh`: Force immediate counter sync.
- `/serverstats remove`: Remove counters and clean up channels.

### 18. 🛠️ Utilities & Server Information (`cogs/utility.py`)
- `/serverinfo`: Server metadata, boosts, creation date, and channel counts.
- `/userinfo [member]`: User roles, permissions, account age, and join date.
- `/avatar [user]`: High-resolution avatar viewer with format downloads.
- `/roll [sides]`: Customizable dice roll.
- `/hello`: Bot greeting.
- `!ping`: Latency check.
- `!sync`: Admin force sync slash commands to current guild.

### 19. 💎 Monetization & License Keys (`cogs/premium.py`)
- `/premium`: Interactive server subscription dashboard displaying active perks, expiration countdown, direct **💳 Buy Subscription** link button, and **🔑 Redeem License** modal.
- `/redeem [key]`: Instant server upgrade with license keys (`PREM-XXXX-XXXX-XXXX`).
- `/license generate [days] [note]`: Administrator command to generate unforgeable license keys for Stripe/Gumroad buyers.
- `/license list`: View all active and redeemed keys in SQLite.
- `/license revoke [guild_id]`: Revoke premium perks from a server.
- Automated background task (`check_expirations_loop`) monitors subscription lifecycle and auto-expires overdue servers.
- *For complete strategy and Stripe/Retainer setup, read [MONETIZATION.md](file:///d:/Discord_Projects/discord-utility-bot/MONETIZATION.md).*

### 20. 📖 Interactive Help Directory (`cogs/help.py`)
- `/help`: Rich interactive command manual with category dropdown navigation.
- Allows server members and administrators to explore all bot systems by category:
  - 🏠 Overview & Quick Start
  - 🛡️ Moderation & Security
  - 📈 Leveling & Economy
  - 📩 Tickets & Roles
  - 💬 Community & Utility
  - 💎 Premium & Monetization

### 21. 🎭 Auto-Role on Join (`cogs/autorole.py`)
- `/autorole set [member_role] [bot_role]`: Automatically assign configured roles to incoming members and bots as soon as they join.
- `/autorole status`: Inspect current auto-role assignments.
- `/autorole remove`: Disable auto-roles for the server.
- Features hierarchy safety guards to prevent privilege escalation.

### 22. ⚡ Keyword Auto-Responder (`cogs/autoresponder.py`)
- `/autoresponder add [trigger] [response] [match_type]`: Create automated keyword responses with choice of **Exact Match** or **Contains Substring**.
- `/autoresponder list`: View all active automated responses with numeric IDs.
- `/autoresponder delete [id]`: Delete an automated response trigger.

### 23. ⚠️ Infractions & Warning System (`cogs/warns.py`)
- `/warn [member] [reason]`: Issue formal warnings with direct message alerts, moderator tags, and SQLite persistence.
- **Automated Punishment Escalation**:
  - **3 Warnings**: Automatically times out member for 1 hour.
  - **5 Warnings**: Automatically kicks member from server.
  - **7 Warnings**: Automatically bans member from server.
- `/warnings [member]`: View full infraction history for any member with timestamps and infraction IDs.
- `/delwarn [id]`: Remove a specific infraction by its ID.
- `/clearwarns [member]`: Purge all warnings for a member.
- Automatically mirrors warning cards to the designated moderation log channel (`/setlogs`).

### 24. 🛡️ 1-Click Member Verification Gate (`cogs/verification.py`)
- `/verifysetup [channel] [role] [title] [description]`: Deploys a persistent, interactive verification panel to stop automated bots and raid accounts.
- Features a persistent **"✅ Verify"** button that survives bot reboots.
- Clicking the button checks role hierarchy, grants the verified role, and confirms via private ephemeral messages.
- `/verifystatus`: Check active verification channel and role assignments.
- `/verifyremove`: Disables the verification gate.

### 25. 🔊 Join-to-Create Dynamic Temp Voice Channels (`cogs/tempvc.py`)
- `/tempvc setup [category] [channel_name]`: Deploys a master `"➕ Join to Create"` generator voice channel.
- **Automated Channel Lifecycle**:
  - When members connect to the generator, the bot creates a private voice channel for them and moves them into it instantly.
  - Automatically cleans up and deletes the channel when all members leave.
- **Channel Owner Controls (`/vc`)**:
  - `/vc lock` & `/vc unlock`: Toggle whether other members can connect.
  - `/vc limit [number]`: Set a user capacity (0 for unlimited, 1–99).
  - `/vc name [new_name]`: Rename your temporary voice channel.
- `/tempvc status` & `/tempvc remove`: Manage Temp VC configuration.

---

## 🗂️ Project Structure

```text
RookieBot/
├── cogs/
│   ├── afk.py           # /afk status and auto-response mention alerts
│   ├── automod.py       # Anti-invite links, mass-mentions, and anti-spam
│   ├── autoresponder.py # Keyword trigger auto-replies (/autoresponder)
│   ├── autorole.py      # Automated role assignment on join (/autorole)
│   ├── economy.py       # /balance, /daily, /pay, and /coinflip mini-games
│   ├── embeds.py        # Interactive announcement modal (/embed)
│   ├── events.py        # Welcome & leave greetings (/setwelcome, /setleave)
│   ├── help.py          # Interactive category dropdown help menu (/help)
│   ├── leveling.py      # XP tracking, /rank cards, /leaderboard, and /levelrole
│   ├── logging.py       # Audit logging for edits, deletes, and bans (/setlogs)
│   ├── moderation.py    # /kick, /ban, /unban, /timeout, /clear, /lock, /slowmode
│   ├── polls.py         # /poll and timed /giveaway
│   ├── premium.py       # Monetization engine, /premium, /redeem, and /license
│   ├── reminders.py     # /remindme with background loop and SQLite queue
│   ├── roles.py         # Persistent button self-role panels (/rolepanel)
│   ├── serverstats.py   # Live locked voice stats channels (/serverstats)
│   ├── starboard.py     # Reaction starboard showcase (/starboard)
│   ├── sticky.py        # Persistent bottom-pinned notices (/sticky)
│   ├── suggestions.py   # Suggestions with persistent voting buttons (/suggest)
│   ├── tags.py          # Custom tags & auto-FAQ with autocomplete (/tag)
│   ├── tempvc.py        # Join-to-Create dynamic voice channels & controls (/tempvc, /vc)
│   ├── tickets.py       # Support ticket panels with private channels (/ticketsetup)
│   ├── utility.py       # /serverinfo, /userinfo, /avatar, /roll, !ping, !sync
│   ├── verification.py  # 1-click verification gate & persistent button (/verifysetup)
│   └── warns.py         # Infraction tracking & auto-escalation (/warn, /warnings)
├── wiki/
│   └── README.md        # Step-by-step Discord command tutorials (15 modules)
├── bot.py               # Main bot launcher and dynamic extension loader
├── database.py          # Asynchronous SQLite multi-tenant data layer & licensing
├── test_bot.py          # Comprehensive 62-test automated test suite
├── MONETIZATION.md      # SaaS, Stripe, and B2B Retainer playbook
├── Dockerfile           # Optimized production container
├── docker-compose.yml   # 24/7 background service orchestration
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
└── README.md
```

---

## 🧪 Automated Testing

The bot includes an automated unit test suite that validates all 25 Cogs, 59 slash commands, database schema migrations, and UI components without requiring manual testing:

```bash
# Run the test suite
python test_bot.py -v
```

All 62 test cases pass with a 100% success rate:
- ✅ 25 Cogs discovery & extension loading
- ✅ 59 Slash commands registered in command tree
- ✅ Multi-tenant database operations (Leveling, Level Roles, AutoRole, AutoResponder, Infractions & Warnings, Verification Gate, Temp VCs, Economy Shop & Inventory, AFK, Reminders, Economy, Sticky, Starboard, Suggestions, Tags, ServerStats, Licensing)
- ✅ AutoMod regex link interception & anti-spam detection
- ✅ UI views & button custom IDs (Tickets, Roles, Suggestions, Premium, Help, Verification)
- ✅ End-to-end slash command callback runtime execution

---

## 🚀 Deployment & Hosting

### Option A: Local Run

1. **Activate virtual environment:**
   ```bash
   .\venv\Scripts\Activate.ps1   # Windows
   source venv/bin/activate       # Linux/macOS
   ```
2. **Install requirements:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure `.env`:**
   ```env
   DISCORD_TOKEN=your_bot_token_here
   ```
4. **Launch:**
   ```bash
   python bot.py
   ```

### Option B: 24/7 Production Deployment (Docker / VPS)

```bash
# Start container in background with automatic restarts
docker compose up -d --build

# View real-time logs
docker compose logs -f
```

---

## ⚖️ Legal & Compliance

- [Terms of Service](TERMS.md)
- [Privacy Policy](PRIVACY.md)
- [Security Policy](SECURITY.md)

