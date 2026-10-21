# Building a Data 360 Code Extension for Contact Data Quality: Hands-On Runbook

**Audience:** Salesforce admin / Data 360 architect + a Python-capable data engineer

**Session:** ~half-day hands-on working session (about 2 hours of building, plus discussion)

**Format:** A **designated driver** shares their screen and we build together, step by step; everyone else follows along.

**Goal:** Leave with a deployed **code extension** that reads 30,000 messy contacts from three source systems, validates and remediates email, phone and country, and writes a clean DQ object with a **DQ hash**. It should run through a batch data transform and be **verified** end to end. You'll also understand when a code extension beats a SQL batch data transform, what it costs, and which of the [use cases in section 9](runbooks/09-use-cases-to-configure.md) to configure next.

> **What a "code extension" is here:** your own **Python (PySpark)** script, deployed into Data 360 and run on Data 360 compute through a **batch data transform**. It reads DLOs and writes DLOs, like a SQL transform. The difference is that the rules are real code, so you can unit-test them on a laptop, version them, and change them in one place.

---

> 📝 **Disclaimer: all names are placeholders.** **Acme Building Technologies (ABT)** is a fictional maker of fire, HVAC and security equipment for buildings. Every account, person, email domain, phone number and object name in this runbook (for example `ABT_Contact_Raw__dll`, `CRM_NA` or `harborview-demo.com`) is a **generic placeholder for demonstration**. Replace them with your own. Never load real customer data into a demo org.

---

## 📑 Table of contents

| # | Section | What's in it |
|---|---------|--------------|
| 0 | **[Before the session](runbooks/00-prerequisites.md)** | Prerequisites, the "driver", lead-time items (Data 360, permission set, laptop toolchain, Docker) + a **copy-paste prerequisites message** |
| 1 | **[Enable code extension + toolchain](runbooks/01-enable-and-toolchain.md)** | Feature Manager, Python 3.11, Java 17, Docker, sf CLI + plugin, CLI login |
| 2 | **[Load the mock data](runbooks/02-load-mock-data.md)** | File Upload stream for 30,000 ABT contacts → `ABT_Contact_Raw__dll` |
| 3 | **[Create the target DLO](runbooks/03-create-target-dlo.md)** | Empty `ABT_Contact_DQ__dll` with 16 fields, created before any run |
| 4 | **[Build and test locally](runbooks/04-build-and-test-locally.md)** | `script init`, the script, 24 unit tests, `scan`, local `run` |
| 5 | **[Deploy and run](runbooks/05-deploy-and-run.md)** | CLI or UI deploy, batch data transform *Create From Code Extension*, Run History |
| 6 | **[Verify and iterate](runbooks/06-verify-and-iterate.md)** | Expected numbers, spot checks, logs, change → redeploy loop, write modes, cost |
| 7 | **[Troubleshoot](runbooks/07-troubleshoot.md)** | Common errors & fixes |
| 8 | **[Golden rules](runbooks/08-golden-rules.md)** | Rules to keep on screen |
| 9 | **[Use cases to configure](runbooks/09-use-cases-to-configure.md)** | The menu: rules as code, identity uplift, hash change detection, MERGE, code extension vs SQL transform, DQ scorecard, promote with a data kit + talk track |

## 🗂️ Repo layout

| Folder | What's in it |
|--------|--------------|
| [`runbooks/`](runbooks/) | Sections 0–9 above, plus [`DATA_DESIGN.md`](runbooks/DATA_DESIGN.md) (the ABT mock data story and demo hooks) and [`verification_queries.sql`](runbooks/verification_queries.sql) (Query Editor checks with expected values) |
| [`code_extension/`](code_extension/README.md) | The script you deploy and its 24 unit tests |
| [`generators/`](generators/generate_seed.py) | `generate_seed.py`: rebuilds the 30,000-row mock CSV (fixed seed, same file every time) |
| `data/` | Where the generated CSV lands. **Gitignored**: run `python3 generators/generate_seed.py` after cloning |
| [`docs/`](docs/deck.html) | `deck.html`: a 19-slide overview deck (open it in a browser, use ← →) |

---

## 🔑 Admin prerequisites: MUST be done first

<details>
<summary><strong>Show admin setup steps</strong></summary>

Before any of the hands-on steps work, confirm:

1. **Data 360 is provisioned** in the target org, and the driver's user has the **Data Cloud Architect** permission set. To run the extension from a transform, that user also needs CRUD on **Data Custom Code Procedure Definitions**.
2. **The org doesn't use Bring Your Own Key (BYOK).** Code extension isn't supported in BYOK orgs.
3. **The driver's laptop has the toolchain installed:** Python **3.11**, Azul Zulu OpenJDK **17**, **Docker Desktop** (running), and Salesforce CLI ≥ 2.130.9 with the `@salesforce/plugin-data-code-extension` plugin. Corporate laptops often block Docker. If so, plan on the **UI upload** deploy path ([section 5](runbooks/05-deploy-and-run.md)).
4. **Someone owns the credits.** Code extension runs consume Data 360 credits ([section 6](runbooks/06-verify-and-iterate.md#-cost-say-this-out-loud-before-scheduling)). In a shared org, agree who is allowed to schedule.

> ⚠️ Missing the **permission set** or the **Code Extension feature** is the **#1 day-of blocker**. A laptop that can't run **Docker** or install **Python 3.11** is **#2**. Check both **before the session**.

</details>

---

## ⚡ Quick reference: the whole flow

<details>
<summary><strong>Show the end-to-end path</strong></summary>

```text
Laptop                               Data 360                                    Downstream
──────                               ────────                                    ──────────
abt_contacts_raw.csv  ──upload──►    ABT_Contact_Raw__dll (30K rows, 3 sources)
                                              │
entrypoint.py  ──pytest (24)                  │  read
   │         ──scan / run                     ▼
   └──deploy──────────────────►      Code extension "ABT_Contact_DQ"           (optional) map to
                                     run by a batch data transform        ──►  Contact Point Email /
                                              │  write (OVERWRITE | MERGE)     Individual → identity
                                              ▼                                resolution: 30K → 18K
                                     ABT_Contact_DQ__dll
                                     status + clean value per field, dq_hash
```

**Once per org:** enable Code Extension → load the CSV stream → create the empty target DLO.
**Every change:** edit rule → bump `RULE_VERSION` → `pytest` → `scan` → `deploy` → Run Now → verify.
**Then pick use cases** from [section 9](runbooks/09-use-cases-to-configure.md): identity uplift · hash change detection · MERGE · code extension vs SQL · DQ scorecard · data kit.

</details>

---

➡️ **Start here: [0. Before the session](runbooks/00-prerequisites.md)**
