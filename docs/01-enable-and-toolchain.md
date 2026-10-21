[← Guide index](../README.md)

# 1. Enable code extension + toolchain

## Step 1.1: Enable Code Extension in the org (2 min)

1. Open **Data Cloud Setup**, then **Feature Management**, then **Feature Manager**.
2. Click **Enable** next to **Code Extension**, accept the terms, and confirm. You may need to refresh the page before **Code Extension** is visible.
3. Check that **Code Extension** now appears in Data Cloud Setup under **Developer Tools**.

## Step 1.2: Install the local toolchain

This takes 20–40 minutes, once per laptop.

| Tool | Version | Check |
|------|---------|-------|
| Python | **3.11.x** exactly | `python3.11 --version` |
| Java | Azul Zulu OpenJDK **17** | `java -version` |
| Docker Desktop | running (needed for the CLI deploy only) | `docker ps` |
| Salesforce CLI | ≥ 2.130.9 | `sf version` |
| Code Extension plugin | ≥ 0.1.5 | `sf plugins` |

```bash
# macOS
brew install pyenv && pyenv install 3.11
brew install --cask zulu@17 docker
npm install -g @salesforce/cli        # or: sf update
sf plugins install @salesforce/plugin-data-code-extension
sf plugins update
```

> 🔤 **Why exactly 3.11 and Java 17?** The Data 360 runtime is PySpark on Python 3.11. Local runs and unit tests start a real Spark session, and Spark needs a JVM. Other versions often work for unit tests, but then fail on `script run` or deploy.

**Optional:** if you use Claude Code, install Salesforce's skills. They can look up live DLO schemas while you write a script.

```bash
npx skills add forcedotcom/sf-skills --skill data360-code-extension-generate data360-schema-get
```

## Step 1.3: Log the CLI in to the org (2 min)

```bash
sf org login web --alias abt-demo --instance-url https://<your-domain>.my.salesforce.com
sf org display --target-org abt-demo        # Connected status, correct username
```

Every command in later sections uses `--target-org abt-demo`.

## ✅ Exit check for section 1

- [ ] **Code Extension** appears under Data Cloud Setup → **Developer Tools**
- [ ] `sf plugins` lists `@salesforce/plugin-data-code-extension`
- [ ] `sf data-code-extension script --help` prints the `init`, `scan`, `run`, `zip` and `deploy` subcommands
- [ ] `sf org display --target-org abt-demo` shows **Connected**

---

[← 0. Before the session](00-prerequisites.md) · [Guide index](../README.md) · **Next: [2. Load the mock data →](02-load-mock-data.md)**
