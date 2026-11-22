# Discord Utility Bot

A feature-rich utility Discord bot built with Python and [discord.py](https://discordpy.readthedocs.io/).

## Features

- **👋 Welcome Greetings (`on_member_join`)**: Automatically greets new members when they join the server with an informative embed displaying join count and account age.
- **📊 Interactive Polls (`/poll`)**: Run polls with up to 10 custom options (auto-adds numbered reaction buttons) or create quick Yes/No polls.
- **🎉 Giveaways (`/giveaway`)**: Host timed giveaways with reaction entry and automatic random winner selection.
- **🛡️ Moderation Commands**:
  - `/kick`: Kick members with permission checks, role hierarchy validation, and audit reason logging.
  - `/timeout`: Mute/timeout disruptive users for a configurable duration (up to 28 days) with automatic DM notice.
  - `/untimeout`: Remove an active timeout from a member.
- **🎲 Fun & Utilities**:
  - `/serverinfo`: Detailed server statistics, creation date, member breakdown, channels, and boost level.
  - `/userinfo`: Deep profile details for any member (join/creation dates, roles, key permissions).
  - `/avatar`: High-resolution avatar viewer with direct PNG/JPG/WEBP download links.
  - `/roll`: Roll a customizable die (default 6-sided).
  - `/hello`: Friendly welcome greeting.
  - `!ping`: Check bot response latency.

---

## Prerequisites

- Python 3.10+
- A Discord Bot Token from the [Discord Developer Portal](https://discord.com/developers/applications)

---

## Setup Instructions

### 1. Clone & Navigate to Project
```bash
git clone <repo_url>
cd discord-utility-bot
```

### 2. Create and Activate Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Open `.env` and fill in your Discord bot token:
```env
DISCORD_TOKEN=your_discord_bot_token_here
```

### 5. Enable Privileged Gateway Intents
In the [Discord Developer Portal](https://discord.com/developers/applications):
1. Select your application.
2. Go to **Bot** in the sidebar.
3. Scroll down to **Privileged Gateway Intents** and enable:
   - ✅ **Server Members Intent** (required for `on_member_join` welcome messages)
   - ✅ **Message Content Intent** (for prefix commands like `!ping`)
4. Under **OAuth2 > URL Generator**, grant the following permissions:
   - `Send Messages`
   - `Embed Links`
   - `Add Reactions`
   - `Read Message History`
   - `Kick Members`
   - `Moderate Members` (for timeouts)

### 6. Run the Bot
```bash
python bot.py
```
