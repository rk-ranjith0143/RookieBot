# 🛡️ Module 3: AutoMod, Word Blacklist & Anti-Raid Shields

RookieBot includes **5 automatic protection shields** that run 24/7 in the background—all **enabled by default** as soon as the bot joins your server.

### 🧱 Built-In Automatic Shields
1. **🔗 Anti-Invite Links**: Blocks unauthorized `discord.gg/...` and `discord.com/invite/...` links.
2. **🚫 Custom Word Blacklist**: Blocks your server's banned words and scam phrases (smart whole-word matching prevents false positives!).
3. **📢 Anti-Mass Mention**: Blocks messages pinging **5 or more users** at once, or unauthorized `@everyone`/`@here` attempts.
4. **⚡ Anti-Spam / Flood**: Deletes messages if someone sends **more than 5 messages in 5 seconds**, and automatically applies a **1-minute timeout** if they hit **8+ messages in 5 seconds**.
5. **🚨 Auto Anti-Raid Join Guard**: Detects sudden join raids (**5+ members joining within 10 seconds**), places incoming raid accounts on a **10-minute containment timeout**, and alerts `#mod-logs`!

### 🛡️ Automatic Staff Exemptions
AutoMod **never** deletes messages from:
* The **Server Owner**
* Any **Bot**
* Members with **Administrator**, **Manage Server**, or **Manage Messages** permissions

---

## 📑 Commands in This Guide
1. [`/automod status`](#-automod-status) — Check all 5 shields
2. [`/automod toggle`](#-automod-toggle) — Turn individual shields On or Off
3. [`/automod word add`](#-automod-word-add) — Add a word/phrase to the blacklist *(Admin)*
4. [`/automod word remove`](#-automod-word-remove) — Remove a word from the blacklist *(Admin)*
5. [`/automod word list`](#-automod-word-list) — View all blacklisted words privately *(Admin)*
6. [What Members & Logs See When Triggered](#-what-members--logs-see-when-automod-triggers)

---

## 🔍 `/automod status`

Displays the live On/Off status of all five AutoMod shields and lists who is exempt.

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/automod status` |
| **Who Can Use It** | `@everyone` |
| **Bot Needs** | `Send Messages`, `Embed Links` |
| **Where It Works** | Any server text channel |
| **What Discord Shows** | Public Embed |

### 2. Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 1:20 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 🛡️ Auto-Moderation System Status                            │
│                                                             │
│ 🔗 Anti-Invite Links                                        │
│ 🟢 Enabled                                                  │
│                                                             │
│ 📢 Anti-Mass Mention                                        │
│ 🟢 Enabled (Blocks 5+ users)                                │
│                                                             │
│ ⚡ Anti-Spam / Flood                                        │
│ 🟢 Enabled (Deletes rapid flood > 5 msgs/5s)                │
│                                                             │
│ 🚫 Custom Word Blacklist                                    │
│ 🟢 Enabled (3 word(s))                                      │
│                                                             │
│ 🚨 Auto Anti-Raid Join Guard                                │
│ 🟢 Enabled (Flags 5+ joins/10s)                             │
│                                                             │
│ 🛡️ Exemptions                                               │
│ Server Owner, Administrators, and Members with              │
│ Manage Messages / Manage Server.                            │
│                                                             │
│ Use /automod toggle or /automod word to configure           │
│ protections.                                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 `/automod toggle`

Turns an individual AutoMod shield **On (`True`)** or **Off (`False`)**.

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/automod toggle filter_name:<choice> enabled:<True|False>` |
| **Who Can Use It** | Members with **Manage Server** (`Manage Guild`) permission |
| **Bot Needs** | `Manage Messages`, `Timeout Members` (`Moderate Members`) |
| **Where It Works** | Any server text channel |
| **What Discord Shows** | Public Embed |

### 2. Parameters
* **`filter_name`** *(Required)*: Pick from Discord's dropdown choices:
  * `Anti-Invite Links`
  * `Anti-Mass Mention`
  * `Anti-Spam / Flood`
  * `Custom Word Blacklist`
  * `Auto Anti-Raid Join Guard`
* **`enabled`** *(Required)*: Choose **`True`** (enable) or **`False`** (disable).

### 3. Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 1:25 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 🛡️ Auto-Mod Setting Updated                                 │
│ Anti-Invite Links is now 🔴 Disabled.                       │
│                                                             │
│ Updated by Moderator                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚫 `/automod word add`

Adds a banned word or scam phrase (`2` to `50` characters, case-insensitive, up to 100 entries per server).

### 1. Exact Step-by-Step Process in Discord
1. Type `/automod word add`.
2. Enter **`word`** (e.g., `free nitro` or a banned word) and press **`Enter`**.

### 2. Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 1:27 PM  👁️ Only you can see │
├─────────────────────────────────────────────────────────────┤
│ 🚫 Blacklisted Word Added                                   │
│ free nitro will now be automatically blocked by AutoMod.    │
└─────────────────────────────────────────────────────────────┘
```
*(If already present: `ℹ️ free nitro is already in the blacklist.`)*

---

## 🗑️ `/automod word remove`

Removes a word or phrase from your server's blacklist.

### Exact What You See in Discord
* **Removed:** `✅ Removed free nitro from the blacklist.` *(Only you can see this)*
* **Not found:** `❌ free nitro was not found in the blacklist.` *(Only you can see this)*

---

## 📋 `/automod word list`

Displays up to 50 blacklisted words privately (`👁️ Only you can see this`) so profanity or scam keywords never leak into public chat.

### Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 1:29 PM  👁️ Only you can see │
├─────────────────────────────────────────────────────────────┤
│ 🚫 AutoMod Blacklisted Words (2)                            │
│ badword, free nitro                                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚨 What Members & Logs See When AutoMod Triggers

When a regular member violates an active AutoMod rule, their message is **deleted immediately**, and RookieBot posts a brief warning that **auto-deletes itself after 5 seconds**:

* **External Discord Invite Blocked:**
  `⚠️ @Member, posting external Discord invite links is not allowed!`
* **Blacklisted Word / Phrase Blocked:**
  `⚠️ @Member, your message contained a restricted word or phrase.`
* **Mass Mention Blocked (5+ pings or unauthorized `@everyone`):**
  `⚠️ @Member, mass mentions and spam pings are prohibited!`
* **Chat Flood Warning (6–7 messages within 5 seconds):**
  `⚠️ @Member, please slow down! You are sending messages too quickly.`
* **Severe Flood Auto-Timeout (8+ messages within 5 seconds):**
  `⏳ @Member was placed on a 1-minute timeout for spamming.`
* **Anti-Raid Join Burst (posted to `#mod-logs` when 5+ members join within 10s):**
  ```text
  ┌─────────────────────────────────────────────────────────────┐
  │ 🚨 Anti-Raid Alert Triggered                                │
  │ Detected 5 joins within 10 seconds!                         │
  │ Incoming join @Raider (123456789) has been placed on a      │
  │ 10-minute containment timeout.                              │
  └─────────────────────────────────────────────────────────────┘
  ```
