# 🧰 Module 14: Utilities, AFK, Reminders, Embeds & Info

All everyday server utilities, profile lookup cards, interactive announcement embeds, personal timers, AFK status notices, and prefix diagnostic commands.

---

## 📑 Commands in This Guide
1. [`/help`](#-help) — Interactive category command directory
2. [`/afk`](#-afk) — Away status with mention auto-replies & return notice
3. [`/remindme`](#-remindme) — Personal timer reminders (`30s`, `10m`, `2h`, `1d`)
4. [`/embed`](#-embed) — Interactive popup modal to design announcements *(Mod)*
5. [`/serverinfo`](#-serverinfo) — Detailed server stats card
6. [`/userinfo`](#-userinfo) — Member profile, roles & permissions card
7. [`/avatar`](#-avatar) — View & download PNG/JPG/WEBP avatars
8. [`/roll`](#-roll) — Roll a dice (default 6 sides)
9. [`/8ball`](#-8ball) — Ask the Magic 8-Ball a yes/no question
10. [`/hello`](#-hello) — Friendly greeting
11. [`/snipe`](#-snipe) — Recover recently deleted messages in a channel
12. [`/editsnipe`](#-editsnipe) — View before/after text of recently edited messages
13. [`!ping`](#-ping-prefix-command) — Check bot latency in milliseconds
14. [`!sync`](#-sync-prefix-command) — Force-sync slash commands *(Admin)*

---

## 📖 `/help`

Opens RookieBot's interactive help directory with a **dropdown menu** (`Select a category to view commands...`) and a direct **GitHub Repository** link button.

### Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 5:30 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 🤖 RookieBot Command Directory                              │
│ Welcome to RookieBot, your enterprise-ready all-in-one      │
│ Discord assistant!                                          │
│                                                             │
│ Use the dropdown menu below to browse commands by category, │
│ or type / in chat to see all slash commands with            │
│ autocompletion.                                             │
│                                                             │
│ 🚀 Quick Start Commands                                     │
│ • /help - View this interactive guide.                      │
│ • /premium - Check subscription tier & perks.               │
│ • /ticketsetup - Deploy a support ticket panel.             │
│ • /setwelcome - Configure greeting cards.                   │
│ • /rank - Inspect your community chat XP & level.           │
│                                                             │
│ 📊 Bot Capabilities                                         │
│ 🛡️ Moderation • 📈 Leveling • 🪙 Economy • 📩 Tickets ...   │
│                                                             │
│ RookieBot • Built with discord.py • 99.9% Uptime            │
├─────────────────────────────────────────────────────────────┤
│ [ ▼ Select a category to view commands...               ]   │
│ [ 🐙 GitHub Repository ↗ ]                                  │
└─────────────────────────────────────────────────────────────┘
```
*Clicking the dropdown lets you switch between `🏠 Overview`, `🛡️ Moderation & Security`, `📈 Leveling & Economy`, `📩 Tickets & Roles`, `💬 Community & Utility`, and `💎 Premium & Monetization`.*

---

## 💤 `/afk`

Marks you as Away From Keyboard (`AFK`). Whenever someone pings you, RookieBot replies politely telling them your reason and how long you've been away (with a 10-second anti-spam cooldown per channel). As soon as you send a message again, RookieBot welcomes you back!

### 1. Parameters
* **`reason`** *(Optional)*: Why you are away (max `150` chars). Defaults to `AFK`.

### 2. Exact What You See in Discord
* **When you run `/afk reason:Studying for finals`:**
  ```text
  🤖 RookieBot  [APP]
  💤 @Alex, I set your AFK: Studying for finals.
  ```
* **When someone mentions `@Alex` in chat:**
  ```text
  🤖 RookieBot  [APP]  (replying to their message)
  💤 Alex is currently AFK: Studying for finals (12 minutes ago).
  ```
* **When you return and send any message (auto-deletes after 6 seconds):**
  ```text
  🤖 RookieBot  [APP]
  👋 Welcome back @Alex! I removed your AFK (You were away for 12 minute(s)).
  ```

---

## ⏰ `/remindme`

Schedules a persistent reminder that survives bot restarts and pings you in the channel when time is up!

### 1. Parameters
* **`time`** *(Required)*: Number + unit (`s` = seconds, `m` = minutes, `h` = hours, `d` = days). Max: `30d`.
  * Examples: `30s`, `10m`, `2h`, `1d`.
* **`message`** *(Required)*: Reminder note (max `500` chars).

### 2. Exact What You See in Discord
* **When scheduled:**
  ```text
  ┌─────────────────────────────────────────────────────────────┐
  │ 🤖 RookieBot  [APP]  Today at 5:35 PM                        │
  ├─────────────────────────────────────────────────────────────┤
  │ ⏰ Reminder Scheduled                                       │
  │ I will remind you in 10 minutes (Nov 25, 2026 at 5:45 PM):  │
  │                                                             │
  │ Take the pizza out of the oven                              │
  │                                                             │
  │ Requested by Alex                                           │
  └─────────────────────────────────────────────────────────────┘
  ```
* **When the timer expires:**
  ```text
  ┌─────────────────────────────────────────────────────────────┐
  │ 🤖 RookieBot  [APP]  Today at 5:45 PM                        │
  │ @Alex                                                       │
  ├─────────────────────────────────────────────────────────────┤
  │ ⏰ Reminder Alert!                                          │
  │ @Alex, here is the reminder you scheduled:                  │
  │                                                             │
  │ Take the pizza out of the oven                              │
  └─────────────────────────────────────────────────────────────┘
  ```

### 3. Common Errors & Solutions
* **`❌ Invalid time format! Please use a number followed by s, m, h, or d (e.g., 10m, 2h, 1d).`**
* **`❌ Reminders cannot be set for more than 30 days into the future.`**

---

## 📝 `/embed` *(Manage Messages)*

Opens an interactive Discord popup **Modal form** where staff can design and post a clean custom announcement embed without typing ugly raw code.

### 1. Exact Step-by-Step Process in Discord
1. Go to your `#announcements` channel, type `/embed`, and press **`Enter`**.
2. Discord pops up a form titled **`Create Custom Announcement Embed`** with 5 boxes:
   * **`Title`** *(Required, max 256 chars)* — e.g., `Server Maintenance Tonight`
   * **`Description`** *(Required, paragraph, max 4000 chars)* — your main announcement text
   * **`Color (Hex code or name e.g. #5865F2, gold)`** *(Optional, defaults to `#5865F2`)* — supports `#hex` or `blue`, `red`, `green`, `gold`, `orange`, `purple`, `blurple`, `dark`
   * **`Image URL (optional banner image)`** *(Optional)* — any `https://...` image link
   * **`Footer Text (optional)`** *(Optional, max 128 chars)* — e.g., `Server Announcements • 2026`
3. Click **`Submit`**.

### 2. Exact What You See in Discord
RookieBot posts your formatted embed directly in the channel (as the bot, not mentioning you) and sends you a private notice:
```text
🤖 RookieBot  [APP]  👁️ Only you can see this
✅ Embed successfully published to this channel!
```

---

## 🏰 `/serverinfo`

Displays a complete summary card of the server: Owner, Server ID, Creation date, Human/Bot member breakdown, Channel counts (Text, Voice, Stage, Categories), Server Boost tier, Roles, Emojis/Stickers, and Discord Verification level.

### Exact Step-by-Step Process in Discord
1. Type `/serverinfo` and press **`Enter`**.

---

## 👤 `/userinfo`

Displays detailed profile information for yourself or another member: Username, ID, Bot status, Top Role, Account Creation date, Server Join date, up to 15 Roles, and Key Moderation Permissions.

### Exact Step-by-Step Process in Discord
1. Type `/userinfo`, optionally pick **`member`**, and press **`Enter`**.

---

## 🖼️ `/avatar`

Shows a user's profile picture in high resolution (`1024px`) with direct clickable download links for **PNG**, **JPG**, and **WEBP**.

### Exact Step-by-Step Process in Discord
1. Type `/avatar`, optionally pick **`user`**, and press **`Enter`**.

---

## 🎲 `/roll` & 🎱 `/8ball` & 👋 `/hello`

* **`/roll [sides:<number>]`**: Rolls a random number from `1` to `sides` (defaults to `6` sides; minimum `2`).
  * Output: `🎲 You rolled a 4 (1–6)`
* **`/8ball question:<text>`**: Ask any yes/no question and get a classic Magic 8-Ball fortune card!
  ```text
  ┌─────────────────────────────────────────────────────────────┐
  │ 🤖 RookieBot  [APP]  Today at 5:40 PM                        │
  ├─────────────────────────────────────────────────────────────┤
  │ 🎱 Magic 8-Ball                                             │
  │                                                             │
  │ Question                                                    │
  │ Will RookieBot hit 1,000 servers?                           │
  │                                                             │
  │ Answer                                                      │
  │ Without a doubt! ✅                                         │
  │                                                             │
  │ Asked by Alex                                               │
  └─────────────────────────────────────────────────────────────┘
  ```
* **`/hello`**: Sends a quick friendly welcome message from RookieBot.
  * Output: `Hey @Alex! I'm Rookie, your all-in-one server utility and community assistant. Type / to see my commands! 👋`

---

## 🎯 `/snipe`

Shows the most recently deleted message in the current channel (up to the last 10 deleted messages per channel cached in memory).

* **Syntax:** `/snipe [index:<1-10>]`
* **Exact Discord Preview:**
  ```text
  ┌─────────────────────────────────────────────────────────────┐
  │ 🤖 RookieBot  [APP]  Today at 5:45 PM                        │
  ├─────────────────────────────────────────────────────────────┤
  │ 👤 Alex                                                     │
  │ Oops I typed that in the wrong channel!                     │
  │                                                             │
  │ Sniped 1/3 • Deleted • Today at 5:44 PM                     │
  └─────────────────────────────────────────────────────────────┘
  ```
* *If nothing is cached:* `ℹ️ Nothing recently deleted in this channel to snipe.`

---

## ✏️ `/editsnipe`

Shows the **Before** and **After** content of the most recently edited message in the current channel (up to the last 10 edits cached per channel).

* **Syntax:** `/editsnipe [index:<1-10>]`
* **Exact Discord Preview:**
  ```text
  ┌─────────────────────────────────────────────────────────────┐
  │ 🤖 RookieBot  [APP]  Today at 5:46 PM                        │
  ├─────────────────────────────────────────────────────────────┤
  │ 👤 Alex                                                     │
  │ Jump to Message                                             │
  │                                                             │
  │ Before                                                      │
  │ Meeting is at 5 PM                                          │
  │                                                             │
  │ After                                                       │
  │ Meeting is at 6 PM                                          │
  │                                                             │
  │ Edit Snipe 1/2 • Edited • Today at 5:45 PM                  │
  └─────────────────────────────────────────────────────────────┘
  ```
* *If nothing is cached:* `ℹ️ Nothing recently edited in this channel to snipe.`

---

## 🏓 `!ping` *(Prefix Command)*

Checks the bot's live Discord WebSocket latency.
1. Type `!ping` in chat (no `/`!) and press **`Enter`**.
2. **Output:** `🏓 Pong! Latency: 42ms`

---

## 🔄 `!sync` *(Admin Prefix Command)*

Instantly force-syncs all 59 slash commands directly to your current server (useful if Discord is slow showing a newly added command).
1. Type `!sync` in chat (requires **Administrator** permission) and press **`Enter`**.
2. **Output:**
   ```text
   ✅ Successfully synced 59 slash command(s) to My Community Server!
   (Tip: If they don't appear in your / menu immediately, press Ctrl + R to reload Discord!)
   ```
