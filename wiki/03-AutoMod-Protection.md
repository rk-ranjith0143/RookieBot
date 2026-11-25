# 🛡️ Module 3: AutoMod & Anti-Raid Shields

RookieBot includes **3 automatic chat protection filters** that run 24/7 in the background—all **enabled by default** as soon as the bot joins your server.

### 🧱 Built-In Automatic Shields
1. **🔗 Anti-Invite Links**: Blocks unauthorized `discord.gg/...` and `discord.com/invite/...` links.
2. **📢 Anti-Mass Mention**: Blocks messages pinging **5 or more users** at once, or unauthorized `@everyone`/`@here` attempts.
3. **⚡ Anti-Spam / Flood**: Deletes messages if someone sends **more than 5 messages in 5 seconds**, and automatically applies a **1-minute timeout** if they hit **8+ messages in 5 seconds**.

### 🛡️ Automatic Staff Exemptions
AutoMod **never** deletes messages from:
* The **Server Owner**
* Any **Bot**
* Members with **Administrator**, **Manage Server**, or **Manage Messages** permissions

---

## 📑 Commands in This Guide
1. [`/automod status`](#-automod-status) — Check which shields are On or Off
2. [`/automod toggle`](#-automod-toggle) — Turn individual shields On or Off
3. [What Members See When Triggered](#-what-members-see-when-automod-triggers)

---

## 🔍 `/automod status`

Displays the live On/Off status of all three AutoMod shields and lists who is exempt.

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/automod status` |
| **Who Can Use It** | `@everyone` |
| **Bot Needs** | `Send Messages`, `Embed Links` |
| **Where It Works** | Any server text channel |
| **What Discord Shows** | Public Embed |

### 2. Exact Step-by-Step Process in Discord
1. Type `/automod status` in the message box.
2. Click **`/automod status`** from the slash popup.
3. Press **`Enter`** (no extra options needed).

### 3. Exact What You See in Discord
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
│ 🛡️ Exemptions                                               │
│ Server Owner, Administrators, and Members with              │
│ Manage Messages / Manage Server.                            │
│                                                             │
│ Use /automod toggle to configure individual protections.    │
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
| **Bot Needs** | `Manage Messages` (to delete rule-breaking msgs), `Timeout Members` (for flood timeout) |
| **Where It Works** | Any server text channel |
| **What Discord Shows** | Public Embed |

### 2. Parameters
* **`filter_name`** *(Required)*: Pick from Discord's dropdown choices:
  * `Anti-Invite Links`
  * `Anti-Mass Mention`
  * `Anti-Spam / Flood`
* **`enabled`** *(Required)*: Choose **`True`** (enable) or **`False`** (disable).

### 3. Exact Step-by-Step Process in Discord
1. Type `/automod toggle` and select the command.
2. In **`filter_name`**, click one of the 3 options from the list (e.g., `Anti-Invite Links`).
3. Press **`Tab`**, then select **`True`** or **`False`** in **`enabled`**.
4. Press **`Enter`**.

### 4. Exact What You See in Discord
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

### 5. Real-World Examples
* **Allow Discord invite links (for a partner channel server):**
  `/automod toggle filter_name:Anti-Invite Links enabled:False`
* **Re-enable Anti-Spam:**
  `/automod toggle filter_name:Anti-Spam / Flood enabled:True`

---

## 🚨 What Members See When AutoMod Triggers

When a regular member violates an active AutoMod rule, their message is **deleted immediately**, and RookieBot posts a brief warning that **auto-deletes itself after 5 seconds** to keep chat clean:

* **External Discord Invite Blocked:**
  ```text
  🤖 RookieBot  [APP]
  ⚠️ @Member, posting external Discord invite links is not allowed!
  ```
* **Mass Mention Blocked (5+ pings or unauthorized `@everyone`):**
  ```text
  🤖 RookieBot  [APP]
  ⚠️ @Member, mass mentions and spam pings are prohibited!
  ```
* **Chat Flood Warning (6–7 messages within 5 seconds):**
  ```text
  🤖 RookieBot  [APP]
  ⚠️ @Member, please slow down! You are sending messages too quickly.
  ```
* **Severe Flood Auto-Timeout (8+ messages within 5 seconds):**
  ```text
  🤖 RookieBot  [APP]
  ⏳ @Member was placed on a 1-minute timeout for spamming.
  ```
