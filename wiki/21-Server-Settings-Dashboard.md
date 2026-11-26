# ⚙️ Module 21: All-in-One Server Setup Dashboard

Inspect every configured RookieBot module at a glance and toggle **AutoMod shields** or bind **Mod Logs**, **Welcome**, and **Suggestions** channels in 1 click using `/settings`.

---

## 📑 Commands in This Guide
1. [`/settings`](#-settings) — Open the interactive all-in-one server configuration dashboard

---

## ⚙️ `/settings`

### 1. Requirements & Overview
| Property | Value |
| :--- | :--- |
| **Command Syntax** | `/settings` |
| **Who Can Use It** | Members with **Manage Server** permission |
| **Bot Needs** | None beyond standard slash command access |
| **Response Visibility** | Ephemeral Interactive Embed (`👁️ Only you can see this`) |

### 2. What You Can Control Inside `/settings`
1. **🛡️ AutoMod Shields Dropdown**: Flip **Anti-Invite**, **Anti-Spam**, **Mass Mention**, **Word Blacklist**, or **Anti-Raid Guard** On/Off immediately.
2. **📺 Quick Channel Pickers**: Select your **#mod-logs**, **#welcome**, and **#suggestions** text channels from native Discord channel menus.
3. **✨ Enable All AutoMod** & **🔄 Refresh**: Turn on all 5 safety shields in 1 click or reload live stats across Tickets, Applications, Verification, Auto-Roles, Level Roles, Reaction Roles, Starboard, Counting, Birthdays, Temp VCs, Schedules, and Premium status.

### 3. Exact What You See in Discord
```text
🤖 RookieBot  [APP]  👁️ Only you can see this
┌─────────────────────────────────────────────────────────────┐
│ ⚙️ My Community Server — Server Setup Dashboard             │
│ Use the dropdowns below to toggle AutoMod shields or bind   │
│ key channels in 1 click.                                    │
│                                                             │
│ 🛡️ AutoMod Shields          📺 Key Channels                 │
│ • Anti-Invite: 🟢 On        • Mod Logs: #mod-logs           │
│ • Anti-Spam: 🟢 On          • Welcome: #welcome             │
│ • Mass Mention: 🟢 On       • Leave: Not Set                │
│ • Word Blacklist: 🟢 On     • Suggestions: #suggestions     │
│ • Anti-Raid Guard: 🟢 On    • Starboard: #starboard (⭐ 3+)  │
│                             • Counting: #counting (12)      │
│                                                             │
│ 🎭 Roles & Onboarding                                       │
│ • Verification Gate: #verify → @Verified                    │
│ • Auto-Role: Human @Member • Bot @Bots                      │
│                                                             │
│ [ ▼ Toggle an AutoMod shield On/Off...                  ]   │
│ [ ▼ Set Mod-Log Channel...                              ]   │
│ [ ▼ Set Welcome Channel...                              ]   │
│ [ ▼ Set Suggestions Channel...                          ]   │
│ [ ✨ Enable All AutoMod ]  [ 🔄 Refresh ]                   │
└─────────────────────────────────────────────────────────────┘
```
