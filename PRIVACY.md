# Privacy Policy for RookieBot

*Last updated: November 24, 2026*

**RookieBot** ("the Bot", "we", "us", or "our") respects your privacy. This Privacy Policy describes how we collect, use, store, and protect information when you invite and use RookieBot in your Discord servers.

---

## 1. Information We Collect

To provide core Discord bot services, RookieBot collects and processes the minimal amount of data necessary:

### A. Discord Identifiers
- **User IDs:** Numeric Discord IDs of members (used to store leveling XP, AFK status, economy balances, and license key redemption).
- **Guild (Server) IDs:** Numeric IDs of Discord servers (used to store server-specific settings, welcome channels, and logging configurations).
- **Channel & Role IDs:** IDs of channels and roles designated for tickets, logging, starboard, and self-role button panels.

### B. Message Content & Audit Data
- **Auto-Moderation:** Messages are scanned in real time in memory to detect unauthorized invite links (`discord.gg`) and spam floods. Message content is processed ephemerally and is **never stored permanently** in our database.
- **Audit Logs:** When configured by server administrators via `/setlogs`, message edit/delete notifications are sent directly to the server's private audit log channel.
- **Custom Content:** Custom welcome templates, canned tag texts, and sticky messages explicitly set by server staff are saved in the server's database record.

### C. Financial & Billing Information
- We **never** collect, store, or have access to your credit card numbers or banking information.
- Payments made via Discord In-App Subscriptions are handled entirely by Discord.
- Payments made via Stripe / external processors are securely handled by those platforms; we only store the resulting license key code and redemption timestamp.

---

## 2. How We Use Collected Information

We use the collected data exclusively to:
- Deliver requested bot features (support tickets, polls, rank cards, economy, reminders, starboard).
- Enforce server moderation and auto-mod filters configured by server admins.
- Track subscription status and manage Premium tier benefits.
- Monitor service health, stability, and prevent abuse.

We **do not** sell, rent, trade, or monetize your personal information to any third parties.

---

## 3. Data Storage & Security

3.1. **Storage:** All server settings, user XP, and records are stored in a private, encrypted SQLite database hosted on dedicated Oracle Cloud infrastructure with restricted firewall access.  
3.2. **Protection:** We implement industry-standard security safeguards to protect stored data from unauthorized access, alteration, or disclosure.

---

## 4. Data Retention & Deletion Rights

4.1. **Retention:** Data is retained only as long as RookieBot remains in your server or as necessary to maintain active features.  
4.2. **Automatic Removal:** When RookieBot is removed from a server, server-specific configurations can be purged upon request.  
4.3. **Data Deletion Requests (GDPR / Discord Compliance):**  
Users or server owners can request the complete deletion of their stored data (XP records, economy balances, or server settings) at any time by opening an issue on GitHub or contacting the developer directly.

---

## 5. Third-Party Services

RookieBot relies on:
- **Discord API:** Governed by the [Discord Privacy Policy](https://discord.com/privacy).
- **Payment Providers (Discord / Stripe):** Governed by their respective privacy policies.

---

## 6. Updates to This Policy

We may update this Privacy Policy from time to time. Any changes will be published in this document with an updated revision date.

---

## 7. Contact Us

If you have questions, concerns, or data deletion requests regarding this Privacy Policy, please reach out via:
- **GitHub Repository:** [https://github.com/rk-ranjith0143/RookieBot](https://github.com/rk-ranjith0143/RookieBot)
- **Developer:** `@rk-ranjith0143`
