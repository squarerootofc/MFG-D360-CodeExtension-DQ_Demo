[← Guide index](../README.md)

# 2. Load the mock data

You'll load **30,000 contacts** for Acme Building Technologies from three source systems
(`CRM_NA`, `CRM_EMEA`, `DEALER_PORTAL`) into one DLO. See the
[data design](DATA_DESIGN.md) for the company story and the demo hooks
built into the data.

## Step 2.1: Generate the file

```bash
python3 generators/generate_seed.py      # wrote 30000 rows to abt_contacts_raw.csv
```

The CSV isn't committed to the repo, so you need to run this once after cloning. Its seed is fixed, so everyone gets the same file.

## Step 2.2: Create a File Upload data stream (10 min)

1. In the Data Cloud app, go to **Data Streams**, click **New**, and choose **File Upload**.
2. Upload `data/abt_contacts_raw.csv` (4.4 MB; the File Upload limit is 2 GB).
3. Set the stream up:

| Setting | Value |
|---------|-------|
| Object name | `ABT_Contact_Raw` (its DLO API name will be `ABT_Contact_Raw__dll`) |
| Category | **Profile** |
| Primary key | `contact_id` |
| Data space | `default` |

4. Leave every field as **Text**, then deploy the stream.

## Step 2.3: Check the field API names (2 min)

When the stream has finished ingesting, open **Data Lake Objects**, then
**ABT_Contact_Raw**, then **Fields**. The script reads these six fields:

| Field API name | The script reads it as |
|----------------|------------------------|
| `contact_id__c` | `contact_id__c` |
| `source_system__c` | `source_system__c` |
| `product_line__c` | `product_line__c` |
| `email__c` | `email__c` |
| `phone__c` | `phone__c` |
| `country__c` | `country__c` |

> 🔤 If an API name differs (for example `Email__c`), it still works, because the script uses **lowercase**. If the *name itself* differs (for example `email_address__c`), change the column list in `transform()` in [`entrypoint.py`](../code_extension/payload/entrypoint.py).

## Step 2.4: Count the rows

In **Query Editor**:

```sql
SELECT source_system__c, COUNT(*) FROM ABT_Contact_Raw__dll GROUP BY source_system__c;
-- CRM_NA 12,059 · CRM_EMEA 9,628 · DEALER_PORTAL 8,313   (30,000 total)
```

## ✅ Exit check for section 2

- [ ] The stream shows **Active**, and the last run shows **Success**
- [ ] `ABT_Contact_Raw__dll` has **30,000** rows, split 12,059 / 9,628 / 8,313
- [ ] The six field API names above are present

---

[← 1. Enable + toolchain](01-enable-and-toolchain.md) · [Guide index](../README.md) · **Next: [3. Create the target DLO →](03-create-target-dlo.md)**
