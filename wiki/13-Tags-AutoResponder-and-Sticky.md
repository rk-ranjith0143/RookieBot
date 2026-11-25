# 🏷️ Module 13: Tags, Auto-Responder & Sticky Notices

Automate repetitive FAQs, keyword triggers, and bottom-pinned channel notices!

> [!NOTE]
> **Free Tier vs. Premium Limits:**
> * **Tags (`/tag add`)**: Free servers can create up to **5 custom tags**. Premium unlocks **Unlimited Tags**.
> * **Sticky Messages (`/sticky set`)**: Free servers can have **1 active sticky channel**. Premium unlocks **Unlimited Sticky Channels**.
> * *(Auto-Responders have no limit!)*

---

## 📑 Commands in This Guide
**Custom FAQ Tags:**
1. [`/tag add`](#-tag-add) — Save a reusable snippet/FAQ *(Mod)*
2. [`/tag get`](#-tag-get) — Post a saved tag (with live autocomplete!)
3. [`/tag list`](#-tag-list) — See all tags and usage counts
4. [`/tag delete`](#-tag-delete) — Delete an existing tag *(Mod)*

**Keyword Auto-Responders:**
5. [`/autoresponder add`](#-autoresponder-add) — Auto-reply when someone types a keyword *(Admin)*
6. [`/autoresponder list`](#-autoresponder-list) — List all active keyword triggers *(Admin)*
7. [`/autoresponder delete`](#-autoresponder-delete) — Remove a trigger by ID *(Admin)*

**Sticky Messages:**
8. [`/sticky set`](#-sticky-set) — Keep an announcement pinned to the bottom of chat *(Mod)*
9. [`/sticky remove`](#-sticky-remove) — Remove the sticky notice *(Mod)*

---

## 🏷️ `/tag add` *(Manage Messages)*

Creates a reusable FAQ snippet or command response.

### 1. Parameters
* **`name`** *(Required)*: Short lowercase tag name, max 32 characters (e.g., `rules`, `ip`, `support`).
* **`content`** *(Required)*: Exact text, formatting, or links the tag outputs.

### 2. Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 5:00 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 🏷️ Tag Created                                              │
│ Tag ip has been saved!                                      │
│ Use /tag get ip to call it.                                 │
└─────────────────────────────────────────────────────────────┘
```
*(If you hit the 5-tag Free Tier cap: `⚠️ Free Tier Limit Reached (5/5 Tags)! ... Upgrade to ⭐ Premium with /premium to unlock unlimited tags!`)*

---

## 🔎 `/tag get`

Fetches and posts a saved tag publicly in chat. Includes **live search autocomplete** as you type the name!

### 1. Exact Step-by-Step Process in Discord
1. Type `/tag get`.
2. Start typing the tag name in **`name`**—Discord immediately shows matching tags in a dropdown list.
3. Click the matching tag and press **`Enter`**.

### 2. Exact What You See in Discord
RookieBot posts the exact saved `content` directly in chat (for example: `Join our Minecraft server at play.example.com!`).

---

## 📜 `/tag list`

Displays up to 30 server tags along with how many times each one has been used.

### Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 5:05 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 🏷️ Server Tags (3)                                          │
│ • ip — 42 uses                                              │
│ • rules — 18 uses                                           │
│ • support — 9 uses                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗑️ `/tag delete` *(Manage Messages)*

Deletes a tag (also supports live autocomplete!).

### Exact What You See in Discord
* **Deleted:** `✅ Tag ip was successfully deleted.` *(Only you can see this)*
* **Missing:** `❌ Tag ip does not exist.` *(Only you can see this)*

---

## ⚡ `/autoresponder add` *(Manage Server)*

Configures RookieBot to automatically reply whenever a member sends a message matching your keyword or phrase.

### 1. Parameters
* **`trigger`** *(Required)*: Word or phrase (`2` to `64` characters, case-insensitive).
* **`response`** *(Required)*: Message text RookieBot replies with (max `1000` characters).
* **`match_type`** *(Required)*: Choose from Discord's dropdown:
  * `Contains (Substring)` — Triggers if the phrase appears *anywhere* inside a message.
  * `Exact Match Only` — Triggers *only* if the entire message matches the trigger.

### 2. Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 5:10 PM                        │
├─────────────────────────────────────────────────────────────┤
│ ⚡ Auto-Responder Created                                   │
│ • ID: #4                                                    │
│ • Trigger: server ip                                        │
│ • Match Type: Contains (Substring)                          │
│ • Response: Our server IP is play.example.com!              │
└─────────────────────────────────────────────────────────────┘
```
*Whenever a member types `"hey what's the server ip?"`, RookieBot immediately replies with `Our server IP is play.example.com!`.*

---

## 📋 `/autoresponder list` *(Manage Server)*

Lists up to 25 active auto-responders with their numeric `#ID`.

### Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 5:12 PM                        │
├─────────────────────────────────────────────────────────────┤
│ ⚡ Server Auto-Responders (2)                               │
│ • #4 [Contains] Trigger: server ip ➔ Our server IP is...    │
│ • #5 [Exact] Trigger: !website ➔ Visit https://example...   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗑️ `/autoresponder delete` *(Manage Server)*

Removes an auto-responder using the ID from `/autoresponder list`.

### Exact What You See in Discord
* **Success:** `✅ Auto-responder #4 has been deleted.` *(Only you can see this)*
* **Not found:** `❌ Auto-responder #99 was not found in this server.` *(Only you can see this)*

---

## 📌 `/sticky set` *(Manage Messages)*

Pins an important notice card to the **bottom** of the current text channel. Every time members send new messages, RookieBot deletes the old sticky card and reposts it at the very bottom so nobody misses it!

### 1. Exact Step-by-Step Process in Discord
1. Go to the channel where you want the sticky notice (e.g., `#trading` or `#help-chat`).
2. Type `/sticky set`.
3. Enter your **`message`** (max `2000` characters) and press **`Enter`**.

### 2. Exact What You See in Discord

**A. Public Sticky Card posted at the bottom of the channel:**
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 5:15 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 📌 Pinned Notice                                            │
│ Read the trading rules before posting offers! No real-money │
│ trades allowed.                                             │
│                                                             │
│ Sticky Notice • Stays at the bottom of the channel          │
└─────────────────────────────────────────────────────────────┘
```

**B. Private confirmation to you:**
```text
🤖 RookieBot  [APP]  👁️ Only you can see this
✅ Sticky message active! It will automatically re-pin to the bottom as members chat.
```
*(Free Tier limit message if trying a 2nd channel: `⚠️ Free Tier Limit Reached (1 Sticky Message)! ...`)*

---

## 🗑️ `/sticky remove` *(Manage Messages)*

Removes the sticky notice from the current channel and stops reposting it.

### Exact What You See in Discord
```text
🤖 RookieBot  [APP]  👁️ Only you can see this
🗑️ Sticky message removed from this channel.
```
