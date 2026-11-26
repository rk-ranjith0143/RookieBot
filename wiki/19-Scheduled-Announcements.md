# 🗓️ Module 19: Recurring Scheduled Announcements

Automatically post repeating announcements (events, bump reminders, rules reminders, server updates) into any text channel on a custom schedule (`1m` to `30d`), persisted cleanly in SQLite across bot restarts.

---

## 📑 Commands in This Guide
1. [`/schedule add`](#-schedule-add) — Create a recurring channel announcement
2. [`/schedule list`](#-schedule-list) — View all scheduled announcements & next post times
3. [`/schedule toggle`](#-schedule-toggle) — Pause or resume a schedule without deleting it
4. [`/schedule remove`](#-schedule-remove) — Delete a scheduled announcement by ID

---

## ➕ `/schedule add`

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/schedule add channel:<#ch> interval:<time> message:<text> [title:<text>] [start_delay:<time>]` |
| **Who Can Use It** | Members with **Manage Server** permission |
| **Bot Needs** | **Send Messages** & **Embed Links** in target channel |
| **Response Visibility** | Ephemeral Embed (`👁️ Only you can see this`) |

### 2. Parameters
* **`channel`** *(Required)*: Target text channel where RookieBot will post.
* **`interval`** *(Required)*: Repeat frequency (`1m` to `30d`, e.g., `30m`, `6h`, `1d`, `7d`).
* **`message`** *(Required)*: Announcement message body (up to 2,000 characters).
* **`title`** *(Optional)*: Custom embed title (defaults to `📢 Scheduled Announcement`).
* **`start_delay`** *(Optional)*: Delay before the **first** post (e.g., `5m`, `1h`). If omitted, the first post happens after 1 full `interval`.

### 3. Exact Step-by-Step Process in Discord
1. Type `/schedule add`.
2. Select **`channel`** (e.g., `#announcements`), set **`interval`** (e.g., `1d`), and enter your **`message`**.
3. *(Optional)* Customize **`title`** or **`start_delay`** (`5m` to post soon, then repeat daily).
4. Press **`Enter`**. RookieBot checks every 30 seconds and posts automatically whenever a schedule is due.

### 4. Exact What You See in Discord
**Confirmation Embed (Ephemeral):**
```text
🤖 RookieBot  [APP]  👁️ Only you can see this
┌─────────────────────────────────────────────────────────────┐
│ 🗓️ Scheduled Announcement Created                           │
│ Schedule #1 will post automatically in #announcements.      │
│                                                             │
│ Repeat Interval          First Post                         │
│ `1d`                     in 5 minutes                       │
│                                                             │
│ Title                                                       │
│ 📣 Daily Community Check-In                                 │
│                                                             │
│ Preview                                                     │
│ Don't forget to check #events and invite your friends!      │
└─────────────────────────────────────────────────────────────┘
```

**Recurring Channel Post:**
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 9:00 AM                        │
├─────────────────────────────────────────────────────────────┤
│ 📣 Daily Community Check-In                                 │
│ Don't forget to check #events and invite your friends!      │
│                                                             │
│ Schedule #1 • Repeats every 1d                              │
└─────────────────────────────────────────────────────────────┘
```

### 5. Common Errors & Solutions
* **`❌ Invalid interval! Please use a duration between \`1m\` and \`30d\` (e.g., \`30m\`, \`6h\`, \`1d\`, \`7d\`).`** → Ensure a single unit with no spaces and at least `1m`.
* **`❌ I need \`Send Messages\` and \`Embed Links\` permissions in #channel!`** → Grant RookieBot send & embed permissions in that channel.

---

## 📋 `/schedule list`

Displays every recurring announcement configured in the server (`🟢 Active` or `⏸️ Paused`), its interval, target channel, next run countdown, and message preview.

* **Syntax:** `/schedule list`
* **Response:** Ephemeral embed titled **🗓️ Recurring Scheduled Announcements** (`• #1 • Title (🟢 Active)`).

---

## ⏯️ `/schedule toggle`

Temporarily pauses or resumes an existing schedule by its ID without losing its message or interval.

* **Syntax:** `/schedule toggle schedule_id:<id> enabled:<True|False>`
* **Exact Response:** `⏸️ Paused scheduled announcement **#1**.` or `🟢 Resumed scheduled announcement **#1**.`

---

## 🗑️ `/schedule remove`

Permanently deletes a scheduled announcement from the server.

* **Syntax:** `/schedule remove schedule_id:<id>`
* **Exact Response:** `🗑️ Deleted scheduled announcement **#1**.`
