# 📊 Module 8: Live Server Stats Counters

Display your server's live member statistics at the very top of your channel sidebar using locked voice channels that **auto-update whenever members join or leave**.

### 📺 What It Creates in Your Channel List
```text
▾ 📊 SERVER STATS
   🔊 👥 Total: 154
   🔊 👤 Members: 148
   🔊 🤖 Bots: 6
```
*(Members can see these channels, but connecting is locked so nobody can join them as voice calls.)*

---

## 📑 Commands in This Guide
1. [`/serverstats setup`](#-serverstats-setup) — Create the stats category and 3 live counter channels
2. [`/serverstats refresh`](#-serverstats-refresh) — Manually force an immediate count refresh
3. [`/serverstats remove`](#-serverstats-remove) — Delete stats channels and stop tracking

---

## 📊 `/serverstats setup`

Automatically creates the `📊 Server Stats` category and three locked voice channels (`👥 Total`, `👤 Members`, `🤖 Bots`).

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/serverstats setup` |
| **Who Can Use It** | Members with **Administrator** permission |
| **Bot Needs** | **Manage Channels** permission |
| **Where It Works** | Any server text channel |
| **What Discord Shows** | Ephemeral Embed *(Only you can see this)* + 3 new Voice Channels |

### 2. Exact Step-by-Step Process in Discord
1. Type `/serverstats setup` in any text channel.
2. Select **`/serverstats setup`** from the menu.
3. Press **`Enter`**.

### 3. Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 2:45 PM  👁️ Only you can see │
├─────────────────────────────────────────────────────────────┤
│ 📊 Server Stats Setup Complete                              │
│ Created stats category 📊 Server Stats with live counters:  │
│ • 🔊 👥 Total: 154 (👥 Total: 154)                          │
│ • 🔊 👤 Members: 148 (👤 Members: 148)                      │
│ • 🔊 🤖 Bots: 6 (🤖 Bots: 6)                                │
│                                                             │
│ These channels are locked and will auto-update whenever     │
│ members join or leave!                                      │
└─────────────────────────────────────────────────────────────┘
```

### 4. Common Errors & Solutions
* **`❌ Missing permissions to create categories or manage channels.`** → Ensure RookieBot's role has **Manage Channels** enabled.

---

## 🔄 `/serverstats refresh`

Forces RookieBot to immediately recalculate and update the channel names (useful if Discord rate-limited a channel rename earlier).

> [!NOTE]
> Discord limits how fast bots can rename channels (up to 2 renames per 10 minutes per channel). If many people join rapidly, use `/serverstats refresh` later to sync the numbers!

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/serverstats refresh` |
| **Who Can Use It** | Members with **Administrator** permission |
| **Response Visibility** | Ephemeral *(Only you can see this)* |

### 2. Exact What You See in Discord
```text
🤖 RookieBot  [APP]  👁️ Only you can see this
✅ Server stats channels have been refreshed!
```

---

## 🗑️ `/serverstats remove`

Deletes the tracked counter voice channels and disables automatic updates in the database.

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/serverstats remove` |
| **Who Can Use It** | Members with **Administrator** permission |
| **Response Visibility** | Ephemeral *(Only you can see this)* |

### 2. Exact What You See in Discord
* **When removed:**
  ```text
  🤖 RookieBot  [APP]  👁️ Only you can see this
  ✅ Server stats tracking has been removed.
  ```
* **If none were set up:**
  ```text
  🤖 RookieBot  [APP]  👁️ Only you can see this
  ℹ️ No stats channels are currently configured.
  ```
*(Note: You can delete the empty `📊 Server Stats` category manually afterward if desired.)*
