# 🪙 Module 10: Virtual Economy, Careers & Role Shop

A complete per-server virtual coin economy! Every member starts with **100 Coins**, can claim daily rewards, work random jobs, gamble on coin flips, trade coins with friends, and spend coins in an admin-customizable **Server Shop** that automatically grants **Discord Roles** or collectibles.

---

## 📑 Commands in This Guide
**For All Members:**
1. [`/balance`](#-balance) — Check coin wallet balance
2. [`/daily`](#-daily) — Claim 200 free coins every 24 hours
3. [`/work`](#-work) — Work a shift for 50–150 coins (1-hour cooldown)
4. [`/pay`](#-pay) — Send coins to another member
5. [`/coinflip`](#-coinflip) — Double-or-nothing Heads/Tails bet
6. [`/shop view`](#-shop-view) — Browse all items and role rewards for sale
7. [`/buy`](#-buy) — Purchase an item and unlock its role
8. [`/inventory`](#-inventory) — View purchased items

**For Server Administrators:**
9. [`/shop add`](#-shop-add) — Add an item or purchasable role to the shop
10. [`/shop remove`](#-shop-remove) — Delete an item from the shop

---

## 🪙 `/balance`

Displays your wallet balance or another member's balance.

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/balance [member:<@user>]` |
| **Who Can Use It** | `@everyone` |
| **Response Visibility** | Public Embed |

### 2. Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 3:15 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 🪙 Alex's Wallet                                            │
│                                                             │
│ Current Balance                                             │
│ 1,250 Coins                                                 │
│                                                             │
│ Use /daily to earn free coins every 24 hours!               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎁 `/daily`

Claims **+200 Coins** once every **24 hours**.

### 1. Exact Step-by-Step Process in Discord
1. Type `/daily` in any channel and press **`Enter`**.

### 2. Exact What You See in Discord
* **When claimed:**
  ```text
  ┌─────────────────────────────────────────────────────────────┐
  │ 🤖 RookieBot  [APP]  Today at 3:16 PM                        │
  ├─────────────────────────────────────────────────────────────┤
  │ 🎁 Daily Reward Claimed!                                    │
  │ You claimed your daily reward of +200 Coins! 🎉             │
  │                                                             │
  │ New Balance: 1,450 Coins                                    │
  │                                                             │
  │ Come back in 24 hours for your next reward!                 │
  └─────────────────────────────────────────────────────────────┘
  ```
* **If on cooldown (Only you see this):**
  ```text
  ⏳ You have already claimed your daily reward! Please wait 14h 22m before claiming again.
  ```

---

## 💼 `/work`

Work a randomized job shift (Barista, Software Developer, Streamer, Mechanic, Chef, or Courier) to earn **50 to 150 Coins** every **1 hour**.

### 1. Exact Step-by-Step Process in Discord
1. Type `/work` and press **`Enter`**.

### 2. Exact What You See in Discord
* **When shift completes:**
  ```text
  ┌─────────────────────────────────────────────────────────────┐
  │ 🤖 RookieBot  [APP]  Today at 3:18 PM                        │
  ├─────────────────────────────────────────────────────────────┤
  │ 💼 Job Shift Completed — 💻 Software Developer              │
  │ You patched critical bugs in a client application and       │
  │ earned +135 Coins! 💰                                       │
  │                                                             │
  │ New Balance: 1,585 Coins                                    │
  │                                                             │
  │ Work again in 1 hour or claim your /daily reward!           │
  └─────────────────────────────────────────────────────────────┘
  ```
* **If on cooldown (Only you see this):**
  ```text
  ⏳ You are tired from your shift! Please rest for 42m 15s before working again.
  ```

---

## 💸 `/pay`

Transfers coins from your wallet directly to another human member.

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/pay member:<@user> amount:<number>` |
| **Who Can Use It** | `@everyone` |
| **Response Visibility** | Public Embed (or Ephemeral error if invalid) |

### 2. Exact Step-by-Step Process in Discord
1. Type `/pay`.
2. Select the recipient in **`member`**.
3. Enter a positive whole number in **`amount`** (e.g., `500`).
4. Press **`Enter`**.

### 3. Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 3:20 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 💸 Payment Successful                                       │
│ @Alex sent 500 Coins to @Sarah!                             │
│                                                             │
│ Your New Balance: 1,085 Coins                               │
└─────────────────────────────────────────────────────────────┘
```

### 4. Common Errors & Solutions
* **`❌ Amount must be at least 1 Coin.`**
* **`❌ You cannot send coins to yourself!`**
* **`❌ You cannot transfer coins to a bot.`**
* **`❌ Insufficient funds! You only have 100 Coins.`**

---

## 🪙 `/coinflip`

Double-or-nothing coin flip wager! Win to gain `+bet` coins, or lose `-bet` coins.

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/coinflip bet:<amount> choice:<Heads 🪙|Tails 🪙>` |
| **Who Can Use It** | `@everyone` |
| **Response Visibility** | Public Embed |

### 2. Exact Step-by-Step Process in Discord
1. Type `/coinflip`.
2. Enter your **`bet`** amount (e.g., `100`).
3. Click **`choice`** and pick **`Heads 🪙`** or **`Tails 🪙`**.
4. Press **`Enter`**.

### 3. Exact What You See in Discord
* **If you win (Green Embed):**
  ```text
  ┌─────────────────────────────────────────────────────────────┐
  │ 🤖 RookieBot  [APP]  Today at 3:22 PM                        │
  ├─────────────────────────────────────────────────────────────┤
  │ 🪙 Coin Flip — You Won (+100 Coins)!                        │
  │ The coin landed on Heads! 🎉                                │
  │ New Balance: 1,185 Coins                                    │
  │                                                             │
  │ Player: Alex                                                │
  └─────────────────────────────────────────────────────────────┘
  ```
* **If you lose (Red Embed):**
  ```text
  ┌─────────────────────────────────────────────────────────────┐
  │ 🤖 RookieBot  [APP]  Today at 3:22 PM                        │
  ├─────────────────────────────────────────────────────────────┤
  │ 🪙 Coin Flip — You Lost (-100 Coins)                        │
  │ The coin landed on Tails. Better luck next time! 😢         │
  │ New Balance: 1,085 Coins                                    │
  │                                                             │
  │ Player: Alex                                                │
  └─────────────────────────────────────────────────────────────┘
  ```

---

## 🏪 `/shop view`

Displays every item and purchasable role listed in the server shop, sorted from lowest to highest price, along with each item's **`#ID`**.

### 1. Exact Step-by-Step Process in Discord
1. Type `/shop view` and press **`Enter`**.

### 2. Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 3:25 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 🏪 My Community Server Server Shop                          │
│ • #1 VIP Pass — 500 Coins [Grants Role: @VIP] - Exclusive   │
│   chat access                                               │
│ • #2 Golden Badge — 1,000 Coins - Collector profile badge   │
│                                                             │
│ Use /buy [item_id] to purchase an item!                     │
└─────────────────────────────────────────────────────────────┘
```
*(If empty: `🏪 The server shop is currently empty! Server admins can add items with /shop add.`)*

---

## 🛍️ `/buy`

Purchases an item from `/shop view` using its numeric ID. If the item has a linked role, RookieBot grants it to you immediately!

### 1. Exact Step-by-Step Process in Discord
1. Run `/shop view` to find the item ID (for example, `#1`).
2. Type `/buy` and enter **`1`** in **`item_id`** (without the `#`).
3. Press **`Enter`**.

### 2. Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 3:27 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 🛍️ Purchase Successful!                                     │
│ ✅ Successfully purchased VIP Pass for 500 Coins!           │
│ 🎉 You have been granted the @VIP role!                     │
│                                                             │
│ Check your items anytime with /inventory                    │
└─────────────────────────────────────────────────────────────┘
```

### 3. Common Errors & Solutions
* **`❌ Item not found in this server's shop.`** → Check `/shop view` for the correct numeric ID.
* **`❌ Insufficient funds! You need 500 Coins, but only have 200 Coins.`** → Earn more with `/daily` and `/work`.

---

## 🎒 `/inventory`

Shows up to 25 purchased items and unlocked roles for yourself or another member.

### 1. Exact Step-by-Step Process in Discord
1. Type `/inventory`.
2. *(Optional)* Select a **`member`**.
3. Press **`Enter`**.

### 2. Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 3:29 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 🎒 Alex's Inventory (1 items)                               │
│ • VIP Pass [Role: @VIP] — Purchased November 25, 2026       │
└─────────────────────────────────────────────────────────────┘
```
*(If empty: `🎒 @Alex's inventory is empty. Browse items in /shop view!`)*

---

## ➕ `/shop add` *(Admin Only)*

Adds a new item or purchasable Discord role to the server shop.

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/shop add name:<text> price:<number> [description:<text>] [role:<@role>]` |
| **Who Can Use It** | Members with **Administrator** permission |
| **Bot Needs** | **Manage Roles** (if linking a role) + higher role than the listed role |

### 2. Parameters
* **`name`** *(Required)*: Item name (up to 64 characters).
* **`price`** *(Required)*: Cost in coins (`1` or more).
* **`description`** *(Optional)*: Up to 200 characters explaining perks.
* **`role`** *(Optional)*: Discord role automatically granted upon purchase.

### 3. Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 3:32 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 🏪 Item Added to Shop                                       │
│ • Item ID: #1                                               │
│ • Name: VIP Pass                                            │
│ • Price: 500 Coins                                          │
│ • Role Granted: @VIP                                        │
│ • Description: Exclusive chat access                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗑️ `/shop remove` *(Admin Only)*

Deletes an item from `/shop view` by its numeric ID.

### 1. Exact Step-by-Step Process in Discord
1. Type `/shop remove`, enter **`item_id`** (e.g., `1`), and press **`Enter`**.

### 2. Exact What You See in Discord
* **Success:** `✅ Shop item #1 has been removed.` *(Only you can see this)*
* **Not found:** `❌ Shop item #99 not found.` *(Only you can see this)*
