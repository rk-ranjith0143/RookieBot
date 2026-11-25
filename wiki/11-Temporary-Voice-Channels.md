# 🔊 Module 11: Join-to-Create Temporary Voice Channels

Keep your voice sidebar super clean! Instead of creating 15 empty voice channels, you deploy **one master `➕ Join to Create` channel**. Whenever a member joins it, RookieBot instantly creates a personal voice room (`🔊 Alex's VC`), moves them into it, gives them room owner controls, and **automatically deletes the room** the moment everyone leaves!

---

## 📑 Commands & Workflows in This Guide
**For Server Administrators:**
1. [`/tempvc setup`](#-tempvc-setup) — Create the master Join-to-Create voice channel
2. [`/tempvc status`](#-tempvc-status) — Check active Temp VC setup
3. [`/tempvc remove`](#-tempvc-remove) — Disable Temp VCs

**For Voice Room Owners (While inside your Temp VC):**
4. [How Join-to-Create Works Automatically](#-what-happens-when-a-member-joins)
5. [`/vc lock`](#-vc-lock) — Lock your room so nobody else can join
6. [`/vc unlock`](#-vc-unlock) — Unlock your room
7. [`/vc limit`](#-vc-limit) — Set max member capacity (0–99)
8. [`/vc name`](#-vc-name) — Rename your voice room

---

## 🛠️ `/tempvc setup` *(Admin)*

Creates the master generator voice channel (with user limit `1` so people get moved immediately) and saves it in the database.

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/tempvc setup [category:<Category>] [channel_name:<text>]` |
| **Who Can Use It** | Members with **Manage Channels** permission |
| **Bot Needs** | **Manage Channels**, **Move Members** |
| **Response Visibility** | Public Embed |

### 2. Parameters
* **`category`** *(Optional)*: Category where the generator channel and all new temporary rooms will spawn.
* **`channel_name`** *(Optional)*: Custom name for the generator voice channel. Defaults to `➕ Join to Create`.

### 3. Exact Step-by-Step Process in Discord
1. Type `/tempvc setup`.
2. *(Optional)* Pick a **`category`** (e.g., `Voice Channels`) and custom **`channel_name`**.
3. Press **`Enter`**.

### 4. Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 4:00 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 🔊 Temp VC Generator Configured                             │
│ • Generator Channel: 🔊 ➕ Join to Create                   │
│ • Category: Voice Channels                                  │
│                                                             │
│ When members connect to 🔊 ➕ Join to Create, a private     │
│ temporary voice channel will automatically be generated for   │
│ them!                                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 `/tempvc status` *(Admin)*

### 1. Exact Step-by-Step Process in Discord
1. Type `/tempvc status` and press **`Enter`**.

### 2. Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 4:02 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 🔊 Join-to-Create Status                                    │
│                                                             │
│ Status         Generator Channel       Category             │
│ 🟢 Active      🔊 ➕ Join to Create    Voice Channels       │
└─────────────────────────────────────────────────────────────┘
```
*(If disabled: `ℹ️ Join-to-Create voice channels are currently disabled or not configured. Use /tempvc setup.`)*

---

## 🛑 `/tempvc remove` *(Admin)*

### 1. Exact Step-by-Step Process in Discord
1. Type `/tempvc remove` and press **`Enter`**.

### 2. Exact What You See in Discord
```text
🤖 RookieBot  [APP]  👁️ Only you can see this
✅ Join-to-create Temp VCs have been disabled for this server.
```

---

## 🎧 What Happens When a Member Joins

1. A member (e.g., **Alex**) clicks **`🔊 ➕ Join to Create`** in the voice channel sidebar.
2. Within 1 second, RookieBot:
   * Creates **`🔊 Alex's VC`** inside the same category.
   * Gives **Alex** `Manage Channels` and `Move Members` permissions on that specific channel.
   * Automatically moves **Alex** out of `➕ Join to Create` and into **`🔊 Alex's VC`**.
3. When the last person disconnects from **`🔊 Alex's VC`**, RookieBot automatically deletes the channel so there is zero clutter left behind.

---

## 🔒 `/vc lock` *(Room Owner)*

Prevents `@everyone` from connecting to your active temporary voice channel. (People already inside stay inside.)

### 1. Exact Step-by-Step Process in Discord
1. Make sure you are **currently connected** inside your own temporary voice channel.
2. Type `/vc lock` in any text channel (or the voice channel's text chat) and press **`Enter`**.

### 2. Exact What You See in Discord
```text
🤖 RookieBot  [APP]  👁️ Only you can see this
🔒 Your voice channel has been locked. Regular members cannot connect.
```

---

## 🔓 `/vc unlock` *(Room Owner)*

Re-opens your temporary voice channel so members can connect again.

### 1. Exact What You See in Discord
```text
🤖 RookieBot  [APP]  👁️ Only you can see this
🔓 Your voice channel has been unlocked. Members can now connect.
```

---

## 👥 `/vc limit` *(Room Owner)*

Sets the maximum number of people who can join your voice room (`0` = unlimited, up to `99`).

### 1. Exact Step-by-Step Process in Discord
1. While connected to your Temp VC, type `/vc limit`.
2. Enter a number from **`0`** to **`99`** in **`limit`** (e.g., `5` for a 5-stack gaming party).
3. Press **`Enter`**.

### 2. Exact What You See in Discord
```text
🤖 RookieBot  [APP]  👁️ Only you can see this
👥 Voice channel capacity set to 5.
```
*(Entering `0` shows `👥 Voice channel capacity set to Unlimited.`)*

---

## 📝 `/vc name` *(Room Owner)*

Renames your temporary voice channel (up to **32 characters**).

### 1. Exact Step-by-Step Process in Discord
1. While connected to your Temp VC, type `/vc name`.
2. Type **`new_name`** (e.g., `Valorant Ranked Squad`).
3. Press **`Enter`**.

### 2. Exact What You See in Discord
```text
🤖 RookieBot  [APP]  👁️ Only you can see this
📝 Voice channel renamed to Valorant Ranked Squad.
```

### ⚠️ Room Owner Error Messages
* **`❌ You must be connected to your voice channel to use this command.`** → Join your voice channel first.
* **`❌ You are not the owner of this temporary voice channel.`** → Only the creator of that Temp VC can run `/vc` controls.
* **`❌ Channel name cannot be empty.`** → Provide at least 1 visible character.
