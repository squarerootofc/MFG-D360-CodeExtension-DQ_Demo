[← Guide index](../README.md)

# Mock seed data: Acme Building Technologies (fire, HVAC, security)

Mock contact data for the code extension runbook. It loads into **Data 360** as a
**File Upload** data stream, and the code extension cleans it so you can walk every
[use case in section 9](09-use-cases-to-configure.md) end to end.

> 📝 **All names are placeholders.** Acme Building Technologies (ABT) is fictional. It
> makes fire detection and suppression, HVAC equipment and controls, and access control
> and video security products for commercial buildings. Every account, person, domain
> and phone number is invented. Email domains end in `-demo.*`; US phone numbers use the
> reserved `555-01xx` range.

## The company and its data problem

ABT sells through two direct CRMs and a dealer network. The same facility manager,
fire engineer or security integrator often exists in more than one system, typed
differently each time:

| Source system | Who's in it | ID prefix | Rows |
|---------------|-------------|-----------|------|
| `CRM_NA` | Direct accounts in the US and Canada: hospitals, office towers, school districts, data centers | `NA-` | 12,059 |
| `CRM_EMEA` | Direct accounts in the UK, Germany and France: retail estates, airports, hotels | `EM-` | 9,628 |
| `DEALER_PORTAL` | Contacts registered by dealers and installers in the US, Canada and Australia | `DP-` | 8,313 |

Each contact carries a `product_line`:

| Product line | Rows |
|--------------|------|
| `FIRE_DETECTION` | 5,081 |
| `FIRE_SUPPRESSION` | 4,963 |
| `HVAC_EQUIPMENT` | 4,998 |
| `HVAC_CONTROLS` | 4,979 |
| `SECURITY_ACCESS` | 4,935 |
| `SECURITY_VIDEO` | 5,044 |

## Scale and identity resolution

- **30,000 contact rows, 18,000 real people.**
- **12,000 duplicate identities.** 12,000 people appear a second time from a different
  source system. The duplicate has the same email, but written differently:
  - 4,800 are identical;
  - 2,400 differ by case or spaces;
  - 2,400 are wrapped as `Name <email>`;
  - 2,400 have stray quotes or a trailing `;`.
- **2,100 people have an email that can't be fixed** (placeholder, disposable, malformed or
  blank). None of them is duplicated.
- **The result:** matching on the cleaned `email_clean__c` resolves 30,000 rows to exactly
  **18,000 people (40% consolidation)**. Matching on the raw email, even lower-cased and
  trimmed, finds 21,755, and 1,045 of its merges are **wrong**. Those wrong merges come from
  1,048 unrelated contacts who share `noemail@example.com`, `na@test.com` or `none@test.com`.
  The code extension marks these INVALID, so they never become a match key.

## Files

| File | What it is |
|------|------------|
| `data/abt_contacts_raw.csv` | **The file you upload.** Not committed: run `generate_seed.py` to create it. 30,000 rows, 4.4 MB. The first 20 are hand-written spot checks (`NA-100001`…`DP-300006`); the rest are generated. |
| [`generators/generate_seed.py`](../generators/generate_seed.py) | Rebuilds the CSV in under a second. Uses only the standard library and a fixed seed, so it always produces the same file. To change the scale, edit `GENERATED_PEOPLE`, `BAD_EMAILS` and `DUPLICATES`. |
| [`runbooks/verification_queries.sql`](verification_queries.sql) | Query Editor checks with the expected value next to each one. Covers row counts, status mix, scorecard, spot checks, identity uplift, false merges, the hash, and logs. |

**Columns:** `contact_id, source_system, account_name, first_name, last_name, job_title,
product_line, email, phone, country`. File Upload turns each header into a field with
the same name followed by `__c` (for example, `email` becomes `email__c`).

## How to load

1. Generate the file: `python3 generators/generate_seed.py`. The CSV isn't committed,
   so run this once after cloning, and again whenever you change the generator.
2. Follow [section 2](02-load-mock-data.md). Create a File Upload stream named
   `ABT_Contact_Raw`, with category **Profile** and primary key `contact_id`.
3. Check the load with `SELECT COUNT(*) FROM ABT_Contact_Raw__dll`. It should return **30,000**.

## What maps to what

| Use case | Object | Data 360 category | Where it goes next |
|----------|--------|-------------------|--------------------|
| **1** rules as code | `ABT_Contact_Raw__dll` → `ABT_Contact_DQ__dll` | Profile → Other | Read by the code extension, written by the code extension |
| **2** identity uplift | `ABT_Contact_DQ__dll` (`email_clean__c`) | Profile, if you map it | **Individual** + **Contact Point Email** / **Phone** |
| **3** change detection | `dq_hash__c`, `rule_version__c` | n/a | Downstream "only reprocess what changed" logic |
| **6** DQ scorecard | `source_system__c`, `product_line__c` | n/a | Calculated insight or dashboard |

## Demo hooks baked into the data

- **Placeholder emails over-merge.** 630 contacts, spread across all three sources (308 /
  187 / 135), use `noemail@example.com`. Show query 7 in `verification_queries.sql`, then explain that a
  raw email match rule would fuse them into one "person".
- **People type notes into phone fields.** Values include `see notes`, `TBD`, `front
  desk`, `call site office` and `0000000`. About 8% of phones are unusable in every
  source. Query 4 shows this for each source and product line.
- **Country chaos.** 7,406 rows say `United States`, `U.S.A.`, `Deutschland`, `England`,
  `AUS` and so on. All of them are remediated to ISO2 codes. 865 rows say `Unknown`, `N/A`,
  `--` or `Atlantis`, and stay INVALID.
- **Extensions on phone numbers.** `ext 12`, `x204`, `#3` and `ext. 7` are cut, and the
  number is kept. Status is REMEDIATED, not INVALID.

---

[← 9. Use cases](09-use-cases-to-configure.md) · [Guide index](../README.md)
