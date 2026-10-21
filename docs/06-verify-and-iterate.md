[← Guide index](../README.md)

# 6. Verify and iterate

Every query below is in [`mock_seed/verification_queries.sql`](../mock_seed/verification_queries.sql), with its expected value beside it.

## Step 6.1: Counts and status mix

```sql
SELECT COUNT(*), COUNT(DISTINCT dq_key__c) FROM ABT_Contact_DQ__dll;     -- 30000, 30000
```

Expected status mix (query 2):

| Field | VALID | REMEDIATED | INVALID | MISSING |
|-------|------:|-----------:|--------:|--------:|
| Email | 22,836 | 5,064 | 1,576 | 524 |
| Phone | 25,249 | 2,381 | 1,469 | 901 |
| Country | 20,793 | 7,406 | 865 | 936 |

**Fully contactable** (all three fields usable): **24,183 of 30,000** (81%, query 3).

> 🔤 If the numbers are off by a few, check whether the upload trimmed leading spaces or turned blanks into nulls. The script handles both, so **statuses** shouldn't move. If the counts differ by a lot, you're probably running an older script version: check `rule_version__c`.

## Step 6.2: Spot checks (query 5)

```sql
SELECT contact_id__c,
       email_raw__c, email_clean__c, email_status__c,
       phone_raw__c, phone_clean__c, phone_status__c,
       country_raw__c, country_iso2__c, country_status__c
FROM ABT_Contact_DQ__dll
WHERE contact_id__c IN ('NA-100001', 'NA-100002', 'NA-100003', 'NA-100004', 'NA-100005',
                        'NA-100006', 'NA-100007', 'NA-100008', 'EM-200001', 'EM-200002',
                        'EM-200003', 'EM-200004', 'EM-200005', 'EM-200006', 'DP-300001',
                        'DP-300002', 'DP-300003', 'DP-300004', 'DP-300005', 'DP-300006')
ORDER BY contact_id__c;                                                  -- 20 rows
```

Compare these rows with the table below:

| Contact | Raw value(s) | Expected |
|---------|--------------|----------|
| NA-100002 | ` Dana.Lopez@Granite-Demo.com `, `312-555-0199 ext 22` | Email **VALID**, because case and spaces don't count as a fix. Phone **REMEDIATED** to `312-555-0199` |
| NA-100003 | `Raj Patel <raj.patel@ironbridge-demo.com>`, `800-555-1234#9`, `us` | Email **REMEDIATED** to `raj.patel@ironbridge-demo.com`. Phone **REMEDIATED**. Country **VALID** |
| NA-100005 | `noemail@example.com`, `000-000-0000`, `N/A` | All **INVALID** |
| NA-100006 | blank email, `123-456-7890`, blank country | **MISSING** / **INVALID** / **MISSING**, but `dq_hash__c` is **not null** |
| NA-100008 | `grace.kim@mailinator.com` | **INVALID** (disposable domain) |
| EM-200001 | `Deutschland` | **REMEDIATED** to `DE` |
| EM-200002 | `030/1234567` | **INVALID** (contains `/`) |
| EM-200006 | `'liam.oconnor@thameside-demo.co.uk'`, `+44 161 496 0000 ext. 4` | Both **REMEDIATED** |
| DP-300001 | `02 9374 4000 x 15` | **REMEDIATED** to `02 9374 4000` |
| DP-300003 | `noah.young@@summitmech-demo.com` | **INVALID** |
| DP-300004 | `call site office` | **INVALID** |
| DP-300006 | `Atlantis` | **INVALID** |

The tests check all 20 spot-check rows (see `EXPECTED` in [`test_entrypoint.py`](../code_extension/tests/test_entrypoint.py)).

## Step 6.3: The identity story (queries 6 and 7)

This is the moment that lands with business stakeholders:

| Match on | People found | False merges |
|----------|-------------:|-------------:|
| Raw email, lower-cased and trimmed | 21,755 | **1,045**. 1,048 unrelated contacts share `noemail@example.com` (630), `na@test.com` (236) or `none@test.com` (182) |
| `email_clean__c` | **18,000** | **0** |

So cleaning the email first **finds 3,755 more duplicates** *and* **removes 1,045 wrong merges**.
The real answer is 18,000 people from 30,000 rows: 40% consolidation. The 630 contacts on
`noemail@example.com` would otherwise become **one** "person" with 630 contact records.

## Step 6.4: Logs (query 9)

```sql
SELECT Timestamp__c, ProcessDefinitionName__c, Message__c
FROM DataCustomCodeLogs__dll
WHERE DataCustomCodeName__c = 'ABT_Contact_DQ'
ORDER BY Timestamp__c DESC LIMIT 200;
```

