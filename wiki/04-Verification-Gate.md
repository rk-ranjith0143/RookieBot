# ✅ Module 4: 1-Click Member Verification Gate

Stop bot raids and unverified accounts before they can view or spam your main channels. Members join, read your rules card, and click one green **`✅ Verify`** button to unlock their Member role.

### 📋 Quick Server Channel Setup Tip
1. Create a role called **`Verified`** (or **`Member`**).
2. Drag **RookieBot's role** *above* the `Verified` role in **Server Settings → Roles**.
3. Hide your normal channels from `@everyone` (`View Channel: ❌`) and allow `Verified` (`View Channel: ✅`).
4. Leave `#verify` visible to `@everyone` (`View Channel: ✅`, `Send Messages: ❌` so users only click the button).
5. Run `/verifysetup`!

---

## 📑 Commands & Interactive Flows in This Guide
1. [`/verifysetup`](#-verifysetup) — Post the persistent verification button panel
2. [What Members See Clicking `✅ Verify`](#-member-experience-clicking--verify)
3. [`/verifystatus`](#-verifystatus) — Check active verification settings
4. [`/verifyremove`](#-verifyremove) — Disable the verification gate

---

## 🛡️ `/verifysetup`

Deploys a persistent verification embed with a green **`✅ Verify`** button into your chosen channel. The button keeps working even if the bot restarts!

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/verifysetup channel:<#channel> role:<@role> [title:<text>] [description:<text>]` |
| **Who Can Use It** | Members with **Administrator** permission |
| **Bot Needs** | **Manage Roles**, `Send Messages`, `Embed Links` |
| **Where It Works** | Any server text channel |
| **What Discord Shows** | Public Verification Card with button in target channel + Ephemeral confirmation to you |

### 2. Parameters
* **`channel`** *(Required)*: Text channel where the verification card will be posted (e.g., `#verify`).
* **`role`** *(Required)*: Role granted when someone clicks `✅ Verify` (e.g., `@Verified`).
* **`title`** *(Optional)*: Custom header. Defaults to `Server Member Verification`.
* **`description`** *(Optional)*: Custom instructions. Defaults to `Click the button below to verify your account and unlock access to the server.`

### 3. Exact Step-by-Step Process in Discord
1. Type `/verifysetup` in any text channel.
2. In **`channel`**, select `#verify`.
3. In **`role`**, select `@Verified`.
4. *(Optional)* Customize **`title`** and **`description`** if you want custom rules text.
5. Press **`Enter`**.

### 4. Exact What You See in Discord

**A. Public Verification Panel posted in `#verify`:**
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 1:30 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 🛡️ Server Member Verification                               │
│ Click the button below to verify your account and unlock    │
│ access to the server.                                       │
│                                                             │
│ 📜 Community Rules                                          │
│ By clicking Verify, you agree to abide by our server rules  │
│ and Discord's Terms of Service.                             │
│                                                             │
│ My Community Server                                         │
├─────────────────────────────────────────────────────────────┤
│ [ ✅ Verify ]  (Green Button)                               │
└─────────────────────────────────────────────────────────────┘
```

**B. Private confirmation only you see:**
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 1:30 PM  👁️ Only you can see │
│ ✅ Verification gate successfully deployed to #verify using │
│ role @Verified!                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5. Real-World Examples
* **Standard setup:** `/verifysetup channel:#verify role:@Verified`
* **Custom welcome rules:** `/verifysetup channel:#rules role:@Member title:Welcome! Verify Here description:Read rules 1-5 above, then click Verify to enter chat.`

### 6. Common Errors & Solutions
* **`❌ I cannot assign @Verified because it is equal to or higher than my highest role.`** → Move **RookieBot** above `@Verified` in **Server Settings → Roles**.

---

## 🖱️ Member Experience: Clicking `✅ Verify`

Everything a member sees after clicking **`✅ Verify`** is **ephemeral** (private to them so the `#verify` channel stays spotless):

* **First-time verification (Success):**
  ```text
  🤖 RookieBot  [APP]  👁️ Only you can see this
  🎉 You have been successfully verified! Welcome to My Community Server!
  ```
* **If they already have the role and click again:**
  ```text
  🤖 RookieBot  [APP]  👁️ Only you can see this
  ℹ️ You are already verified on this server!
  ```
* **If an admin disabled verification or deleted the role:**
  ```text
  🤖 RookieBot  [APP]  👁️ Only you can see this
  ❌ Verification is currently disabled or not configured on this server.
  ```

---

## 🔍 `/verifystatus`

Shows whether verification is active, which channel hosts the panel, and which role is granted.

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/verifystatus` |
| **Who Can Use It** | `@everyone` |
| **Response Visibility** | Public Embed (or Ephemeral notice if not set up) |

### 2. Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 1:35 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 🛡️ Verification Gate Status                                 │
│                                                             │
│ Status         Channel       Role Granted                   │
│ 🟢 Active      #verify       @Verified                      │
└─────────────────────────────────────────────────────────────┘
```
*(If not configured: `ℹ️ Verification is currently disabled or not set up. Use /verifysetup.`)*

---

## 🛑 `/verifyremove`

Turns off the verification gate in the database so clicking existing `✅ Verify` buttons will no longer grant roles.

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/verifyremove` |
| **Who Can Use It** | Members with **Administrator** permission |
| **Response Visibility** | Ephemeral *(Only you can see this)* |

### 2. Exact What You See in Discord
* **When disabled:**
  ```text
  🤖 RookieBot  [APP]  👁️ Only you can see this
  ✅ Verification gate has been disabled.
  ```
* **If it wasn't set up:**
  ```text
  🤖 RookieBot  [APP]  👁️ Only you can see this
  ℹ️ Verification was not configured.
  ```
