# 🎂 Module 16: Server Birthday Tracker & Auto-Celebrations

Let community members save their birthday (month & day—privacy-friendly with no birth year required!) and let RookieBot automatically post celebration cards and grant an optional `@Birthday` role!

---

## 📑 Commands & Events in This Guide
**For All Members:**
1. [`/birthday set`](#-birthday-set) — Save your birthday
2. [`/birthday view`](#-birthday-view) — Check your or someone else's birthday countdown
3. [`/birthday upcoming`](#-birthday-upcoming) — See the next 10 upcoming server birthdays
4. [`/birthday remove`](#-birthday-remove) — Delete your saved birthday

**For Server Administrators:**
5. [`/birthday setup`](#-birthday-setup-admin) — Configure the announcement channel & optional Birthday role
6. [`/birthday disable`](#-birthday-disable-admin) — Turn off automated birthday announcements
7. [Automatic Daily Celebration Card](#-what-appears-in-chat-on-a-members-birthday)

---

## 🎂 `/birthday set`

Saves your birth month and day for the current server.

### 1. Parameters
* **`month`** *(Required)*: Choose `January` through `December` from Discord's dropdown menu.
* **`day`** *(Required)*: Day of the month (`1` to `31`; invalid calendar dates like February 30 are rejected).

### 2. Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 6:20 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 🎂 Birthday Saved!                                          │
│ @Alex's birthday is set to November 25! 🎉                  │
│                                                             │
│ Use /birthday upcoming to see upcoming server birthdays.    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 `/birthday view`

Displays your or another member's saved birthday and exact days remaining.

### Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 6:22 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 🎂 Alex's Birthday                                          │
│ Date: November 25                                           │
│ Next Celebration: in 12 day(s)                              │
└─────────────────────────────────────────────────────────────┘
```
*(If not saved yet: `ℹ️ @Alex has not set their birthday yet. Use /birthday set!`)*

---

## 🎈 `/birthday upcoming`

Lists the **next 10 upcoming birthdays** across the server sorted by closest date.

### Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 6:24 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 🎈 Upcoming Birthdays (3 saved)                             │
│ • @Alex — November 25 (🎉 Today!)                           │
│ • @Sarah — December 2 (in 7 day(s))                         │
│ • @Sam — January 14 (in 50 day(s))                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗑️ `/birthday remove`

Deletes your saved birthday from this server.

### Exact What You See in Discord
```text
🤖 RookieBot  [APP]  👁️ Only you can see this
✅ Your birthday has been removed from this server.
```

---

## ⚙️ `/birthday setup` *(Admin)*

Sets which channel receives automated birthday announcements and optionally links a `@Birthday` role! *(Requires **Manage Server** permission.)*

### 1. Parameters
* **`channel`** *(Required)*: Text channel where birthday celebration cards will be posted (e.g., `#celebrations`).
* **`role`** *(Optional)*: Role granted automatically on the member's birthday (drag RookieBot's role above it in **Server Settings → Roles**).

### 2. Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 6:26 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 🎂 Birthday System Configured                               │
│ • Announcement Channel: #celebrations                       │
│ • Birthday Role: @Birthday                                  │
│                                                             │
│ Members can save their birthdays anytime using /birthday set!│
└─────────────────────────────────────────────────────────────┘
```

---

## 🛑 `/birthday disable` *(Admin)*

Turns off automated daily birthday announcements (without erasing members' saved dates).

### Exact What You See in Discord
```text
🤖 RookieBot  [APP]  👁️ Only you can see this
✅ Automated birthday announcements have been disabled.
```

---

## 🥳 What Appears in Chat on a Member's Birthday

Every 30 minutes, RookieBot checks the current UTC date and celebrates any members whose birthday matches today (once per calendar year):

```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 12:00 AM UTC                  │
│ 🎉 Happy Birthday @Alex!                                    │
├─────────────────────────────────────────────────────────────┤
│ 🎂 Happy Birthday! 🎉                                       │
│ Join us in wishing @Alex a very Happy Birthday today! 🥳🎈  │
│                                                             │
│ Hope you have an awesome day!                               │
└─────────────────────────────────────────────────────────────┘
```
*(And if a `role` was set in `/birthday setup`, RookieBot assigns it automatically!)*