> ⚠️ Anyone with access can read `DataCustomCodeLogs__dll`, and **governance policies don't apply to it**. **Never `print()` record values or PII** from the script. Log counts and step names only.

## Step 6.5: Change a rule and redeploy

This is the loop you'll repeat forever. Scenario: *ABT sold its Kingsway Airports
contract, and every `kingsway-demo.co.uk` address now bounces.*

1. In `entrypoint.py`, add `"kingsway-demo.co.uk"` to `JUNK_DOMAINS`.
2. Bump `RULE_VERSION = "abt-dq-1.1.0"`. Every hash changes, which proves the new rules reached every row.
3. Run `pytest`. **1 test fails:** people by clean email is now **18,854**, not 18,000. The test caught the change. Update the expected value to 18,854 (the rules owner confirms that's intended).
4. Run `script scan`, then `script run`.
5. `script deploy … --package-version 1.1.0`
6. On the transform, check it uses the new version (edit it and reselect the extension if needed). Click **Run Now**.
7. Check:
   - `SELECT rule_version__c, COUNT(*) FROM ABT_Contact_DQ__dll GROUP BY 1` returns **one** row: `abt-dq-1.1.0`, 30,000.
   - Email INVALID is now **3,614** (it was 1,576).

Undo the change afterwards (or keep it as v1.1.0) so the numbers in this guide still match.

## Step 6.6: Write modes, OVERWRITE vs MERGE

| Mode | What it does | Use when |
|------|--------------|----------|
| `WriteMode.OVERWRITE` | Replaces the whole target | Full refresh. Simplest, and what this demo uses |
| `WriteMode.APPEND` | Adds rows | Run logs and history tables |
| `WriteMode.MERGE` | Upserts on the target's primary key (`dq_key__c`) | Incremental runs. Rows deleted at source **stay** in the target |
| `WriteMode.MERGE_UPSERT_DELETE` | Upserts **and** deletes. Every row needs `_merge_record_type` set to UPSERT or DELETE | Incremental runs where source deletes must flow through |

```python
from datacustomcode.io.writer.base import MERGE_RECORD_TYPE_COLUMN, MergeRecordType, WriteMode
from pyspark.sql.functions import lit

client.write_to_dlo(TARGET_DLO, result, write_mode=WriteMode.MERGE)

out = result.withColumn(MERGE_RECORD_TYPE_COLUMN, lit(MergeRecordType.UPSERT))
client.write_to_dlo(TARGET_DLO, out, write_mode=WriteMode.MERGE_UPSERT_DELETE)
```

**To try it:**
1. Delete `DP-300006` from the CSV and change `NA-100001`'s email.
2. Re-upload the file. Data Streams → **Update** replaces the data, and the columns must match the original exactly.
3. Rerun under each mode. For each one, note whether DP-300006 disappears, whether NA-100001 updates, and the rows written.

## 💰 Cost: say this out loud before scheduling

| What | Billed as | Shows in Digital Wallet under |
|------|-----------|-------------------------------|
| Deployed run | **Compute hours × CU rate**: CPU_L 4 · XL 8 · 2XL 16 · 4XL 32 CU/hr. Runs under 1 minute bill as 60 seconds; after that, per second | *Code Extension* |
| Local `script run` | Query API reads | *Data Queries* |
| A SQL batch data transform (for comparison) | Rows processed: the larger of rows read and rows written | *Batch Data Transforms* |

- A 30,000-row run on CPU_L is small. Take the runtime from Run History and multiply it by 4 CU/hr to show the real number.
- **A schedule left running on a demo org isn't small.** Turn it off when the session ends.
- Leaving `--cpu-size` off gets you CPU_2XL, at **4×** the CPU_L rate.

## Step 6.7: Schedule and clean up

- **Schedule:** set a schedule on the transform only after manual runs are clean, and only if someone owns the credits.
- **Clean up**, in this order:
  1. the batch data transform;
  2. the code extension deployment;
  3. `ABT_Contact_DQ__dll`;
  4. the data stream;
  5. `ABT_Contact_Raw__dll`.

## ✅ Exit check for section 6

- [ ] Status mix matches the table in 6.1
- [ ] People by clean email = **18,000**; people by raw email = **21,755**
- [ ] Logs show the run and contain **no record values**
- [ ] One full change → test → deploy → run loop completed (6.5)
- [ ] Someone has said the cost model out loud

---

[← 5. Deploy and run](05-deploy-and-run.md) · [Guide index](../README.md) · **Next: [7. Troubleshoot →](07-troubleshoot.md)**
