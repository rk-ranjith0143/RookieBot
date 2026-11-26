# 📝 Module 18: Custom Staff Applications & Forms

Accept staff, creator, event host, or whitelist applications directly inside Discord! Admins configure up to **5 custom questions**, a **private `#staff-apps` review channel**, and an optional **`@AcceptedRole`**. Members click **`📝 Apply Now`** to open a popup Modal form, and staff review submissions with 1-click **`✅ Accept`** / **`❌ Deny`** buttons!

---

## 📑 Commands & Workflows in This Guide
1. [`/apply setup`](#-apply-setup-admin) — Configure questions & post the `📝 Apply Now` panel
2. [Member Experience: Filling the Application Modal](#-member-experience-clicking--apply-now)
3. [Staff Review: `✅ Accept` & `❌ Deny` Buttons](#-staff-review--accept---deny)
4. [`/apply status`](#-apply-status) — Check active channels, role & questions
5. [`/apply disable`](#-apply-disable-admin) — Close applications

---

## ⚙️ `/apply setup` *(Manage Server)*

Posts a persistent **`📝 Apply Now`** card into `panel_channel` and saves up to 5 custom questions in SQLite.

### 1. Parameters
* **`panel_channel`** *(Required)*: Public channel where members click `📝 Apply Now` (e.g., `#apply`).
* **`review_channel`** *(Required)*: Private staff channel where submitted applications appear (e.g., `#staff-apps`).
* **`question1`** *(Required)* + **`question2`–`question5`** *(Optional)*: Up to 5 custom form questions *(keep each under 45 characters so Discord displays the full label cleanly inside the popup!)*.
* **`accept_role`** *(Optional)*: Role automatically granted to accepted applicants.
* **`title`** *(Optional)*: Defaults to `Staff & Team Application`.
* **`description`** *(Optional)*: Instructions shown on the public card.

### 2. Exact What You See in Discord

**A. Public Panel posted in `#apply`:**
```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 8:00 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 📝 Staff & Team Application                                 │
│ Interested in joining our team? Click Apply Now below to    │
│ submit your application!                                    │
│                                                             │
│ 📋 Form Details                                             │
│ • Questions: 3                                              │
│ • Privacy: Reviewed privately by staff.                     │
│                                                             │
│ My Community Server                                         │
├─────────────────────────────────────────────────────────────┤
│ [ 📝 Apply Now ]  (Blurple Button)                          │
└─────────────────────────────────────────────────────────────┘
```

**B. Private confirmation only you see:**
```text
🤖 RookieBot  [APP]  👁️ Only you can see this
✅ Application panel deployed to #apply! Submissions will go to #staff-apps.
```

---

## ✍️ Member Experience: Clicking `📝 Apply Now`

1. A member clicks **`📝 Apply Now`**.
2. Discord pops up a **Modal form** displaying your server's exact configured questions (up to 5 paragraph boxes).
3. When they click **`Submit`**, only they see:
   ```text
   🤖 RookieBot  [APP]  👁️ Only you can see this
   ✅ Your application (#1) has been submitted to the staff team! You will receive a DM once it is reviewed.
   ```

---

## ⚖️ Staff Review: `✅ Accept` & `❌ Deny`

Inside `#staff-apps`, RookieBot posts the full application card:

```text
┌─────────────────────────────────────────────────────────────┐
│ 🤖 RookieBot  [APP]  Today at 8:02 PM                        │
├─────────────────────────────────────────────────────────────┤
│ 📝 New Application (#1)                                     │
│ Applicant: @Alex (alex#0000 - 123456789012345678)           │
│                                                             │
│ Account Created                                             │
│ 2 years ago                                                 │
│                                                             │
│ Status                                                      │
│ ⏳ Pending Review                                           │
│                                                             │
│ Q1. Why do you want to join our staff team?                 │
│ I'm active daily and love helping newcomers.                │
│                                                             │
│ Q2. What is your timezone?                                  │
│ UTC+5:30                                                    │
│                                                             │
│ Application #1 • User ID: 123456789012345678                │
├─────────────────────────────────────────────────────────────┤
│ [ ✅ Accept ]  (Green)          [ ❌ Deny ]  (Red)           │
└─────────────────────────────────────────────────────────────┘
```

* Staff with `Administrator`, `Manage Server`, or `Manage Roles` click **`✅ Accept`** or **`❌ Deny`**.
* RookieBot updates the card color, locks both buttons, grants `accept_role` (if configured & accepted), and **DMs the applicant** with the decision!

---

## 🔍 `/apply status` & 🛑 `/apply disable`

* **`/apply status`**: Privately shows whether applications are `🟢 Open`, the Panel/Review channels, `Accepted Role`, and all numbered questions.
* **`/apply disable`** *(Manage Server)*: Closes the form (`✅ Applications are now closed for this server.`).
