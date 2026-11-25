# 📨 Module 17: Invite & Referral Tracker

Automatically track who invited every new member using real Discord invite links! RookieBot counts **Regular** joins, subtracts **Left** members automatically when someone leaves, and lets staff award **Bonus** invites for referral contests.

> [!NOTE]
> Make sure RookieBot's role has the **Manage Server** (`Manage Guild`) permission so Discord allows it to read invite link usage counts!

---

## 📑 Commands in This Guide
**For All Members:**
1. [`/invites`](#-invites) — View your or another member's invite breakdown
2. [`/inviteleaderboard`](#-inviteleaderboard) — View the Top 10 server inviters

**For Server Staff:**
3. [`/invitebonus`](#-invitebonus-manage-server) — Add or subtract bonus invites
4. [`/invitereset`](#-invitereset-admin) — Reset all server invite stats

---

## 📨 `/invites`

Shows a clean breakdown of **Total Active Invites**, **Regular Joins**, **Left Members**, and **Bonus Invites** (`Total = Regular - Left + Bonus`).

### 1. Exact Step-by-Step Process in Discord
1. Type `/invites`.
2. *(Optional)* Select a **`member`** (or leave blank to view your own invites).
3. Press **`Enter`**.

### 2. Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 7:00 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 📨 Invite Stats — Alex                                      │
│ @Alex currently has 8 active invite(s)!                     │
│                                                             │
│ 👥 Regular           🚪 Left            🎁 Bonus            │
│ 7                    1                  2                   │
│                                                             │
│ Use /inviteleaderboard to see the top server inviters!      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🏆 `/inviteleaderboard`

Displays the **Top 10 server inviters** sorted by net total invites.

### Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 7:02 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 🏆 My Community Server — Invite Leaderboard                 │
│ 🥇 @Sarah — 14 Invites (15 regular • 1 left • 0 bonus)      │
│                                                             │
│ 🥈 @Alex — 8 Invites (7 regular • 1 left • 2 bonus)         │
│                                                             │
│ 🥉 @Sam — 5 Invites (5 regular • 0 left • 0 bonus)          │
└─────────────────────────────────────────────────────────────┘
```
*(If no invites tracked yet: `📨 No invites tracked yet! Invite friends to claim the #1 spot.`)*

---

## 🎁 `/invitebonus` *(Manage Server)*

Adds or subtracts bonus invites for a member (enter a positive number like `5` or negative like `-2`).

### Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 7:05 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 🎁 Bonus Invites Updated                                    │
│ Adjusted @Alex's invites by +5.                             │
│ New Total: 13 Invite(s)                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧹 `/invitereset` *(Administrator)*

Clears all tracked invite counts and invited-member history for this server (useful when starting a fresh monthly invite contest!).

### Exact What You See in Discord
```text
🤖 RookieBot  [APP]  👁️ Only you can see this
🧹 All tracked invite statistics for this server have been reset.
```
