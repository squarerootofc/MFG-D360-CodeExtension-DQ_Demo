-- ============================================================================
-- Verification queries: ABT contact DQ code extension
-- ----------------------------------------------------------------------------
-- Run in Data 360 Query Editor after the batch data transform has run
-- (runbooks/06-verify-and-iterate.md). Expected values come from a local run of
-- code_extension/tests against data/abt_contacts_raw.csv.
--
-- Field names are the DLO field API names. Query Editor is case-insensitive;
-- the code extension script is not (it needs lowercase).
-- ============================================================================

-- 1. Row counts: source and target must match --------------------------------
SELECT COUNT(*) AS raw_rows FROM ABT_Contact_Raw__dll;             -- 30000
SELECT COUNT(*) AS dq_rows, COUNT(DISTINCT dq_key__c) AS dq_keys
FROM ABT_Contact_DQ__dll;                                           -- 30000, 30000

-- 2. Status mix per field -----------------------------------------------------
--    email:   VALID 22,836 · REMEDIATED 5,064 · INVALID 1,576 · MISSING 524
--    phone:   VALID 25,249 · REMEDIATED 2,381 · INVALID 1,469 · MISSING 901
--    country: VALID 20,793 · REMEDIATED 7,406 · INVALID 865   · MISSING 936
SELECT 'email' AS field, email_status__c AS status, COUNT(*) AS n FROM ABT_Contact_DQ__dll GROUP BY email_status__c
UNION ALL
SELECT 'phone', phone_status__c, COUNT(*) FROM ABT_Contact_DQ__dll GROUP BY phone_status__c
UNION ALL
SELECT 'country', country_status__c, COUNT(*) FROM ABT_Contact_DQ__dll GROUP BY country_status__c
ORDER BY 1, 3 DESC;

-- 3. Fully contactable: all three fields VALID or REMEDIATED ---------------  24,183
SELECT COUNT(*) AS fully_contactable
FROM ABT_Contact_DQ__dll
WHERE email_status__c   IN ('VALID', 'REMEDIATED')
  AND phone_status__c   IN ('VALID', 'REMEDIATED')
  AND country_status__c IN ('VALID', 'REMEDIATED');

-- 4. DQ scorecard by source system and product line --------------------------
SELECT source_system__c,
       product_line__c,
       COUNT(*) AS contacts,
       ROUND(100.0 * SUM(CASE WHEN email_status__c IN ('VALID', 'REMEDIATED') THEN 1 ELSE 0 END) / COUNT(*), 1) AS email_usable_pct,
       ROUND(100.0 * SUM(CASE WHEN phone_status__c IN ('VALID', 'REMEDIATED') THEN 1 ELSE 0 END) / COUNT(*), 1) AS phone_usable_pct,
       ROUND(100.0 * SUM(CASE WHEN email_status__c = 'REMEDIATED' THEN 1 ELSE 0 END) / COUNT(*), 1) AS email_fixed_pct
FROM ABT_Contact_DQ__dll
GROUP BY source_system__c, product_line__c
ORDER BY source_system__c, product_line__c;

-- 5. Spot checks (the 20 hand-written rows; expected values in runbooks/06) ------
SELECT contact_id__c,
       email_raw__c, email_clean__c, email_status__c,
       phone_raw__c, phone_clean__c, phone_status__c,
       country_raw__c, country_iso2__c, country_status__c
FROM ABT_Contact_DQ__dll
WHERE contact_id__c IN ('NA-100001', 'NA-100002', 'NA-100003', 'NA-100004', 'NA-100005',
                        'NA-100006', 'NA-100007', 'NA-100008', 'EM-200001', 'EM-200002',
                        'EM-200003', 'EM-200004', 'EM-200005', 'EM-200006', 'DP-300001',
                        'DP-300002', 'DP-300003', 'DP-300004', 'DP-300005', 'DP-300006')
ORDER BY contact_id__c;

-- 6. Identity uplift: how many people would an email match rule find? --------
--    raw, lower/trim only:  21,755   (includes 1,045 false merges on placeholder emails)
--    cleaned email:         18,000   (40% consolidation, no false merges)
SELECT
  COUNT(DISTINCT LOWER(TRIM(email_raw__c)))
    + SUM(CASE WHEN email_raw__c IS NULL OR TRIM(email_raw__c) = '' THEN 1 ELSE 0 END) AS people_by_raw_email,
  COUNT(DISTINCT email_clean__c)
    + SUM(CASE WHEN email_clean__c IS NULL THEN 1 ELSE 0 END)                       AS people_by_clean_email
FROM ABT_Contact_DQ__dll;

-- 7. The false merges: unrelated contacts sharing a placeholder email --------
--    noemail@example.com 630 · na@test.com 236 · none@test.com 182
SELECT LOWER(TRIM(email_raw__c)) AS shared_email, COUNT(*) AS contacts,
       COUNT(DISTINCT source_system__c) AS sources
FROM ABT_Contact_DQ__dll
WHERE email_status__c = 'INVALID'
GROUP BY LOWER(TRIM(email_raw__c))
HAVING COUNT(*) > 1
ORDER BY contacts DESC;

-- 8. Rule version and hash: one version, no null hashes -----------------------
SELECT rule_version__c, COUNT(*) AS n,
       SUM(CASE WHEN dq_hash__c IS NULL THEN 1 ELSE 0 END) AS null_hashes
FROM ABT_Contact_DQ__dll
GROUP BY rule_version__c;                                           -- abt-dq-1.0.0, 30000, 0

-- 9. Run logs (never print record values from the script: this DLO has no governance)
SELECT Timestamp__c, ProcessDefinitionName__c, Message__c
FROM DataCustomCodeLogs__dll
WHERE DataCustomCodeName__c = 'ABT_Contact_DQ'
ORDER BY Timestamp__c DESC
LIMIT 200;
