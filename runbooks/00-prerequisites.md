[← Guide index](../README.md)

# 0. Before the session

## 👤 Roles

| Role | Who | Does what |
|------|-----|-----------|
| **Driver** | One person with the toolchain installed and the permission set assigned | Shares their screen, types every command, clicks every button |
| **Data 360 admin** | Can enable features and assign permission sets | Step 1, plus unblocking permissions on the day |
| **Rules owner** | Knows what counts as a good email, phone or country for the business | Signs off on the rules in [section 4](04-build-and-test-locally.md) and the use cases in [section 9](09-use-cases-to-configure.md) |
| **Everyone else** | Follows along | Asks "why", and tries the SQL in [section 6](06-verify-and-iterate.md) |

> Pick **one** driver. Two people deploying the same extension name to the same org at the same time makes for a confusing Run History.

## 🔑 Lead-time items: start these days ahead

| # | Item | Why it takes time |
|---|------|-------------------|
| 1 | **Data 360 provisioned** in the org (an SDO or sandbox is fine) | Provisioning can take days |
| 2 | **Data Cloud Architect** permission set assigned to the driver, plus CRUD on *Data Custom Code Procedure Definitions* | Needs an admin. Without it, *Create From Code Extension* doesn't appear |
| 3 | **Org isn't BYOK** | Code extension isn't supported in BYOK orgs, and you can't work around it |
| 4 | **Toolchain on the driver's laptop** ([section 1](01-enable-and-toolchain.md#step-12-install-the-local-toolchain)) | Corporate IT may need to approve Docker, Java 17 or Python 3.11 |
| 5 | **Docker allowed**, or the UI upload path agreed | The CLI deploy builds in Docker. The UI upload doesn't need it |
| 6 | **Credit owner agreed** | Runs consume Data 360 credits. Decide who may schedule runs |

## ✅ Copy-paste prerequisites message

Send this to the customer about a week before:

```text
Hi team, ahead of our Data 360 code extension working session, please confirm:

1. Data 360 is provisioned in <ORG NAME>, and it does NOT use Bring Your Own Key.
2. <DRIVER NAME> has the "Data Cloud Architect" permission set, plus CRUD on
   "Data Custom Code Procedure Definitions".
3. <DRIVER NAME>'s laptop has:
     - Python 3.11
     - Azul Zulu OpenJDK 17
     - Docker Desktop, running
     - Salesforce CLI 2.130.9 or later
     - the plugin: sf plugins install @salesforce/plugin-data-code-extension
   If Docker isn't allowed, tell us and we'll deploy through the UI instead.
4. Someone can enable "Code Extension" in Data Cloud Setup > Feature Manager.
5. We'll use mock data only (a fictional building-equipment manufacturer).
   No customer data is needed.

Thanks!
```

## ✅ Exit check for section 0

- [ ] The driver can log in to the org and open **Data Cloud Setup**
- [ ] The permission set is assigned, and the org is confirmed **not BYOK**
- [ ] `python3.11 --version`, `java -version` (17), `docker ps` and `sf version` all work on the driver's laptop
- [ ] Everyone has this repo open, or a link to it

---

[Guide index](../README.md) · **Next: [1. Enable code extension + toolchain →](01-enable-and-toolchain.md)**
