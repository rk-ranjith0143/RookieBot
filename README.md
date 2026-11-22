# Discord Utility Bot

A utility Discord bot built with Python and [discord.py](https://discordpy.readthedocs.io/).

## Prerequisites

- Python 3.10+
- A Discord Bot Token from the [Discord Developer Portal](https://discord.com/developers/applications)

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

> **Important:** Enable **Message Content Intent** in the [Discord Developer Portal](https://discord.com/developers/applications) under **Bot > Privileged Gateway Intents**.

### 5. Run the Bot
```bash
python bot.py
```
