# Security Policy 🛡️

The **RookieBot** project takes the security and integrity of community servers, user data, and bot infrastructure seriously. We appreciate responsible disclosure and will make every effort to acknowledge, triage, and patch confirmed vulnerabilities promptly.

---

## 📦 Supported Versions

Security updates and critical patches are actively applied to the following branch:

| Version / Branch | Supported | Notes |
| :--- | :--- | :--- |
| `main` (Latest) | :white_check_mark: Yes | Actively maintained with security fixes |
| `<= 1.0.0` (Legacy `discord-utility-bot`) | :x: No | Please upgrade to the latest `RookieBot` release |

---

## 🚨 Reporting a Vulnerability

**Please DO NOT report security vulnerabilities via public GitHub issues, discussions, or Discord channels.**

If you discover a vulnerability, misconfiguration, or data-handling issue in RookieBot, please submit a report privately via GitHub Private Vulnerability Reporting:

👉 **[Open a Private Security Advisory](https://github.com/rk-ranjith0143/RookieBot/security/advisories/new)**

This ensures your report is encrypted and delivered directly to the project maintainers without exposing server details before a patch is released.

---

## 📝 What to Include in Your Report

To help us investigate and reproduce the issue quickly, please include:
1. **Description:** A clear summary of the vulnerability and its potential impact.
2. **Component Affected:** The specific Cog, command, or file (e.g. `cogs/moderation.py`, `database.py`, `cogs/verification.py`).
3. **Proof of Concept / Reproduction Steps:** Step-by-step instructions or test script demonstrating how the vulnerability can be triggered.
4. **Suggested Mitigation (Optional):** If you have identified a fix or architectural improvement, feel free to include code snippets or patch diffs.

---

## ⏱️ Response Timelines & SLAs

We follow a coordinated vulnerability disclosure process:
* **Initial Acknowledgment:** Within **24 to 48 hours** of receiving your report.
* **Triage & Severity Assessment:** Within **72 hours**, confirming whether the issue is reproducible and determining severity (CVSS).
* **Patch Development & Release:** We prioritize high-severity vulnerabilities and aim to deliver a tested hotfix as quickly as possible.
* **Public Disclosure:** Coordinated with the reporter after a patch has been merged and deployed.

---

## 🎯 Scope

### In-Scope:
* **Privilege Escalation:** Bypassing Discord role hierarchy checks, server administrative permissions, or moderator enforcement rules.
* **SQL Injection / Parameter Tampering:** Vulnerabilities affecting SQLite queries in `database.py`.
* **Remote Code Execution (RCE):** Any vector allowing unauthorized arbitrary execution on the host system or container.
* **Denial of Service (DoS):** Exploits that crash bot loops, lock SQLite transactions indefinitely, or exhaust VPS memory.
* **Data Leakage:** Exposure of server configuration, license keys, or sensitive audit logs.

### Out-of-Scope:
* Vulnerabilities in upstream libraries (e.g., `discord.py`, `aiohttp`, `sqlite3`, Python core) unless directly caused by our usage. (Please report those directly to the upstream maintainers).
* Denial of Service through volumetric network floods targeting Discord's gateway servers or cloud hosts.
* Social engineering attacks targeting server owners, bot developers, or Discord staff.
* Attacks requiring physical access or root/admin access to the user's host machine.

---

## 🔒 Security Best Practices for Self-Hosters

If you host an instance of RookieBot:
1. **Protect Your Token:** Never share your `DISCORD_TOKEN` or commit your `.env` file to public version control.
2. **Enable 2FA:** Require Two-Factor Authentication on your Discord Developer Portal account.
3. **Role Hierarchy:** Ensure the bot's highest role is positioned correctly in your Discord Server Settings — below Server Owners and Administrators, but above regular members.
4. **Firewall & Permissions:** On your VPS or host machine, keep permissions locked (`chmod 600 .env`) and keep your Docker environment updated.

---

Thank you for helping keep **RookieBot** and our community safe! 🚀
