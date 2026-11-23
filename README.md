# Discord Utility Bot 🚀

An enterprise-ready, modular, multi-tenant Discord utility and community management bot built with Python 3.12 and [discord.py 2.x](https://discordpy.readthedocs.io/).

Engineered for 24/7 uptime, server monetization, community engagement, and multi-guild administration with SQLite async persistence and automated unit testing.

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

### 3. 📈 Leveling & Gamification (`cogs/leveling.py`)
- Automated chat activity XP system with 60s cooldowns to prevent spam abuse.
- `/rank [member]`: View dynamic rank cards with ASCII progress bars, level, current XP, and XP required for next level.
- `/leaderboard`: Display the top 10 most active community members.

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

### 10. 💤 AFK Status System (`cogs/afk.py`)
- `/afk [reason]`: Set an AFK status.
- When mentioned in chat, the bot automatically notifies callers of your AFK status with cooldown prevention.
- Automatically removes AFK status and greets you upon your next message.

### 11. ⏰ Reminders & Timers (`cogs/reminders.py`)
- `/remindme [time] [message]`: Schedule timers and reminders (e.g. `30s`, `10m`, `2h`, `1d`).
- High-efficiency background task polls SQLite and pings you when your reminder is due.

### 12. 🪙 Virtual Server Economy & Mini-Games (`cogs/economy.py`)
- `/balance [member]`: Inspect personal wallet or check another member's coin balance.
- `/daily`: Claim 200 free coins every 24 hours with strict cooldown enforcement.
- `/pay [member] [amount]`: Transfer coins securely between server members.
- `/coinflip [bet] [choice]`: Double-or-nothing coin toss mini-game against the house.

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
- `/premium`: View premium features and server status.
- `!ping`: Latency check.
- `!sync`: Admin force sync slash commands to current guild.

---

## 🗂️ Project Structure

```text
discord-utility-bot/
├── cogs/
│   ├── afk.py           # /afk status and auto-response mention alerts
│   ├── automod.py       # Anti-invite links, mass-mentions, and anti-spam
│   ├── economy.py       # /balance, /daily, /pay, and /coinflip mini-games
│   ├── embeds.py        # Interactive announcement modal (/embed)
│   ├── events.py        # Welcome & leave greetings (/setwelcome, /setleave)
│   ├── leveling.py      # XP tracking, /rank cards, and /leaderboard
│   ├── logging.py       # Audit logging for edits, deletes, and bans (/setlogs)
│   ├── moderation.py    # /kick, /ban, /unban, /timeout, /untimeout, /clear
│   ├── polls.py         # /poll and timed /giveaway
│   ├── reminders.py     # /remindme with background loop and SQLite queue
│   ├── roles.py         # Persistent button self-role panels (/rolepanel)
│   ├── serverstats.py   # Live locked voice stats channels (/serverstats)
│   ├── starboard.py     # Reaction starboard showcase (/starboard)
│   ├── sticky.py        # Persistent bottom-pinned notices (/sticky)
│   ├── suggestions.py   # Suggestions with persistent voting buttons (/suggest)
│   ├── tags.py          # Custom tags & auto-FAQ with autocomplete (/tag)
│   ├── tickets.py       # Support ticket panels with private channels (/ticketsetup)
│   └── utility.py       # /serverinfo, /userinfo, /avatar, /roll, /premium, !ping, !sync
├── bot.py               # Main bot launcher and dynamic extension loader
├── database.py          # Asynchronous SQLite multi-tenant data layer
├── test_bot.py          # Comprehensive 20-test automated test suite
├── Dockerfile           # Optimized production container
├── docker-compose.yml   # 24/7 background service orchestration
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
└── README.md
```

---

## 🧪 Automated Testing

The bot includes an automated unit test suite that validates all 18 Cogs, 37 slash commands, database schema migrations, and UI components without requiring manual testing:

```bash
# Run the test suite
python test_bot.py -v
```

All 20 test cases pass with a 100% success rate:
- ✅ 18 Cogs discovery & extension loading
- ✅ 37 Slash commands registered in command tree
- ✅ Multi-tenant database operations (Leveling, AFK, Reminders, Economy, Sticky, Starboard, Suggestions, Tags, ServerStats)
- ✅ AutoMod regex link interception & anti-spam detection
- ✅ UI views & button custom IDs (Tickets, Roles, Suggestions)
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
