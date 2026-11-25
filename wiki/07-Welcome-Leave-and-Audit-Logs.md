# 👋 Module 7: Welcome, Leave & Audit Logging

Greet newcomers automatically with rich profile cards or custom text templates, announce departures, and record deleted/edited messages, leaves, bans, and unbans in a staff audit channel.

---

## 📑 Commands & Event Cards in This Guide
1. [`/setwelcome`](#-setwelcome) — Configure automated join greetings
2. [`/setleave`](#-setleave) — Configure automated leave notices
3. [`/setlogs`](#-setlogs) — Configure the staff audit log channel
4. [All 5 Audit Log Cards](#-exact-audit-log-events-logged-automatically)

---

## 👋 `/setwelcome`

Sets the channel where RookieBot greets new members (and optionally sets a custom text template instead of the default card). Leaving `channel` blank disables custom welcome configuration.

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/setwelcome [channel:<#channel>] [custom_message:<text>]` |
| **Who Can Use It** | Members with **Manage Server** (`Manage Guild`) permission |
| **Bot Needs** | `Send Messages`, `Embed Links` in the chosen channel |
| **Response Visibility** | Public Embed when enabling / Ephemeral when disabling |

### 2. Parameters & Supported Placeholders
* **`channel`** *(Optional)*: Text channel for greetings (e.g., `#welcome`). Leave blank to disable.
* **`custom_message`** *(Optional)*: Custom text template. Supported placeholders:
  * `{user}` → Mentions the user (`@Alex`)
  * `{username}` → Plain username (`alex`)
  * `{server}` → Server name (`My Community Server`)
  * `{count}` → New total member count (`152`)

### 3. Exact Step-by-Step Process in Discord
1. Type `/setwelcome`.
2. Select **`channel`** (e.g., `#welcome`).
3. *(Optional)* Enter **`custom_message`** (e.g., `Welcome {user} to {server}! You are member #{count}!`).
4. Press **`Enter`**.

### 4. Exact What You See in Discord

**A. Configuration confirmation:**
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 2:30 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 👋 Welcome System Configured                                │
│ New member greetings will be sent to #welcome.              │
│                                                             │
│ Template: Default Embed Welcome Card                        │
│                                                             │
│ Tags supported: {user}, {username}, {server}, {count}       │
└─────────────────────────────────────────────────────────────┘
```

**B. Default Welcome Card posted in `#welcome` when a member joins (if no `custom_message` is set):**
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 2:32 PM                        │
│ Welcome @Alex!                                              │
├─────────────────────────────────────────────────────────────┤
│ 👋 Welcome to My Community Server!                          │
│ Hey @Alex, welcome to the server! 🎉                        │
│ We're glad to have you here. Please make sure to check the  │
│ rules and enjoy your stay!                                  │
│                                                             │
│ Account Created        Member Count                         │
│ 2 years ago            #152                                 │
│                                                             │
│ User ID: 123456789012345678                                 │
└─────────────────────────────────────────────────────────────┘
```
*(Tip: If you don't run `/setwelcome`, RookieBot automatically falls back to Discord's System Channel or a channel named `welcome`, `welcomes`, `general`, `lobby`, or `chat`.)*

**C. When disabling (`/setwelcome` with no parameters):**
```text
🤖 RookieBot  [APP]  👁️ Only you can see this
🛑 Welcome greetings have been disabled.
```

---

## 👋 `/setleave`

Posts a notice whenever someone leaves the server.

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/setleave [channel:<#channel>] [custom_message:<text>]` |
| **Who Can Use It** | Members with **Manage Server** (`Manage Guild`) permission |
| **Supported Tags** | `{username}`, `{server}`, `{count}` |

### 2. Exact Step-by-Step Process in Discord
1. Type `/setleave`.
2. Select **`channel`** (e.g., `#goodbyes`), or leave blank to disable.
3. *(Optional)* Enter **`custom_message`** (e.g., `**{username}** has left {server}. We now have {count} members.`).
4. Press **`Enter`**.

### 3. Exact What You See in Discord

**A. Confirmation after setup:**
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 2:35 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 👋 Leave Messages Configured                                │
│ Departure notices will be sent to #goodbyes.                │
│                                                             │
│ Template: Default Goodbye Embed                             │
│                                                             │
│ Tags supported: {username}, {server}, {count}               │
└─────────────────────────────────────────────────────────────┘
```

**B. Default Goodbye Card when a member leaves:**
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 2:37 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 👋 Goodbye!                                                 │
│ alex#0000 has left the server. We now have 151 members.     │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 `/setlogs`

Assigns a private staff channel to receive automatic real-time audit logs whenever messages are deleted or edited, members leave/get banned/unbanned, or `/warn` is issued.

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/setlogs [channel:<#channel>]` |
| **Who Can Use It** | Members with **Manage Server** (`Manage Guild`) permission |
| **Bot Needs** | `Send Messages`, `Embed Links` in the log channel |
| **Response Visibility** | Confirmation card inside log channel + Ephemeral confirmation to you |

### 2. Exact Step-by-Step Process in Discord
1. Create a private `#mod-logs` channel visible only to staff and RookieBot.
2. Type `/setlogs` and pick **`channel:#mod-logs`** (or leave blank to disable logs).
3. Press **`Enter`**.

### 3. Exact What You See in Discord
* **Inside `#mod-logs`:**
  ```text
  ┌─────────────────────────────────────────────────────────────┐
  │ 🤖 RookieBot  [APP]  Today at 2:40 PM                        │
  ├─────────────────────────────────────────────────────────────┤
  │ 📋 Mod-Logs Configured                                      │
  │ Server audit events will now be logged to #mod-logs.        │
  │                                                             │
  │ Configured by AdminUser                                     │
  └─────────────────────────────────────────────────────────────┘
  ```
* **Private confirmation to you:**
  ```text
  🤖 RookieBot  [APP]  👁️ Only you can see this
  ✅ Mod-logs channel set to #mod-logs!
  ```
* **If disabled (`/setlogs` with empty `channel`):**
  ```text
  🤖 RookieBot  [APP]  👁️ Only you can see this
  🛑 Mod-logs have been disabled for this server.
  ```

---

## 🕵️ Exact Audit Log Events Logged Automatically

Once `/setlogs` is active, RookieBot automatically posts these cards into `#mod-logs`:

1. **🗑️ Message Deleted** (includes author, `#channel`, text content up to 1024 chars, attachment filenames, and Message ID)
2. **✏️ Message Edited** (includes author, `#channel`, clickable `[Go to Message]` jump link, `Before` text, `After` text, and Message ID)
3. **👋 Member Left** (includes member mention, ID, avatar, and updated `Total Members`)
4. **🔨 Member Banned** (includes user mention, ID, and avatar)
5. **🕊️ Member Unbanned** (includes user mention, ID, and avatar)
6. **⚠️ Member Warned** (mirrored automatically whenever a mod runs `/warn`)
