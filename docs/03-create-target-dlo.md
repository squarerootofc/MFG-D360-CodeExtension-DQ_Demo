[← Guide index](../README.md)

# 3. Create the target DLO

The code extension writes to a DLO that **must already exist**, with fields that match
the DataFrame the script produces. Create it empty now.

## Step 3.1: Create the DLO (10 min)

1. Go to **Data Lake Objects**, click **New**, and create a new DLO (not from a template).
2. Set it up:

| Setting | Value |
|---------|-------|
| Name | `ABT_Contact_DQ` |
| API name | `ABT_Contact_DQ__dll` |
| Category | **Other** |

> ⚠️ **You can't change the category later.** Choose **Profile** instead only if you plan to map this DLO to **Contact Point Email** / **Individual** for identity resolution ([use case 2](09-use-cases-to-configure.md#use-case-2--identity-uplift-match-on-the-cleaned-email)). For a first build, **Other** is fine.

## Step 3.2: Add the fields

Every field is **Text** except `processed_at`, which is **DateTime**. Each field's API name is its label followed by `__c`.

| Label | API name | Notes |
|-------|----------|-------|
| dq_key | `dq_key__c` | **Primary key**: `source_system:contact_id` |
| contact_id | `contact_id__c` | |
| source_system | `source_system__c` | `CRM_NA` / `CRM_EMEA` / `DEALER_PORTAL` |
| product_line | `product_line__c` | Passed through for the scorecard |
| email_raw | `email_raw__c` | Exactly what the source sent |
| email_clean | `email_clean__c` | Null unless VALID or REMEDIATED |
| email_status | `email_status__c` | VALID / REMEDIATED / INVALID / MISSING |
| phone_raw | `phone_raw__c` | |
| phone_clean | `phone_clean__c` | |
| phone_status | `phone_status__c` | |
| country_raw | `country_raw__c` | |
| country_iso2 | `country_iso2__c` | |
| country_status | `country_status__c` | |
| dq_hash | `dq_hash__c` | SHA-256 of the rule version + source fields |
| rule_version | `rule_version__c` | `abt-dq-1.0.0` |
| processed_at | `processed_at__c` | **DateTime** |

## Step 3.3: Wait for Active

Wait until the DLO status shows **Active** before going on.

## ✅ Exit check for section 3

- [ ] `ABT_Contact_DQ__dll` exists, is **Active**, and has **16** fields
- [ ] `dq_key__c` is the primary key
- [ ] `processed_at__c` is DateTime, and every other field is Text

---

[← 2. Load the mock data](02-load-mock-data.md) · [Guide index](../README.md) · **Next: [4. Build and test locally →](04-build-and-test-locally.md)**
