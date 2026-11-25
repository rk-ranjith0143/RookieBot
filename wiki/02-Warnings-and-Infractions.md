# ⚠️ Module 2: Warning & Infraction Tracking System

RookieBot saves every formal warning in its persistent SQLite database and **automatically escalates punishments** when a member accumulates too many warnings.

### 🔄 Automatic 3 → 5 → 7 Escalation Ladder
| Total Warnings Reached | Automatic Punishment |
| :--- | :--- |
| **3 Warnings** | ⏳ **1-Hour Timeout** automatically applied |
| **5 Warnings** | 👢 **Automatic Kick** from the server |
| **7+ Warnings** | 🔨 **Automatic Ban** from the server |

> [!NOTE]
> If you configured a Mod-Log channel with `/setlogs`, every `/warn` embed is also mirrored automatically into your audit log channel!

---

## 📑 Commands in This Guide
1. [`/warn`](#-warn) — Issue a warning and trigger auto-escalation
2. [`/warnings`](#-warnings) — View a member's infraction history
3. [`/delwarn`](#-delwarn) — Delete one specific warning by ID
4. [`/clearwarns`](#-clearwarns) — Reset all warnings for a member

---

## ⚠️ `/warn`

Issues a formal warning, sends a Direct Message embed to the member, records a unique numeric **Infraction ID** (e.g., `#12`), and checks the 3-5-7 auto-escalation thresholds.

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/warn member:<@user> [reason:<text>]` |
| **Who Can Use It** | Members with **Timeout Members** (`Moderate Members`) permission |
| **Bot Needs** | **Timeout Members** permission (+ **Kick** / **Ban** if escalation reaches 5 or 7) |
| **Where It Works** | Any server text channel |
| **What Discord Shows** | Public Embed + Member DM + Automatic copy in `/setlogs` channel (if set) |

### 2. Parameters
* **`member`** *(Required)*: The member receiving the warning.
* **`reason`** *(Optional)*: Explanation of the rule broken. Defaults to `No reason provided`.

### 3. Exact Step-by-Step Process in Discord
1. Type `/warn` in any server text channel and select the command.
2. In **`member`**, select the member to warn.
3. *(Optional)* Click **`reason`** and describe the violation (e.g., `Disrespectful behavior in #general`).
4. Press **`Enter`**.

### 4. Exact What You See in Discord

**A. Direct Message sent to the warned member:**
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 1:00 PM                        │
├─────────────────────────────────────────────────────────────┤
│ ⚠️ Warning Received in My Community Server                   │
│ You have been formally warned by staff.                     │
│ Reason: Disrespectful behavior in #general                  │
│ Total Warnings: 3                                           │
└─────────────────────────────────────────────────────────────┘
```

**B. Public Embed in channel (example when hitting Warning #3):**
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 1:00 PM                        │
├─────────────────────────────────────────────────────────────┤
│ ⚠️ Member Warned                                            │
│                                                             │
│ Member                                                      │
│ @Troublemaker (troublemaker#0000 - 112233445566778899)      │
│                                                             │
│ Moderator       Total Warnings       Infraction ID          │
│ @Moderator      3                    #14                    │
│                                                             │
│ Reason                                                      │
│ Disrespectful behavior in #general                          │
│                                                             │
│ Punishment Escalation                                       │
│ ⏳ Auto-Escalation: Reached 3 warnings ➔ Member Timed Out   │
│ for 1 hour!                                                 │
└─────────────────────────────────────────────────────────────┘
```

### 5. Real-World Examples
* `/warn member:@Member reason:Spamming caps in chat`
* `/warn member:@Member` *(uses default reason `No reason provided`)*

### 6. Common Errors & Solutions
* **`❌ You cannot warn yourself!`** / **`❌ You cannot warn the bot!`** / **`❌ You cannot warn the server owner!`** → Safety guards prevent invalid targets.
* **`❌ You cannot warn someone with a role equal to or higher than yours!`** → Role hierarchy check failed.
* **`⚠️ Escalation triggered but failed: ...`** → RookieBot issued the warning, but lacked `Kick Members` or `Ban Members` permission (or had a lower role) when trying to auto-punish at 5 or 7 warnings.

---

## 📋 `/warnings`

Displays the last 15 warnings/infractions for any member (or yourself if left blank).

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/warnings [member:<@user>]` |
| **Who Can Use It** | `@everyone` (All server members) |
| **Bot Needs** | `Send Messages`, `Embed Links` |
| **Where It Works** | Any server text channel |
| **What Discord Shows** | Public Embed (or Ephemeral notice if 0 warnings) |

### 2. Parameters
* **`member`** *(Optional)*: Member whose infractions you want to inspect. Defaults to **you**.

### 3. Exact Step-by-Step Process in Discord
1. Type `/warnings`.
2. *(Optional)* Select a **`member`** to check their history, or leave blank to check your own.
3. Press **`Enter`**.

### 4. Exact What You See in Discord

**A. When the member has recorded warnings:**
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 1:05 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 📋 Infraction History for Troublemaker                      │
│ • #12 [WARN] - 2 days ago by @Moderator                     │
│   └ Reason: Spamming emojis                                 │
│ • #14 [WARN] - 5 minutes ago by @Moderator                  │
│   └ Reason: Disrespectful behavior in #general              │
│                                                             │
│ Total Infractions: 2                                        │
└─────────────────────────────────────────────────────────────┘
```

**B. When the member has zero warnings:**
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 1:05 PM  👁️ Only you can see │
│ ✅ @GoodMember has no recorded warnings or infractions.     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗑️ `/delwarn`

Deletes a single warning using its `#ID` shown in `/warn` or `/warnings` (which also lowers the member's active warning count).

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/delwarn infraction_id:<number>` |
| **Who Can Use It** | Members with **Timeout Members** (`Moderate Members`) permission |
| **Bot Needs** | `Send Messages` |
| **Where It Works** | Any server text channel |
| **What Discord Shows** | Public message if deleted / Ephemeral error if not found |

### 2. Parameters
* **`infraction_id`** *(Required)*: The numeric warning ID (for `#14`, type **`14`** without the `#`).

### 3. Exact Step-by-Step Process in Discord
1. Run `/warnings member:@User` to check the warning ID (for example, `#14`).
2. Type `/delwarn` and enter **`14`** in **`infraction_id`**.
3. Press **`Enter`**.

### 4. Exact What You See in Discord
* **If found & deleted:**
  ```text
  🤖 RookieBot  [APP]  Today at 1:10 PM
  ✅ Infraction #14 has been deleted.
  ```
* **If ID does not exist in this server:**
  ```text
  🤖 RookieBot  [APP]  Today at 1:10 PM  👁️ Only you can see
  ❌ Infraction #999 not found for this server.
  ```

---

## 🧹 `/clearwarns`

Permanently deletes **all** warnings and infractions recorded for a member in this server.

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/clearwarns member:<@user>` |
| **Who Can Use It** | Members with **Administrator** permission |
| **Bot Needs** | `Send Messages` |
| **Where It Works** | Any server text channel |
| **What Discord Shows** | Public confirmation message |

### 2. Parameters
* **`member`** *(Required)*: The member whose infraction history you want to wipe clean.

### 3. Exact Step-by-Step Process in Discord
1. Type `/clearwarns` in chat.
2. Select the target user in **`member`**.
3. Press **`Enter`**.

### 4. Exact What You See in Discord
```text
🤖 RookieBot  [APP]  Today at 1:15 PM
🧹 Cleared 3 warning(s) for @Troublemaker.
```
