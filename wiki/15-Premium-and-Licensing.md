# 💎 Module 15: Premium Tiers & License Key System

Manage server subscriptions, compare Free vs. Premium limits, redeem license keys (`PREM-XXXX-XXXX-XXXX`), and generate or revoke keys as a Bot Administrator.

---

## 📑 Commands & Interactive Modals in This Guide
**For Server Owners & Admins:**
1. [`/premium`](#-premium) — View server subscription status, perks & Redeem button
2. [`/redeem`](#-redeem) — Activate a license key directly via slash command

**For Bot Owners / Self-Host Administrators:**
3. [`/license generate`](#-license-generate) — Generate a new `PREM-XXXX-XXXX-XXXX` key
4. [`/license list`](#-license-list) — View the last 20 keys and redemption status
5. [`/license revoke`](#-license-revoke) — Remove Premium status from a server ID

---

## 💎 `/premium`

Displays whether your server is on the **Free Tier** or **⭐ Premium Server**, lists the exact perks, and provides two buttons: **`🛒 💳 Buy Subscription`** and **`🔑 Redeem License Key`**.

### 1. Exact Step-by-Step Process in Discord
1. Type `/premium` in any text channel and press **`Enter`**.
2. To redeem a key via popup, click the green **`🔑 Redeem License Key`** button, paste your key (`PREM-XXXX-XXXX-XXXX`), and click **`Submit`**.

### 2. Exact What You See in Discord

**When on the Free Tier:**
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 6:00 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 💎 Server Subscription: Free Tier                           │
│ My Community Server is currently on the Free Tier.          │
│ Upgrade for just $1/mo (available for all servers) to       │
│ unlock unlimited tags, unlimited sticky notices, all live   │
│ stats channels, and priority uptime!                        │
│                                                             │
│ 🆓 Free Tier Limits                                         │
│ • All standard Moderation tools (/kick, /ban, /timeout...)  │
│ • Up to 5 Custom Tags (/tag)                                │
│ • 1 Sticky Message per server (/sticky)                     │
│ • 1 Live Stats Channel (👥 Total Members)                   │
│ • Community Suggestions, Polls & Giveaways                  │
│                                                             │
│ ⭐ Premium Perks ($1/mo)                                    │
│ • Unlimited Custom Tags & Auto-FAQs                         │
│ • Unlimited Sticky Notices across multiple channels         │
│ • Full Live Stats Suite (Total, Humans, Bots, Boosts)       │
│ • Priority 99.9% Cloud Uptime & Instant Response            │
│ • Direct Developer Support & White-Label Retainer Access    │
├─────────────────────────────────────────────────────────────┤
│ [ 🛒 💳 Buy Subscription ↗ ]   [ 🔑 Redeem License Key ]    │
└─────────────────────────────────────────────────────────────┘
```

**When clicking `🔑 Redeem License Key`, Discord opens this Modal:**
```text
┌─────────────────────────────────────────────────────────────┐
│ Redeem Premium License Key                              [X] │
├─────────────────────────────────────────────────────────────┤
│ LICENSE KEY *                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ PREM-XXXX-XXXX-XXXX                                     │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                        [Cancel]  [ Submit ] │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔑 `/redeem`

Activates a Premium license key on the current server without opening the modal. *(If the server already has active Premium time left, the new key extends the current expiration date!)*

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/redeem key:<PREM-XXXX-XXXX-XXXX>` |
| **Who Can Use It** | `@everyone` *(Any server member with a valid key)* |
| **Response Visibility** | Public Gold Embed (or Ephemeral error if invalid/used) |

### 2. Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 6:05 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 🎉 License Redeemed Successfully!                           │
│ My Community Server has been upgraded to ⭐ Premium!        │
│                                                             │
│ • Expiration: December 25, 2026 (12:35 UTC)                 │
│ • Redeemed By: @ServerOwner                                 │
│                                                             │
│ All feature limits have been lifted. Use /premium to view   │
│ your active status.                                         │
└─────────────────────────────────────────────────────────────┘
```

### 3. Common Errors & Solutions
* **`❌ Invalid license key. Please check the key and try again.`** → Check for typos; keys are formatted like `PREM-A1B2-C3D4-E5F6`.
* **`❌ This license key has already been redeemed.`** → Each key can only be redeemed once.

---

## ⚙️ `/license generate` *(Bot Admin / Owner)*

Generates a brand-new, unforgeable `PREM-XXXX-XXXX-XXXX` license key stored in SQLite.

### 1. Parameters
* **`duration_days`** *(Optional)*: Number of valid days (defaults to `30`). Enter **`-1`** for **Lifetime**.
* **`note`** *(Optional)*: Customer or tracking note (e.g., `Client: GamerHub`).

### 2. Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 6:10 PM  👁️ Only you can see │
├─────────────────────────────────────────────────────────────┤
│ 🔑 Premium License Key Generated                            │
│ A new license key has been generated and is ready to        │
│ deliver to your client or customer:                         │
│                                                             │
│ PREM-4F9A-82C1-0E7B                                         │
│                                                             │
│ • Duration: 30 Days                                         │
│ • Note: Client: GamerHub                                    │
│                                                             │
│ The recipient can activate it using /redeem                 │
│ PREM-4F9A-82C1-0E7B in their server.                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 `/license list` *(Bot Admin / Owner)*

Lists the **20 most recent** license keys privately so only you can see them, showing whether each is `🟢 Available` or `🔴 Redeemed`.

### Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 6:12 PM  👁️ Only you can see │
├─────────────────────────────────────────────────────────────┤
│ 🔑 License Keys (2)                                         │
│ • PREM-4F9A-82C1-0E7B | 30d | 🟢 Available (GamerHub)       │
│ • PREM-11AA-22BB-33CC | Lifetime | 🔴 Redeemed              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚫 `/license revoke` *(Bot Admin / Owner)*

Immediately downgrades a server back to the Free Tier using its numeric Server ID.

### 1. Exact Step-by-Step Process in Discord
1. Enable Developer Mode in Discord, right-click the server icon, and click **Copy Server ID**.
2. Type `/license revoke`, paste **`guild_id`**, and press **`Enter`**.

### 2. Exact What You See in Discord
```text
🤖 RookieBot  [APP]  👁️ Only you can see this
✅ Premium tier revoked for Server ID 987654321098765432.
```
