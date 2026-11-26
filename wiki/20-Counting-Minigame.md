# 🔢 Module 20: Counting Channel Minigame

Turn any text channel into an addictive collaborative counting game with SQLite streak persistence, high-score tracking, optional safe arithmetic expressions (`40 + 2`), and player leaderboards.

---

## 📑 Commands in This Guide
1. [`/counting setup`](#-counting-setup) — Configure the counting channel and math expression mode
2. [`/counting stats`](#-counting-stats) — Inspect current count, all-time high score, and user accuracy
3. [`/counting leaderboard`](#-counting-leaderboard) — View the Top 10 counters in the server
4. [`/counting disable`](#-counting-disable) — Turn off the counting minigame

---

## ⚙️ `/counting setup`

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/counting setup channel:<#channel> [allow_math:<True|False>]` |
| **Who Can Use It** | Members with **Manage Channels** permission |
| **Bot Needs** | **Send Messages** & **Add Reactions** in the counting channel |
| **Response Visibility** | Public Embed |

### 2. How the Minigame Works
1. Members take turns posting the next number (`1`, `2`, `3`, ...).
2. If **Math Expressions** are enabled, players can also post valid integer math such as `40 + 2` or `(10 + 5) * 2`. Non-math chat messages are ignored safely without breaking the streak!
3. RookieBot reacts with **`✅`** on valid numbers, **`💯`** on multiples of `100`, and **`🏆`** whenever the server sets a new all-time high score!
4. Posting the **wrong number** or counting **twice in a row** reacts with **`❌`**, logs a ruined count, and resets the streak back to **1**.

### 3. Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 9:15 AM                        │
├─────────────────────────────────────────────────────────────┤
│ 🔢 Counting Channel Configured                              │
│ The counting minigame is now active in #counting!           │
│                                                             │
│ Next Number               Math Expressions                  │
│ 1                         Allowed ✅                        │
│                                                             │
│ Rules: Count +1 in order. No counting twice in a row!       │
└─────────────────────────────────────────────────────────────┘
```

**When a Streak Breaks:**
> ❌ @Member ruined the count at **42**! You cannot count two numbers in a row.
> Next number: **1**.

---

## 📊 `/counting stats`

Shows the active counting channel, current streak, next expected number, all-time high score, and an individual player's correct vs. ruined count record.

* **Syntax:** `/counting stats [member:<@user>]`

---

## 🏆 `/counting leaderboard`

Displays the Top 10 server counters ranked by total valid numbers counted.

* **Syntax:** `/counting leaderboard`
* **Exact Response:** Gold embed titled **🏆 Top Server Counters** (`🥇 @User — **120** correct (ruined: 1)`).

---

## 🛑 `/counting disable`

Disables the counting minigame in the server.

* **Syntax:** `/counting disable`
* **Exact Response:** `🛑 Counting minigame disabled for this server.`
