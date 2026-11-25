# 🛡️ Module 1: Core Moderation Suite

Keep your Discord server safe, clean, and under control. This guide explains every moderation command with the **exact steps** inside Discord and **exact previews** of what you and your members will see on screen.

> [!TIP]
> **Role Hierarchy Rule (Important!)**
> Discord never allows a moderator or a bot to kick, ban, or timeout someone whose highest role is **equal to or higher** than theirs.
> Make sure **RookieBot's role** is dragged above regular member roles in **Server Settings → Roles**.

---

## 📑 Commands in This Guide
1. [`/kick`](#-kick) — Remove a member from the server
2. [`/ban`](#-ban) — Permanently ban a user (with optional message cleanup)
3. [`/unban`](#-unban) — Unban a user by their User ID
4. [`/timeout`](#-timeout) — Temporarily mute a member (1 min to 28 days)
5. [`/untimeout`](#-untimeout) — Remove an active timeout early
6. [`/clear`](#-clear) — Bulk delete up to 100 messages
7. [`/slowmode`](#-slowmode) — Set a typing cooldown in a text channel
8. [`/lock`](#-lock) — Prevent `@everyone` from sending messages in a channel
9. [`/unlock`](#-unlock) — Re-open a locked channel

---

## 👢 `/kick`

Removes a member from the server immediately. They can rejoin later if they have a valid invite link.

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/kick member:<@user> [reason:<text>]` |
| **Who Can Use It** | Members with **Kick Members** permission |
| **Bot Needs** | **Kick Members** permission + higher role than target |
| **Where It Works** | Any server text channel |
| **What Discord Shows** | Public Embed in channel + Direct Message to the kicked user |

### 2. Parameters
* **`member`** *(Required)*: Pick the server member from Discord's user list.
* **`reason`** *(Optional)*: Why they are being kicked. Defaults to `No reason provided`.

### 3. Exact Step-by-Step Process in Discord
1. Click the message bar in any text channel and type `/kick`.
2. Click **`/kick`** in the Discord popup menu (`Kick a member from the server`).
3. In the **`member`** box, select or type the member's name (e.g., `@Spammer`).
4. *(Optional)* Press **`Tab`** or click **`+1 more`** / **`reason`**, then type your reason (e.g., `Ignoring staff warnings`).
5. Press **`Enter`** to send.

### 4. Exact What You See in Discord

**A. What the kicked member receives in their DMs (if their DMs are open):**
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 12:00 PM                       │
│ ⚠️ You were kicked from My Community Server.                │
│ Reason: Ignoring staff warnings                             │
└─────────────────────────────────────────────────────────────┘
```

**B. What appears publicly in the channel:**
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 12:00 PM                       │
├─────────────────────────────────────────────────────────────┤
│ 👢 Member Kicked                                            │
│                                                             │
│ Member                                                      │
│ @Spammer (spammer#0000)                                     │
│                                                             │
│ Moderator                                                   │
│ @Moderator                                                  │
│                                                             │
│ Reason                                                      │
│ Ignoring staff warnings                                     │
└─────────────────────────────────────────────────────────────┘
```

### 5. Real-World Examples
* **Quick kick without a reason:**
  `/kick member:@TrollUser`
* **Kick with an audit reason:**
  `/kick member:@TrollUser reason:Posting inappropriate links after warning`

### 6. Common Errors & Solutions
* **`❌ You cannot kick yourself!`** → You selected your own account.
* **`❌ You cannot kick the server owner!`** → Server owners cannot be kicked.
* **`❌ You cannot kick someone with a role equal to or higher than yours!`** → Your top role is not higher than the target's top role.
* **`❌ I cannot kick someone with a role equal to or higher than my highest role!`** → Go to **Server Settings → Roles** and drag **RookieBot** above the target member's highest role.

---

## 🔨 `/ban`

Bans a user from the server permanently (until unbanned) and optionally deletes their recent messages. You can even ban someone who already left the server by pasting their User ID into `user`.

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/ban user:<@user or ID> [delete_message_days:<choice>] [reason:<text>]` |
| **Who Can Use It** | Members with **Ban Members** permission |
| **Bot Needs** | **Ban Members** permission + higher role than target (if in server) |
| **Where It Works** | Any server text channel |
| **What Discord Shows** | Public Embed in channel + Direct Message to target (if in server) |

### 2. Parameters
* **`user`** *(Required)*: Select a server member or paste a Discord User ID.
* **`delete_message_days`** *(Optional)*: Choose from Discord's dropdown:
  * `Don't delete any messages` *(Default)*
  * `Previous 24 Hours (1 day)`
  * `Previous 7 Days`
* **`reason`** *(Optional)*: Reason saved in Discord Audit Log and shown in the embed. Defaults to `No reason provided`.

### 3. Exact Step-by-Step Process in Discord
1. Type `/ban` in the chat box and select **`/ban`** from the slash menu.
2. In the **`user`** box, pick the user or paste their Discord User ID.
3. *(Optional)* Click **`delete_message_days`** and choose **`Don't delete any messages`**, **`Previous 24 Hours (1 day)`**, or **`Previous 7 Days`**.
4. *(Optional)* Click **`reason`** and type why they are being banned.
5. Press **`Enter`**.

### 4. Exact What You See in Discord

**A. Direct Message sent to the user before the ban (if they are in the server and DMs are open):**
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 12:05 PM                       │
│ 🔨 You were banned from My Community Server.                │
│ Reason: Raid account                                        │
└─────────────────────────────────────────────────────────────┘
```

**B. Public embed posted in the channel:**
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 12:05 PM                       │
├─────────────────────────────────────────────────────────────┤
│ 🔨 Member Banned                                            │
│                                                             │
│ User                                                        │
│ @Raider (raider_acc - 123456789012345678)                   │
│                                                             │
│ Moderator              Deleted Messages                     │
│ @Moderator             7 day(s)                             │
│                                                             │
│ Reason                                                      │
│ Raid account                                                │
└─────────────────────────────────────────────────────────────┘
```

### 5. Real-World Examples
* **Ban a raid account and wipe 7 days of spam:**
  `/ban user:@Raider delete_message_days:Previous 7 Days reason:Spamming scam links`
* **Ban without deleting messages:**
  `/ban user:@RuleBreaker reason:Repeated harassment`

### 6. Common Errors & Solutions
* **`❌ I cannot ban someone with a role equal to or higher than my highest role!`** → Drag **RookieBot** higher in **Server Settings → Roles**.
* **`❌ You cannot ban yourself!` / `❌ I cannot ban myself!` / `❌ You cannot ban the server owner!`** → Self-ban, bot-ban, and owner-ban are blocked for safety.

---

## 🕊️ `/unban`

Removes an active ban from a user using their numeric Discord User ID.

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/unban user_id:<ID> [reason:<text>]` |
| **Who Can Use It** | Members with **Ban Members** permission |
| **Bot Needs** | **Ban Members** permission |
| **Where It Works** | Any server text channel |
| **What Discord Shows** | Public Embed in channel |

### 2. Parameters
* **`user_id`** *(Required)*: The 17–20 digit numeric Discord ID of the banned user.
  * *How to find it:* Enable **Developer Mode** in Discord (**User Settings → Advanced → Developer Mode**), go to **Server Settings → Bans**, right-click the user, and click **Copy User ID**.
* **`reason`** *(Optional)*: Reason for unbanning. Defaults to `Unbanned by moderator`.

### 3. Exact Step-by-Step Process in Discord
1. Copy the banned user's numeric ID from **Server Settings → Bans**.
2. Type `/unban` in a text channel.
3. Paste the numeric ID into **`user_id`**.
4. *(Optional)* Click **`reason`** and enter an explanation (e.g., `Ban appeal accepted`).
5. Press **`Enter`**.

### 4. Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 12:10 PM                       │
├─────────────────────────────────────────────────────────────┤
│ 🕊️ User Unbanned                                            │
│                                                             │
│ User                                                        │
│ @FormerMember (former_user - 123456789012345678)            │
│                                                             │
│ Moderator                                                   │
│ @Moderator                                                  │
│                                                             │
│ Reason                                                      │
│ Ban appeal accepted                                         │
└─────────────────────────────────────────────────────────────┘
```

### 5. Real-World Examples
* `/unban user_id:123456789012345678 reason:Appeal approved by admin team`

### 6. Common Errors & Solutions
* **`❌ Invalid User ID. Please provide a numeric Discord User ID (e.g., 123456789012345678).`** → You typed a `@username` instead of numbers. Paste only the digits.
* **`❌ No ban found for User ID 123456789012345678 in this server.`** → Double-check the ID in **Server Settings → Bans**; the user is not currently banned.

---

## ⏳ `/timeout`

Temporarily mutes a member using Discord's native Timeout feature (they cannot send messages, react, or join voice channels until the timer expires).

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/timeout member:<@user> duration:<minutes> [reason:<text>]` |
| **Who Can Use It** | Members with **Timeout Members** (`Moderate Members`) permission |
| **Bot Needs** | **Timeout Members** (`Moderate Members`) permission + higher role |
| **Where It Works** | Any server text channel |
| **What Discord Shows** | Public Embed + Direct Message to the muted member |

### 2. Parameters
* **`member`** *(Required)*: The member to timeout.
* **`duration`** *(Required)*: Number of **minutes** (`1` to `40320` minutes = up to 28 days).
  * Quick reference: `10` = 10 mins, `60` = 1 hour, `1440` = 1 day, `10080` = 7 days.
* **`reason`** *(Optional)*: Reason for the timeout. Defaults to `No reason provided`.

### 3. Exact Step-by-Step Process in Discord
1. Type `/timeout` and select the command.
2. Pick the target user in **`member`**.
3. Enter a whole number of minutes in **`duration`** (e.g., `60` for 1 hour).
4. *(Optional)* Enter a **`reason`** (e.g., `Cool down after argument`).
5. Press **`Enter`**.

### 4. Exact What You See in Discord

**A. Direct Message sent to the member:**
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 12:15 PM                       │
│ ⏳ You have been timed out in My Community Server for       │
│ 1 hour(s) 0 minute(s).                                      │
│ Reason: Cool down after argument                            │
└─────────────────────────────────────────────────────────────┘
```

**B. Public Embed in channel:**
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 12:15 PM                       │
├─────────────────────────────────────────────────────────────┤
│ ⏳ Member Timed Out                                         │
│                                                             │
│ Member                                                      │
│ @User (username#0000)                                       │
│                                                             │
│ Duration               Moderator                            │
│ 1 hour(s) 0 minute(s)  @Moderator                           │
│                                                             │
│ Reason                                                      │
│ Cool down after argument                                    │
└─────────────────────────────────────────────────────────────┘
```

### 5. Real-World Examples
* **10-minute cooldown:** `/timeout member:@User duration:10 reason:Spamming chat`
* **24-hour mute:** `/timeout member:@User duration:1440 reason:Inappropriate behavior`

### 6. Common Errors & Solutions
* **`❌ Duration must be between 1 minute and 40,320 minutes (28 days).`** → Discord limits timeouts to 28 days max (`40320` minutes).

---

## 🔊 `/untimeout`

Immediately removes an active timeout so the member can talk again.

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/untimeout member:<@user> [reason:<text>]` |
| **Who Can Use It** | Members with **Timeout Members** (`Moderate Members`) permission |
| **Bot Needs** | **Timeout Members** permission + higher role |
| **Where It Works** | Any server text channel |
| **What Discord Shows** | Public Embed |

### 2. Parameters
* **`member`** *(Required)*: The currently timed-out member.
* **`reason`** *(Optional)*: Reason for ending the timeout early. Defaults to `Timeout removed by moderator`.

### 3. Exact Step-by-Step Process in Discord
1. Type `/untimeout` and select the command.
2. Select the timed-out user in **`member`**.
3. *(Optional)* Add a **`reason`** and press **`Enter`**.

### 4. Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 12:20 PM                       │
├─────────────────────────────────────────────────────────────┤
│ 🔊 Timeout Removed                                          │
│ Timeout removed for @User (username#0000).                  │
│                                                             │
│ Moderator                                                   │
│ @Moderator                                                  │
│                                                             │
│ Reason                                                      │
│ Apologized in ticket                                        │
└─────────────────────────────────────────────────────────────┘
```

### 5. Common Errors & Solutions
* **`❌ @User is not currently timed out.`** *(Only you can see this)* → That member does not have an active timeout.

---

## 🧹 `/clear`

Bulk-deletes between `1` and `100` recent messages from the current channel, optionally filtering by one specific user.

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/clear amount:<1-100> [member:<@user>]` |
| **Who Can Use It** | Members with **Manage Messages** permission |
| **Bot Needs** | **Manage Messages** permission |
| **Where It Works** | Current text channel |
| **What Discord Shows** | Ephemeral confirmation *(Only you can see this)* |

### 2. Parameters
* **`amount`** *(Required)*: How many recent messages to scan/delete (`1` to `100`).
* **`member`** *(Optional)*: If chosen, scans the last `amount` messages and deletes **only** messages sent by this member.

### 3. Exact Step-by-Step Process in Discord
1. Go to the channel you want to clean.
2. Type `/clear` and enter a number in **`amount`** (e.g., `25`).
3. *(Optional)* Pick a user in **`member`** if you only want to delete their messages.
4. Press **`Enter`**. RookieBot will briefly show *`RookieBot is thinking...`* privately, delete the messages, and update you privately.

### 4. Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 12:25 PM  👁️ Only you can see │
│ 🧹 Successfully cleared 25 message(s) from @Spammer!        │
└─────────────────────────────────────────────────────────────┘
```

### 5. Real-World Examples
* **Delete the last 50 messages in chat:** `/clear amount:50`
* **Delete only @Troll's messages within the last 100 messages:** `/clear amount:100 member:@Troll`

### 6. Common Errors & Solutions
* **`❌ Please specify an amount between 1 and 100.`** → Enter a number from `1` to `100`.
* **`❌ Failed to delete messages: ... (Discord does not permit bulk deleting messages older than 14 days).`** → Discord's API blocks bots from bulk-deleting messages older than 2 weeks.

---

## ⏱️ `/slowmode`

Sets or disables the slowmode message cooldown in a text channel.

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/slowmode seconds:<0-21600> [channel:<#channel>]` |
| **Who Can Use It** | Members with **Manage Channels** permission |
| **Bot Needs** | **Manage Channels** permission |
| **Where It Works** | Any text channel |
| **What Discord Shows** | Public confirmation message |

### 2. Parameters
* **`seconds`** *(Required)*: Cooldown delay in seconds (`0` to turn off, up to `21600` = 6 hours).
* **`channel`** *(Optional)*: Target text channel. If left blank, applies to the channel you are currently typing in.

### 3. Exact Step-by-Step Process in Discord
1. Type `/slowmode`.
2. In **`seconds`**, enter `5` (for 5 seconds) or `0` (to turn slowmode off).
3. *(Optional)* Select a different **`channel`**.
4. Press **`Enter`**.

### 4. Exact What You See in Discord
* **When enabling (`seconds > 0`):**
  ```text
  🤖 RookieBot  [APP]  Today at 12:30 PM
  ⏱️ Slowmode set to 10s for #general.
  ```
* **When disabling (`seconds = 0`):**
  ```text
  🤖 RookieBot  [APP]  Today at 12:31 PM
  ✅ Slowmode disabled for #general.
  ```

---

## 🔒 `/lock`

Stops `@everyone` from sending messages in a text channel (useful during raids or announcements). Staff with explicit channel permissions can still talk.

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/lock [channel:<#channel>] [reason:<text>]` |
| **Who Can Use It** | Members with **Manage Channels** permission |
| **Bot Needs** | **Manage Channels** permission |
| **Where It Works** | Any text channel |
| **What Discord Shows** | Public Lock Embed in the locked channel + Ephemeral confirmation to you |

### 2. Parameters
* **`channel`** *(Optional)*: Channel to lock. Defaults to your current channel.
* **`reason`** *(Optional)*: Explanation shown inside the lock banner. Defaults to `No reason provided`.

### 3. Exact Step-by-Step Process in Discord
1. Type `/lock` in the channel you want to lock (or pick another channel in **`channel`**).
2. *(Optional)* Type a **`reason`** (e.g., `Raid protection`).
3. Press **`Enter`**.

### 4. Exact What You See in Discord

**A. Public banner posted inside the locked channel:**
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 12:35 PM                       │
├─────────────────────────────────────────────────────────────┤
│ 🔒 Channel Locked                                           │
│ This channel has been locked by staff.                      │
│ Reason: Raid protection                                     │
└─────────────────────────────────────────────────────────────┘
```

**B. Private confirmation only you see:**
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 12:35 PM  👁️ Only you can see │
│ 🔒 #general has been locked.                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔓 `/unlock`

Restores the `@everyone` send-message permission for a channel previously locked with `/lock`.

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/unlock [channel:<#channel>]` |
| **Who Can Use It** | Members with **Manage Channels** permission |
| **Bot Needs** | **Manage Channels** permission |
| **Where It Works** | Any text channel |
| **What Discord Shows** | Public Unlock Embed in target channel + Ephemeral confirmation to you |

### 2. Parameters
* **`channel`** *(Optional)*: Channel to unlock. Defaults to the current channel.

### 3. Exact Step-by-Step Process in Discord
1. Type `/unlock`.
2. *(Optional)* Select **`channel`** if unlocking a different channel.
3. Press **`Enter`**.

### 4. Exact What You See in Discord

**A. Public banner posted inside the unlocked channel:**
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 12:40 PM                       │
├─────────────────────────────────────────────────────────────┤
│ 🔓 Channel Unlocked                                         │
│ This channel has been unlocked. Members can now send        │
│ messages.                                                   │
└─────────────────────────────────────────────────────────────┘
```

**B. Private confirmation only you see:**
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 12:40 PM  👁️ Only you can see │
│ 🔓 #general has been unlocked.                              │
└─────────────────────────────────────────────────────────────┘
```
