# 📩 Module 5: Interactive Support Tickets

Give your community a clean, private way to contact staff without flooding public channels. Members click one **`📩 Open Ticket`** button to get their own private text channel visible **only to them and your Support Role**—complete with staff **`✋ Claim Ticket`** ownership and **automatic `.txt` transcripts** saved when closed!

---

## 📑 What This Guide Covers
1. [`/ticketsetup`](#-ticketsetup) — Deploy the persistent ticket launcher panel
2. [Member Experience: Clicking `📩 Open Ticket`](#-member-experience-clicking--open-ticket)
3. [Staff Claiming (`✋ Claim Ticket`)](#-staff-claiming--claim-ticket)
4. [Closing & Automatic Transcripts (`🔒 Close Ticket`)](#-closing--automatic-transcripts--close-ticket)

---

## 📩 `/ticketsetup`

Posts a permanent ticket launcher card in a channel and optionally saves which **Category** new tickets go into, which **Support Role** can view them, and which **Transcript Channel** archives closed ticket logs.

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/ticketsetup [channel:<#ch>] [category:<Category>] [support_role:<@role>] [transcript_channel:<#ch>] [title:<text>] [description:<text>]` |
| **Who Can Use It** | Members with **Manage Server** (`Manage Guild`) permission |
| **Bot Needs** | **Manage Channels**, `Send Messages`, `Embed Links`, `Attach Files` |
| **Where It Works** | Any server text channel |
| **What Discord Shows** | Public Ticket Launcher Embed with `📩 Open Ticket` button + Ephemeral confirmation |

### 2. Parameters
* **`channel`** *(Optional)*: Where to post the ticket panel. Defaults to your current channel.
* **`category`** *(Optional)*: Discord Category where new `ticket-...` channels will be created. *(If omitted, RookieBot looks for or creates a category named `Tickets` automatically!)*
* **`support_role`** *(Optional)*: Staff role automatically granted permission to view, reply, and claim every new ticket.
* **`transcript_channel`** *(Optional)*: Channel where `.txt` transcripts are uploaded when tickets close. *(If omitted, RookieBot automatically falls back to your `/setlogs` channel!)*
* **`title`** *(Optional)*: Defaults to `Need Help? Open a Support Ticket`.
* **`description`** *(Optional)*: Defaults to `Click the button below to start a private conversation with our support team.`

### 3. Exact Step-by-Step Process in Discord
1. Go to your support channel (e.g., `#support`) and type `/ticketsetup`.
2. *(Optional)* Fill **`channel`**, **`category`** (e.g., `Tickets`), **`support_role`** (e.g., `@Staff`), and **`transcript_channel`** (e.g., `#ticket-logs`).
3. *(Optional)* Customize **`title`** and **`description`**.
4. Press **`Enter`**.

### 4. Exact What You See in Discord

**A. Public Ticket Launcher Panel posted in `#support`:**
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 2:00 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 📩 Need Help? Open a Support Ticket                         │
│ Click the button below to start a private conversation with │
│ our support team.                                           │
│                                                             │
│ 🔒 Privacy Guaranteed                                       │
│ Each ticket creates a private text channel accessible only  │
│ to you and staff members.                                   │
│                                                             │
│ My Community Server                                         │
├─────────────────────────────────────────────────────────────┤
│ [ 📩 Open Ticket ]  (Blurple Button)                        │
└─────────────────────────────────────────────────────────────┘
```

**B. Private confirmation only you see:**
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 2:00 PM  👁️ Only you can see │
│ ✅ Ticket panel successfully deployed to #support!          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎟️ Member Experience: Clicking `📩 Open Ticket`

1. A member clicks **`📩 Open Ticket`**.
2. RookieBot creates a private channel named **`#ticket-username`** (for example, `#ticket-alex`) inside your configured Category.
   * `@everyone` has `View Channel = ❌`.
   * The ticket creator and your `support_role` have `View Channel`, `Send Messages`, `Read Message History`, and `Attach Files` enabled.
3. **Only the clicking member sees this private redirect message:**
   ```text
   ┌─────────────────────────────────────────────────────────────┐
   │ 🤖 RookieBot  [APP]  👁️ Only you can see this               │
   │ ✅ Ticket created! Head over to #ticket-alex.               │
   └─────────────────────────────────────────────────────────────┘
   ```
4. **Inside the brand-new `#ticket-alex` channel, RookieBot sends:**
   ```text
   ┌─────────────────────────────────────────────────────────────┐
   │ 🤖 RookieBot  [APP]  Today at 2:01 PM                        │
   │ @Alex Support staff has been notified.                      │
   ├─────────────────────────────────────────────────────────────┤
   │ 📩 Support Ticket Opened                                    │
   │ Welcome @Alex!                                              │
   │                                                             │
   │ Please describe your question or issue in detail. A staff   │
   │ member will be with you shortly.                            │
   │                                                             │
   │ When you are finished, click the Close Ticket button below. │
   │                                                             │
   │ Ticket ID: #123456789012345678                              │
   ├─────────────────────────────────────────────────────────────┤
   │ [ 🔒 Close Ticket ]  (Red)   [ ✋ Claim Ticket ]  (Grey)    │
   └─────────────────────────────────────────────────────────────┘
   ```

* **Duplicate Prevention:** If the user already has `#ticket-alex` open and clicks `Open Ticket` again, only they see:
  ```text
  ⚠️ You already have an open ticket in #ticket-alex!
  ```

---

## ✋ Staff Claiming (`✋ Claim Ticket`)

Staff members can click **`✋ Claim Ticket`** so the member and other moderators know who is handling the request.

1. A staff member (anyone with `Administrator`, `Manage Channels`, `Manage Messages`, or your configured `support_role`) clicks **`✋ Claim Ticket`**.
2. The button updates to green **`✋ Claimed by StaffName`** (disabled so it isn't claimed twice), the channel topic updates with `| Claimed by ...`, and RookieBot posts inside the ticket:
   ```text
   ┌─────────────────────────────────────────────────────────────┐
   │ 🤖 RookieBot  [APP]  Today at 2:03 PM                        │
   ├─────────────────────────────────────────────────────────────┤
   │ ✋ Ticket Claimed                                           │
   │ @StaffMember has claimed this ticket and will assist you    │
   │ shortly!                                                    │
   └─────────────────────────────────────────────────────────────┘
   ```
3. *(If a regular member without staff/support permissions clicks Claim, only they see: `❌ Only staff or support team members can claim a ticket.`)*

---

## 🔒 Closing & Automatic Transcripts (`🔒 Close Ticket`)

1. Either the member or a staff member clicks **`🔒 Close Ticket`** inside the ticket channel.
2. Both buttons disable immediately, and RookieBot posts:
   ```text
   ┌─────────────────────────────────────────────────────────────┐
   │ 🤖 RookieBot  [APP]  Today at 2:10 PM                        │
   ├─────────────────────────────────────────────────────────────┤
   │ 🔒 Ticket Closed                                            │
   │ Ticket closed by @StaffMember.                              │
   │ Generating transcript and deleting channel in 5 seconds...  │
   └─────────────────────────────────────────────────────────────┘
   ```
3. Before deleting the channel, RookieBot reads up to 500 messages in chronological order, builds **`transcript-ticket-alex.txt`** (with timestamps, author IDs, message text, and attachment links), and:
   * Uploads the `.txt` transcript + **`📜 Ticket Transcript`** summary embed to your **`transcript_channel`** (or your `/setlogs` channel if no separate transcript channel was set).
   * Attempts to **DM a copy** of the transcript directly to the ticket owner (if their DMs are open).
4. After **5 seconds**, the private ticket channel is deleted cleanly.
