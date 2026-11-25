# 📈 Module 9: Chat XP, Leaderboards & Level Roles

Reward active community members automatically! Every message a member sends earns **15–25 random XP** (with a **60-second cooldown** to prevent spam). Reaching new levels posts a **Level Up** celebration card and unlocks automatic **Level Role Rewards**.

### 🧮 How Leveling Works
* Every level requires **`Current Level × 100` XP**:
  * Level 1 → Level 2: `100 XP`
  * Level 2 → Level 3: `200 XP`
  * Level 5 → Level 6: `500 XP`
* Bots do not earn XP.

---

## 📑 Commands & Events in This Guide
1. [Automatic `🎉 Level Up!` Card](#-what-appears-in-chat-on-level-up)
2. [`/rank`](#-rank) — View your rank card and progress bar
3. [`/leaderboard`](#-leaderboard) — View the Top 10 server chatters
4. [`/levelrole add`](#-levelrole-add) — Auto-award a role when reaching a level
5. [`/levelrole list`](#-levelrole-list) — See all configured level role milestones
6. [`/levelrole remove`](#-levelrole-remove) — Delete a level milestone reward

---

## 🎉 What Appears in Chat on Level Up

Whenever a member crosses the XP threshold in chat, RookieBot posts this card directly in the channel (and unlocks any role assigned to that level):

```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 3:00 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 🎉 Level Up!                                                │
│ Congratulations @Alex! You advanced to Level 5! 🚀          │
│ 🎁 Role Reward Unlocked: @Active Member!                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 `/rank`

Shows a visual rank card with server rank (`#1`, `#2`, etc.), current level, XP toward next level, and an ASCII progress bar (`[▓▓▓▓▓░░░░░] 50%`).

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/rank [member:<@user>]` |
| **Who Can Use It** | `@everyone` |
| **Bot Needs** | `Send Messages`, `Embed Links` |
| **Response Visibility** | Public Embed |

### 2. Parameters
* **`member`** *(Optional)*: Inspect someone else's rank card, or leave blank for your own.

### 3. Exact Step-by-Step Process in Discord
1. Type `/rank`.
2. *(Optional)* Select a **`member`**.
3. Press **`Enter`**.

### 4. Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 3:02 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 📊 Rank Card — Alex                                         │
│                                                             │
│ 🏆 Server Rank     ⭐ Level           ✨ XP Progress        │
│ #2                 Level 5            240 / 500 XP          │
│                                                             │
│ 📈 Progress to Next Level                                   │
│ [▓▓▓▓▓░░░░░] 48%                                            │
│                                                             │
│ Requested by Alex                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🏆 `/leaderboard`

Displays the **Top 10** most active members in the server ranked by Level and XP.

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/leaderboard` |
| **Who Can Use It** | `@everyone` |
| **Response Visibility** | Public Embed (or Ephemeral notice if nobody has XP yet) |

### 2. Exact Step-by-Step Process in Discord
1. Type `/leaderboard` in chat and press **`Enter`**.

### 3. Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 3:05 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 🏆 My Community Server — XP Leaderboard                     │
│                                                             │
│ 🥇 @Sarah — Level 12 (850 XP)                               │
│                                                             │
│ 🥈 @Alex — Level 5 (240 XP)                                 │
│                                                             │
│ 🥉 @Sam — Level 4 (110 XP)                                  │
│                                                             │
│ #4 @Jordan — Level 2 (95 XP)                                │
│                                                             │
│ Earn XP by chatting in the server!                          │
└─────────────────────────────────────────────────────────────┘
```
*(If no chat activity exists yet: `📜 No activity recorded yet! Start chatting to earn XP and claim the top spot.`)*

---

## 🎁 `/levelrole add`

Links a Discord role to a specific level (`1` to `100`). Anyone who hits that level automatically receives the role.

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/levelrole add level:<1-100> role:<@role>` |
| **Who Can Use It** | Members with **Manage Roles** permission |
| **Bot Needs** | **Manage Roles** + higher role than the reward role |
| **Response Visibility** | Public Embed |

### 2. Parameters
* **`level`** *(Required)*: Target level (`1` to `100`).
* **`role`** *(Required)*: Role to reward automatically.

### 3. Exact Step-by-Step Process in Discord
1. Type `/levelrole add`.
2. Enter a number in **`level`** (e.g., `5`).
3. Pick a **`role`** (e.g., `@Active Member`).
4. Press **`Enter`**.

### 4. Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 3:10 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 🎁 Level Reward Configured                                  │
│ Members will automatically receive @Active Member when they │
│ reach Level 5!                                              │
└─────────────────────────────────────────────────────────────┘
```

### 5. Common Errors & Solutions
* **`❌ I cannot assign @Role because it is equal to or higher than my highest role.`** → Move RookieBot above `@Role` in **Server Settings → Roles**.

---

## 📜 `/levelrole list`

Lists every level milestone role configured on the server.

### 1. Exact Step-by-Step Process in Discord
1. Type `/levelrole list` and press **`Enter`**.

### 2. Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 3:12 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 🎁 Level Role Rewards (2)                                   │
│ • Level 5 ➔ @Active Member                                  │
│ • Level 10 ➔ @Server Veteran                                │
└─────────────────────────────────────────────────────────────┘
```
*(If none configured: `ℹ️ No level roles configured yet. Use /levelrole add.`)*

---

## 🗑️ `/levelrole remove`

Removes an existing level role milestone.

### 1. Exact Step-by-Step Process in Discord
1. Type `/levelrole remove`.
2. Enter the **`level`** number (e.g., `5`) and press **`Enter`**.

### 2. Exact What You See in Discord
* **Success:** `✅ Removed role reward for Level 5.` *(Only you can see this)*
* **Not found:** `❌ No role reward was found for Level 5.` *(Only you can see this)*
