# 🎭 Module 6: Self-Roles, Role Management & Auto-Roles

Let members pick their own notification/hobby roles with 1-click buttons, let moderators toggle roles on users quickly, and automatically give roles to new humans or bots the moment they join.

> [!IMPORTANT]
> For all role commands to work, **RookieBot's role must be higher** in **Server Settings → Roles** than every role you want it to give or remove!

---

## 📑 Commands in This Guide
1. [`/rolepanel`](#-rolepanel) — Create a persistent button panel for self-assignable roles (up to 5)
2. [`/rolemenu`](#-rolemenu) — Create a persistent dropdown menu (up to 10 roles, optional Exclusive mode)
3. [`/role`](#-role) — Manually add or remove a role from a member
4. [`/temprole`](#-temprole) — Assign a temporary role that auto-expires cleanly
5. [`/autorole set`](#-autorole-set) — Auto-assign roles when new humans or bots join
6. [`/autorole status`](#-autorole-status) — Check current join auto-role settings
7. [`/autorole remove`](#-autorole-remove) — Turn off auto-roles

---

## 🎭 `/rolepanel`

Builds an interactive role picker embed with up to **5 clickable role buttons**. Clicking a button adds the role if the member doesn't have it, or removes it if they already do! These buttons survive bot restarts.

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/rolepanel title:<text> role1:<@role> [description:<text>] [role2..5:<@role>]` |
| **Who Can Use It** | Members with **Manage Roles** permission |
| **Bot Needs** | **Manage Roles**, `Send Messages`, `Embed Links` |
| **Where It Works** | Channel where you want the panel posted |
| **What Discord Shows** | Public Role Panel with buttons + Ephemeral confirmation to you |

### 2. Parameters
* **`title`** *(Required)*: Heading for the panel (e.g., `Pick Your Notification Roles`).
* **`role1`** *(Required)*: First self-assignable role.
* **`description`** *(Optional)*: Instructions shown above the roles list. Defaults to `Click a button below to get or remove a role!`.
* **`role2` to `role5`** *(Optional)*: Up to 4 additional roles (5 total buttons per panel).

### 3. Exact Step-by-Step Process in Discord
1. Open the channel where you want the role menu (e.g., `#roles`).
2. Type `/rolepanel`.
3. Fill **`title`** and select **`role1`**.
4. *(Optional)* Fill **`description`** and add **`role2`**, **`role3`**, **`role4`**, **`role5`**.
5. Press **`Enter`**.

### 4. Exact What You See in Discord

**A. Public Panel posted in `#roles`:**
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 2:15 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 🎭 Pick Your Notification Roles                             │
│ Click a button below to get or remove a role!               │
│                                                             │
│ Available Roles                                             │
│ • @Announcements                                            │
│ • @Giveaways                                                │
│ • @Events                                                   │
│                                                             │
│ Click a button to toggle your role!                         │
├─────────────────────────────────────────────────────────────┤
│ [ Announcements ]   [ Giveaways ]   [ Events ]              │
└─────────────────────────────────────────────────────────────┘
```

**B. Private confirmation only you see:**
```text
🤖 RookieBot  [APP]  👁️ Only you can see this
✅ Self-role panel created successfully!
```

**C. What a member privately sees when clicking a role button:**
* When added: `➕ Added @Giveaways to your roles!`
* When clicked again to remove: `➖ Removed @Giveaways from your roles.`

### 5. Common Errors & Solutions
* **`❌ You cannot include @everyone in a self-role panel.`** → Choose an actual custom role.
* **`❌ BotRole is a bot-managed role and cannot be assigned manually.`** → Integrated roles (like a bot's own auto-created role or Server Booster role) cannot be given via buttons.
* **`❌ VIP is higher than or equal to my highest role. Move my bot role above VIP in Server Settings > Roles.`** → Drag RookieBot above that role.

---

## 🎨 `/rolemenu`

Creates a sleek **dropdown Select menu** supporting up to **10 roles** in one compact embed! Supports two modes:
* **`exclusive: False` (Default — Multi-Select Toggle):** Members can pick multiple hobby/notification roles at once to add or remove them.
* **`exclusive: True` (Single Choice — Exclusive Mode):** Ideal for **Color Roles**, **Pronouns**, or **Team Roles**—picking a new option automatically removes any other role from that menu!

### 1. Parameters
* **`title`** *(Required)*: Heading for the dropdown card (e.g., `Pick Your Name Color`).
* **`role1`** *(Required)* + **`role2` to `role10`** *(Optional)*: Up to 10 self-assignable roles.
* **`description`** *(Optional)*: Defaults to `Select a role from the dropdown menu below!`.
* **`exclusive`** *(Optional)*: Choose `True` for single-choice switching or `False` for multi-select toggling.

### 2. Exact What You See in Discord

**A. Public Dropdown Role Menu Card:**
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 2:18 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 🎨 Pick Your Name Color                                     │
│ Select a role from the dropdown menu below!                 │
│                                                             │
│ Available Roles                                             │
│ • @Red                                                      │
│ • @Blue                                                     │
│ • @Gold                                                     │
│                                                             │
│ Mode: Single Choice (Exclusive) • Select from the menu below│
├─────────────────────────────────────────────────────────────┤
│ [ ▼ Choose 1 role (Exclusive)...                        ]   │
└─────────────────────────────────────────────────────────────┘
```

**B. What a member privately sees when switching an Exclusive role (`@Red` → `@Blue`):**
```text
🤖 RookieBot  [APP]  👁️ Only you can see this
🎨 Updated! You now have @Blue (removed @Red).
```

---

## 🛡️ `/role`

Quickly toggles a role on a specific member (adds it if missing, removes it if already equipped).

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/role member:<@user> role:<@role> [reason:<text>]` |
| **Who Can Use It** | Members with **Manage Roles** permission |
| **Bot Needs** | **Manage Roles** + higher role than target role |
| **Response Visibility** | Public Embed |

### 2. Parameters
* **`member`** *(Required)*: Target server member.
* **`role`** *(Required)*: Role to add or remove.
* **`reason`** *(Optional)*: Saved in Discord Audit Log and shown in the embed. Defaults to `Updated by moderator`.

### 3. Exact Step-by-Step Process in Discord
1. Type `/role`.
2. Pick **`member`** and **`role`**.
3. *(Optional)* Add **`reason`** and press **`Enter`**.

### 4. Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 2:20 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 🛡️ Role Updated                                             │
│ Added @VIP to @Alex.                                        │
│                                                             │
│ Moderator                                                   │
│ @Moderator                                                  │
│                                                             │
│ Reason                                                      │
│ Event winner                                                │
└─────────────────────────────────────────────────────────────┘
```
*(If the member already had the role, it shows `Removed @VIP from @Alex.` with an orange embed bar.)*

---

## ⏳ `/temprole`

Assigns a role to a member for a limited time (e.g., `6h`, `7d`) and persists the expiry timestamp in SQLite so **RookieBot automatically removes the role** when time is up—even across bot restarts.

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/temprole member:<@user> role:<@role> duration:<time> [reason:<text>]` |
| **Who Can Use It** | Members with **Manage Roles** permission |
| **Bot Needs** | **Manage Roles** + higher role than target role |
| **Response Visibility** | Public Embed |

### 2. Parameters
* **`member`** *(Required)*: Target server member.
* **`role`** *(Required)*: Role to temporarily grant.
* **`duration`** *(Required)*: Role length (`s`, `m`, `h`, or `d`, max `365d`, e.g., `6h`, `7d`).
* **`reason`** *(Optional)*: Saved in Discord Audit Log and shown in the embed. Defaults to `Temporary role assignment`.

### 3. Exact Step-by-Step Process in Discord
1. Type `/temprole`.
2. Pick **`member`**, **`role`**, and enter **`duration`** (e.g., `7d`).
3. *(Optional)* Enter **`reason`** and press **`Enter`**.
4. RookieBot assigns the role immediately and checks every 30 seconds to remove it once expired.

### 4. Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 2:25 PM                        │
├─────────────────────────────────────────────────────────────┤
│ ⏳ Temporary Role Assigned                                  │
│ Granted @Event VIP to @Alex for `7d`.                       │
│                                                             │
│ Expires                                                     │
│ in 7 days                                                   │
│                                                             │
│ Moderator                                                   │
│ @Moderator                                                  │
│                                                             │
│ Reason                                                      │
│ Weekend tournament winner                                   │
└─────────────────────────────────────────────────────────────┘
```

### 5. Common Errors & Solutions
* **`❌ Invalid duration! Use a number followed by \`s\`, \`m\`, \`h\`, or \`d\` (max \`365d\`, e.g., \`6h\`, \`7d\`).`** → Use a single unit with no spaces (`30m`, `6h`, `7d`).
* **`❌ I cannot manage that role because it is equal to or higher than my highest role!`** → Move RookieBot's role above the target role in **Server Settings → Roles**.

---

## 🤖 `/autorole set`

Automatically assigns a role to every new **human member** and/or **bot** as soon as they join the server.

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/autorole set [member_role:<@role>] [bot_role:<@role>]` |
| **Who Can Use It** | Members with **Manage Roles** permission |
| **Bot Needs** | **Manage Roles** + higher role than assigned roles |
| **Response Visibility** | Public Embed |

### 2. Parameters
* **`member_role`** *(Optional)*: Role given automatically to new human joins (e.g., `@Member`).
* **`bot_role`** *(Optional)*: Role given automatically to newly invited bots (e.g., `@Bots`).
*(You must specify at least one of the two!)*

### 3. Exact Step-by-Step Process in Discord
1. Type `/autorole set` and pick it from the slash menu.
2. Select **`member_role`** (e.g., `@Member`) and/or **`bot_role`** (e.g., `@Bots`).
3. Press **`Enter`**.

### 4. Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 2:25 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 🎭 Auto-Roles Configured                                    │
│ • Human Members: @Member                                    │
│ • Bots: @Bots                                               │
│                                                             │
│ New joins will automatically receive their assigned role.   │
└─────────────────────────────────────────────────────────────┘
```

### 5. Common Errors & Solutions
* **`⚠️ Please specify at least one role (member_role or bot_role).`** → You ran `/autorole set` without filling either option.
* **`❌ I cannot assign @Role because it is equal to or higher than my highest role.`** → Move RookieBot higher in **Server Settings → Roles**.

---

## 🔍 `/autorole status`

Shows which Human Member Role and Bot Role are currently assigned on join.

### 1. Exact Step-by-Step Process in Discord
1. Type `/autorole status` and press **`Enter`**.

### 2. Exact What You See in Discord
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 2:26 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 🎭 Auto-Role Status                                         │
│ • Human Member Role: @Member                                │
│ • Bot Role: @Bots                                           │
└─────────────────────────────────────────────────────────────┘
```
*(If none configured: `ℹ️ No auto-roles are currently configured. Use /autorole set.`)*

---

## 🛑 `/autorole remove`

Disables automatic join roles for the server.

### 1. Exact Step-by-Step Process in Discord
1. Type `/autorole remove` and press **`Enter`**.

### 2. Exact What You See in Discord
```text
🤖 RookieBot  [APP]  👁️ Only you can see this
✅ Auto-roles have been disabled for this server.
```
