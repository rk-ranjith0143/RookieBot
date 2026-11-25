# 💬 Module 12: Suggestions, Starboard, Polls & Giveaways

Engage your community with structured idea voting, a starboard hall-of-fame, instant reaction polls, and timed giveaways.

---

## 📑 Commands in This Guide
**Suggestions System:**
1. [`/setsuggestchannel`](#-setsuggestchannel) — Set where suggestions appear *(Admin)*
2. [`/suggest`](#-suggest) — Submit an idea with live `👍`/`👎` buttons
3. [`/suggeststatus`](#-suggeststatus) — Approve, Deny, or Consider an idea *(Admin)*

**Starboard Hall-of-Fame:**
4. [`/starboard setup`](#-starboard-setup) — Feature popular ⭐ messages *(Admin)*
5. [`/starboard disable`](#-starboard-disable) — Turn off Starboard *(Admin)*

**Polls & Giveaways:**
6. [`/poll`](#-poll) — Create a Yes/No or up to 10-option poll
7. [`/giveaway`](#-giveaway) — Launch a timed giveaway with random winner selection

---

## 💡 `/setsuggestchannel` *(Admin)*

Sets the text channel where all `/suggest` submissions will be sent.

### 1. Exact Step-by-Step Process in Discord
1. Type `/setsuggestchannel`, select **`channel`** (e.g., `#suggestions`), and press **`Enter`**.

### 2. Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 4:10 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 💡 Suggestions Channel Updated                              │
│ Community suggestions will now be submitted to #suggestions.│
└─────────────────────────────────────────────────────────────┘
```

---

## 🗳️ `/suggest`

Submits a suggestion card into the server's `#suggestions` channel with persistent **`👍 Upvote`** and **`👎 Downvote`** buttons!

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/suggest suggestion:<text>` |
| **Who Can Use It** | `@everyone` |
| **Response Visibility** | Ephemeral confirmation to you + Public Vote Card in `#suggestions` |

### 2. Exact Step-by-Step Process in Discord
1. Type `/suggest` in any channel.
2. Type your idea in **`suggestion`** (e.g., `Add a dedicated Minecraft channel!`).
3. Press **`Enter`**.

### 3. Exact What You See in Discord

**A. Private confirmation to you:**
```text
🤖 RookieBot  [APP]  👁️ Only you can see this
✅ Your suggestion (#1) has been submitted to #suggestions!
```

**B. Public Suggestion Card posted in `#suggestions`:**
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 4:12 PM                        │
├─────────────────────────────────────────────────────────────┤
│ Alex                                                        │
│ 💡 New Suggestion                                           │
│ Add a dedicated Minecraft channel!                          │
│                                                             │
│ Status                        Votes                         │
│ ⏳ Pending Review             👍 0 • 👎 0 (Score: 0)        │
│                                                             │
│ Suggestion #1 • Submitted by alex#0000                      │
├─────────────────────────────────────────────────────────────┤
│ [ 👍 Upvote (0) ]   [ 👎 Downvote (0) ]                     │
└─────────────────────────────────────────────────────────────┘
```

**C. What members see privately when clicking Upvote or Downvote:**
```text
🤖 RookieBot  [APP]  👁️ Only you can see this
Your vote has been updated! (Current: 👍 4 | 👎 1)
```
*(Both the button counters and the `Votes` field on the embed update live!)*

---

## ⚖️ `/suggeststatus` *(Admin)*

Updates a suggestion's status (`Approved`, `Denied`, or `Considered`), changes the embed color, attaches an optional management note, and locks voting if Approved or Denied.

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/suggeststatus suggestion_id:<number> status:<choice> [reason:<text>]` |
| **Who Can Use It** | Members with **Manage Server** (`Manage Guild`) permission |

### 2. Parameters
* **`suggestion_id`** *(Required)*: Numeric ID shown in the card footer (e.g., `1` for `Suggestion #1`).
* **`status`** *(Required)*: Pick from Discord's menu:
  * `Approved` *(turns embed green, disables vote buttons)*
  * `Denied` *(turns embed red, disables vote buttons)*
  * `Considered` *(turns embed gold, keeps voting open)*
* **`reason`** *(Optional)*: Explanation added as `Admin Note (YourName)`.

### 3. Exact What You See in Discord
* **Private confirmation to you:** `✅ Suggestion #1 status updated to Approved.`
* **Updated card in `#suggestions`:**
  ```text
  Status                        Votes
  ✅ Approved                   👍 12 • 👎 1 (Score: 11)

  Admin Note (AdminUser)
  Great idea! Channel created under Gaming.
  ```
*(If someone tries voting after it's Approved/Denied: `Voting is closed because this suggestion is already APPROVED.`)*

---

## ⭐ `/starboard setup` *(Admin)*

Highlights community favorite messages automatically! Whenever any message gets enough `⭐` reactions, RookieBot posts it into your Starboard channel and updates the star count live (or removes it if stars drop below the threshold).

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/starboard setup channel:<#channel> [threshold:<1-50>]` |
| **Who Can Use It** | Members with **Manage Server** (`Manage Guild`) permission |
| **Bot Needs** | `Send Messages`, `Embed Links` in the Starboard channel |

### 2. Parameters
* **`channel`** *(Required)*: Destination channel (e.g., `#starboard`).
* **`threshold`** *(Optional)*: Minimum `⭐` reactions needed (`1` to `50`). Defaults to **`3`**.

### 3. Exact What You See in Discord

**A. Setup Confirmation:**
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 4:20 PM                        │
├─────────────────────────────────────────────────────────────┤
│ ⭐ Starboard Configured                                     │
│ • Channel: #starboard                                       │
│ • Star Threshold: 3 ⭐                                      │
│ • Status: Active                                            │
│                                                             │
│ React to messages with ⭐ to feature them!                  │
└─────────────────────────────────────────────────────────────┘
```

**B. What appears in `#starboard` when a message hits the threshold:**
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 4:25 PM                        │
│ ⭐ 4 #general                                               │
├─────────────────────────────────────────────────────────────┤
│ Alex                                                        │
│ That joke had the whole voice call crying 😂                │
│                                                             │
│ Source                                                      │
│ Jump to message                                             │
│                                                             │
│ ID: 987654321098765432                                      │
└─────────────────────────────────────────────────────────────┘
```
*(Also attaches the message's image automatically if one was posted!)*

---

## 🛑 `/starboard disable` *(Admin)*

Turns off Starboard tracking for the server.

### Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 4:28 PM                        │
├─────────────────────────────────────────────────────────────┤
│ ⭐ Starboard Disabled                                       │
│ Starboard has been turned off for this server. You can      │
│ re-enable it anytime with /starboard setup.                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 `/poll`

Creates an instant reaction poll—either a quick **Yes/No (`👍`/`👎`)** poll or a multi-choice poll with up to **10 numbered options (`1️⃣` to `🔟`)**.

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/poll question:<text> [option1..option10:<text>]` |
| **Who Can Use It** | `@everyone` |
| **Bot Needs** | `Send Messages`, `Embed Links`, `Add Reactions` |

### 2. Exact Step-by-Step Process in Discord
* **For a Yes/No poll:** Type `/poll`, fill only **`question`**, leave all `option` fields blank, and press **`Enter`**.
* **For a multi-choice poll:** Fill **`question`**, **`option1`**, **`option2`**, and up to **`option10`**, then press **`Enter`**.

### 3. Exact What You See in Discord

**Multi-Choice Poll Example:**
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 4:30 PM                        │
├─────────────────────────────────────────────────────────────┤
│ Alex                                                        │
│ 📊 Which game should we host for Friday Movie/Game Night?   │
│ 1️⃣ Among Us                                                 │
│                                                             │
│ 2️⃣ Minecraft                                                │
│                                                             │
│ 3️⃣ Valorant                                                 │
│                                                             │
│ Click a reaction below to cast your vote!                   │
├─────────────────────────────────────────────────────────────┤
│ [1️⃣ 1]  [2️⃣ 1]  [3️⃣ 1]                                      │
└─────────────────────────────────────────────────────────────┘
```
*(Yes/No polls show: `React with 👍 for Yes or 👎 for No.` with `👍` and `👎` reactions.)*

### 4. Common Errors & Solutions
* **`❌ A poll needs at least 2 options! Leave options blank if you want a Yes/No poll.`** → You filled `option1` without filling `option2`.

---

## 🎉 `/giveaway`

Starts a timed giveaway using `🎉` reactions and automatically picks random winners when time expires!

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/giveaway prize:<text> duration:<minutes> [winners:<number>]` |
| **Who Can Use It** | `@everyone` |
| **Bot Needs** | `Send Messages`, `Embed Links`, `Add Reactions` |

### 2. Parameters
* **`prize`** *(Required)*: What you are giving away (e.g., `Discord Nitro (1 Month)`).
* **`duration`** *(Required)*: Length in **minutes** (must be `1` or more).
* **`winners`** *(Optional)*: How many random winners to draw. Defaults to **`1`**.

### 3. Exact What You See in Discord

**A. Active Giveaway Card:**
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 4:35 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 🎉 GIVEAWAY! 🎉                                             │
│ Prize: Discord Nitro (1 Month)                              │
│ Hosted by: @Alex                                            │
│ Winners: 1                                                  │
│ Ends: in 30 minutes (November 25, 2026 at 5:05 PM)          │
│                                                             │
│ React with 🎉 to enter!                                     │
│                                                             │
│ Ends at                                                     │
├─────────────────────────────────────────────────────────────┤
│ [🎉 1]                                                      │
└─────────────────────────────────────────────────────────────┘
```

**B. When the timer finishes:**
RookieBot edits the embed to green **`🎉 Giveaway Ended 🎉`** with the winner(s) and sends a celebration ping in chat:
```text
🤖 RookieBot  [APP]
Congratulations @Sarah! You won the Discord Nitro (1 Month)! 🎁
```
*(If nobody reacted, the embed turns grey with `No one entered the giveaway! 😢`.)*
