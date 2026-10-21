[← Guide index](../README.md)

# 9. Use cases to configure during the session

Sections 1–6 give you one working code extension. This page is the **menu of use cases**
to build on top of it, in priority order. Pick with the customer based on their stated
concern. Don't try to do them all.

## 🔤 Placeholders: swap these for the customer's real values

Fill these in during scoping, so the use cases read as *their* scenario rather than a generic script:

| Placeholder | Means | Example (in this demo) |
|-------------|-------|------------------------|
| `[SOURCES]` | The systems feeding contacts | `CRM_NA`, `CRM_EMEA`, `DEALER_PORTAL` |
| `[CORE_ENTITY]` | The object whose quality matters most | Contact, Lead, Account, Asset |
| `[DQ_FIELDS]` | The fields the business acts on | email, phone, country (+ state, postcode) |
| `[MATCH_KEY]` | What identity resolution matches on | cleaned email |
| `[SEGMENT]` | A business cut for the scorecard | product line: fire / HVAC / security |
| `[CONSUMER]` | Who uses the clean data | marketing journeys, service, dealer portal |
| `[NEXT_ORG]` | Where this gets promoted | sandbox → production |

> **Start every session by naming the core problem.** The most common real problem behind "we need data quality" is: *the same person exists in several `[SOURCES]`, typed differently, so `[CONSUMER]` either misses them or hits them twice.* If that's the problem, use cases 1–2 prove it directly. Pin the problem before you configure anything.

## Use case 1 — Rules as code *(always do this)*

**Configure:** the extension from sections 4–5: email, phone and country, each with a status plus a cleaned value.
**Prove:** the rules are **unit-tested on a laptop** (24 tests, no org) *before* they touch Data 360, and one change to the script changes every row consistently.
**Myth to bust:** "code extension means unmanaged code." It's versioned (`--package-version`), tested, and promoted through a data kit, which is more governed than SQL pasted into a transform UI.

## Use case 2 — Identity uplift: match on the cleaned email

**Configure:** create the target DLO as **Profile** (it can't be changed later). Map `ABT_Contact_DQ__dll` to **Individual** and **Contact Point Email**, using `email_clean__c` as the email. Then build a match rule on exact email.
**Prove:** 30,000 rows → **18,000 unified profiles**. On raw email, the same rule finds 21,755, and **1,045 of its merges are wrong**: 1,048 unrelated contacts share `noemail@example.com`, `none@test.com` or `na@test.com` ([section 6.3](06-verify-and-iterate.md#step-63-the-identity-story-queries-6-and-7)).
**Why it lands:** fewer duplicates **and** fewer false merges. A placeholder email that fuses a contact in `CRM_NA` with an unrelated one in `CRM_EMEA` is a real compliance problem, not just a cosmetic one.

## Use case 3 — Change detection with the DQ hash

**Configure:** keep `dq_hash__c` and `rule_version__c`. Downstream jobs compare the hash with the last value they processed.
**Prove:** re-upload the file with one changed email. Exactly one hash changes. Then bump `RULE_VERSION`, and **every** hash changes ([section 6.5](06-verify-and-iterate.md#step-65-change-a-rule-and-redeploy)).
**Cost caveat:** the hash saves **downstream** work, such as re-syncing, re-activating or re-scoring. It doesn't make the extension's own run cheaper, because the extension still reads every row.

## Use case 4 — Incremental writes with MERGE / MERGE_UPSERT_DELETE

**Configure:** switch `write_mode` from `OVERWRITE` to `MERGE`, then to `MERGE_UPSERT_DELETE` ([section 6.6](06-verify-and-iterate.md#step-66-write-modes-overwrite-vs-merge)).
**Prove:** a deleted source row (`DP-300006`) survives under MERGE but is removed under MERGE_UPSERT_DELETE, and an updated row (`NA-100001`) updates in place.
**When:** the target is large, consumers can't tolerate a full replace, or source deletes have to flow through.

## Use case 5 — Code extension vs a SQL batch data transform

**Discuss and compare:** build the same email rule as a SQL batch data transform, run both, and compare their Run History.

| | SQL batch data transform | Code extension |
|---|---|---|
| Rules live in | SQL in the transform UI | Python in version control |
| Unit tests | None (test in the org) | `pytest`, no org |
| Billing | Rows processed | Compute time × CU size |
| Best for | Simple joins and filters, SQL-only teams | Many rules, regex-heavy cleansing, reuse across objects, teams who want CI |

**Cost caveat:** neither is free. Measure both on **the customer's volume** (for example 150K and 1M rows) before claiming either is cheaper.

## Use case 6 — DQ scorecard by source and product line

**Configure:** query 4 in [`verification_queries.sql`](../mock_seed/verification_queries.sql), as a calculated insight or a dashboard.
**Prove:** usable-email and usable-phone percentages for each `source_system` × `product_line`. About 8% of phones are unusable in every source, so the fix is a *data-entry standard* across all three, not a tooling change in one. With the customer's real data, this is where one source usually stands out.
**Extension:** add a **release gate**: a second write (APPEND) of one summary row per run to a `ABT_DQ_Run_Summary__dll`, so downstream jobs stop if, say, email usability drops below 85%.

## Use case 7 — Promote to the next org with a data kit

**Configure:** in DevOps, create a **data kit**. Add the **batch data transform**; the code extension comes with it automatically. Add any DLOs `[NEXT_ORG]` doesn't have, then publish and deploy.
**Prove:** the same `rule_version__c` lands in `[NEXT_ORG]` without rebuilding anything by hand.
**When:** the customer asks "how does this get to production?", and they always ask.

---

## Talk track: what customers always ask

- **"Why not just do this in SQL?"** → You can, for a few rules. Once you have dozens of regex rules across several objects, you'll want unit tests, versions and one place to change them. See use case 5.
- **"How many credits does it cost?"** → Compute time × CU size. Every run bills at least 60 seconds; measure your volume. Always set `--cpu-size`. See [section 6](06-verify-and-iterate.md#-cost-say-this-out-loud-before-scheduling).
- **"Can it break identity resolution?"** → It improves it: 18,000 correct profiles instead of 21,755 with 1,045 wrong merges. Use case 2.
- **"What if the rules are wrong?"** → Change one function, bump the version, the tests show the effect, redeploy, and every hash proves the new rule reached every row.
- **"Is our data safe in logs?"** → Only if you never print record values. The logs DLO has no governance policies.

---

[← 8. Golden rules](08-golden-rules.md) · [Guide index](../README.md)
